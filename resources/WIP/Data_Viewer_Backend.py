from datetime import date, datetime
import mysql.connector
from cryptography.fernet import Fernet
import logging
from tkinter import messagebox
from configparser import ConfigParser
config = ConfigParser()
config.read("CONFIG.ini")
from config import *
from ..Logics import DB
from ..LoginSystem import LoginSystem

################################    Path variables and Setup  ###########################################################
log_path = config["Path Variables" ]["Log_PATH"]

logging.basicConfig(filename="data_viewer.log",
                    format='%(asctime)s %(levelname)s: %(message)s   func:%(funcName)s',
                    )
logger=logging.getLogger()
logger.setLevel(logging.INFO)
##############################################################################################################
class GlobalVar():
    user_name = ""
    def set_user_name(name):
        GlobalVar.user_name = name
##############################################################################################################
def error_msg(text):
    return messagebox.showerror("Error",text)
##############################################################################################################
def init_DB():
    """Establish a connection to MySQL database
    """
    global db , cursor
    try:
        fernet = Fernet(b'DQ8rEkx7wCZAAD4AWKUrJ8dTlPhaAguPfSCCKGCV-30=')
        MySQL_str = config["MySQL Variables"]['MySQL_str'].encode()
        MySQL_str = fernet.decrypt(MySQL_str).decode()
        MySQL_str = MySQL_str.split("|")
        db = mysql.connector.connect(
            host=MySQL_str[0],
            port=MySQL_str[1],
            user= MySQL_str[2],
            passwd=MySQL_str[3],
            database=MySQL_str[4],
            buffered=True
        )
        cursor =  db.cursor()
    except:
        msg = "Couldn't connect to database!!"
        messagebox.showerror("ERORR",msg)
        logger.error(msg)
        db = cursor = None
    return db , cursor
