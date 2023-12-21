from py3dbp import Packer, Bin, Item
from config import *
from ..Logics import DB , update_log_table , update_main_inventory
from ..LoginSystem import LoginSystem
from pandas import DataFrame

class PackedLabels():
    def __init__(self):
        self.PL = {"customer":[],"partNo":[],"quantity":[],"dateCode":[],"packingDate":[],"remarks":[], "deliveryOrder":[], "carton_no":[], "deliveryOrderID":[],"counter":[]}

    def add_label(self, customer="",partNo="",Qty=0,UoM="",dateCode="" ,remarks="",cartonQuantity=0 , deliveryOrder ="", carton_no="", deliveryOrderID="",current_counter=0,last_counter=0):
        for i in range(cartonQuantity):
            self.PL["customer"].append(customer)
            self.PL["partNo"].append(partNo)
            self.PL["quantity"].append(str(Qty) + " " + str(UoM))
            dateCode = dateCode.replace("0000", "N/A")
            self.PL["dateCode"].append(dateCode)
            self.PL["remarks"].append(remarks)
            self.PL["packingDate"].append(date.today().isoformat())
            self.PL["deliveryOrder"].append(deliveryOrder)
            self.PL["carton_no"].append(carton_no)
            self.PL["deliveryOrderID"].append(deliveryOrderID)
            current_counter+=1
            counter = str(current_counter) + "/" + str(last_counter)
            self.PL["counter"].append(counter)

    def to_csv(self):
        df = DataFrame.from_dict(self.PL)
        now_date_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        df.to_csv (r'{}\{}_packed_label.csv'.format(cartonlabel_path,now_date_time), index = False, header=True)
        process_info = []
        process_info.append("\n* '" + now_date_time + "_packed_label.csv' has been created successfully. ")
        logger.info("'" + now_date_time + "_packed_label.csv' has been created successfully. ")
        return process_info


    def clear(self):
        self.PL = {"customer":[],"partNo":[],"quantity":[],"dateCode":[],"packingDate":[],"remarks":[],"deliveryOrder":[],"carton_no":[],"deliveryOrderID":[],"counter":[]}

    def __str__(self):
        text = "customer: " +str(self.PL["customer"]) +"\tpartNo: " +str(self.PL["partNo"]) +"\tquantity: " +str(self.PL["quantity"]) \
               +"\tdateCode: " +str(self.PL["packingDate"])  +"\tdateCode: " +str(self.PL["packingDate"])+"\tremarks: " +str(self.PL["remarks"]) \
               +"\tcarton_no: " +str(self.PL["carton_no"])
        return text

# Function 1 to add new delivery orders, takes in customer name, partNo, quantity, uom, delivery order no, delivery date and weight limit.
def addDeliveryOrderNew(customer, partNo, quantity, uom, deliveryOrder, deliveryDate, weightLimit):
    #todayDate = date.today().isoformat()
    reorganizeDeliveryOrders()
    process_info = []
    uom = uom.upper()
    customer = customer.upper()
    DB.cursor.execute("SELECT customer FROM delivery_orders WHERE delivery_order = %s", (deliveryOrder,))
    customerName = DB.cursor.fetchone()
    user_name = LoginSystem.user_name
    if not customerName:
        DB.cursor.execute(
            "INSERT INTO delivery_orders (customer, part_no, quantity, uom, delivery_order, delivery_date, fulfilled_quantity,weight_limit,time_created,user_name) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (customer, partNo, quantity, uom, deliveryOrder,  deliveryDate, 0, weightLimit, datetime.now(),user_name)   )
    else:
        customer = customerName[0]
        DB.cursor.execute(
            "INSERT INTO delivery_orders (customer, part_no, quantity, uom, delivery_order, delivery_date, fulfilled_quantity, weight_limit,time_created,user_name) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (customer, partNo, quantity, uom, deliveryOrder, deliveryDate, 0, weightLimit, datetime.now(),user_name))
    DB.conn.commit()
    DB.cursor.execute("UPDATE part_info SET uom = %s WHERE part_no = %s", (uom, partNo))
    DB.conn.commit()
    DB.cursor.execute("SELECT id FROM delivery_orders ORDER BY id DESC")
    insertedId = DB.cursor.fetchone()
    insertedId = int(insertedId[0])
    description = "(" + str(customer) + "," + str(partNo) + "," + str(quantity) \
                  + "," + str(uom) + "," + str(deliveryOrder) + "," + str(deliveryDate) + ")"
    update_log_table("New DO", "N/A", description, "N/A")
    #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
    #               (insertedId, partNo, 0, "New DO", datetime.now()))
    DB.conn.commit()
    DB.cursor.execute("SELECT id FROM logger ORDER BY id DESC")
    loggerId = DB.cursor.fetchone()
    loggerId = int(loggerId[0])
    DB.cursor.execute("UPDATE delivery_orders SET log_id = %s WHERE id = %s", (loggerId, insertedId))
    DB.conn.commit()
    logger.info("Delivery Order added to database: ID (" + str(insertedId) + "), " + customer + ", " + partNo)
    process_info.append("\n* The ID for the new delivery order is " + str(insertedId) + ".")
    process_info_2 = checkFulfilledOrder(partNo, quantity, weightLimit, insertedId, True)
    if process_info_2 is not None:
        process_info.extend(process_info_2)
    return process_info
##############################################################################################################
# This function is used to check if the delivery order itself can be fulfilled.
def checkFulfilledOrder( partNo, quantity, weightLimit, requestedID, continueFlag):
    # Find any delivery orders if there's any earlier ones than that partNo:
    process_info = []
    hasCSV = False
    quantity = int(quantity)
    DB.cursor.execute(
        "SELECT delivery_date FROM delivery_orders WHERE part_no = %s AND quantity > fulfilled_quantity ORDER BY delivery_date",
        (partNo,))
    earliestdd = DB.cursor.fetchone()
    DB.cursor.execute(
        "SELECT delivery_date FROM delivery_orders WHERE id = %s",
        (requestedID,))
    givenDate = DB.cursor.fetchone()
    if earliestdd == givenDate:
        DB.cursor.execute("SELECT old_stock FROM main_inventory WHERE part_no = %s AND total_stock > 0", (partNo,))
        old_stock = DB.cursor.fetchone()
        if not old_stock:
            process_info.append("\n* ERROR: Part No " + partNo + " not found in the inventory!")
            logger.info("ERROR: Part No " + partNo + " not found in the inventory!")
            if continueFlag:
                process_info_2 = evaluate_part_list(partNo)
                if process_info_2 is not None:
                    process_info.extend(process_info_2)
            return process_info
        else:
            old_stock = int(old_stock[0])
            if old_stock > 0 and quantity > 0:
                DB.cursor.execute("SELECT fulfilled_quantity FROM delivery_orders WHERE id = %s", (requestedID,))
                memory = DB.cursor.fetchone()
                memoryFulfilled = int(memory[0])
                if old_stock >= quantity:
                    process_info.append("\n* NOTE: Tell the packing department that " + str(quantity) + " of the old stock for part " + partNo + " needed to be packed!")
                    logger.info(str(quantity) + " of the old stock for part " + partNo + " is allocated to the delivery order ID " + str(requestedID) + ".")
                    if memoryFulfilled == 0:
                        DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity + %s, cartons_id = %s WHERE id = %s",
                                       (quantity, "old_stock (" + str(quantity) + ")", requestedID))
                        #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Quantity, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
                        #               "Delivery Order", partNo, "OS = " + str(quantity),"DO = (" + str(requestedID) + ")", datetime.now())
                    else:
                        DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity + %s, cartons_id = CONCAT(COALESCE(cartons_id,''), %s) WHERE id = %s",
                                       (quantity, " | old_stock (" + str(quantity) + ")", requestedID))
                        #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Quantity, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
                        #               "Delivery Order", partNo, "OS = " + str(quantity),"DO = (" + str(requestedID) + ")", datetime.now())
                    DB.cursor.execute("UPDATE main_inventory SET old_stock = old_stock - %s WHERE part_no = %s", (quantity, partNo))
                    #old_description = "(" + str(requestedID) + "," + str(partNo) + "," + str(
                    #    int(memoryFulfilled)) + ")"
                    DB.cursor.execute("SELECT log_id FROM delivery_orders WHERE id = %s", (requestedID,))
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
                    DB.cursor.execute("SELECT quantity FROM delivery_orders WHERE id = %s", (requestedID,))
                    memoryT = DB.cursor.fetchone()
                    memoryTotal = int(memoryT[0])
                    new_description = "(" + str(requestedID) + "," + str(partNo) + "," + str(
                        int(memoryFulfilled + quantity)) + "/" + str(int(memoryTotal)) + ")"
                    update_log_table("Fulfill Quantity", old_description, new_description, "N/A")
                    #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
                    #               (requestedID,partNo, quantity, "Fulfill Quantity", datetime.now()))
                    DB.conn.commit()
                    old_stock -= int(quantity)
                    quantity -= quantity
                else:
                    process_info.append("\n* NOTE: Tell the packing department that " + str(old_stock) + " of the old stock for part " + partNo + " needed to be packed!")
                    logger.info(str(old_stock) + " of the old stock for part " + partNo + " is allocated to the delivery order ID " + str(requestedID) + ".")
                    if memoryFulfilled == 0:
                        DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity + %s, cartons_id = %s WHERE id = %s",
                                       (old_stock, "old_stock (" + str(old_stock) + ")", requestedID))
                        #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Quantity, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
                        #               "Delivery Order", partNo, "OS = " + str(old_stock),"DO = (" + str(requestedID) + ")", datetime.now())
                    else:
                        DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity + %s, cartons_id = CONCAT(COALESCE(cartons_id,''), %s) WHERE id = %s",
                                       (old_stock, " | old_stock (" + str(old_stock) + ")", requestedID))
                        #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Quantity, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
                        #               "Delivery Order", partNo, "OS = " + str(old_stock),"DO = (" + str(requestedID) + ")", datetime.now())
                    #old_description = "(" + str(requestedID) + "," + str(partNo) + "," + str(
                    #    int(memoryFulfilled)) + ")"
                    DB.cursor.execute("SELECT log_id FROM delivery_orders WHERE id = %s", (requestedID,))
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
                    DB.cursor.execute("SELECT quantity FROM delivery_orders WHERE id = %s", (requestedID,))
                    memoryT = DB.cursor.fetchone()
                    memoryTotal = int(memoryT[0])
                    new_description = "(" + str(requestedID) + "," + str(partNo) + "," + str(
                        int(memoryFulfilled + old_stock)) + "/" + str(int(memoryTotal)) + ")"
                    update_log_table("Fulfill Quantity", old_description, new_description, "N/A")
                    #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
                    #               (requestedID,partNo, old_stock, "Fulfill Quantity", datetime.now()))
                    DB.cursor.execute("UPDATE main_inventory SET old_stock = 0 WHERE part_no = %s", (partNo,))
                    DB.conn.commit()
                    quantity -= old_stock
                    old_stock = 0
                update_main_inventory(partNo)

        # Check if there's available cartons! But first, check if part exists in part_info......
        if quantity > 0:
            packed_labels = PackedLabels()
            DB.cursor.execute("SELECT bundle_qty, stn_qty, uom, cavity, stn_carton FROM part_info WHERE part_no = %s", (partNo,))
            partInfoResults = DB.cursor.fetchone()

            if not partInfoResults:
                process_info.append("\n* ERROR: Part No " + partNo + " not found in the database! Please fill in the values for that part no.")
                logger.info("ERROR: Part No " + partNo + " not found in the database! Please fill in the values for that part no.")
                return process_info
            else:
                if int(partInfoResults[0]) == 0 or int(partInfoResults[1]) == 0 or partInfoResults[2] == None or partInfoResults[2] == "" or \
                        (partInfoResults[2] == "PANEL" and partInfoResults[3] == 0) or (partInfoResults[2] == "PNL" and partInfoResults[3] == 0):
                    process_info.append("\n* ERROR: Part No " + partNo + " has missing information for bundleQty/stnQty/uom/cavity! Please fill in the values for that part no.")
                    logger.info("ERROR: Part No " + partNo + " has missing information for bundleQty/stnQty/uom/cavity! Please fill in the values for that part no.")
                    return process_info

            DB.cursor.execute("SELECT part_no, carton_quantity, sealed_quantity FROM main_inventory WHERE part_no = %s AND total_stock > 0", (partNo,))
            packedResults = DB.cursor.fetchone()

            if not packedResults:
                process_info.append("\n* ERROR: Part No " + partNo + " not found in the inventory!")
                logger.info("ERROR: Part No " + partNo + " not found in the inventory!")
                return process_info

            stnQty = int(partInfoResults[1])
            uom = str(partInfoResults[2])
            if uom == "PCS":
                cavity = int(partInfoResults[3])
                if cavity > 1:
                    stnQty *= cavity
            totalStnCarton = math.floor(quantity/stnQty)
            loosePartsAvailable = int(packedResults[2])
            log_id = 0

            if packedResults[1] == 0 and totalStnCarton >= 1 and loosePartsAvailable >= stnQty:
                noCartonsNeeded = totalStnCarton
                currentLoose = loosePartsAvailable
                while noCartonsNeeded > 0 and currentLoose >= stnQty:
                    DB.cursor.execute("SELECT part_no, carton_quantity, sealed_quantity FROM main_inventory WHERE part_no = %s AND total_stock > 0", (partNo,))
                    packedResults = DB.cursor.fetchone()
                    process_info.append("\n* No cartons available for " + partNo + ", but has enough quantity in sealed inventory to create a carton!")
                    logger.info("No cartons available for " + partNo + ", but has enough quantity in sealed inventory to create a carton!")
                    DB.cursor.execute("SELECT date_code FROM sealed_inventory WHERE part_no = %s ORDER BY id", (partNo,))
                    getDateCode = DB.cursor.fetchone()
                    sealed_info = ""
                    if len(getDateCode) <= 4:
                        DB.cursor.execute("SELECT id, date_code, remarks, quantity, log_id FROM sealed_inventory WHERE part_no = %s AND quantity > 0 ORDER BY Right(date_code,2), Left(date_code,2), quantity DESC, id", (partNo,))
                        sealed_info = DB.cursor.fetchall()
                    else:
                        DB.cursor.execute("SELECT id, date_code, remarks, quantity, log_id FROM sealed_inventory WHERE part_no = %s AND quantity > 0 ORDER BY Right(date_code,2), Right(Left(date_code,4),2), Left(date_code, 2), quantity DESC, id", (partNo,))
                        sealed_info = DB.cursor.fetchall()
                    sealed_info= list(map(list, sealed_info))
                    remainingSealedToStandard = stnQty
                    sealedDateCodes = ""
                    sealedRemarks = ""
                    moreThanOneDateCode = False
                    y = 0
                    while remainingSealedToStandard > 0:
                        log_id = sealed_info[y][4]
                        if sealed_info[y][4] is None:
                            log_id = 0
                        if sealed_info[y][2] == None or sealed_info[y][2] == "":
                            sealed_info[y][2] = ""
                        if int(sealed_info[y][3]) >= remainingSealedToStandard:
                            if moreThanOneDateCode:
                                sealedDateCodes += str(sealed_info[y][1])
                                sealedDateCodes += "="
                                sealedDateCodes += str(remainingSealedToStandard)
                                sealedRemarks += "("
                                sealedRemarks += sealed_info[y][2]
                                sealedRemarks += ")="
                                sealedRemarks += str(remainingSealedToStandard)
                            else:
                                sealedDateCodes += str(sealed_info[y][1])
                                sealedRemarks += sealed_info[y][2]
                            sealed_info[y][3] -= remainingSealedToStandard
                            remainingSealedToStandard -= remainingSealedToStandard
                        else:
                            moreThanOneDateCode = True
                            sealedDateCodes += str(sealed_info[y][1])
                            sealedDateCodes += "="
                            sealedDateCodes += str(sealed_info[y][3])
                            sealedDateCodes += " "
                            sealedRemarks += "("
                            sealedRemarks += sealed_info[y][2]
                            sealedRemarks += ")="
                            sealedRemarks += str(sealed_info[y][3])
                            sealedRemarks += " "
                            remainingSealedToStandard -= sealed_info[y][3]
                            sealed_info[y][3] -= sealed_info[y][3]
                        y += 1
                    user_name = LoginSystem.user_name
                    DB.cursor.execute(
                        "INSERT INTO carton_table (part_no, carton_quantity, date_codes, earliest_date_code, remarks, loose_quantity, carton_no, delivery_id, packing_date, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (partNo, 1, sealedDateCodes, sealed_info[0][1], sealedRemarks, 0 ,partInfoResults[4], 0, str_todate(date.today().isoformat()), log_id, datetime.now(), user_name))
                    DB.conn.commit()
                    DB.cursor.execute("SELECT id FROM carton_table ORDER BY id DESC")
                    insertedId = DB.cursor.fetchone()
                    insertedId = int(insertedId[0])
                    DB.cursor.execute("SELECT quantity, fulfilled_quantity FROM delivery_orders WHERE id = %s", (requestedID,))
                    memory = DB.cursor.fetchone()
                    memoryQuantity = int(memory[0])
                    memoryFulfilled = int(memory[1])
                    current_counter =  math.ceil(memoryFulfilled/stnQty) - 1
                    last_counter =  math.ceil(memoryQuantity/stnQty)
                    DB.cursor.execute("SELECT customer, delivery_order FROM delivery_orders WHERE id = %s",(requestedID,))
                    delivery_temp_info = DB.cursor.fetchone()
                    packed_labels.add_label(delivery_temp_info[0], partNo,stnQty,uom, sealedDateCodes, sealedRemarks, 1,delivery_temp_info[1],partInfoResults[4],requestedID, current_counter, last_counter)
                    hasCSV = True
                    for b in range(y):
                        DB.cursor.execute("UPDATE sealed_inventory SET quantity = %s WHERE id = %s",(sealed_info[b][3],sealed_info[b][0]))
                        DB.conn.commit()
                    update_main_inventory(partNo)
                    noCartonsNeeded -= 1
                    currentLoose -= stnQty

            DB.cursor.execute("SELECT part_no, carton_quantity, sealed_quantity FROM main_inventory WHERE part_no = %s AND total_stock > 0", (partNo,))
            packedResults = DB.cursor.fetchone()

            if packedResults[1] == 0 and totalStnCarton >= 1:
                process_info.append("\n* The Part No " + partNo + " has no available cartons in the inventory!")
                logger.info("ERROR: The Part No " + partNo + " has no available cartons in the inventory!")
                if continueFlag:
                    process_info_2 = evaluate_part_list(partNo)
                    if process_info_2 is not None:
                        process_info.extend(process_info_2)
                return process_info
            else:
                DB.cursor.execute(
                    "SELECT customer, uom, delivery_order, fulfilled_quantity, quantity FROM delivery_orders WHERE id = %s",
                    (requestedID,))
                packedLabelsQuery = DB.cursor.fetchone()
                customer = packedLabelsQuery[0]
                uom = packedLabelsQuery[1]
                deliveryOrder = packedLabelsQuery[2]

                if int(weightLimit) > 0:
                    DB.cursor.execute("SELECT weight FROM part_info WHERE part_no = %s", (partNo,))
                    weight = DB.cursor.fetchone()
                    weight = int(weight[0])
                    if weight == 0:
                        process_info.append("\n* The Part No " + partNo + " has a weight of zero, unable to fulfill cartons with weight limit, please fill in and try again!")
                        logger.info("The Part No " + partNo + " has a weight of zero, unable to fulfill cartons with weight limit, please fill in and try again!")
                        return process_info
                    else:
                        if weight * stnQty * 1.01 > int(weightLimit):
                            process_info.append("\n* This delivery order has a weight limit in which it is lower than the weight of a standard carton, and will be skipped.")
                            logger.info("This delivery order has a weight limit in which it is lower than the weight of a standard carton, and will be skipped.")
                            return process_info

                DB.cursor.execute("SELECT fulfilled_quantity, quantity FROM delivery_orders WHERE id = %s", (requestedID,))
                memory = DB.cursor.fetchone()
                memoryFulfilled = int(memory[0])
                memoryQuantity = int(memory[1])
                noLooseCarton = 0
                quantity = memoryQuantity - memoryFulfilled
                if old_stock == 0 and quantity > 0:
                    totalLooseQty = quantity - (totalStnCarton * stnQty)
                    remainingCartonForOrder = totalStnCarton
                    remainingCartonInInventory = packedResults[1]
                    carton_info = ""
                    if remainingCartonInInventory > 0:
                        DB.cursor.execute("SELECT earliest_date_code FROM carton_table WHERE part_no = %s AND carton_quantity > 0 AND loose_quantity = 0 AND (delivery_id = 0 OR delivery_id IS NULL OR LENGTH(delivery_id & '') = 0) ORDER BY earliest_date_code", (partNo,))
                        getDateCode = DB.cursor.fetchone()
                        if len(getDateCode) <= 4:
                            DB.cursor.execute("SELECT id, date_codes, remarks, carton_quantity, carton_no, earliest_date_code, packing_date, log_id FROM carton_table WHERE part_no = %s AND carton_quantity > 0 AND loose_quantity = 0 AND (delivery_id = 0 OR delivery_id IS NULL OR LENGTH(delivery_id & '') = 0) ORDER BY Right(earliest_date_code,2), Left(earliest_date_code,2), id",(partNo,))
                            carton_info = DB.cursor.fetchall()
                        else:
                            DB.cursor.execute("SELECT id, date_codes, remarks, carton_quantity, carton_no, earliest_date_code, packing_date, log_id FROM carton_table WHERE part_no = %s AND carton_quantity > 0 AND loose_quantity = 0 AND (delivery_id = 0 OR delivery_id IS NULL OR LENGTH(delivery_id & '') = 0) ORDER BY Right(earliest_date_code,2), Right(Left(earliest_date_code,4),2), Left(earliest_date_code, 2), id",(partNo,))
                            carton_info = DB.cursor.fetchall()
                    carton_info= list(map(list, carton_info))
                    x = 0
                    carton_id = ""
                    noOfCartons = 0
                    while remainingCartonForOrder > 0 and remainingCartonInInventory > 0:
                        noDecrement = 0
                        if int(carton_info[x][3]) >= remainingCartonForOrder:
                            noDecrement = remainingCartonForOrder
                        else:
                            noDecrement = int(carton_info[x][3])
                        if carton_info[x][2] == None:
                            carton_info[x][2] = ""
                        noOfCartons += noDecrement
                        user_name = LoginSystem.user_name
                        DB.cursor.execute(
                            "INSERT INTO carton_table (part_no, carton_quantity, date_codes, earliest_date_code, remarks, carton_no, delivery_id, packing_date, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (partNo, noDecrement, carton_info[x][1], carton_info[x][5], carton_info[x][2], carton_info[0][4], requestedID, carton_info[x][6], carton_info[x][7], datetime.now(), user_name))
                        DB.conn.commit()
                        dateCodeRemarksCarton = str(carton_info[x][1])
                        if carton_info[x][2] == "":
                            dateCodeRemarksCarton += ", N/A"
                        else:
                            dateCodeRemarksCarton += ", " + carton_info[x][2]
                        DB.conn.commit()
                        if x > 0:
                            carton_id += " | "
                        DB.cursor.execute("SELECT id FROM carton_table ORDER BY id DESC")
                        insertedId = DB.cursor.fetchone()
                        insertedId = int(insertedId[0])
                        carton_id += str(insertedId)
                        carton_info[x][3] -= noDecrement
                        remainingCartonForOrder -= noDecrement
                        remainingCartonInInventory -= noDecrement
                        if carton_info[x][3] == 0:
                            x += 1
                        memoryFulfilled += (stnQty * noDecrement)
                    if noOfCartons > 0:
                        process_info.append("\n*" + str(noOfCartons) + " cartons have been allocated for " + partNo + " for the delivery order ID of " + str(requestedID))
                        logger.info(str(noOfCartons) + " cartons have been allocated for " + partNo + " for the delivery order ID of " + str(requestedID))
                    cartonBreak = False
                    if remainingCartonForOrder == 0 and totalLooseQty > 0 and loosePartsAvailable < totalLooseQty and remainingCartonInInventory > 0:
                        if carton_info[x][2] == None:
                            carton_info[x][2] = ""
                        process_info.append("* One carton will be broken for part " + partNo + ", with dateCodes of '" + str(carton_info[x][1]) + "', and remarks of '" + str(carton_info[x][2]) +"'.")
                        logger.info("One carton will be broken for part " + partNo + ", with dateCodes of '" + str(carton_info[x][1]) + "', and remarks of '" + str(carton_info[x][2]) +"'.")
                        cartonBreak = True
                        carton_info[x][3] -= 1
                        loosePartsAvailable += stnQty
                        if "=" not in carton_info[x][1]:
                            getDateCode = carton_info[x][1]
                            getRemark = carton_info[x][2]
                            DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, getDateCode, getRemark))
                            sealedResult = DB.cursor.fetchone()
                            user_name = LoginSystem.user_name
                            if not sealedResult:
                                DB.cursor.execute(
                                    "INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                    (partNo, stnQty, getDateCode, getRemark, carton_info[x][7], datetime.now(), user_name))
                            else:
                                DB.cursor.execute(
                                    "UPDATE sealed_inventory SET quantity = quantity + %s WHERE part_no = %s AND date_code = %s AND remarks = %s AND id = %s",
                                    (stnQty, partNo, getDateCode, getRemark, sealedResult[0]))
                        else:
                            dateCodeSplit = carton_info[x][1].split(" ")
                            remarkSplit = carton_info[x][2].split(")")
                            for m in range(len(dateCodeSplit)):
                                getDateCode = dateCodeSplit[m].split("=")[0]
                                getQuantity = dateCodeSplit[m].split("=")[1]
                                getRemark = remarkSplit[m].split("(")[1]
                                '''
                                if m == 0:
                                    getRemark = carton_info[x][2].rpartition("="+str(getQuantity))
                                else:
                                    getRemark = carton_info[x][2][carton_info[x][2].find("="+str(dateCodeSplit[m-1].split("=")[1]))+len("="+str(dateCodeSplit[m-1].split("=")[1])):carton_info[x][2].rfind("="+dateCodeSplit[m].split("=")[1])]
                                getRemark = ''.join(getRemark)
                                getRemark = getRemark.replace("(","")
                                getRemark = getRemark.replace(")","")
                                getRemark = getRemark.lstrip()
                                '''
                                DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, getDateCode, getRemark))
                                sealedResult = DB.cursor.fetchone()
                                #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Temp_carton, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
                                #               "Break Carton", partNo, " (\"" + str(carton_info[0][4]) + "\")=-1", "(" + str(getDateCode) + ", " + getRemark + ")=-1, (Take out " + str(stnQty-totalLooseQty) + ")", datetime.now())
                                user_name = LoginSystem.user_name
                                if not sealedResult:
                                    DB.cursor.execute(
                                        "INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                        (partNo, getQuantity, getDateCode, getRemark, carton_info[x][7], datetime.now(), user_name))
                                else:
                                    DB.cursor.execute(
                                        "UPDATE sealed_inventory SET quantity = quantity + %s WHERE part_no = %s AND date_code = %s AND remarks = %s AND id = %s",
                                        (getQuantity, partNo, getDateCode, getRemark, sealedResult[0]))
                        DB.cursor.execute("UPDATE main_inventory SET carton_quantity = carton_quantity - 1, sealed_quantity = sealed_quantity + stn_qty WHERE part_no = %s", (partNo,))
                        DB.conn.commit()
                    if remainingCartonForOrder == 0 and totalLooseQty > 0 and loosePartsAvailable >= totalLooseQty:
                        moreThanOneDateCode = False
                        DB.cursor.execute("SELECT date_code FROM sealed_inventory WHERE part_no = %s ORDER BY id", (partNo,))
                        getDateCode = DB.cursor.fetchone()
                        sealed_info = ""
                        if len(getDateCode) <= 4:
                            DB.cursor.execute("SELECT id, date_code, remarks, quantity, log_id FROM sealed_inventory WHERE part_no = %s AND quantity > 0 ORDER BY Right(date_code,2), Left(date_code,2), quantity DESC, id", (partNo,))
                            sealed_info = DB.cursor.fetchall()
                        else:
                            DB.cursor.execute("SELECT id, date_code, remarks, quantity, log_id FROM sealed_inventory WHERE part_no = %s AND quantity > 0 ORDER BY Right(date_code,2), Right(Left(date_code,4),2), Left(date_code, 2), quantity DESC, id", (partNo,))
                            sealed_info = DB.cursor.fetchall()
                        sealed_info= list(map(list, sealed_info))
                        remainingSealedForOrder = totalLooseQty
                        sealedDateCodes = ""
                        sealedRemarks = ""
                        y = 0
                        log_id = 0
                        #sealedCarton_no = threedbp(totalLooseQty,weightLimit, partNo)
                        #if str(sealedCarton_no) != "None":
                        while remainingSealedForOrder > 0:
                            log_id = sealed_info[y][4]
                            if sealed_info[y][4] is None:
                                log_id = 0
                            if sealed_info[y][2] == None or sealed_info[y][2] == "":
                                sealed_info[y][2] = ""
                            if int(sealed_info[y][3]) >= remainingSealedForOrder:
                                if moreThanOneDateCode:
                                    sealedDateCodes += str(sealed_info[y][1])
                                    sealedDateCodes += "="
                                    sealedDateCodes += str(remainingSealedForOrder)
                                    sealedRemarks += sealed_info[y][2]
                                    sealedRemarks += "="
                                    sealedRemarks += str(remainingSealedForOrder)
                                else:
                                    sealedDateCodes += str(sealed_info[y][1])
                                    sealedRemarks += sealed_info[y][2]
                                sealed_info[y][3] -= remainingSealedForOrder
                                remainingSealedForOrder -= remainingSealedForOrder
                            else:
                                moreThanOneDateCode = True
                                sealedDateCodes += str(sealed_info[y][1])
                                sealedDateCodes += "="
                                sealedDateCodes += str(sealed_info[y][3])
                                sealedDateCodes += " "
                                sealedRemarks += sealed_info[y][2]
                                sealedRemarks += "="
                                sealedRemarks += str(sealed_info[y][3])
                                sealedRemarks += " "
                                remainingSealedForOrder -= sealed_info[y][3]
                                sealed_info[y][3] -= sealed_info[y][3]
                            if not cartonBreak:
                                dateCodeRemarksSealed = str(sealed_info[y][1])
                                if sealed_info[y][2] == "":
                                    dateCodeRemarksSealed += ", N/A"
                                else:
                                    dateCodeRemarksSealed += ", " + sealed_info[y][2]
                            y += 1
                            if carton_id != "":
                                carton_id +=  " | "
                            user_name = LoginSystem.user_name
                            DB.cursor.execute(
                                "INSERT INTO carton_table (part_no, carton_quantity, date_codes, earliest_date_code, remarks, loose_quantity, carton_no, delivery_id, packing_date, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                (partNo, 1, sealedDateCodes, sealed_info[0][1], sealedRemarks, totalLooseQty ,"L", requestedID, str_todate(date.today().isoformat()) , log_id, datetime.now(), user_name))
                            DB.conn.commit()
                            dateCodeRemarksLoose = str(sealedDateCodes)
                            if sealedRemarks == "":
                                dateCodeRemarksLoose += ", N/A"
                            else:
                                dateCodeRemarksLoose += ", " + sealedRemarks
                            DB.cursor.execute("SELECT id FROM carton_table ORDER BY id DESC")
                            insertedId = DB.cursor.fetchone()
                            insertedId = int(insertedId[0])
                            carton_id += str(insertedId)
                            current_counter =  math.ceil(memoryQuantity/stnQty) - 1
                            last_counter =  math.ceil(memoryQuantity/stnQty)
                            packed_labels.add_label(customer, partNo,totalLooseQty,uom, sealedDateCodes, sealedRemarks, 1,deliveryOrder,"L",requestedID, current_counter, last_counter)
                            hasCSV = True
                            for b in range(y):
                                DB.cursor.execute("UPDATE sealed_inventory SET quantity = %s WHERE id = %s",(sealed_info[b][3],sealed_info[b][0]))
                                DB.conn.commit()
                            noLooseCarton += 1
                    if carton_info:
                        for a in range(len(carton_info)):
                            DB.cursor.execute("UPDATE carton_table SET carton_quantity = %s WHERE id = %s",(carton_info[a][3],carton_info[a][0]))
                            DB.conn.commit()
                    DB.cursor.execute("SELECT fulfilled_quantity FROM delivery_orders WHERE id = %s", (requestedID,))
                    memoryAgain = DB.cursor.fetchone()
                    memoryFulfilledAgain = int(memoryAgain[0])
                    DB.cursor.execute("SELECT quantity FROM delivery_orders WHERE id = %s", (requestedID,))
                    memoryT = DB.cursor.fetchone()
                    memoryTotal = int(memoryT[0])
                    if noOfCartons > 0 or loosePartsAvailable >= totalLooseQty:
                        if remainingCartonForOrder == 0 and totalLooseQty > 0 and loosePartsAvailable >= totalLooseQty:
                            if memoryFulfilledAgain == 0:
                                DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = quantity, cartons_id = CONCAT(COALESCE(cartons_id,''), %s) WHERE id = %s",
                                               (carton_id, requestedID))
                            else:
                                DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = quantity, cartons_id = CONCAT(COALESCE(cartons_id,''), %s) WHERE id = %s",
                                               (" | " + carton_id, requestedID))
                            #old_description = "(" + str(requestedID) + "," + str(partNo) + "," + str(
                            #    int(memoryFulfilledAgain)) + ")"
                            DB.cursor.execute("SELECT log_id FROM delivery_orders WHERE id = %s", (requestedID,))
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
                            new_description = "(" + str(requestedID) + "," + str(partNo) + "," + str(
                                int(memoryFulfilledAgain + (stnQty * noOfCartons + totalLooseQty))) + "/" + str(int(memoryTotal)) + ")"
                            update_log_table("Fulfill Quantity", old_description, new_description, "N/A")
                            #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
                            #               (requestedID,partNo, stnQty * noOfCartons + totalLooseQty, "Fulfill Quantity", datetime.now()))
                            DB.cursor.execute("UPDATE main_inventory SET carton_quantity = carton_quantity - %s, sealed_quantity = sealed_quantity - %s WHERE part_no = %s", (noOfCartons, totalLooseQty, partNo))
                        else:
                            if memoryFulfilledAgain == 0:
                                DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = %s, cartons_id = CONCAT(COALESCE(cartons_id,''), %s) WHERE id = %s",
                                               (stnQty * noOfCartons, carton_id, requestedID))
                            else:
                                DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity + %s, cartons_id = CONCAT(COALESCE(cartons_id,''), %s) WHERE id = %s",
                                               (stnQty * noOfCartons," | " + carton_id, requestedID))
                            #old_description = "(" + str(requestedID) + "," + str(partNo) + "," + str(
                            #    int(memoryFulfilledAgain)) + ")"
                            DB.cursor.execute("SELECT log_id FROM delivery_orders WHERE id = %s", (requestedID,))
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
                            new_description = "(" + str(requestedID) + "," + str(partNo) + "," + str(
                                int(memoryFulfilledAgain + (stnQty * noOfCartons))) + "/" + str(int(memoryTotal)) + ")"
                            update_log_table("Fulfill Quantity", old_description, new_description, "N/A")
                            #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
                            #               (requestedID,partNo, stnQty * noOfCartons, "Fulfill Quantity", datetime.now()))
                            DB.cursor.execute("UPDATE main_inventory SET carton_quantity = carton_quantity - %s WHERE part_no = %s", (noOfCartons, partNo))
                        DB.conn.commit()
                    update_main_inventory(partNo)

            if hasCSV:
                #process_info.append("Cartons have been allocated for this delivery order!")
                #process_info_3 = packed_labels.to_csv()
                #if process_info_3 is not None:
                #    process_info.extend(process_info_3)
                return process_info
    else:
        # If not earliest, ignore it.......
        if continueFlag:
            process_info_2 = evaluate_part_list(partNo)
            if process_info_2 is not None:
                process_info.extend(process_info_2)
        return process_info