##############################################################################################################
def update_log_table(process_name, old_description="", new_description="",reason=""):
    if type(new_description) is list or type(new_description) is tuple:
        new_description  = "(" +  ', '.join(map(str, new_description)) + ')'
    if type(old_description) is list or type(old_description) is tuple:
        old_description  = "(" +  ', '.join(map(str, old_description)) + ')'
    user_name = LoginSystem.user_name
    DB.cursor.execute("INSERT INTO logger (program, process_name, old_description, new_description, reason, time_added , user_name) " "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                   ("Data Viewer", process_name, old_description, new_description, reason,datetime.now() ,user_name)       )
    DB.conn.commit()
##############################################################################################################
def checkCompletelyFulfilledID(order_id):
    try:
        DB.cursor.execute("SELECT quantity, fulfilled_quantity FROM delivery_orders WHERE id = %s", (order_id,))
        do_data = DB.cursor.fetchone()
        if do_data and int(do_data[0]) > int(do_data[1]):
            return True
        else:
            return False
    except Exception as e:
        messagebox(f"Error while checking order fulfillment: {str(e)}")
        return False
##############################################################################################################
def checkCompletelyFulfilledNo(order_no):
    try:
        DB.cursor.execute(
            "SELECT quantity, fulfilled_quantity FROM delivery_orders WHERE delivery_order = %s",
            ((order_no,)))
        do_data = DB.cursor.fetchall()

        for do in do_data:
            if int(do[0]) > int(do[1]):
                return True

        return False
    except Exception as e:
        messagebox(f"Error while checking order fulfillment: {str(e)}")
        return False
##############################################################################################################
def archiveDeliveryOrder(id):
    user_name = LoginSystem.user_name
    DB.cursor.execute("SELECT id, customer ,part_no, quantity, uom ,delivery_order ,delivery_date ,fulfilled_quantity ,weight_limit , cartons_id, time, log_id, user_name FROM delivery_orders WHERE id = %s", (id,))
    deliveryOrderInfo = DB.cursor.fetchone()
    DB.cursor.execute("INSERT INTO archived_delivery_orders (id, customer ,part_no, quantity, uom ,delivery_order ,delivery_date ,fulfilled_quantity ,weight_limit,cartons_id , time_added, time_archived, log_id, user_name,user_name_archived) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);" ,
                   (deliveryOrderInfo[0],deliveryOrderInfo[1],deliveryOrderInfo[2],deliveryOrderInfo[3],deliveryOrderInfo[4],deliveryOrderInfo[5],deliveryOrderInfo[6],deliveryOrderInfo[7],deliveryOrderInfo[8],deliveryOrderInfo[9],deliveryOrderInfo[10],datetime.now(),deliveryOrderInfo[11],deliveryOrderInfo[12],user_name))
    description = "(" + str(deliveryOrderInfo[1]) + "," + str(deliveryOrderInfo[2]) + "," + str(deliveryOrderInfo[3]) + "," + str(deliveryOrderInfo[7]) \
                  + "," + str(deliveryOrderInfo[4]) + "," + str(deliveryOrderInfo[5]) + "," + str(deliveryOrderInfo[6]) + ")"
    update_log_table("DO Archived", "", description)
    DB.cursor.execute("SELECT id FROM archived_delivery_orders ORDER BY id DESC")
    insertedId = DB.cursor.fetchone()
    insertedId = int(insertedId[0])
    DB.cursor.execute("SELECT id FROM logger ORDER BY id DESC")
    loggerId = DB.cursor.fetchone()
    loggerId = int(loggerId[0])
    DB.cursor.execute("UPDATE archived_delivery_orders SET log_id = %s WHERE id = %s", (loggerId, insertedId))
    DB.conn.commit()
    #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
    #               (id,deliveryOrderInfo[2], 0, "DO Archived", datetime.now()))
    DB.conn.commit()
    DB.cursor.execute("SELECT id, part_no, carton_quantity,carton_no, date_codes, earliest_date_code, remarks , loose_quantity , delivery_id, packing_date, log_id, time_added, user_name FROM carton_table WHERE delivery_id = %s;" ,(id,))
    carton_records = DB.cursor.fetchall()
    carton_records= list(map(list, carton_records))
    for carton in carton_records:
        DB.cursor.execute("INSERT INTO archived_carton_table (id,part_no, carton_quantity,carton_no, date_codes, earliest_date_code, remarks , loose_quantity , delivery_id , packing_date, time, log_id, time_added, user_name, user_name_archived) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                       (carton[0],carton[1],carton[2],carton[3],carton[4],carton[5],carton[6],carton[7],carton[8] , carton[9], datetime.now(), carton[10], carton[11], carton[12], user_name)  )
    DB.conn.commit()
    DB.cursor.execute("DELETE FROM delivery_orders WHERE id = %s", (id,))
    DB.cursor.execute("DELETE FROM carton_table WHERE delivery_id = %s", (id,))
    logger.info("Delivery Order ID " + str(id) + " has been archived.")
    DB.conn.commit()
##############################################################################################################
def archive_fulfilled_order_by_no(deliveryOrderNoInput):
    process_info = []
    DB.cursor.execute("SELECT id FROM delivery_orders WHERE delivery_order = %s AND quantity = fulfilled_quantity", (deliveryOrderNoInput,))
    idAllocation = DB.cursor.fetchall()
    idAllocation= list(map(list, idAllocation))
    for a in range(len(idAllocation)):
        archiveDeliveryOrder(idAllocation[a])
        process_info.append("\n* Delivery Order ID " + str(idAllocation[a]) + " archival is successful!")
    process_info.append("\n* Delivery Order No " + str(deliveryOrderNoInput) + " archival is successful!")
    return process_info
##############################################################################################################
def archive_all_orders_by_no(deliveryOrderNoInput):
    process_info = []
    DB.cursor.execute("SELECT id FROM delivery_orders WHERE delivery_order = %s", (deliveryOrderNoInput,))
    idAllocation = DB.cursor.fetchall()
    idAllocation= [i[0] for i in idAllocation ]
    for a in range(len(idAllocation)):
        archiveDeliveryOrder(idAllocation[a])
        process_info.append("\n* Delivery Order ID " + str(idAllocation[a]) + " archival is successful!")
    process_info.append("\n* Delivery Order No " + str(deliveryOrderNoInput) + " archival is successful!")
    return process_info
##############################################################################################################
# Must be in YYYY-MM-DD format
def archive_fulfilled_order_by_date(deliveryDate):
    process_info = []
    DB.cursor.execute("SELECT id FROM delivery_orders WHERE delivery_date = %s AND quantity = fulfilled_quantity", (deliveryDate,))
    idAllocation = DB.cursor.fetchall()
    idAllocation= list(map(list, idAllocation))
    for a in range(len(idAllocation)):
        archiveDeliveryOrder(idAllocation[a])
        process_info.append("\n* Delivery Order ID " + str(idAllocation[a]) + " archival is successful!")
    process_info.append("\n* Delivery Order Date " + str(deliveryDate) + " archival is successful!")
    return process_info
##############################################################################################################
# Must be in YYYY-MM-DD format
def archive_all_orders_by_date(deliveryDate):
    process_info = []
    DB.cursor.execute("SELECT id FROM delivery_orders WHERE delivery_date = %s", (deliveryDate,))
    idAllocation = DB.cursor.fetchall()
    idAllocation= [i[0] for i in idAllocation ]
    for a in range(len(idAllocation)):
        archiveDeliveryOrder(idAllocation[a])
        process_info.append("\n* Delivery Order ID " + str(idAllocation[a]) + " archival is successful!")
    process_info.append("\n* Delivery Order Date " + str(deliveryDate) + " archival is successful!")
    return process_info
##############################################################################################################
# NEW function for Data Viewer: Unarchiving Delivery Order.
def unarchive_delivery_order (id):
    DB.cursor.execute("SELECT customer ,part_no, quantity, uom ,delivery_order ,delivery_date ,fulfilled_quantity ,weight_limit , cartons_id, time_added, user_name FROM archived_delivery_orders WHERE id = %s", (id,))
    archivedDeliveryOrderInfo = DB.cursor.fetchone()
    DB.cursor.execute("INSERT INTO delivery_orders (customer ,part_no, quantity, uom ,delivery_order ,delivery_date ,fulfilled_quantity ,weight_limit,cartons_id , time, user_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);" ,
                   (archivedDeliveryOrderInfo[0],archivedDeliveryOrderInfo[1],archivedDeliveryOrderInfo[2],archivedDeliveryOrderInfo[3],archivedDeliveryOrderInfo[4],archivedDeliveryOrderInfo[5],archivedDeliveryOrderInfo[6],archivedDeliveryOrderInfo[7],archivedDeliveryOrderInfo[8],archivedDeliveryOrderInfo[9],archivedDeliveryOrderInfo[10]))
    DB.conn.commit()
    DB.cursor.execute("SELECT id FROM delivery_orders ORDER BY id DESC")
    insertedId = DB.cursor.fetchone()
    insertedId = int(insertedId[0])
    DB.cursor.execute("SELECT part_no, carton_quantity,carton_no, date_codes, earliest_date_code, remarks , loose_quantity,user_name FROM archived_carton_table WHERE delivery_id = %s;" ,(id,))
    archived_carton_records = DB.cursor.fetchall()
    archived_carton_records= list(map(list, archived_carton_records))
    for carton in archived_carton_records:
        DB.cursor.execute("INSERT INTO carton_table (part_no, carton_quantity,carton_no, date_codes, earliest_date_code, remarks , loose_quantity , delivery_id, user_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                       (carton[0],carton[1],carton[2],carton[3],carton[4],carton[5],carton[6],insertedId,carton[7]))
    new_description = "(" + str(archivedDeliveryOrderInfo[0]) + "," + str(archivedDeliveryOrderInfo[1]) + "," + str(archivedDeliveryOrderInfo[2]) + "," + str(archivedDeliveryOrderInfo[6]) \
                  + "," + str(archivedDeliveryOrderInfo[3]) + "," + str(archivedDeliveryOrderInfo[4]) + "," + str(archivedDeliveryOrderInfo[5]) + ")"
    DB.cursor.execute("SELECT log_id FROM archived_delivery_orders WHERE id = %s", (id,))
    log_id = DB.cursor.fetchone()
    if log_id is not None:
        if log_id[0] is not None:
            log_id = int(log_id[0])
        else:
            log_id = 0
    else:
        log_id = 0
    DB.cursor.execute("SELECT user_name FROM logger WHERE id = %s", (log_id,))
    user_name = DB.cursor.fetchone()
    if user_name is not None:
        if user_name[0] is not None:
            user_name = str(user_name[0])
        else:
            user_name = ""
    else:
        user_name = ""
    old_description = str(log_id) + " | " + str(user_name)
    update_log_table("DO Unarchived", old_description, new_description)

    DB.cursor.execute("SELECT id FROM delivery_orders ORDER BY id DESC")
    insertedId = DB.cursor.fetchone()
    insertedId = int(insertedId[0])
    DB.cursor.execute("SELECT id FROM logger ORDER BY id DESC")
    loggerId = DB.cursor.fetchone()
    loggerId = int(loggerId[0])
    DB.cursor.execute("UPDATE delivery_orders SET log_id = %s WHERE id = %s", (loggerId, insertedId))
    DB.conn.commit()
    #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
    #               (insertedId,archivedDeliveryOrderInfo[1], 0, "DO Unarchived", datetime.now()))
    DB.conn.commit()

    cartonsID = ""
    old_stock = 0
    cartonIDList = []
    if archivedDeliveryOrderInfo[8] is not None:
        if "|" in archivedDeliveryOrderInfo[8]:
            cartonIDList = archivedDeliveryOrderInfo[8].split(" | ")
        else:
            cartonIDList.append(archivedDeliveryOrderInfo[8])
    for x in range(len(cartonIDList)):
        if "old_stock" in cartonIDList[x]:
            old_stock += int(cartonIDList[x][cartonIDList[x].find("(")+1:cartonIDList[x].find(")")])
    if old_stock > 0:
        cartonsID += "old_stock ("
        cartonsID += str(old_stock)
        cartonsID += ")"
    DB.cursor.execute("SELECT id FROM carton_table WHERE delivery_id = %s", (insertedId,))
    leftCartonList = DB.cursor.fetchall()
    leftCartonList= list(map(list, leftCartonList))
    for z in range(len(leftCartonList)):
        if cartonsID != "":
            cartonsID += " | "
        cartonsID += str(leftCartonList[z][0])
    DB.cursor.execute("UPDATE delivery_orders SET cartons_id = %s WHERE id = %s", (cartonsID, insertedId))
    DB.conn.commit()

    DB.cursor.execute("DELETE FROM archived_delivery_orders WHERE id = %s", (id,))
    DB.cursor.execute("DELETE FROM archived_carton_table WHERE delivery_id = %s", (id,))
    logger.info("Delivery Order ID " + str(id) + " has been unarchived.")
    DB.conn.commit()
##############################################################################################################
# NEW function for Data Viewer: Unarchiving Delivery Order by DO No.
def unarchive_delivery_order_by_deliver_order_no (do_no):
    process_info = []
    DB.cursor.execute("SELECT id FROM archived_delivery_orders WHERE delivery_order = %s", (do_no,))
    archived_ids = DB.cursor.fetchall()
    archived_ids= list(map(list, archived_ids))
    for a in range(len(archived_ids)):
        unarchive_delivery_order(archived_ids[a])
        process_info.append("\n* Delivery Order ID " + str(archived_ids[a]) + " reverse archival is successful!")
    process_info.append("\n* Delivery Order No " + str(do_no) + " reverse archival is successful!")
    return process_info
##############################################################################################################
def reorganizeDeliveryOrders():
    # This function helps to reorganize the delivery orders, should any delivery order ID already exist in the archived DO list.
    DB.cursor.execute("SELECT id FROM delivery_orders ORDER BY id")
    allIDs = DB.cursor.fetchall()
    for a in range(len(allIDs)):
        DB.cursor.execute("SELECT id FROM archived_delivery_orders WHERE id = %s", (allIDs[a][0],))
        foundID = DB.cursor.fetchone()
        if foundID:
            #print("ID existed in archived DO! ID: " + str(foundID[0]))
            DB.cursor.execute("SELECT customer, part_no, quantity, uom, delivery_order, delivery_date, fulfilled_quantity, weight_limit, cartons_id, time, log_id, user_name FROM delivery_orders WHERE id = %s", (allIDs[a][0],))
            DOInfo = DB.cursor.fetchone()
            existID = True
            while existID:
                DB.cursor.execute("INSERT INTO delivery_orders (customer, part_no, quantity, uom, delivery_order, delivery_date, fulfilled_quantity, weight_limit, cartons_id, time, log_id, user_name) "
                               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                               (DOInfo[0], DOInfo[1], DOInfo[2], DOInfo[3], DOInfo[4], DOInfo[5], DOInfo[6], DOInfo[7], DOInfo[8], DOInfo[9], DOInfo[10], DOInfo[11]))
                DB.cursor.execute("SELECT id FROM delivery_orders ORDER BY id DESC")
                insertedId = DB.cursor.fetchone()
                insertedId = int(insertedId[0])
                DB.cursor.execute("SELECT id FROM archived_delivery_orders WHERE id = %s", (insertedId,))
                foundID2 = DB.cursor.fetchone()
                if foundID2:
                    DB.cursor.execute("DELETE FROM delivery_orders WHERE id = %s", (insertedId,))
                    DB.conn.commit()
                else:
                    existID = False
                DB.cursor.execute("UPDATE carton_table SET delivery_id = %s WHERE delivery_id = %s", (insertedId, allIDs[a][0],))
                DB.conn.commit()
            DB.cursor.execute("DELETE FROM delivery_orders WHERE id = %s", (allIDs[a][0],))
            DB.conn.commit()
##############################################################################################################