##############################################################################################################
# Function used to find delivery order searches by partNo and customer.
def findDeliveryOrderByPartNoCustomer (partNo, customer):
    DB.cursor.execute("SELECT id, customer, part_no, quantity, uom, delivery_order, delivery_date FROM delivery_orders WHERE part_no LIKE '%%%s%%' AND customer LIKE '%%%s%%';" % (partNo, customer))
    results = DB.cursor.fetchall()
    results= list(map(list, results))
    return results
##############################################################################################################
# Function used to find delivery order searches by its ID.
def findDeliveryOrderByID (ID):
    DB.cursor.execute("SELECT id, customer, part_no, quantity, uom, delivery_order, delivery_date FROM delivery_orders WHERE id = %s", (ID,))
    results = DB.cursor.fetchall()
    results= list(map(list, results))
    return results
##############################################################################################################
# Function used to find delivery order searches by its delivery order no.
def findDeliveryOrderByDONo (deliveryOrder):
    DB.cursor.execute("SELECT id, customer, part_no, quantity, uom, delivery_order, delivery_date FROM delivery_orders WHERE delivery_order = %s", (deliveryOrder,))
    results = DB.cursor.fetchall()
    results= list(map(list, results))
    return results
##############################################################################################################
# Function 2 to edit the delivery date of a delivery order, and once it's finished editing, the delivery order is checked if it can be fulfilled or not.
def editDeliveryDate(ID, deliveryDate, reason=""):
    process_info = []
    DB.cursor.execute("SELECT delivery_date FROM delivery_orders WHERE id = %s", (ID,))
    olddeliveryDate = DB.cursor.fetchone()
    olddeliveryDate = str(olddeliveryDate[0])
    DB.cursor.execute("UPDATE delivery_orders SET delivery_date = %s WHERE id = %s", (deliveryDate, ID))
    logger.info("Delivery date for delivery order ID " + str(ID) + " is changed to " + str(deliveryDate))
    DB.conn.commit()
    process_info.append("\n* The delivery date is successfully edited!")
    DB.cursor.execute("SELECT part_no, quantity, fulfilled_quantity, weight_limit FROM delivery_orders WHERE id = %s", (ID,))
    deliveryOrderInfo = DB.cursor.fetchone()
    quantity = int(deliveryOrderInfo[1]) - int(deliveryOrderInfo[2])
    process_info_2 = checkFulfilledOrder(deliveryOrderInfo[0], quantity, deliveryOrderInfo[3], ID, True)
    if process_info_2 is not None:
        process_info.extend(process_info_2)
    DB.cursor.execute("SELECT log_id FROM delivery_orders WHERE id = %s", (ID,))
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
    #old_description = "(" + str(ID) + "," + str(olddeliveryDate) + ")"
    new_description = "(" + str(ID) + "," + str(olddeliveryDate) + " -> " + str(deliveryDate) + ")"
    update_log_table("DO Date Change", old_description, new_description, reason)
    #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
    #               (ID,deliveryOrderInfo[0], 0, "Delivery Date Change: " + str(deliveryDate), datetime.now()))
    DB.conn.commit()
    return process_info
##############################################################################################################
# NEW FUNCTION, that edits the delivery date for the entire delivery order no.
def editDeliveryDateByDO(deliveryOrderNo, deliveryDate, reason=""):
    process_info = []
    DB.cursor.execute("SELECT id FROM delivery_orders WHERE delivery_order = %s", (deliveryOrderNo,))
    delivery_order_ids = DB.cursor.fetchall()
    delivery_order_ids= list(map(list, delivery_order_ids))
    for a in range(len(delivery_order_ids)):
        process_info_2 = editDeliveryDate(delivery_order_ids[a][0], deliveryDate , reason)
        if process_info_2 is not None:
            process_info.extend(process_info_2)
    process_info.append("\n* Delivery Order No " + str(deliveryOrderNo) + " delivery date editing is successful!")
    return process_info
##############################################################################################################
# Function 2 to edit the partNo of a delivery order. If the delivery order has no cartons allocated, the partNo is directly changed and the delivery order
# is checked if it can be fulfilled. If there are cartons allocated to it, the cartons are sent back with the delivery order deleted, followed by adding
# a new delivery order with the partNo changed.
def editPartNo(ID, partNo, reason=""):
    process_info = []
    DB.cursor.execute("SELECT part_no FROM delivery_orders WHERE id = %s", (ID,))
    oldpartNo = DB.cursor.fetchone()
    oldpartNo = str(oldpartNo)
    DB.cursor.execute("SELECT customer, quantity, uom, delivery_order, delivery_date, weight_limit, fulfilled_quantity FROM delivery_orders WHERE id = %s", (ID,))
    deliveryOrderInfo = DB.cursor.fetchone()
    if int(deliveryOrderInfo[6]) == 0:
        DB.cursor.execute("UPDATE delivery_orders SET part_no = %s WHERE id = %s", (partNo, ID))
        old_description = "(" + str(ID) + "," + str(oldpartNo) + ")"
        new_description = "(" + str(ID) + "," + str(partNo) + ")"
        update_log_table("DO Part No Change", old_description, new_description, reason)
        #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
        #               (ID,partNo, 0, "Part No Change", datetime.now()))
        DB.conn.commit()
        process_info_2 = checkFulfilledOrder(partNo, deliveryOrderInfo[1], deliveryOrderInfo[5], ID, True)
        if process_info_2 is not None:
            process_info.extend(process_info_2)
    else:
        process_info_3 = addDeliveryOrderNew(deliveryOrderInfo[0], partNo, int(deliveryOrderInfo[1]), deliveryOrderInfo[2], deliveryOrderInfo[3], deliveryOrderInfo[4], deliveryOrderInfo[5])
        if process_info_3 is not None:
            process_info.extend(process_info_3)
        process_info_4 = deleteDeliveryOrderEntry(ID)
        if process_info_4 is not None:
            process_info.extend(process_info_4)
    logger.info("Part No for delivery order ID " + str(ID) + " is changed to " + partNo)
    process_info.append("\n* New Part No: " + partNo + " successfully edited!")
    return process_info
    #print("\n* New Part No: " + partNo)
    #print("\n* The old delivery order is successfully deleted with a new one is made for the new Part no!")
##############################################################################################################
# Function 2 to edit the quantity of a delivery order, and once it's finished editing, the delivery order is checked if it can be fulfilled or not.
# If the quantity is lowered and even below the fulfilled quantity, some cartons are sent back to the inventory.
def editQuantity(ID, quantity, reason=""):
    process_info = []
    # Process for editQuantity:
    # 1. If the edited quantity is higher, leave it be.
    # 2. If the edited quantity is lower, check if there's allocated delivery orders to it.
    # 3. If there are, find if there's cartons and loose quantities needed to be sent out.
    # Finds the deliveryOrderNo, and then deletes.
    DB.cursor.execute(
        "SELECT id, part_no, fulfilled_quantity, quantity, weight_limit, cartons_id FROM delivery_orders WHERE id = %s",
        (ID,))
    deliveryOrderInfo = DB.cursor.fetchone()
    oldQuantity = deliveryOrderInfo[3]
    cartonIDList = []
    if deliveryOrderInfo[5] is not None:
        if "|" in deliveryOrderInfo[5]:
            cartonIDList = deliveryOrderInfo[5].split(" | ")
        else:
            cartonIDList.append(deliveryOrderInfo[5])
    partNo = deliveryOrderInfo[1]
    DB.cursor.execute("UPDATE delivery_orders SET quantity = %s WHERE id = %s", (quantity, ID))
    #old_description = "(" + str(ID) + "," + str(partNo) + "," + str(deliveryOrderInfo[3]) + ")"
    DB.cursor.execute("SELECT log_id FROM delivery_orders WHERE id = %s", (ID,))
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
    new_description = "(" + str(ID) + "," + str(partNo) + "," + str(oldQuantity) + " -> " + str(quantity) + ")"
    update_log_table("DO Quantity Change", old_description, new_description, reason)
    #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
    #               (ID,deliveryOrderInfo[1], 0, "Quantity Change: " + str(quantity), datetime.now()))
    DB.conn.commit()
    logger.info("Quantity for delivery order ID " + str(ID) + " is changed to " + str(quantity))
    cartonsID = ""
    if quantity >= int(deliveryOrderInfo[3]):
        # Best to send out the loose quantity carton first.
        possibleExcess = 0
        if int(deliveryOrderInfo[2]) == int(deliveryOrderInfo[3]):
            DB.cursor.execute("SELECT id, carton_quantity, loose_quantity, date_codes, remarks, carton_no, log_id FROM carton_table WHERE delivery_id = %s AND loose_quantity > 0", (ID,))
            looseCartonList = DB.cursor.fetchall()
            looseCartonList= list(map(list, looseCartonList))
            for y in range(len(looseCartonList)):
                noOfParts = int(looseCartonList[y][1]) * int(looseCartonList[y][2])
                possibleExcess += noOfParts
                logger.info("Loose quantity carton allocated to delivery order ID " + str(ID) + " is sent back to the sealed inventory containing amount of " + str(noOfParts))
                if "=" not in looseCartonList[y][3]:
                    DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, looseCartonList[y][3], looseCartonList[y][4]))
                    sealedResult = DB.cursor.fetchone()
                    user_name = LoginSystem.user_name
                    if not sealedResult:
                        DB.cursor.execute(
                            "INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                            (partNo, int(looseCartonList[y][1]) * int(looseCartonList[y][2]), looseCartonList[y][3], looseCartonList[y][4], looseCartonList[y][6], datetime.now(), user_name))
                    else:
                        DB.cursor.execute(
                            "UPDATE sealed_inventory SET quantity = quantity + %s WHERE part_no = %s AND date_code = %s AND remarks = %s AND id = %s",
                            (int(looseCartonList[y][1]) * int(looseCartonList[y][2]), partNo, looseCartonList[y][3], looseCartonList[y][4], sealedResult[0]))
                    #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Packed_carton, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
                    #               "Remove + Break Carton", partNo, "(\"" + str(looseCartonList[y][5]) + "\")=-1", "DO = (" + str(ID) + "), (" + str(looseCartonList[y][3]) + " , " + str(looseCartonList[y][4]) + ")", datetime.now())
                    DB.conn.commit()
                else:
                    dateCodeSplit = looseCartonList[y][3].split(" ")
                    remarkSplit = looseCartonList[y][4].split(")")
                    for m in range(len(dateCodeSplit)):
                        getDateCode = dateCodeSplit[m].split("=")[0]
                        getQuantity = dateCodeSplit[m].split("=")[1]
                        getRemark = remarkSplit[m].split("(")[1]
                        '''
                        if m == 0:
                            getRemark = looseCartonList[y][4].split("="+str(getQuantity))[0]
                        else:
                            getRemark = looseCartonList[y][4][looseCartonList[y][4].find("="+str(dateCodeSplit[m-1].split("=")[1]))+len("="+str(dateCodeSplit[m-1].split("=")[1])):looseCartonList[y][4].rfind("="+dateCodeSplit[m].split("=")[1])]
                        replaced = dateCodeSplit[m-1].split("=")[1]
                        getRemark = ''.join(getRemark.replace(replaced,""))
                        getRemark = getRemark.replace("(","")
                        getRemark = getRemark.replace(")","")
                        getRemark = getRemark.lstrip()
                        '''

                        DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, getDateCode, getRemark))
                        sealedResult = DB.cursor.fetchone()
                        user_name = LoginSystem.user_name
                        #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Packed_carton, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
                        #               "Remove + Break Carton", partNo, "(\"" + str(looseCartonList[y][5]) + "\")=-1", "(" + str(getDateCode) + " , " + str(getRemark) + "), Quantity: " + str(getQuantity), datetime.now())
                        if not sealedResult:
                            DB.cursor.execute("INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                           (partNo, int(getQuantity), str(getDateCode), getRemark, looseCartonList[y][6],datetime.now(), LoginSystem.user_name))
                        else:
                            DB.cursor.execute(
                                "UPDATE sealed_inventory SET quantity = quantity + %s WHERE part_no = %s AND date_code = %s AND remarks = %s AND id = %s",
                                (getQuantity, partNo, getDateCode, getRemark, sealedResult[0]))
                        DB.conn.commit()
            DB.cursor.execute("DELETE FROM carton_table WHERE delivery_id = %s AND loose_quantity > 0", (ID,))
            DB.conn.commit()
            old_stock = 0
            for x in range(len(cartonIDList)):
                if "old_stock" in cartonIDList[x]:
                    old_stock += int(cartonIDList[x][cartonIDList[x].find("(")+1:cartonIDList[x].find(")")])
            if old_stock > 0:
                cartonsID += "old_stock ("
                cartonsID += str(old_stock)
                cartonsID += ")"
            DB.cursor.execute("SELECT id FROM carton_table WHERE delivery_id = %s AND loose_quantity = 0", (ID,))
            leftCartonList = DB.cursor.fetchall()
            leftCartonList= list(map(list, leftCartonList))
            for z in range(len(leftCartonList)):
                if cartonsID != "":
                    cartonsID += " | "
                cartonsID += str(leftCartonList[z][0])
            update_main_inventory(partNo)
            DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity - %s, cartons_id = %s WHERE id = %s", (possibleExcess, cartonsID, ID))
            description = "(" + str(ID) + "," + str(partNo) + "," + str(possibleExcess) + ")"
            update_log_table("Removing Cartons", "N/A", description, reason)
            #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
            #               (ID,deliveryOrderInfo[1], 0-possibleExcess, "Cartons Sent Out", datetime.now()))
            DB.conn.commit()
        process_info_2 = checkFulfilledOrder(partNo, quantity - (int(deliveryOrderInfo[2]) - possibleExcess), int(deliveryOrderInfo[4]), ID, True)
        if process_info_2 is not None:
            process_info.extend(process_info_2)
        process_info.append("\n* New Quantity Successfully Edited: " + str(quantity))
    elif quantity < int(deliveryOrderInfo[2]):
        excessParts = int(deliveryOrderInfo[2]) - quantity
        DB.cursor.execute("SELECT stn_qty, uom, cavity, stn_carton FROM part_info WHERE part_no = %s", (partNo,))
        part_info = DB.cursor.fetchone()
        stnQty = int(part_info[0])
        uom = str(part_info[1])
        stnCarton = str(part_info[3])
        if uom == "PCS":
            cavity = int(part_info[2])
            if cavity > 1:
                stnQty *= cavity
        hasCSV = False
        old_stock = 0
        # temporary_label = TemporaryLabels()
        quantitySentOut = 0
        # Calculating the old stock......
        for x in range(len(cartonIDList)):
            if "old_stock" in cartonIDList[x]:
                old_stock += int(cartonIDList[x][cartonIDList[x].find("(")+1:cartonIDList[x].find(")")])
        # Check if sending out the loose quantity carton is good enough%s
        DB.cursor.execute("SELECT id, carton_quantity, loose_quantity, date_codes, remarks, carton_no, log_id FROM carton_table WHERE delivery_id = %s AND loose_quantity > 0", (ID,))
        looseCartonList = DB.cursor.fetchall()
        looseCartonList= list(map(list, looseCartonList))
        for y in range(len(looseCartonList)):
            noOfParts = int(looseCartonList[y][1]) * int(looseCartonList[y][2])
            logger.info("Loose quantity carton allocated to delivery order ID " + str(ID) + " is sent back to the sealed inventory containing amount of " + str(noOfParts))
            excessParts -= noOfParts
            quantitySentOut += noOfParts
            if "=" not in looseCartonList[y][3]:
                DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, looseCartonList[y][3], looseCartonList[y][4]))
                sealedResult = DB.cursor.fetchone()
                user_name = LoginSystem.user_name
                if not sealedResult:
                    DB.cursor.execute(
                        "INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                        (partNo, int(looseCartonList[y][1]) * int(looseCartonList[y][2]), looseCartonList[y][3], looseCartonList[y][4], looseCartonList[y][6],datetime.now(), user_name))
                else:
                    DB.cursor.execute(
                        "UPDATE sealed_inventory SET quantity = quantity + %s WHERE part_no = %s AND date_code = %s AND remarks = %s AND id = %s",
                        (int(looseCartonList[y][1]) * int(looseCartonList[y][2]), partNo, looseCartonList[y][3], looseCartonList[y][4], sealedResult[0]))
                #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Packed_carton, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
                #               "Remove + Break Carton", partNo, "(\"" + str(looseCartonList[y][5]) + "\")=-1", "DO = (" + str(ID) + "), (" + str(looseCartonList[y][3]) + " , " + str(looseCartonList[y][4]) + ")", datetime.now())
                DB.conn.commit()
            else:
                dateCodeSplit = looseCartonList[y][3].split(" ")
                remarkSplit = looseCartonList[y][4].split(")")
                for m in range(len(dateCodeSplit)):
                    getDateCode = dateCodeSplit[m].split("=")[0]
                    getQuantity = dateCodeSplit[m].split("=")[1]
                    getRemark = remarkSplit[m].split("(")[1]
                    '''
                    if m == 0:
                        getRemark = looseCartonList[y][4].split("="+str(getQuantity))[0]
                    else:
                        getRemark = looseCartonList[y][4][looseCartonList[y][4].find("="+str(dateCodeSplit[m-1].split("=")[1]))+len("="+str(dateCodeSplit[m-1].split("=")[1])):looseCartonList[y][4].rfind("="+dateCodeSplit[m].split("=")[1])]
                    replaced = dateCodeSplit[m-1].split("=")[1]
                    getRemark = ''.join(getRemark.replace(replaced,""))
                    getRemark = getRemark.replace("(","")
                    getRemark = getRemark.replace(")","")
                    getRemark = getRemark.lstrip()
                    '''

                    DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, getDateCode, getRemark))
                    sealedResult = DB.cursor.fetchone()
                    user_name = LoginSystem.user_name
                    #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Packed_carton, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
                    #              "Remove + Break Carton", partNo, "(\"" + str(looseCartonList[y][5]) + "\")=-1", " (" + str(getDateCode) + " , " + str(getRemark) + ")", datetime.now())
                    if not sealedResult:
                        DB.cursor.execute("INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                       (partNo, int(getQuantity), str(getDateCode), getRemark, looseCartonList[y][6],datetime.now(), user_name))
                    else:
                        DB.cursor.execute(
                            "UPDATE sealed_inventory SET quantity = quantity + %s WHERE part_no = %s AND date_code = %s AND remarks = %s AND id = %s",
                            (getQuantity, partNo, getDateCode, getRemark, sealedResult[0]))
                    DB.conn.commit()
        DB.cursor.execute("DELETE FROM carton_table WHERE delivery_id = %s AND loose_quantity > 0", (ID,))
        DB.conn.commit()
        # If not enough, send out some of the standard quantities
        if excessParts > 0:
            DB.cursor.execute("SELECT id, carton_quantity, date_codes, remarks, earliest_date_code, carton_no, log_id FROM carton_table WHERE delivery_id = %s AND loose_quantity = 0", (ID,))
            cartonList = DB.cursor.fetchall()
            cartonList= list(map(list, cartonList))
            for z in range(len(cartonList)):
                if excessParts > 0:
                    noCartonsPreferSent = math.ceil(excessParts/stnQty)
                    if noCartonsPreferSent <= cartonList[z][1]:
                        logger.info("Some standard cartons allocated to delivery order ID " + str(ID) + " are sent back to the carton table: Carton ID of " + str(cartonList[z][0]))
                        #temporary_label.add_label(partNo,noCartonsPreferSent,cartonList[z][2],cartonList[z][3],stnQty,stnCarton)
                        #hasCSV = True
                        user_name = LoginSystem.user_name
                        DB.cursor.execute("UPDATE carton_table SET carton_quantity = carton_quantity - %s WHERE id = %s", (noCartonsPreferSent,cartonList[z][0]))
                        DB.cursor.execute(
                            "INSERT INTO carton_table (part_no, carton_quantity, date_codes, earliest_date_code, remarks, carton_no, delivery_id, packing_date, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (partNo, noCartonsPreferSent, cartonList[z][2], cartonList[z][4], cartonList[z][3], stnCarton, 0, str_todate(date.today().isoformat()), cartonList[z][6], datetime.now(), user_name))
                        #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Packed_carton, Temp_carton, Notes, time) ""VALUES (%s,%s,%s,%s,%s,%s)",
                        #               "Remove Carton", partNo, "(\"" + str(cartonList[0][5]) + "\")=-" + str(noCartonsPreferSent), "(\"" + str(cartonList[0][5]) + "\")=+" + str(noCartonsPreferSent), "DO = (" + str(ID) + ")", datetime.now())
                        DB.conn.commit()
                        excessParts -= (noCartonsPreferSent * stnQty)
                        quantitySentOut += (noCartonsPreferSent * stnQty)
                    else:
                        #temporary_label.add_label(partNo,cartonList[z][1],cartonList[z][2],cartonList[z][3],stnQty,stnCarton)
                        #hasCSV = True
                        logger.info("Standard cartons allocated to delivery order ID " + str(ID) + " are sent back to the carton table: Carton ID of " + str(cartonList[z][0]))
                        DB.cursor.execute("UPDATE carton_table SET delivery_id = 0 WHERE id = %s", (cartonList[z][0],))
                        #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Packed_carton, Temp_carton, Notes, time) ""VALUES (%s,%s,%s,%s,%s,%s)",
                        #               "Remove Carton", partNo, "(\"" + str(cartonList[0][5]) + "\")=-" + str(cartonList[z][1]),"(\"" + str(cartonList[0][5]) + "\")=+" + str(cartonList[z][1]), "DO = (" + str(ID) + ")", datetime.now())
                        DB.conn.commit()
                        excessParts -= (cartonList[z][1] * stnQty)
                        quantitySentOut += (cartonList[z][1] * stnQty)
        # If still not enough, deduct old stock.
        if excessParts > 0:
            logger.info("Some old stock allocated to delivery order ID " + str(ID) + " is sent back to the inventory, quantity of " + str(excessParts))
            DB.cursor.execute("SELECT part_no FROM main_inventory WHERE part_no = %s", (partNo,))
            findPartNo = DB.cursor.fetchone()
            if findPartNo:
                DB.cursor.execute("UPDATE main_inventory SET old_stock = old_stock + %s, total_stock = total_stock + %s WHERE part_no = %s", (excessParts, excessParts, partNo))
            else:
                DB.cursor.execute("INSERT INTO main_inventory (part_no, stn_qty, old_stock, total_stock) " "VALUES (%s,%s,%s,%s)", (partNo, stnQty, excessParts, excessParts))
            quantitySentOut += excessParts
            old_stock -= excessParts
            #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Quantity, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
            #               "Remove Old Stock", partNo, "OS = - " + str(excessParts) + "(returned)", "DO = (" + str(ID) + ")", datetime.now())
            DB.conn.commit()
        # if hasCSV:
        #     temporary_label.to_csv()
        if old_stock > 0:
            cartonsID += "old_stock ("
            cartonsID += str(old_stock)
            cartonsID += ")"
        update_main_inventory(partNo)
        DB.cursor.execute("SELECT id FROM carton_table WHERE delivery_id = %s AND loose_quantity = 0", (ID,))
        leftCartonList = DB.cursor.fetchall()
        leftCartonList= list(map(list, leftCartonList))
        for z in range(len(leftCartonList)):
            if cartonsID != "":
                cartonsID += " | "
            cartonsID += str(leftCartonList[z][0])
        DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity - %s, cartons_id = %s WHERE id = %s", (quantitySentOut, cartonsID, ID))
        description = "(" + str(ID) + "," + str(partNo) + "," + str(quantitySentOut) + ")"
        update_log_table("Removing Cartons", "N/A", description, reason)
        #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
        #               (ID,deliveryOrderInfo[1], 0-quantitySentOut, "Cartons Sent Out", datetime.now()))
        DB.conn.commit()
        process_info.append("\n* New Quantity Successfully Edited: " + str(quantity))
        process_info_3 = checkOtherOrders(partNo)
        if process_info_3 is not None:
            process_info.extend(process_info_3)
    else:
        process_info.append("\n* New Quantity Successfully Edited: " + str(quantity))
    return process_info
##############################################################################################################
# This function is used to check for to check if the delivery orders containing this partNo can be fulfilled, used to fulfill early delivery orders with this partNo.
def checkOtherOrders (partNo):
    process_info = []
    DB.cursor.execute("SELECT id, quantity, fulfilled_quantity, weight_limit FROM delivery_orders WHERE part_no = %s AND quantity > fulfilled_quantity ORDER BY delivery_date", (partNo,))
    relevantOrders = DB.cursor.fetchall()
    relevantOrders= list(map(list, relevantOrders))
    for x in range(len(relevantOrders)):
        process_info_2 = checkFulfilledOrder( partNo, relevantOrders[x][1] - relevantOrders[x][2], relevantOrders[x][3], relevantOrders[x][0], False)
        if process_info_2 is not None:
            process_info.extend(process_info_2)
    return process_info
##############################################################################################################
# Function 3 to delete a delivery order entry, based on the delivery order ID. Cartons allocated to this delivery order will be sent back to inventory,
# however these cartons will be checked if they can be allocated to other delivery orders.
def deleteDeliveryOrderEntry(deliveryOrderID,reason=""):
    process_info = []
    # Finds the deliveryOrderNo, and then deletes.
    DB.cursor.execute(
        "SELECT part_no, cartons_id, fulfilled_quantity FROM delivery_orders WHERE id = %s",
        (deliveryOrderID,))
    deliveryOrderInfo = DB.cursor.fetchone()
    partNo = str(deliveryOrderInfo[0])
    cartons_ID = str(deliveryOrderInfo[1])
    fulfilledQuantity = int(deliveryOrderInfo[2])
    DB.cursor.execute("DELETE FROM delivery_orders WHERE id = %s", (deliveryOrderID,))
    description = "(" + str(deliveryOrderID) + "," + deliveryOrderInfo[0] + "," + str(fulfilledQuantity) + ")"
    update_log_table("DO Deletion", "N/A", description, "reason")
    #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
    #               (deliveryOrderID,deliveryOrderInfo[0], 0-fulfilledQuantity, "Delivery Order Deletion", datetime.now()))
    DB.conn.commit()
    # Returning standard quantity stock
    DB.cursor.execute("SELECT COUNT(*) FROM carton_table WHERE delivery_id = %s AND loose_quantity = 0", (deliveryOrderID,))
    noOfCartons = DB.cursor.fetchone()
    noOfCartons = int(noOfCartons[0])
    DB.cursor.execute("SELECT stn_qty, stn_carton FROM part_info WHERE part_no = %s", (partNo,))
    part_infopart = DB.cursor.fetchone()
    DB.cursor.execute("SELECT carton_quantity, date_codes, remarks, carton_no FROM carton_table WHERE delivery_id = %s AND loose_quantity = 0", (deliveryOrderID,))
    getCartons = DB.cursor.fetchall()
    getCartons= list(map(list, getCartons))
    if getCartons:
        # temporary_label = TemporaryLabels()
        #for z in range(len(getCartons)):
        #    temporary_label.add_label(partNo,getCartons[z][0],getCartons[z][1],getCartons[z][2],part_infopart[0],part_infopart[1])
        #temporary_label.to_csv()
        DB.cursor.execute("UPDATE carton_table SET delivery_id = %s WHERE delivery_id = %s AND loose_quantity = 0", (0,deliveryOrderID))
        logger.info("Standard cartons allocated to deleted delivery order ID " + str(deliveryOrderID) + " are sent back to the inventory")
        #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Packed_carton, Temp_carton, Notes, time) ""VALUES (%s,%s,%s,%s,%s,%s)",
        #               "Remove Carton", partNo, "(\"" + str(getCartons[0][3]) + "\")=-" + str(noOfCartons), "(\"" + str(getCartons[0][3]) + "\")=+" + str(noOfCartons), "DO = (" + str(deliveryOrderID) + ")", datetime.now())
        DB.conn.commit()
    # Returning old stock
    if deliveryOrderInfo[1] is not None:
        if "old_stock" in cartons_ID:
            old_stock_quantity = 0
            if "|" in cartons_ID:
                cartonList = cartons_ID.split(" | ")
                for x in range(len(cartonList)):
                    if "old_stock" in cartonList[x]:
                        old_stock_quantity += int(cartonList[x][cartonList[x].find("(")+1:cartonList[x].find(")")])
            else:
                old_stock_quantity += int(cartons_ID[cartons_ID.find("(")+1:cartons_ID.find(")")])
            DB.cursor.execute("SELECT id FROM main_inventory WHERE part_no = %s", (partNo,))
            findPartNo = DB.cursor.fetchone()
            if findPartNo:
                DB.cursor.execute("UPDATE main_inventory SET old_stock = old_stock + %s, total_stock = total_stock + %s WHERE part_no = %s", (old_stock_quantity, old_stock_quantity, partNo))
            else:
                DB.cursor.execute("SELECT stn_qty FROM part_info WHERE part_no = %s", (partNo,))
                stnQtyPart = DB.cursor.fetchone()
                stnQty = int(stnQtyPart[0])
                DB.cursor.execute("INSERT INTO main_inventory (part_no, stn_qty, old_stock, total_stock) " "VALUES (%s,%s,%s,%s)",(partNo, stnQty, old_stock_quantity, old_stock_quantity))
                update_main_inventory(partNo)
            logger.info("Old stock allocated to deleted delivery order ID " + str(deliveryOrderID) + " is sent back to the inventory, quantity of " + str(old_stock_quantity))
            #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Quantity, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
            #               "Remove Old Stock", partNo, "OS = - " + str(old_stock_quantity) + "(returned)", "DO = (" + str(deliveryOrderID) + ")", datetime.now())
            DB.conn.commit()
    # Returning loose quantity stock to sealed inventory
    DB.cursor.execute("SELECT carton_quantity, date_codes, remarks, loose_quantity, carton_no, log_id FROM carton_table WHERE delivery_id = %s AND loose_quantity > 0", (deliveryOrderID,))
    looseQuantityGet = DB.cursor.fetchall()
    looseQuantityGet= list(map(list, looseQuantityGet))
    if looseQuantityGet:
        for y in range(len(looseQuantityGet)):
            if "=" not in looseQuantityGet[y][1]:
                DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, looseQuantityGet[y][1], looseQuantityGet[y][2]))
                sealedResult = DB.cursor.fetchone()
                user_name = LoginSystem.user_name
                if not sealedResult:
                    DB.cursor.execute(
                        "INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                        (partNo, int(looseQuantityGet[y][0]) * int(looseQuantityGet[y][3]), looseQuantityGet[y][1], looseQuantityGet[y][2], looseQuantityGet[y][5], datetime.now(), user_name))
                else:
                    DB.cursor.execute(
                        "UPDATE sealed_inventory SET quantity = quantity + %s WHERE part_no = %s AND date_code = %s AND remarks = %s AND id = %s",
                        (int(looseQuantityGet[y][0]) * int(looseQuantityGet[y][3]), partNo, looseQuantityGet[y][1], looseQuantityGet[y][2], sealedResult[0]))
                logger.info("Loose quantity allocated to deleted delivery order ID " + str(deliveryOrderID) + " is sent back to the inventory, quantity of " + str(int(looseQuantityGet[y][0]) * int(looseQuantityGet[y][3])))
                #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Packed_carton, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
                #               "Remove + Break Carton", partNo, "(\"" + str(looseQuantityGet[y][4]) + "\")=-1", "DO = (" + str(deliveryOrderID) + "), (" + str(looseQuantityGet[y][1]) + " , " + str(looseQuantityGet[y][2]) + ")", datetime.now())
                DB.conn.commit()
            else:
                dateCodeSplit = looseQuantityGet[y][1].split(" ")
                remarkSplit = looseQuantityGet[y][2].split(")")
                for m in range(len(dateCodeSplit)):
                    getDateCode = dateCodeSplit[m].split("=")[0]
                    getQuantity = dateCodeSplit[m].split("=")[1]
                    getRemark = remarkSplit[m].split("(")[1]
                    '''
                    if m == 0:
                        getRemark = looseQuantityGet[y][2].split("="+str(getQuantity))[0]
                    else:
                        getRemark = looseQuantityGet[y][2][looseQuantityGet[y][2].find("="+str(dateCodeSplit[m-1].split("=")[1]))+len("="+str(dateCodeSplit[m-1].split("=")[1])):looseQuantityGet[y][2].rfind("="+dateCodeSplit[m].split("=")[1])]
                    replaced = dateCodeSplit[m-1].split("=")[1]
                    getRemark = ''.join(getRemark.replace(replaced,""))
                    getRemark = getRemark.replace("(","")
                    getRemark = getRemark.replace(")","")
                    getRemark = getRemark.lstrip()
                    '''

                    DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, getDateCode, getRemark))
                    sealedResult = DB.cursor.fetchone()
                    user_name = LoginSystem.user_name
                    #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Packed_carton, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
                    #               "Remove + Break Carton", partNo, "(\"" + str(looseQuantityGet[y][4]) + "\")=-1", "(" + str(getDateCode) + " , " + str(getRemark) + ")", datetime.now())
                    if not sealedResult:
                        DB.cursor.execute("INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                       (partNo, int(getQuantity), str(getDateCode), getRemark, looseQuantityGet[y][5], datetime.now(), user_name))
                    else:
                        DB.cursor.execute(
                            "UPDATE sealed_inventory SET quantity = quantity + %s WHERE part_no = %s AND date_code = %s AND remarks = %s AND id = %s",
                            (getQuantity, partNo, getDateCode, getRemark, sealedResult[0]))
                    DB.conn.commit()
                    logger.info("Loose quantity allocated to deleted delivery order ID " + str(deliveryOrderID) + " is sent back to the inventory, quantity of " + str(int(looseQuantityGet[y][0]) * int(looseQuantityGet[y][3])))
            DB.cursor.execute("DELETE FROM carton_table WHERE delivery_id = %s AND loose_quantity > 0", (deliveryOrderID,))
            DB.conn.commit()
    update_main_inventory(partNo)
    process_info.append("\n* The delivery order " + str(deliveryOrderID) + " is successfully deleted!")
    process_info_2 = checkOtherOrders(partNo)
    if process_info_2 is not None:
        process_info.extend(process_info_2)
    return process_info
##############################################################################################################
# Function 3 to delete multiple delivery order entries, based on the delivery order no.
def deleteDeliveryOrderNo(deliveryOrderNo, reason):
    # Finds the deliveryOrderNo, and then deletes.
    process_info = []
    DB.cursor.execute("SELECT id FROM delivery_orders WHERE delivery_order = %s", (deliveryOrderNo,))
    deliveryOrderInfo = DB.cursor.fetchall()
    deliveryOrderInfo= list(map(list, deliveryOrderInfo))
    noDeliveryOrders = len(deliveryOrderInfo)
    for x in range(noDeliveryOrders):
        process_info_2 = deleteDeliveryOrderEntry(deliveryOrderInfo[x][0], reason)
        if process_info_2 is not None:
            process_info.extend(process_info_2)
    process_info.append("\n* The delivery orders related to the delivery order no " + str(deliveryOrderNo) + " are successfully deleted!")
    return process_info
##############################################################################################################
def str_todate(text):
    text = re.sub(r"[^\d-]", "", text)
    return datetime.strptime(text, "%Y-%m-%d").date()
##############################################################################################################
def threedbp(looseQty, weightLimit, partNo):
    # Considering that 3DBP won't be used, this may not be needed! Process_info is removed for this function.
    DB.cursor.execute("SELECT * FROM part_info WHERE part_no = %s", (partNo,))
    part_info = DB.cursor.fetchone()
    if int(part_info[6]) == 0 or int(part_info[8]) == 0:
        return "N/A"
    if part_info[10] == "PCS" and part_info[11] > 0:
        looseQty = math.ceil(looseQty/part_info[11])
    DB.cursor.execute("SELECT recommend_carton1, recommend_carton2, recommend_carton3 FROM carton_reference "
                   "WHERE partNo = %s AND quantity >= %s ORDER BY quantity", (partNo, looseQty))
    getCarton = DB.cursor.fetchone()
    if getCarton:
        if getCarton[0] != "":
            DB.cursor.execute("SELECT quantity FROM carton_info WHERE carton_no = %s", (getCarton[0],))
            getQuantityOne = DB.cursor.fetchone()
            if getQuantityOne:
                if int(getQuantityOne[0]) > 0:
                    DB.cursor.execute("UPDATE carton_info SET quantity = quantity - 1 WHERE carton_no = %s", (getCarton[0],))
                    logger.info("Carton No. " + str(getCarton[0]) + " is used for the loose quantity.")
                    DB.conn.commit()
                    return str(getCarton[0])

        if getCarton[1] != "":
            DB.cursor.execute("SELECT quantity FROM carton_info WHERE carton_no = %s", (getCarton[1],))
            getQuantityOne = DB.cursor.fetchone()
            if getQuantityOne:
                if int(getQuantityOne[0]) > 0:
                    DB.cursor.execute("UPDATE carton_info SET quantity = quantity - 1 WHERE carton_no = %s", (getCarton[1],))
                    logger.info("Carton No. " + str(getCarton[1]) + " is used for the loose quantity.")
                    DB.conn.commit()
                    return str(getCarton[1])

        if getCarton[2] != "":
            DB.cursor.execute("SELECT quantity FROM carton_info WHERE carton_no = %s", (getCarton[2],))
            getQuantityOne = DB.cursor.fetchone()
            if getQuantityOne:
                if int(getQuantityOne[0]) > 0:
                    DB.cursor.execute("UPDATE carton_info SET quantity = quantity - 1 WHERE carton_no = %s", (getCarton[2],))
                    logger.info("Carton No. " + str(getCarton[2]) + " is used for the loose quantity.")
                    DB.conn.commit()
                    return str(getCarton[2])

        #process_info.append("\n* ERROR: No best carton available. Please update empty stock cartons!")
        logger.info("ERROR: No best carton available. Please update empty stock cartons!")
        return None
    else:
        packer = Packer()
        my_bins = {}
        bundle = []
        offsetPercentage = 1.01
        best_bin = None

        DB.cursor.execute("SELECT * FROM carton_info WHERE quantity > 0")
        carton_info = DB.cursor.fetchall()
        carton_info= list(map(list, carton_info))
        m = 0
        for l in range(len(carton_info)):
            my_bins[m] = Bin(carton_info[l][0], carton_info[l][2], carton_info[l][3], carton_info[l][4],
                             weightLimit)
            packer.add_bin(my_bins[m])
            m+=1

        bundle.append(part_info[1])
        bundle.append(float(part_info[2]))
        bundle.append(float(part_info[3]))
        bundle.append(float(part_info[4]) * int(part_info[6]) * offsetPercentage)
        bundle.append(float(part_info[9]) * int(part_info[6]) * offsetPercentage)
        no_bundle = math.ceil(looseQty / int(part_info[6]))
        for k in range(int(no_bundle)):
            packer.add_item(Item(bundle[0], bundle[1], bundle[2], bundle[3], bundle[4]))
        packer.pack()
        for i in range(len(my_bins)):
            if len(my_bins[i].items) == no_bundle:
                best_bin = my_bins[i]
                break
        if best_bin:
            DB.cursor.execute("UPDATE carton_info SET quantity = quantity - 1 WHERE carton_no = %s", (best_bin.name,))
            logger.info("Carton No. " + str(best_bin.name) + " is used for the loose quantity.")
            DB.conn.commit()
            return best_bin.name
        else:
            bestCartonNo = "N/A"
            #process_info.append("\n* ERROR: No best carton available. Please check the dimensions/bundle quantity/standard quantity for partNo " + str(partNo) + "!")
            logger.info("ERROR: No best carton available. Please check the dimensions/bundle quantity/standard quantity for partNo " + str(partNo) + "!")
            return str(bestCartonNo)
##############################################################################################################
# Function used to send back allocated cartons to the inventory used for automatic carton reallocation.
def remove_cartons(ID):
    # Finds the deliveryOrderNo, and then blanks the cartons_ID.
    DB.cursor.execute("SELECT part_no, cartons_id, fulfilled_quantity FROM delivery_orders WHERE id = %s",(ID,))
    deliveryOrderInfo = DB.cursor.fetchone()
    blankCartonsID = ""
    DB.cursor.execute("UPDATE delivery_orders SET cartons_id = %s, fulfilled_quantity = 0 WHERE id = %s",(blankCartonsID,ID))
    DB.conn.commit()
    partNo = str(deliveryOrderInfo[0])
    cartons_ID = str(deliveryOrderInfo[1])
    fulfilledQuantity = str(deliveryOrderInfo[2])
    description = "(" + str(ID) + "," + str(partNo) + "," + str(fulfilledQuantity) + ")"
    update_log_table("Removing Cartons", "N/A", description, "N/A")
    #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
    #               (ID,partNo, 0-fulfilledQuantity, "Cartons Sent Out", datetime.now()))
    DB.conn.commit()
    # Returning standard quantity stock
    DB.cursor.execute("SELECT COUNT(*) FROM carton_table WHERE delivery_id = %s AND loose_quantity = 0", (ID,))
    noOfCartons = DB.cursor.fetchone()
    noOfCartons = int(noOfCartons[0])
    DB.cursor.execute("SELECT carton_quantity, date_codes, remarks, carton_no FROM carton_table WHERE delivery_id = %s AND loose_quantity = 0", (ID,))
    getCartons = DB.cursor.fetchall()
    getCartons= list(map(list, getCartons))
    if getCartons:
        DB.cursor.execute("UPDATE carton_table SET delivery_id = %s WHERE delivery_id = %s AND loose_quantity = 0", (0,ID))
        logger.info("Standard cartons allocated to deleted delivery order ID " + str(ID) + " are sent back to the inventory")
        #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Packed_carton, Temp_carton, Notes, time) ""VALUES (%s,%s,%s,%s,%s,%s)",
        #               "Remove Carton", partNo, "(\"" + str(getCartons[0][3]) + "\")=-" + str(noOfCartons), "(\"" + str(getCartons[0][3]) + "\")=+" + str(noOfCartons), "DO = (" + str(ID) + ")", datetime.now())
        DB.conn.commit()
    # Returning old stock
    if deliveryOrderInfo[1] is not None:
        if "old_stock" in cartons_ID:
            old_stock_quantity = 0
            if "|" in cartons_ID:
                cartonList = cartons_ID.split(" | ")
                for x in range(len(cartonList)):
                    if "old_stock" in cartonList[x]:
                        old_stock_quantity += int(cartonList[x][cartonList[x].find("(")+1:cartonList[x].find(")")])
            else:
                old_stock_quantity += int(cartons_ID[cartons_ID.find("(")+1:cartons_ID.find(")")])
            DB.cursor.execute("SELECT id FROM main_inventory WHERE part_no = %s", (partNo,))
            findPartNo = DB.cursor.fetchone()
            if findPartNo:
                DB.cursor.execute("UPDATE main_inventory SET old_stock = old_stock + %s, total_stock = total_stock + %s WHERE part_no = %s", (old_stock_quantity, old_stock_quantity, partNo))
            else:
                DB.cursor.execute("SELECT stn_qty FROM part_info WHERE part_no = %s", (partNo,))
                stnQtyPart = DB.cursor.fetchone()
                stnQty = int(stnQtyPart[0])
                DB.cursor.execute("INSERT INTO main_inventory (part_no, stn_qty, old_stock, total_stock) " "VALUES (%s,%s,%s,%s)", (partNo, stnQty, old_stock_quantity, old_stock_quantity))
                update_main_inventory(partNo)
            logger.info("Old stock allocated to deleted delivery order ID " + str(ID) + " is sent back to the inventory, quantity of " + str(old_stock_quantity))
            #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Quantity, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
            #               "Remove Old Stock", partNo, "OS = - " + str(old_stock_quantity) + "(returned)", "DO = (" + str(ID) + ")", datetime.now())
            DB.conn.commit()
    # Returning loose quantity stock to sealed inventory
    DB.cursor.execute("SELECT carton_quantity, date_codes, remarks, loose_quantity, carton_no, log_id FROM carton_table WHERE delivery_id = %s AND loose_quantity > 0", (ID,))
    looseQuantityGet = DB.cursor.fetchall()
    looseQuantityGet= list(map(list, looseQuantityGet))
    if looseQuantityGet:
        for y in range(len(looseQuantityGet)):
            if "=" not in looseQuantityGet[y][1]:
                DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, looseQuantityGet[y][1], looseQuantityGet[y][2]))
                sealedResult = DB.cursor.fetchone()
                user_name = LoginSystem.user_name
                if not sealedResult:
                    DB.cursor.execute(
                        "INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                        (partNo, int(looseQuantityGet[y][0]) * int(looseQuantityGet[y][3]), looseQuantityGet[y][1], looseQuantityGet[y][2], looseQuantityGet[y][5], datetime.now(), user_name))
                else:
                    DB.cursor.execute(
                        "UPDATE sealed_inventory SET quantity = quantity + %s WHERE part_no = %s AND date_code = %s AND remarks = %s AND id = %s",
                        (int(looseQuantityGet[y][0]) * int(looseQuantityGet[y][3]), partNo, looseQuantityGet[y][1], looseQuantityGet[y][2], sealedResult[0]))
                #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Packed_carton, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
                #               "Remove + Break Carton", partNo, "(\"" + str(looseQuantityGet[y][4]) + "\")=-1", "DO = (" + str(ID) + "), (" + str(looseQuantityGet[y][1]) + " , " + str(looseQuantityGet[y][2]) + ")", datetime.now())
                DB.conn.commit()
                logger.info("Loose quantity allocated to deleted delivery order ID " + str(ID) + " is sent back to the inventory, quantity of " + str(int(looseQuantityGet[y][0]) * int(looseQuantityGet[y][3])))
            else:
                dateCodeSplit = looseQuantityGet[y][1].split(" ")
                remarkSplit = looseQuantityGet[y][2].split(")")
                for m in range(len(dateCodeSplit)):
                    getDateCode = dateCodeSplit[m].split("=")[0]
                    getQuantity = dateCodeSplit[m].split("=")[1]
                    getRemark = remarkSplit[m].split("(")[1]
                    '''
                    if m == 0:
                        getRemark = looseQuantityGet[y][2].split("="+str(getQuantity))[0]
                    else:
                        getRemark = looseQuantityGet[y][2][looseQuantityGet[y][2].find("="+str(dateCodeSplit[m-1].split("=")[1]))+len("="+str(dateCodeSplit[m-1].split("=")[1])):looseQuantityGet[y][2].rfind("="+dateCodeSplit[m].split("=")[1])]
                    replaced = dateCodeSplit[m-1].split("=")[1]
                    getRemark = ''.join(getRemark.replace(replaced,""))
                    getRemark = getRemark.replace("(","")
                    getRemark = getRemark.replace(")","")
                    getRemark = getRemark.lstrip()
                    '''

                    DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, getDateCode, getRemark))
                    sealedResult = DB.cursor.fetchone()
                    user_name = LoginSystem.user_name
                    #DB.cursor.execute("INSERT INTO job_task (Job_Name, partNo, Packed_carton, Notes, time) ""VALUES (%s,%s,%s,%s,%s)",
                    #               "Remove + Break Carton", partNo, "(\"" + str(looseQuantityGet[y][4]) + "\")=-1", "(" + str(getDateCode) + " , " + str(getRemark) + ")", datetime.now())
                    if not sealedResult:
                        DB.cursor.execute("INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                       (partNo, int(getQuantity), str(getDateCode), getRemark, looseQuantityGet[y][5], datetime.now(), user_name))
                    else:
                        DB.cursor.execute(
                            "UPDATE sealed_inventory SET quantity = quantity + %s WHERE part_no = %s AND date_code = %s AND remarks = %s AND id = %s",
                            (getQuantity, partNo, getDateCode, getRemark, sealedResult[0]))
                    DB.conn.commit()
                    logger.info("Loose quantity allocated to deleted delivery order ID " + str(ID) + " is sent back to the inventory, quantity of " + str(int(looseQuantityGet[y][0]) * int(looseQuantityGet[y][3])))
            DB.cursor.execute("DELETE FROM carton_table WHERE delivery_id = %s AND loose_quantity > 0", (ID,))
            DB.conn.commit()
    update_main_inventory(partNo)
##############################################################################################################
# Function used to evaluate the delivery orders if the earliest delivery orders based on the partNo are fulfilled compared with the later ones, used for automatic
# carton reallocation.
def evaluate_part_list(partNo):
    process_info = []
    DB.cursor.execute("SELECT delivery_date FROM delivery_orders WHERE part_no = %s AND quantity > fulfilled_quantity ORDER BY delivery_date",(partNo,))
    earliestdd = DB.cursor.fetchone()
    fulfilledIDs = None
    if earliestdd:
        DB.cursor.execute("SELECT id FROM delivery_orders WHERE delivery_date > %s AND part_no = %s AND fulfilled_quantity > 0 ORDER BY delivery_date", (earliestdd[0],partNo))
        fulfilledIDs = DB.cursor.fetchall()
    if fulfilledIDs:
        fulfilledIDs= list(map(list, fulfilledIDs))
        process_info.append("Fulfilled orders for partNo " + partNo + " are found. Will be removed and allocated......")
        for x in range(len(fulfilledIDs)):
            remove_cartons(fulfilledIDs[x][0])
        process_info_2 = checkOtherOrders(partNo)
        if process_info_2 is not None:
            process_info.extend(process_info_2)
    return process_info
##############################################################################################################
# Function used to obtain a list of cartons allocated to a certain specific delivery order ID to be used for Function 4.
def get_delivery_order_carton_list(deliveryOrder):
    DB.cursor.execute("SELECT date_codes, remarks, carton_no, loose_quantity, carton_quantity, part_no, id FROM carton_table WHERE delivery_id = %s", (deliveryOrder,))
    deliveryOrderInfo = DB.cursor.fetchall()
    if not deliveryOrderInfo:
        messagebox.showerror("Error","No cartons are allocated to this delivery order!")
        return None
    else:
        deliveryOrderInfo= list(map(list, deliveryOrderInfo))
        cartonTableList = []
        for x in range(len(deliveryOrderInfo)):
            if deliveryOrderInfo[x][1] == None:
                deliveryOrderInfo[x][1] = ""
            quantityInCarton = 0
            if deliveryOrderInfo[x][3] == 0:
                DB.cursor.execute("SELECT stn_qty, stn_carton, uom, cavity from part_info WHERE part_no = %s;", (deliveryOrderInfo[x][5],))
                stnQtyCtn = DB.cursor.fetchone()
                stnQty = int(stnQtyCtn[0])
                uom = str(stnQtyCtn[2])
                if uom == "PCS":
                    cavity = int(stnQtyCtn[3])
                    if cavity > 1:
                        stnQty *= cavity
                quantityInCarton = stnQty
            else:
                quantityInCarton = deliveryOrderInfo[x][3]
            cartonTableList.append([x+1,deliveryOrderInfo[x][0],deliveryOrderInfo[x][1],deliveryOrderInfo[x][2], quantityInCarton, deliveryOrderInfo[x][4]])
        return cartonTableList
##############################################################################################################
'''
def reject_carton(deliveryOrder,optionSelected):
    # Note that the optionSelected is -1!
    process_info = []
    DB.cursor.execute("SELECT dateCodes, remarks, carton_no, looseQuantity, cartonQuantity, partNo, ID FROM carton_table WHERE delivery_ID = %s", deliveryOrder)
    deliveryOrderInfo = DB.cursor.fetchall()
    cartonTableList = []
    for x in range(len(deliveryOrderInfo)):
        if deliveryOrderInfo[x][1] == None:
            deliveryOrderInfo[x][1] = ""
        quantityInCarton = 0
        if deliveryOrderInfo[x][3] == 0:
            DB.cursor.execute("SELECT stnQty, stnCarton, uom, cavity from part_info WHERE partNo = %s;", deliveryOrderInfo[x][5])
            stnQtyCtn = DB.cursor.fetchone()
            stnQty = int(stnQtyCtn[0])
            uom = str(stnQtyCtn[2])
            if uom == "PCS":
                cavity = int(stnQtyCtn[3])
                if cavity > 1:
                    stnQty *= cavity
            quantityInCarton = stnQty
        else:
            quantityInCarton = int(deliveryOrderInfo[x][3])
        cartonTableList.append([x+1,deliveryOrderInfo[x][0],deliveryOrderInfo[x][1],deliveryOrderInfo[x][2], quantityInCarton, deliveryOrderInfo[x][4]])
    excessParts = 0
    if int(deliveryOrderInfo[int(optionSelected)-1][3]) == 0:
        excessParts += (deliveryOrderInfo[0][4] * stnQty)
    else:
        excessParts += deliveryOrderInfo[0][3]
    logger.info("Rejecting carton batch of carton ID of " + str(deliveryOrderInfo[int(optionSelected)-1][6]))
    DB.cursor.execute("DELETE FROM carton_table WHERE ID = %s", (deliveryOrderInfo[int(optionSelected)-1][6]))
    DB.conn.commit()
    DB.cursor.execute("SELECT cartons_ID FROM delivery_orders WHERE ID = %s",deliveryOrder)
    cartonDeliveryInfo = DB.cursor.fetchone()
    old_stock = 0
    cartonsID = ""
    cartonIDList = []
    if cartonDeliveryInfo is not None:
        if "|" in cartonDeliveryInfo[0]:
            cartonIDList = cartonDeliveryInfo[0].split(" | ")
        else:
            cartonIDList.append(cartonDeliveryInfo[0])
    for x in range(len(cartonIDList)):
        if "old_stock" in cartonIDList[x]:
            old_stock += int(cartonIDList[x][cartonIDList[x].find("(")+1:cartonIDList[x].find(")")])
    if old_stock > 0:
        cartonsID += "old_stock ("
        cartonsID += str(old_stock)
        cartonsID += ")"
    DB.cursor.execute("SELECT ID FROM carton_table WHERE delivery_id = %s", deliveryOrder)
    leftCartonList = DB.cursor.fetchall()
    for z in range(len(leftCartonList)):
        if cartonsID != "":
            cartonsID += " | "
        cartonsID += str(leftCartonList[z][0])
    update_main_inventory(deliveryOrderInfo[0][5])
    DB.cursor.execute("UPDATE delivery_orders SET fulfilledQuantity = fulfilledQuantity - %s, cartons_ID = %s WHERE id = %s", (excessParts,cartonsID,deliveryOrder))
    DB.conn.commit()
    process_info.append("Carton(s) rejected successfully!")
    return process_info
    '''
##############################################################################################################
# Function 4: Reject carton batch based on carton ID. Once it's rejected it's removed from the database!
def reject_carton(carton_ID):
    process_info = []
    DB.cursor.execute("SELECT delivery_id, loose_quantity, carton_quantity, part_no FROM carton_table WHERE id = %s", (carton_ID,))
    delivery_id_info = DB.cursor.fetchone()
    logger.info("Rejecting carton batch of carton ID of " + str(carton_ID))
    DB.cursor.execute("DELETE FROM carton_table WHERE id = %s", (carton_ID,))
    DB.conn.commit()
    DB.cursor.execute("SELECT date_codes, remarks, carton_no, loose_quantity, carton_quantity, part_no, id FROM carton_table WHERE delivery_id = %s", (delivery_id_info[0],))
    deliveryOrderInfo = DB.cursor.fetchall()
    deliveryOrderInfo= list(map(list, deliveryOrderInfo))
    DB.cursor.execute("SELECT stn_qty, stn_carton, uom, cavity from part_info WHERE part_no = %s;", (delivery_id_info[3],))
    stnQtyCtn = DB.cursor.fetchone()
    stnQty = int(stnQtyCtn[0])
    uom = str(stnQtyCtn[2])
    if uom == "PCS":
        cavity = int(stnQtyCtn[3])
        if cavity > 1:
            stnQty *= cavity
    excessParts = 0
    if int(delivery_id_info[1]) == 0:
        excessParts += (int(delivery_id_info[2]) * stnQty)
    else:
        excessParts += int(delivery_id_info[1])
    DB.cursor.execute("SELECT cartons_id FROM delivery_orders WHERE id = %s",(delivery_id_info[0],))
    cartonDeliveryInfo = DB.cursor.fetchone()
    old_stock = 0
    cartonsID = ""
    cartonIDList = []
    if cartonDeliveryInfo is not None:
        if "|" in cartonDeliveryInfo[0]:
            cartonIDList = cartonDeliveryInfo[0].split(" | ")
        else:
            cartonIDList.append(cartonDeliveryInfo[0])
    for x in range(len(cartonIDList)):
        if "old_stock" in cartonIDList[x]:
            old_stock += int(cartonIDList[x][cartonIDList[x].find("(")+1:cartonIDList[x].find(")")])
    if old_stock > 0:
        cartonsID += "old_stock ("
        cartonsID += str(old_stock)
        cartonsID += ")"
    DB.cursor.execute("SELECT id FROM carton_table WHERE delivery_id = %s", (delivery_id_info[0],))
    leftCartonList = DB.cursor.fetchall()
    leftCartonList= list(map(list, leftCartonList))
    for z in range(len(leftCartonList)):
        if cartonsID != "":
            cartonsID += " | "
        cartonsID += str(leftCartonList[z][0])
    update_main_inventory(delivery_id_info[3])
    DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity - %s, cartons_id = %s WHERE id = %s", (excessParts,cartonsID,delivery_id_info[0]))
    DB.conn.commit()
    description = "(" + str(delivery_id_info[0]) + "," + str(delivery_id_info[3]) + "," + str(excessParts) + ")"
    update_log_table("Removing Cartons", "N/A", description, "N/A")
    #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
    #               (delivery_id_info[0],delivery_id_info[3], 0-excessParts, "Cartons Rejected", datetime.now()))
    DB.conn.commit()
    process_info.append("Carton(s) rejected successfully!")
    return process_info
##############################################################################################################
# Function used to obtain old stock allocated to a certain specific delivery order ID to be used for Function 4.
def get_old_stock_from_delivery_order(deliveryOrder):
    DB.cursor.execute("SELECT cartons_id FROM delivery_orders WHERE id = %s", (deliveryOrder,))
    deliveryOrderInfo = DB.cursor.fetchone()
    if deliveryOrderInfo[0] is not None:
        if "old_stock" not in deliveryOrderInfo[0]:
            messagebox.showerror("Error","No old stock is allocated to this delivery order!")
            return None
        else:
            old_stock = 0
            for x in range(len(deliveryOrderInfo)):
                if "old_stock" in deliveryOrderInfo[x]:
                    old_stock += int(deliveryOrderInfo[x][deliveryOrderInfo[x].find("(")+1:deliveryOrderInfo[x].find(")")])
            return old_stock
##############################################################################################################
# Function 4: Reject old stock allocated to a certain delivery order ID. Once it's rejected it's removed from the database!
def reject_old_stock(deliveryOrder,deducted_quantity):
    process_info = []
    DB.cursor.execute("SELECT cartons_id FROM delivery_orders WHERE id = %s", (deliveryOrder,))
    deliveryOrderInfo = DB.cursor.fetchone()
    DB.cursor.execute("SELECT part_no FROM delivery_orders WHERE id = %s", (deliveryOrder,))
    partNo = DB.cursor.fetchone()
    if deliveryOrderInfo[0] is not None:
        old_stock = 0
        for x in range(len(deliveryOrderInfo)):
            if "old_stock" in deliveryOrderInfo[x]:
                old_stock += int(deliveryOrderInfo[x][deliveryOrderInfo[x].find("(")+1:deliveryOrderInfo[x].find(")")])
        cartonsID = ""
        if (old_stock-deducted_quantity) > 0:
            cartonsID += "old_stock ("
            cartonsID += str(old_stock-deducted_quantity)
            cartonsID += ")"
        DB.cursor.execute("SELECT id FROM carton_table WHERE delivery_id = %s", (deliveryOrder,))
        leftCartonList = DB.cursor.fetchall()
        leftCartonList= list(map(list, leftCartonList))
        for z in range(len(leftCartonList)):
            if cartonsID != "":
                cartonsID += " | "
            cartonsID += str(leftCartonList[z][0])
        DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity - %s, cartons_id = %s WHERE id = %s", (deducted_quantity,cartonsID,deliveryOrder))
        description = "(" + str(deliveryOrder) + "," + str(partNo) + "," + str(deducted_quantity) + ")"
        update_log_table("Removing Cartons", "N/A", description, "N/A")
        #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
        #               (deliveryOrder,partNo, 0-deducted_quantity, "Old Stock Rejected", datetime.now()))
        DB.conn.commit()
        logger.info("Rejecting old stock quantity of " + str(deducted_quantity) + " from original quantity of " + str(old_stock))
        process_info.append("\n* The old stock is successfully rejected!")
    return process_info
##############################################################################################################
# Function used to get quantity of empty cartons to be used for Function 5, based on carton no.
def get_quantity_of_empty_carton(carton_no):
    DB.cursor.execute("SELECT quantity FROM carton_info WHERE carton_no = %s", (carton_no,))
    foundCarton = DB.cursor.fetchone()
    if not foundCarton:
        messagebox.showerror("Error","Invalid input. Please try again!")
        return None
    else:
        return int(foundCarton[0])
##############################################################################################################
# Function 5: Editing quantity of empty cartons based on the carton no.
def change_quantity_of_empty_carton(carton_no, new_quantity):
    process_info = []
    DB.cursor.execute("SELECT quantity FROM carton_info WHERE carton_no = %s", (carton_no,))
    foundCarton = DB.cursor.fetchone()
    if not foundCarton:
        messagebox.showerror("Error","Invalid input. Please try again!")
        process_info.append("\n* ERROR: Invalid input. Please try again!")
    else:
        DB.cursor.execute("UPDATE carton_info SET quantity = %s WHERE carton_no = %s", (new_quantity, carton_no))
        DB.conn.commit()
        process_info.append("\n* The carton info is successfully updated!")
    logger.info("Quantity for carton no " + str(carton_no) + " has changed to " + str(new_quantity))
    return process_info
##############################################################################################################
# Function used to get quantity of filled cartons to be used for Function 6, based on partNo.
def get_filled_carton_list(partNo):
    DB.cursor.execute("SELECT id, carton_quantity, date_codes, remarks, packing_date FROM carton_table WHERE part_no = %s AND loose_quantity = 0 AND (delivery_id = 0 OR delivery_id IS NULL OR LENGTH(delivery_id & '') = 0)", (partNo,))
    filled_carton_table = DB.cursor.fetchall()
    filled_carton_table= list(map(list, filled_carton_table))
    return filled_carton_table
##############################################################################################################
# Function 6: Editing quantity of filled cartons based on the carton ID.
def change_quantity_of_filled_carton(idCarton, quantity, reason=""):
    process_info = []
    DB.cursor.execute("SELECT carton_quantity, date_codes, remarks, part_no, log_id FROM carton_table WHERE id = %s", (idCarton,))
    carton_table = DB.cursor.fetchone()
    DB.cursor.execute("UPDATE carton_table SET carton_quantity = %s WHERE id = %s", (quantity, idCarton))
    DB.conn.commit()
    changeInQuantity = int(quantity) - carton_table[0]
    DB.cursor.execute("UPDATE main_inventory SET carton_quantity = carton_quantity + %s WHERE part_no = %s", (changeInQuantity, carton_table[3]))
    DB.cursor.execute("SELECT stn_qty, uom, cavity from part_info WHERE part_no = %s;", (carton_table[3],))
    stnQtyCtn = DB.cursor.fetchone()
    stnQty = int(stnQtyCtn[0])
    uom = str(stnQtyCtn[1])
    if uom == "PCS":
        cavity = int(stnQtyCtn[2])
        if cavity > 1:
            stnQty *= cavity
    if carton_table[4] is not None:
        log_id = int(carton_table[4])
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
    #old_description = "(" + str(idCarton) + "," + str(carton_table[3]) + "," + str(carton_table[0]) + ")"
    new_description = "(" + str(idCarton) + "," + str(carton_table[3]) + "," + str(carton_table[0]) + " -> " + str(quantity) + ")"
    update_log_table("Change Quantity (Carton)", old_description, new_description, reason)
    #DB.cursor.execute("INSERT INTO part_no_entry_tracker (partNo,quantityChange,description,newPartNo,time) VALUES (%s,%s,%s,%s,%s)", (carton_table[3],stnQty*changeInQuantity,"Carton Quantity Change","N/A", datetime.now()))
    DB.conn.commit()
    process_info.append("\n* The carton table is successfully updated!")
    logger.info("Quantity for carton ID " + str(idCarton) + " has changed to " + str(quantity))
    update_main_inventory(carton_table[3])
    return process_info
##############################################################################################################
def change_part_no_of_filled_carton(idCarton, new_part_no, reason=""):
    process_info = []
    DB.cursor.execute("SELECT part_no, log_id FROM carton_table WHERE id = %s", (idCarton,))
    carton_table = DB.cursor.fetchone()
    old_part_no = str(carton_table[0])
    log_id = 0
    DB.cursor.execute("UPDATE carton_table SET part_no = %s WHERE id = %s", (new_part_no, idCarton))
    DB.conn.commit()

    if carton_table[1] is not None:
        log_id = int(carton_table[1])
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
    #old_description = "(" + str(idCarton) + "," + str(carton_table[3]) + "," + str(carton_table[0]) + ")"
    new_description = "(" + str(idCarton) + "," + old_part_no + " -> " + str(new_part_no) + ")"
    update_log_table("Change Part No (Carton)", old_description, new_description, reason)
    #DB.cursor.execute("INSERT INTO part_no_entry_tracker (partNo,quantityChange,description,newPartNo,time) VALUES (%s,%s,%s,%s,%s)", (carton_table[3],stnQty*changeInQuantity,"Carton Quantity Change","N/A", datetime.now()))
    DB.conn.commit()
    process_info.append("\n* The carton table is successfully updated!")
    logger.info("Part No for carton ID " + str(idCarton) + " has changed to " + str(new_part_no))
    update_main_inventory(old_part_no)
    update_main_inventory(new_part_no)
    return process_info
##############################################################################################################
# NEW FUNCTION: Adding quantity of filled cartons.
def add_quantity_of_new_filled_carton(partNo, cartonQuantity, dateCodes, earliestDateCode, remarks, packingDate):
    process_info = []
    DB.cursor.execute("SELECT stn_carton FROM part_info WHERE part_no = %s", (partNo,))
    stn_carton = DB.cursor.fetchone()
    user_name = LoginSystem.user_name
    DB.cursor.execute("INSERT INTO carton_table (part_no, carton_quantity, date_codes, earliest_date_code, remarks, loose_quantity, carton_no, delivery_id, packing_date, time_created, user_name) "
                   "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (partNo, cartonQuantity, dateCodes, earliestDateCode, remarks, 0, stn_carton[0], 0, packingDate, datetime.now(), user_name))
    DB.conn.commit()
    DB.cursor.execute("SELECT stn_qty, uom, cavity from part_info WHERE part_no = %s;", (partNo,))
    stnQtyCtn = DB.cursor.fetchone()
    stnQty = int(stnQtyCtn[0])
    uom = str(stnQtyCtn[1])
    if uom == "PCS":
        cavity = int(stnQtyCtn[2])
        if cavity > 1:
            stnQty *= cavity
    DB.cursor.execute("SELECT id FROM main_inventory WHERE part_no = %s", (partNo,))
    partID = DB.cursor.fetchone()
    if partID:
        DB.cursor.execute("UPDATE main_inventory SET carton_quantity = carton_quantity + %s, new_stock = new_stock + %s, total_stock = total_stock + %s  WHERE part_no = %s", (cartonQuantity, int(cartonQuantity) * stnQty, int(cartonQuantity) * stnQty, partNo))
    else:
        DB.cursor.execute("INSERT INTO main_inventory (part_no, stn_qty, new_stock, total_stock) " "VALUES (%s,%s,%s,%s)", (partNo, stnQty, int(cartonQuantity) * stnQty, int(cartonQuantity) * stnQty))
    DB.conn.commit()
    process_info.append("\n* The cartons are successfully added!")
    update_main_inventory(partNo)
    return process_info
##############################################################################################################
# Function used to get quantity of sealed inventory to be used for Function 7, based on partNo.
def get_sealed_list(partNo):
    DB.cursor.execute("SELECT id, quantity, date_code, remarks FROM sealed_inventory WHERE part_no = %s", (partNo,))
    sealed_inventory = DB.cursor.fetchall()
    sealed_inventory= list(map(list, sealed_inventory))
    return sealed_inventory
##############################################################################################################
# Function 7: Editing quantity of sealed inventory based on the sealed ID.
def change_quantity_of_sealed_inventory(idSealed, quantity, reason=""):
    process_info = []
    DB.cursor.execute("SELECT quantity, date_code, remarks, part_no, log_id FROM sealed_inventory WHERE id = %s", (idSealed,))
    sealed_inventory = DB.cursor.fetchone()
    DB.cursor.execute("UPDATE sealed_inventory SET quantity = %s WHERE id = %s", (quantity, idSealed))
    DB.conn.commit()
    changeInQuantity = int(quantity) - int(sealed_inventory[0])
    DB.cursor.execute("UPDATE main_inventory SET sealed_quantity = sealed_quantity + %s WHERE part_no = %s", (changeInQuantity, sealed_inventory[3]))
    if sealed_inventory[4] is not None:
        log_id = int(sealed_inventory[4])
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
    #old_description = "(" + str(idSealed) + str(sealed_inventory[3]) + "," + str(sealed_inventory[0]) + ")"
    new_description = "(" + str(idSealed) + str(sealed_inventory[3]) + "," + str(sealed_inventory[0]) + " -> " + str(quantity) + ")"
    update_log_table("Change Quantity (Sealed)", old_description, new_description, reason)
    #DB.cursor.execute("INSERT INTO part_no_entry_tracker (partNo,quantityChange,description,newPartNo,time) VALUES (%s,%s,%s,%s,%s)", (sealed_inventory[3],changeInQuantity,"Sealed Quantity Change","N/A", datetime.now()))
    DB.conn.commit()
    process_info.append("\n* The carton table is successfully updated!")
    logger.info("Quantity for sealed ID " + str(idSealed) + " has changed to " + str(quantity))
    update_main_inventory(sealed_inventory[3])
    return process_info
##############################################################################################################
def change_part_no_of_sealed_batch(idSealed, new_part_no, reason=""):
    process_info = []
    DB.cursor.execute("SELECT part_no, log_id FROM sealed_inventory WHERE id = %s", (idSealed,))
    sealed_inventory = DB.cursor.fetchone()
    old_part_no = str(sealed_inventory[0])
    DB.cursor.execute("UPDATE sealed_inventory SET part_no = %s WHERE id = %s", (new_part_no, idSealed))
    DB.conn.commit()

    if sealed_inventory[1] is not None:
        log_id = int(sealed_inventory[1])
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
    #old_description = "(" + str(idSealed) + str(sealed_inventory[3]) + "," + str(sealed_inventory[0]) + ")"
    new_description = "(" + str(idSealed) + str(old_part_no) + " -> " + str(new_part_no) + ")"
    update_log_table("Change Part No (Sealed)", old_description, new_description, reason)
    #DB.cursor.execute("INSERT INTO part_no_entry_tracker (partNo,quantityChange,description,newPartNo,time) VALUES (%s,%s,%s,%s,%s)", (sealed_inventory[3],changeInQuantity,"Sealed Quantity Change","N/A", datetime.now()))
    DB.conn.commit()
    process_info.append("\n* The sealed inventory is successfully updated!")
    logger.info("Part No for sealed ID " + str(idSealed) + " has changed to " + str(new_part_no))
    update_main_inventory(old_part_no)
    update_main_inventory(new_part_no)
    return process_info
##############################################################################################################
# NEW FUNCTION: Adding quantity of sealed stock.
def add_quantity_of_new_sealed_stock(partNo, quantity, dateCode, remarks, additional_info):
    process_info = []
    user_name = LoginSystem.user_name
    DB.cursor.execute("INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, additional_info, time_created, user_name) " "VALUES (%s,%s,%s,%s,%s,%s,%s)", (partNo, quantity, dateCode, remarks, additional_info, datetime.now(), user_name))
    DB.cursor.execute("SELECT id FROM main_inventory WHERE part_no = %s", (partNo,))
    partID = DB.cursor.fetchone()
    if partID:
        DB.cursor.execute("UPDATE main_inventory SET sealed_quantity = sealed_quantity + %s, new_stock = new_stock + %s, total_stock = total_stock + %s  WHERE part_no = %s", (quantity, quantity, quantity, partNo))
    else:
        DB.cursor.execute("INSERT INTO main_inventory (part_no, sealed_quantity, new_stock, total_stock) " "VALUES (%s,%s,%s,%s)", (partNo, quantity, quantity, quantity))
    DB.conn.commit()
    process_info.append("\n* The sealed stock is successfully added!")
    update_main_inventory(partNo)
    return process_info
##############################################################################################################
# Function used to get quantity of old stock to be used for Function 8, based on partNo.
def get_old_stock_from_part_no(partNo):
    DB.cursor.execute("SELECT old_stock FROM main_inventory WHERE part_no = %s", (partNo,))
    old_stock = DB.cursor.fetchone()
    old_stock = int(old_stock[0])
    return old_stock
##############################################################################################################
# Function 8: Editing quantity of old stock based on the partNo.
def change_quantity_of_old_stock(partNo, quantity, reason=""):
    process_info = []
    DB.cursor.execute("SELECT part_no, old_stock FROM main_inventory WHERE part_no = %s", (partNo,))
    checkPartExists = DB.cursor.fetchone()
    if checkPartExists:
        oldOldStock = checkPartExists[1]
        DB.cursor.execute("UPDATE main_inventory SET old_stock = %s WHERE part_no = %s", (quantity,partNo))
        DB.conn.commit()
        DB.cursor.execute("UPDATE main_inventory SET total_stock = old_stock + new_stock WHERE part_no = %s", (partNo,))
        old_description = "(" + str(partNo) + "," + str(oldOldStock) + ")"
        new_description = "(" + str(partNo) + "," + str(quantity) + ")"
        update_log_table("Change Quantity (Old Stock)", old_description, new_description, reason)
        #DB.cursor.execute("INSERT INTO part_no_entry_tracker (partNo,quantityChange,description,newPartNo,time) VALUES (%s,%s,%s,%s,%s)", (partNo,quantity-int(oldOldStock),"Old Stock Change","N/A", datetime.now()))
        DB.conn.commit()
    else:
        DB.cursor.execute("SELECT stn_qty, uom, cavity from part_info WHERE part_no = %s;", (partNo,))
        stnQtyCtn = DB.cursor.fetchone()
        stnQty = int(stnQtyCtn[0])
        uom = str(stnQtyCtn[1])
        if uom == "PCS":
            cavity = int(stnQtyCtn[2])
            if cavity > 1:
                stnQty *= cavity
        DB.cursor.execute("INSERT INTO main_inventory (part_no, stn_qty, old_stock, total_stock) " "VALUES (%s,%s,%s,%s)", (partNo, stnQty, quantity, quantity))
        old_description = "(" + str(partNo) + ", 0" + ")"
        new_description = "(" + str(partNo) + "," + str(quantity) + ")"
        update_log_table("Change Quantity (Old Stock)", old_description, new_description, reason)
        #DB.cursor.execute("INSERT INTO part_no_entry_tracker (partNo,quantityChange,description,newPartNo,time) VALUES (%s,%s,%s,%s,%s)", (partNo,quantity,"Old Stock Change","N/A", datetime.now()))
        DB.conn.commit()
    process_info.append("\n* The old stock quantity has been updated!")
    logger.info("Quantity for old stock for " + str(partNo) + " has changed to " + str(quantity))
    update_main_inventory(partNo)
    return process_info
##############################################################################################################
# Function 9: Goes through each partNo and updates the inventory, as well as reorganizing the delivery orders.
def auto_update_inventory():
    process_info = []
    DB.cursor.execute("SELECT part_no FROM part_info")
    part_info = DB.cursor.fetchall()
    part_info= list(map(list, part_info))
    for i in range(len(part_info)):
        update_main_inventory(part_info[i][0])
        process_info.append("\n* PartNo " + part_info[i][0] + " successfully updated!")
    process_info.append("\n* The main inventory is successfully updated!")
    DB.cursor.execute("DELETE FROM main_inventory WHERE part_no IS NULL")
    DB.conn.commit()
    DB.cursor.execute("SELECT part_no FROM main_inventory WHERE total_stock = 0")
    no_stock_main_inventory = DB.cursor.fetchall()
    no_stock_main_inventory = list(map(list, no_stock_main_inventory))
    for part in no_stock_main_inventory:
        DB.cursor.execute("SELECT part_no FROM part_info WHERE part_no = %s", (part[0],))
        hasPartInPartInfo = DB.cursor.fetchone()
        if not hasPartInPartInfo:
            DB.cursor.execute("DELETE FROM main_inventory WHERE part_no = %s", (part[0],))
    reorganizeDeliveryOrders()
    return process_info
##############################################################################################################
# Function used to get the entries from entry tracker based on partNo, to be used for Function 10.
def get_entry_tracker_list(partNo):
    DB.cursor.execute("SELECT TOP 20 quantity, date_code, remarks, time_created, additional_info, id FROM entry_tracker WHERE part_no = %s ORDER BY time_created DESC", (partNo,))
    entryTrackerInfo = DB.cursor.fetchall()
    if not entryTrackerInfo:
        messagebox.showerror("Error","No entries for this partNo are available!!")
        return None
    else:
        entryTrackerInfo= list(map(list, entryTrackerInfo))
        return entryTrackerInfo
##############################################################################################################
# Function 10: Returns a entry tracker reference list for the end user to see what are the cartons/sealed inventory/allocated cartons which contain
# the same dateCode and remarks and partNo for reference to reject.
def entry_tracker_references(entry_tracker_id):
    quantityInCarton = 0
    DB.cursor.execute("SELECT quantity, date_code, remarks, time_created, additional_info, id, part_no FROM entry_tracker WHERE id = %s;", (entry_tracker_id,))
    selectedEntry = DB.cursor.fetchone()
    partNo = selectedEntry[6]

    quantityToBeSentOut = selectedEntry[0]
    DB.cursor.execute("SELECT stn_qty, stn_carton, uom, cavity from part_info WHERE part_no = %s;", (partNo,))
    stnQtyCtn = DB.cursor.fetchone()
    stnQty = int(stnQtyCtn[0])
    uom = str(stnQtyCtn[2])
    if uom == "PCS":
        cavity = int(stnQtyCtn[3])
        if cavity > 1:
            stnQty *= cavity

    DB.cursor.execute("SELECT id, carton_quantity, date_codes, remarks, loose_quantity, packing_date, delivery_id FROM carton_table WHERE date_codes LIKE '%%%s%%' AND remarks LIKE '%%%s%%' AND part_no = '%s' AND delivery_id > 0" % (selectedEntry[1], selectedEntry[2], partNo))
    cartonDOGet = DB.cursor.fetchall()
    deliveryCartonTable = []
    if cartonDOGet:
        cartonDOGet= list(map(list, cartonDOGet))
        for x in range(len(cartonDOGet)):
            if cartonDOGet[x][3] == None:
                cartonDOGet[x][3] = ""
            if cartonDOGet[x][4] != 0:
                deliveryCartonTable.append([cartonDOGet[x][6],cartonDOGet[x][0],cartonDOGet[x][1],cartonDOGet[x][2],cartonDOGet[x][3], cartonDOGet[x][4], cartonDOGet[x][4] * cartonDOGet[x][1], cartonDOGet[x][5]])
            else:
                deliveryCartonTable.append([cartonDOGet[x][6],cartonDOGet[x][0],cartonDOGet[x][1],cartonDOGet[x][2],cartonDOGet[x][3], stnQty, stnQty * cartonDOGet[x][1], cartonDOGet[x][5]])

    DB.cursor.execute("SELECT id, carton_quantity, date_codes, remarks, loose_quantity, packing_date FROM carton_table WHERE date_codes LIKE '%%%s%%' AND remarks LIKE '%%%s%%' AND part_no = '%s' AND (delivery_id = 0 OR delivery_id IS NULL OR LENGTH(delivery_id & '') = 0)" % (selectedEntry[1], selectedEntry[2], partNo))
    cartonGet = DB.cursor.fetchall()
    selectionCartonTable = []
    if cartonGet:
        cartonGet= list(map(list, cartonGet))
        for x in range(len(cartonGet)):
            if cartonGet[x][3] == None:
                cartonGet[x][3] = ""
            if cartonGet[x][4] != 0:
                selectionCartonTable.append([cartonGet[x][0],cartonGet[x][1],cartonGet[x][2],cartonGet[x][3], cartonGet[x][4], cartonGet[x][4] * cartonGet[x][1], cartonGet[x][5]])
            else:
                selectionCartonTable.append([cartonGet[x][0],cartonGet[x][1],cartonGet[x][2],cartonGet[x][3], stnQty, stnQty * cartonGet[x][1], cartonGet[x][5]])

    DB.cursor.execute("SELECT id, quantity, date_code, remarks FROM sealed_inventory WHERE date_code LIKE '%%%s%%' AND remarks LIKE '%%%s%%' AND part_no = '%s'" % (selectedEntry[1], selectedEntry[2], partNo))
    sealedGet = DB.cursor.fetchall()
    sealedTable = []
    if sealedGet:
        sealedGet= list(map(list, sealedGet))
        for x in range(len(sealedGet)):
            if sealedGet[x][3] == None:
                sealedGet[x][3] = ""
            sealedTable.append([sealedGet[x][0],sealedGet[x][1],sealedGet[x][2],sealedGet[x][3]])
    return deliveryCartonTable, selectionCartonTable, sealedTable
    #print(tabulate(deliveryCartonTable, headers=["DO ID","ID","Quantity of Cartons","DateCode", "Remarks", "Quantity", "Total Quantity", "Packing Date"]))
    #print(tabulate(selectionCartonTable, headers=["ID","Quantity of Cartons","DateCode", "Remarks", "Quantity", "Total Quantity", "Packing Date"]))
    #print(tabulate(sealedTable, headers=["ID","Quantity","DateCode", "Remarks"]))
##############################################################################################################
# Function 11: Deletes entries from entry tracker.
def delete_entry_tracker(entry_tracker_id, reason=""):
    process_info = []
    DB.cursor.execute("SELECT part_no, quantity, date_code, remarks, additional_info FROM entry_tracker WHERE id = %s", (entry_tracker_id,))
    entry_obtain = DB.cursor.fetchone()
    description = "(" + str(entry_obtain[0]) + "," + str(entry_obtain[1]) + "," + str(entry_obtain[2]) + "," \
                  + str(entry_obtain[3]) + "," + str(entry_obtain[4]) + "," +")"
    update_log_table("Entry Tracker Deletion", "N/A", description, reason)
    #DB.cursor.execute("INSERT INTO reverse_entry_tracker (partNo, quantity, dateCode, remarks, additional_info,time) VALUES (%s,%s,%s,%s,%s,%s)", (entry_obtain[0],entry_obtain[1],entry_obtain[2],entry_obtain[3], entry_obtain[4],datetime.now()))
    DB.conn.commit()
    DB.cursor.execute("DELETE FROM entry_tracker WHERE id = %s", (entry_tracker_id,))
    DB.conn.commit()
    process_info.append("\n* Entry deleted, please remember to revert the inputs inputted into carton table and sealed inventory!")
    return process_info
##############################################################################################################
# NEW FUNCTION: Adding a new partNo.
def add_new_part_no (partNo, reason=""):
    process_info = []
    DB.cursor.execute("SELECT part_no FROM part_info WHERE part_no = %s", (partNo,))
    results = DB.cursor.fetchone()
    user_name = LoginSystem.user_name
    if not results:
        DB.cursor.execute("INSERT INTO part_info (part_no, time_created, user_name) VALUES (%s)", (partNo,datetime.now(), user_name))
        description = "(" + str(partNo) + ")"
        update_log_table("New Part No (Name)", "N/A", description, reason)
        #DB.cursor.execute("INSERT INTO part_no_entry_tracker (partNo,quantityChange,description,newPartNo,time) VALUES (%s,%s,%s,%s,%s)", (partNo,0,"New Part No","N/A", datetime.now()))
        DB.conn.commit()
        process_info.append(f"\n* PartNo {partNo} successfully added!")
        return process_info
    else:
        process_info.append(f"\n* ERROR: PartNo {partNo} already existed in the database!")
        return process_info
##############################################################################################################
def add_new_part_no_excel (partNo, customer, cavity, uom, reason=""):
    process_info = []
    DB.cursor.execute("SELECT part_no FROM part_info WHERE part_no = %s", (partNo,))
    results = DB.cursor.fetchone()
    user_name = LoginSystem.user_name
    if not results:
        if cavity != None and uom != None:
            if customer == None:
                customer = ""
            DB.cursor.execute("INSERT INTO part_info (part_no, customer, cavity, uom, time_created, user_name) VALUES (%s,%s,%s,%s,%s,%s)", (partNo,customer,cavity,uom,datetime.now(),user_name))
            description = f"({partNo}, {customer}, {cavity}, {uom})"
            update_log_table("New Part No (Excel)", "N/A", description, reason)
            #DB.cursor.execute("INSERT INTO part_no_entry_tracker (partNo,quantityChange,description,newPartNo,time) VALUES (%s,%s,%s,%s,%s)", (partNo,0,"New Part No","N/A", datetime.now()))
            DB.conn.commit()
            process_info.append(f"\n* PartNo {partNo} successfully added!")
            return process_info
        else:
            process_info.append(f"\n* PartNo {partNo} has missing information regarding cavity and/or uom. Please recheck your Excel sheet and try again!")
            return process_info
    else:
        process_info.append(f"\n* ERROR: PartNo {partNo} already existed in the database!")
        return process_info
##############################################################################################################
def checkSimilarPartNos (part_no):
    part_no_list = []
    part_no_without_spaces = part_no.replace(" ", "")
    part_no_before_bracket = part_no.split("(", 1)[0] if "(" in part_no else None
    part_no_before_space = part_no.split(" ", 1)[0] if " " in part_no else None
    DB.cursor.execute("SELECT part_no FROM part_info")
    part_no_records = DB.cursor.fetchall()
    for part_no_to_iterate in part_no_records:
        part_no_iterate = part_no_to_iterate[0]
        part_no_iterate_without_spaces = part_no_iterate.replace(" ", "")
        if (part_no in part_no_iterate or (part_no_without_spaces is not None and part_no_without_spaces in part_no_iterate) or
                (part_no_before_bracket is not None and part_no_before_bracket in part_no_iterate) or
                (part_no_before_space is not None and part_no_before_space in part_no_iterate) or
                part_no in part_no_iterate_without_spaces or (part_no_without_spaces is not None and part_no_without_spaces in part_no_iterate_without_spaces) or
                (part_no_before_bracket is not None and part_no_before_bracket in part_no_iterate_without_spaces) or
                (part_no_before_space is not None and part_no_before_space in part_no_iterate_without_spaces)):
                part_no_list.append(part_no_iterate)
    return part_no_list
##############################################################################################################
# NEW FUNCTION: Editing partNo name. The old_part_no must exist in part_info!
def edit_part_no (old_part_no, new_part_no):
    process_info = []
    DB.cursor.execute("SELECT total_stock FROM main_inventory WHERE part_no = %s", (old_part_no,))
    totalStock = DB.cursor.fetchone()
    DB.cursor.execute("UPDATE part_info SET part_no = %s WHERE part_no = %s", (new_part_no,old_part_no))
    DB.conn.commit()
    DB.cursor.execute("UPDATE main_inventory SET part_no = %s WHERE part_no = %s", (new_part_no,old_part_no))
    DB.conn.commit()
    DB.cursor.execute("UPDATE carton_table SET part_no = %s WHERE part_no = %s", (new_part_no,old_part_no))
    DB.conn.commit()
    DB.cursor.execute("UPDATE sealed_inventory SET part_no = %s WHERE part_no = %s", (new_part_no,old_part_no))
    description = "(" + str(old_part_no) + "," + str(new_part_no) + ")"
    update_log_table("Edit Part No", str(old_part_no), str(new_part_no), "N/A")
    #DB.cursor.execute("INSERT INTO part_no_entry_tracker (partNo,quantityChange,description,newPartNo,time) VALUES (%s,%s,%s,%s,%s)", (old_part_no,0-int(totalStock[0]),"Edit Part No",new_part_no, datetime.now()))
    #DB.cursor.execute("INSERT INTO part_no_entry_tracker (partNo,quantityChange,description,newPartNo,time) VALUES (%s,%s,%s,%s,%s)", (new_part_no,int(totalStock[0]),"Edit Part No","N/A", datetime.now()))
    DB.conn.commit()
    update_main_inventory(new_part_no)
    process_info.append("\n* PartNo successfully edited!")
    return process_info
##############################################################################################################
# NEW FUNCTION: Deleting partNo name. The partNo itself must have no stock in the inventory before being deleted. The partNo name must exist in part_info:
def delete_part_no (partNo):
    process_info = []
    DB.cursor.execute("SELECT id FROM main_inventory WHERE part_no = %s AND total_stock > 0", (partNo,))
    findPart = DB.cursor.fetchone()
    if findPart:
        process_info.append("\n* ERROR: Please clear the stock from the partNo first!")
        return process_info
    else:
        DB.cursor.execute("DELETE FROM part_info WHERE part_no = %s", (partNo,))
        DB.cursor.execute("DELETE FROM main_inventory WHERE part_no = %s", (partNo,))
        description = "(" + str(partNo) + ")"
        update_log_table("Delete Part No", "N/A", description, "N/A")
        #DB.cursor.execute("INSERT INTO part_no_entry_tracker (partNo,quantityChange,description,newPartNo,time) VALUES (%s,%s,%s,%s,%s)", (partNo,0,"Delete Part No","N/A", datetime.now()))
        DB.conn.commit()
        process_info.append("\n* PartNo successfully deleted!")
        return process_info
##############################################################################################################
# NEW FUNCTION: Transfer stock between partNos. This must require both partNos to have the same part information.
def transfer_stock (old_part_no, new_part_no):
    process_info = []
    DB.cursor.execute("SELECT bundle_qty, stn_carton, stn_qty, uom, cavity, customer FROM part_info WHERE part_no = %s", (old_part_no,))
    old_part_info = DB.cursor.fetchone()
    DB.cursor.execute("SELECT id FROM part_info WHERE part_no = %s AND bundle_qty = %s AND stn_carton = %s AND stn_qty = %s AND uom = %s AND cavity = %s AND customer = %s", (new_part_no, old_part_info[0], old_part_info[1], old_part_info[2], old_part_info[3], old_part_info[4], old_part_info[5]))
    newPartFound = DB.cursor.fetchone()
    if newPartFound:
        DB.cursor.execute("SELECT total_stock FROM main_inventory WHERE part_no = %s", (old_part_no,))
        totalStock = DB.cursor.fetchone()
        DB.cursor.execute("SELECT old_stock FROM main_inventory WHERE part_no = %s", (old_part_no,))
        oldStock = DB.cursor.fetchone()
        DB.cursor.execute("UPDATE carton_table SET part_no = %s WHERE part_no = %s", (new_part_no,old_part_no))
        DB.conn.commit()
        DB.cursor.execute("UPDATE sealed_inventory SET part_no = %s WHERE part_no = %s", (new_part_no,old_part_no))
        DB.conn.commit()
        DB.cursor.execute("UPDATE main_inventory SET old_stock = %s WHERE part_no = %s", (oldStock[0], new_part_no))
        DB.conn.commit()
        DB.cursor.execute("UPDATE main_inventory SET old_stock = %s WHERE part_no = %s", (0, old_part_no))
        DB.conn.commit()
        update_main_inventory(new_part_no)
        update_main_inventory(old_part_no)
        description = "(" + str(old_part_no) + " -> " + str(new_part_no) + "," + str(totalStock[0]) + ")"
        update_log_table("Transfer Stock", "N/A", description, "N/A")
        #DB.cursor.execute("INSERT INTO part_no_entry_tracker (partNo,quantityChange,description,newPartNo,time) VALUES (%s,%s,%s,%s,%s)", (old_part_no,0-int(totalStock[0]),"Transfer Stock","N/A", datetime.now()))
        #DB.cursor.execute("INSERT INTO part_no_entry_tracker (partNo,quantityChange,description,newPartNo,time) VALUES (%s,%s,%s,%s,%s)", (new_part_no,int(totalStock[0]),"Transfer Stock","N/A", datetime.now()))
        DB.conn.commit()
        process_info.append("\n* The partNo stock has been succesfully transferred!")
        return process_info
    else:
        process_info.append("\n* ERROR: Both partNos have different information. Please make sure the information are the same to proceed! (bundleQty, stnCarton, stnQty, uom, cavity, customer)")
        return process_info
##############################################################################################################
def reorganizeDeliveryOrders():
    # This function helps to reorganize the delivery orders, should any delivery order ID already exist in the archived DO list.
    DB.cursor.execute("SELECT id FROM delivery_orders ORDER BY id")
    allIDs = DB.cursor.fetchall()
    allIDs= list(map(list, allIDs))
    for a in range(len(allIDs)):
        DB.cursor.execute("SELECT id FROM archived_delivery_orders WHERE id = %s", (allIDs[a][0],))
        foundID = DB.cursor.fetchone()
        if foundID:
            #print("ID existed in archived DO! ID: " + str(foundID[0]))
            DB.cursor.execute("SELECT customer, part_no, quantity, uom, delivery_order, delivery_date, fulfilled_quantity, weight_limit, cartons_id, time_created, log_id, user_name FROM delivery_orders WHERE id = %s", (allIDs[a][0],))
            DOInfo = DB.cursor.fetchone()
            user_name = LoginSystem.user_name
            existID = True
            while existID:
                DB.cursor.execute("INSERT INTO delivery_orders (customer, part_no, quantity, uom, delivery_order, delivery_date, fulfilled_quantity, weight_limit, cartons_id, time_created, log_id, user_name) "
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
                DB.cursor.execute("UPDATE carton_table SET delivery_id = %s WHERE delivery_id = %s", (insertedId, allIDs[a][0]))
                DB.conn.commit()
            DB.cursor.execute("DELETE FROM delivery_orders WHERE id = %s", (allIDs[a][0],))
            DB.conn.commit()
##############################################################################################################
# The following backend functions are for DataViewer for archiving delivery orders!
##############################################################################################################
def archiveDeliveryOrder(id):
    user_name = LoginSystem.user_name
    DB.cursor.execute("SELECT id, customer ,part_no, quantity, uom ,delivery_order ,delivery_date ,fulfilled_quantity ,weight_limit , cartons_id, time_created, user_name FROM delivery_orders WHERE id = %s", (id,))
    deliveryOrderInfo = DB.cursor.fetchone()
    DB.cursor.execute("INSERT INTO archived_delivery_orders (id, customer ,part_no, quantity, uom ,delivery_order ,delivery_date ,fulfilled_quantity ,weight_limit,cartons_id , time_created, time_archived, user_name, user_name_archived) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);" ,
                   (deliveryOrderInfo[0],deliveryOrderInfo[1],deliveryOrderInfo[2],deliveryOrderInfo[3],deliveryOrderInfo[4],deliveryOrderInfo[5],deliveryOrderInfo[6],deliveryOrderInfo[7],deliveryOrderInfo[8],deliveryOrderInfo[9],deliveryOrderInfo[10],datetime.now(), deliveryOrderInfo[11], user_name))
    description = "(" + str(deliveryOrderInfo[1]) + "," + str(deliveryOrderInfo[2]) + "," + str(deliveryOrderInfo[3]) + "," + str(deliveryOrderInfo[7]) \
                  + "," + str(deliveryOrderInfo[4]) + "," + str(deliveryOrderInfo[5]) + "," + str(deliveryOrderInfo[6]) + ")"
    update_log_table("DO Archived", "N/A", description, "N/A")
    #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
    #               (id,deliveryOrderInfo[2], 0, "DO Archived", datetime.now()))
    DB.conn.commit()
    DB.cursor.execute("SELECT id, part_no, carton_quantity,carton_no, date_codes, earliest_date_code, remarks , loose_quantity , delivery_id, time_created, user_name FROM carton_table WHERE delivery_id = %s;" ,(id,))
    carton_records = DB.cursor.fetchall()
    carton_records= list(map(list, carton_records))
    for carton in carton_records:
        DB.cursor.execute("INSERT INTO archived_carton_table (id,part_no, carton_quantity,carton_no, date_codes, earliest_date_code, remarks , loose_quantity , delivery_id , time_archived, time_created, user_name, user_name_archived) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                       (carton[0],carton[1],carton[2],carton[3],carton[4],carton[5],carton[6],carton[7],carton[8] ,datetime.now(), carton[9], carton[10], user_name)  )
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
    idAllocation= list(map(list, idAllocation))
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
    idAllocation= list(map(list, idAllocation))
    for a in range(len(idAllocation)):
        archiveDeliveryOrder(idAllocation[a])
        process_info.append("\n* Delivery Order ID " + str(idAllocation[a]) + " archival is successful!")
    process_info.append("\n* Delivery Order Date " + str(deliveryDate) + " archival is successful!")
    return process_info
##############################################################################################################
# NEW function for Data Viewer: Unarchiving Delivery Order.
def unarchive_delivery_order (id):
    DB.cursor.execute("SELECT customer ,part_no, quantity, uom ,delivery_order ,delivery_date ,fulfilled_quantity ,weight_limit , cartons_id, time_created, user_name FROM archived_delivery_orders WHERE id = %s", (id,))
    archivedDeliveryOrderInfo = DB.cursor.fetchone()
    DB.cursor.execute("INSERT INTO delivery_orders (customer ,part_no, quantity, uom ,delivery_order ,delivery_date ,fulfilled_quantity ,weight_limit,cartons_id , time_created,user_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);" ,
                   (archivedDeliveryOrderInfo[0],archivedDeliveryOrderInfo[1],archivedDeliveryOrderInfo[2],archivedDeliveryOrderInfo[3],archivedDeliveryOrderInfo[4],archivedDeliveryOrderInfo[5],archivedDeliveryOrderInfo[6],archivedDeliveryOrderInfo[7],archivedDeliveryOrderInfo[8],archivedDeliveryOrderInfo[9],archivedDeliveryOrderInfo[10]))
    DB.conn.commit()
    DB.cursor.execute("SELECT id FROM delivery_orders ORDER BY id DESC")
    insertedId = DB.cursor.fetchone()
    insertedId = int(insertedId[0])
    DB.cursor.execute("SELECT part_no, carton_quantity,carton_no, date_codes, earliest_date_code, remarks , loose_quantity, time_created, user_name FROM archived_carton_table WHERE delivery_id = %s;" ,(id,))
    archived_carton_records = DB.cursor.fetchall()
    archived_carton_records= list(map(list, archived_carton_records))
    for carton in archived_carton_records:
        DB.cursor.execute("INSERT INTO carton_table (part_no, carton_quantity,carton_no, date_codes, earliest_date_code, remarks , loose_quantity , delivery_id, time_created, user_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                       (carton[0],carton[1],carton[2],carton[3],carton[4],carton[5],carton[6],insertedId, carton[7], carton[8]))
    description = "(" + str(archivedDeliveryOrderInfo[0]) + "," + str(archivedDeliveryOrderInfo[1]) + "," + str(archivedDeliveryOrderInfo[2]) + "," + str(archivedDeliveryOrderInfo[6]) \
                  + "," + str(archivedDeliveryOrderInfo[3]) + "," + str(archivedDeliveryOrderInfo[4]) + "," + str(archivedDeliveryOrderInfo[5]) + ")"
    update_log_table("DO Unarchived", "N/A", description, "N/A")
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