from config import *
from ..Logics import DB , update_main_inventory , update_log_table
from ..LoginSystem import LoginSystem

def excel_sheet_to_delivery_order(file_path):
    # 1. First function: Converting a delivery order Excel sheet to delivery order list.

    # This function returns three variables, first being a Boolean to check if it's processed or not (True and False), a process_list, and a list of delivery orders.
    process_info = []
    file_name = os.path.basename(file_path)
    if not file_name.endswith('.xls'):
        messagebox.showerror("Error","File name does not end with .XLS format!")
        logger.info("ERROR: File name does not end with .XLS format!")
        return False,process_info, None
    df = pd.read_excel(file_path, engine='xlrd')
    noRow = len(df)
    noColumns = len(df.columns)
    # Initiate customer , and customer:
    hasCustomer = False
    customer = ""
    DO_list = []
    # Iterate through df:
    for x in range(noRow):
        if pd.notna(df.iloc[x, 2]) and not hasCustomer and pd.isnull(df.iloc[x,10]) and pd.isnull(df.iloc[x,11]) and pd.isnull(df.iloc[x,6]) and pd.isnull(df.iloc[x,7]):
            customer = df.iloc[x, 2]
            if "CUSTOMER NAME" not in customer:
                hasCustomer = True
            else:
                customer = ""
        elif isinstance(df.iloc[x, 0], date):
            customer = ""
            hasCustomer = False
        elif pd.notna(df.iloc[x, 2]) and hasCustomer and pd.isnull(df.iloc[x,10]) and pd.isnull(df.iloc[x,11]) and pd.isnull(df.iloc[x,6]) and pd.isnull(df.iloc[x,7]):
            customer = df.iloc[x, 2]
            hasCustomer = True
        elif pd.notna(df.iloc[x, 2]) and hasCustomer:
            if pd.isnull(df.iloc[x,10]) or pd.isnull(df.iloc[x,11]) or pd.isnull(df.iloc[x,6]) or pd.isnull(df.iloc[x,7]):
                process_info.append("\n* ERROR: This delivery order has missing information and program will return to the main menu. Please refill the details below and try again.")
                process_info.append("\n** Part No: " + df.iloc[x,2])
                process_info.append("\n** Delivery Order: " + df.iloc[x,6])
                process_info.append("\n** Delivery Date: " + str(df.iloc[x,7]))
                process_info.append("\n** Quantity: " + str(df.iloc[x,10]))
                process_info.append("\n** UOM: " + df.iloc[x,11])
                logger.info("ERROR: This delivery order has missing information and program will return to the main menu. Please refill the details and try again.")
                logger.info("* Part No: " + df.iloc[x,2])
                logger.info("* Delivery Order: " + df.iloc[x,6])
                logger.info("* Delivery Date: " + str(df.iloc[x,7]))
                logger.info("* Quantity: " + str(df.iloc[x,10]))
                logger.info("* UOM: " + df.iloc[x,11])
                return False, process_info, None

            partNo = df.iloc[x, 2]
            quantity = df.iloc[x, 10]
            uom = df.iloc[x, 11]

            DB.cursor.execute("UPDATE part_info SET uom = %s WHERE part_no = %s", (uom, partNo))
            DB.conn.commit()

            deliveryOrder = df.iloc[x, 6]
            deliveryDate = df.iloc[x, 7]
            # Tell those to include weightLimit under remarks! Also must be in grams!
            # weightLimit = 100000
            if noColumns < 13:
                weightLimit = 0
            else:
                weightLimit = df.iloc[x, 13]
                if math.isnan(weightLimit):
                    weightLimit = 0

            DB.cursor.execute("SELECT COUNT(*) FROM delivery_orders WHERE delivery_order = '" + str(deliveryOrder) + "'")
            noRepeatList = DB.cursor.fetchall()
            noRepeatList= list(map(list, noRepeatList))
            noInstances = noRepeatList[0][0]
            DB.cursor.execute("SELECT COUNT(*) FROM archived_delivery_orders WHERE delivery_order = '" + str(deliveryOrder) + "'")
            noARepeatList = DB.cursor.fetchall()
            noARepeatList= list(map(list, noARepeatList))
            noAInstances = noARepeatList[0][0]
            temp_process_info = []
            temp_process_info.append(customer)
            temp_process_info.append(partNo)
            temp_process_info.append(quantity)
            temp_process_info.append(uom)
            temp_process_info.append(deliveryOrder)
            temp_process_info.append(deliveryDate)
            temp_process_info.append(weightLimit)
            if noInstances == 0 and noAInstances == 0:
                temp_process_info.append(False)
            else:
                temp_process_info.append(True)
            DO_list.append(temp_process_info)

    return True, process_info, DO_list
##############################################################################################################
def import_order_to_database(file_path):
    # 3. This third function aims to import the delivery order and processes them to add to the database, as well as fulfilling delivery orders.

    # This function returns two variables, first being a Boolean to check if it's processed or not (True and False), and a process_list.
    reorganizeDeliveryOrders()
    process_info = []
    delivery_order_data_frame = pd.DataFrame(
        columns=['customer', 'partNo', 'quantity', 'uom', 'deliveryOrder', 'deliveryDate','weightLimit'])
    file_name = os.path.basename(file_path)
    if not file_name.endswith('.xls'):
        process_info.append("\n* ERROR: File name does not end with .XLS format!")
        logger.info("ERROR: File name does not end with .XLS format!")
        return False,process_info
    df = pd.read_excel(file_path, engine='xlrd')
    noRow = len(df)
    noColumns = len(df.columns)
    # Initiate customer , and customer:
    hasCustomer = False
    customer = ""
    # Iterate through df:
    for x in range(noRow):
        if pd.notna(df.iloc[x, 2]) and not hasCustomer and pd.isnull(df.iloc[x,10]) and pd.isnull(df.iloc[x,11]) and pd.isnull(df.iloc[x,6]) and pd.isnull(df.iloc[x,7]):
            customer = df.iloc[x, 2]
            if "CUSTOMER NAME" not in customer:
                hasCustomer = True
            else:
                customer = ""
        elif isinstance(df.iloc[x, 0], date):
            customer = ""
            hasCustomer = False
        elif pd.notna(df.iloc[x, 2]) and hasCustomer and pd.isnull(df.iloc[x,10]) and pd.isnull(df.iloc[x,11]) and pd.isnull(df.iloc[x,6]) and pd.isnull(df.iloc[x,7]):
            customer = df.iloc[x, 2]
            hasCustomer = True
        elif pd.notna(df.iloc[x, 2]) and hasCustomer:
            if pd.isnull(df.iloc[x,10]) or pd.isnull(df.iloc[x,11]) or pd.isnull(df.iloc[x,6]) or pd.isnull(df.iloc[x,7]):
                process_info.append("\n* ERROR: This delivery order has missing information and program will return to the main menu. Please refill the details below and try again.")
                process_info.append("\n** Part No: " + df.iloc[x,2])
                process_info.append("\n** Delivery Order: " + df.iloc[x,6])
                process_info.append("\n** Delivery Date: " + str(df.iloc[x,7]))
                process_info.append("\n** Quantity: " + str(df.iloc[x,10]))
                process_info.append("\n** UOM: " + df.iloc[x,11])
                logger.info("ERROR: This delivery order has missing information and program will return to the main menu. Please refill the details and try again.")
                logger.info("* Part No: " + df.iloc[x,2])
                logger.info("* Delivery Order: " + df.iloc[x,6])
                logger.info("* Delivery Date: " + str(df.iloc[x,7]))
                logger.info("* Quantity: " + str(df.iloc[x,10]))
                logger.info("* UOM: " + df.iloc[x,11])
                return False, process_info

            partNo = df.iloc[x, 2]
            quantity = df.iloc[x, 10]
            uom = df.iloc[x, 11]

            DB.cursor.execute("SELECT part_no FROM part_info WHERE part_no = %s", (str(partNo),))
            valid_part_no = DB.cursor.fetchone()

            if valid_part_no:
                DB.cursor.execute("UPDATE part_info SET uom = %s WHERE part_no = %s", (uom, partNo))
                DB.conn.commit()

                deliveryOrder = df.iloc[x, 6]
                deliveryDate = df.iloc[x, 7]
                # Tell those to include weightLimit under remarks! Also must be in grams!
                # weightLimit = 100000
                if noColumns < 13:
                    weightLimit = 0
                else:
                    weightLimit = df.iloc[x, 13]
                    if math.isnan(weightLimit):
                        weightLimit = 0

                DB.cursor.execute("SELECT COUNT(*) FROM delivery_orders WHERE delivery_order = '" + str(deliveryOrder) + "'")
                noRepeatList = DB.cursor.fetchall()
                noRepeatList= list(map(list, noRepeatList))
                noInstances = noRepeatList[0][0]
                DB.cursor.execute("SELECT COUNT(*) FROM archived_delivery_orders WHERE delivery_order = '" + str(deliveryOrder) + "'")
                noARepeatList = DB.cursor.fetchall()
                noARepeatList= list(map(list, noARepeatList))
                noAInstances = noARepeatList[0][0]
                if noInstances == 0 and noAInstances == 0:
                    tempdf = {'customer': customer, 'partNo': partNo, 'quantity': quantity, 'uom': uom, 'deliveryOrder': deliveryOrder,
                              'deliveryDate': deliveryDate, 'weightLimit': weightLimit}
                    delivery_order_data_frame = delivery_order_data_frame.append(tempdf, ignore_index=True)
                else:
                    process_info.append("\n* ERROR: Delivery Order " + deliveryOrder + " already exists in the database!")
                    logger.info("ERROR: Delivery Order " + deliveryOrder + " already exists in the database!")
            else:
                process_info.append("\n* ERROR: Part No " + partNo + " does not exist in the database!")
                logger.info("ERROR: Part No " + partNo + " does not exist in the database!")
    delivery_order_data_frame = delivery_order_data_frame.sort_values(by=['deliveryDate', 'customer', 'partNo', 'deliveryOrder'])
    process_info_2, idList, processed_do_dataframe = process_order(delivery_order_data_frame)
    if process_info_2 is not None:
        process_info.extend(process_info_2)
    process_info_3 = fulfill_order(True, idList, processed_do_dataframe)
    if process_info_3 is not None:
        process_info.extend(process_info_3)
    return True, process_info
##############################################################################################################
def process_order(delivery_order_data_frame):
    process_info = []
    temp3df = {}
    orderNo = 0
    idList = []
    processed_do_dataframe = pd.DataFrame(
        columns=['customer', 'partNo', 'quantity', 'uom', 'deliveryOrder', 'deliveryDate','weightLimit'])
    # Some customers cannot be combined and should be hardcoded here.
    print("Combining the delivery orders......")
    for i2 in range(len(delivery_order_data_frame)):
        if i2 == 0:
            temp3df = {'customer': delivery_order_data_frame.iloc[[i2]].customer.to_string(index=False),
                       'partNo': delivery_order_data_frame.iloc[[i2]].partNo.to_string(index=False),
                       'quantity': delivery_order_data_frame.iloc[[i2]].quantity.to_string(index=False),
                       'uom': delivery_order_data_frame.iloc[[i2]].uom.to_string(index=False),
                       'deliveryOrder': delivery_order_data_frame.iloc[[i2]].deliveryOrder.to_string(index=False),
                       'deliveryDate': delivery_order_data_frame.iloc[[i2]].deliveryDate.to_string(index=False),
                       'weightLimit': delivery_order_data_frame.iloc[[i2]].weightLimit.to_string(index=False)}
        #elif orderNo == 0:
        else:
            if delivery_order_data_frame.iloc[[i2]].customer.to_string(index=False) == temp3df['customer'] and delivery_order_data_frame.iloc[
                [i2]].partNo.to_string(index=False) == temp3df['partNo'] \
                    and delivery_order_data_frame.iloc[[i2]].deliveryOrder.to_string(index=False) == temp3df['deliveryOrder'] and \
                    delivery_order_data_frame.iloc[[i2]].deliveryDate.to_string(index=False) == temp3df['deliveryDate'] and not \
                    ("MITSUBISHI" in temp3df['customer'] or ("PANASONIC SYSTEM NETWORK" in temp3df['customer'] and "VIETNAM" in temp3df['customer']) or \
                     ("PANASONIC PROCUREMENT MALAYSIA" in temp3df['customer'] and "(KL)" in temp3df['customer']) or \
                     ("PANASONIC PROCUREMENT MALAYSIA" in temp3df['customer'] and "(JB)" in temp3df['customer']) or \
                     ("PANASONIC PROCUREMENT MALAYSIA" in temp3df['customer'] and "ASIA PACIFIC" in temp3df['customer']) or \
                     ("SONY" in temp3df['customer'] and "SUPPLY CHAIN" in temp3df['customer'])):
                temp3df['quantity'] = (int(temp3df['quantity']) + delivery_order_data_frame.iloc[[i2]].quantity).to_string(index=False)
            else:
                orderNo += 1
                processed_do_dataframe = processed_do_dataframe.append(temp3df, ignore_index=True)
                temp3df = {'customer': delivery_order_data_frame.iloc[[i2]].customer.to_string(index=False),
                           'partNo': delivery_order_data_frame.iloc[[i2]].partNo.to_string(index=False),
                           'quantity': delivery_order_data_frame.iloc[[i2]].quantity.to_string(index=False),
                           'uom': delivery_order_data_frame.iloc[[i2]].uom.to_string(index=False),
                           'deliveryOrder': delivery_order_data_frame.iloc[[i2]].deliveryOrder.to_string(index=False),
                           'deliveryDate': delivery_order_data_frame.iloc[[i2]].deliveryDate.to_string(index=False),
                           'weightLimit': delivery_order_data_frame.iloc[[i2]].weightLimit.to_string(index=False)}

        if i2 == len(delivery_order_data_frame) - 1:
            processed_do_dataframe = processed_do_dataframe.append(temp3df, ignore_index=True)

    print("Adding the delivery orders to the database......")
    for index, row in processed_do_dataframe.iterrows():
        DB.cursor.execute("INSERT INTO delivery_orders (customer, part_no, quantity, uom, delivery_order, delivery_date, fulfilled_quantity, weight_limit, time_created, user_name) "
                       "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                       (row['customer'], row['partNo'], row['quantity'], row['uom'], row['deliveryOrder'], row['deliveryDate'], 0, row['weightLimit'], datetime.now(), LoginSystem.user_name))
        DB.conn.commit()
        DB.cursor.execute("SELECT id FROM delivery_orders ORDER BY id DESC")
        insertedId = DB.cursor.fetchone()
        insertedId = int(insertedId[0])
        idList += [insertedId]
        description = "(" + str(row['customer']) + "," + str(row['partNo']) + "," + str(row['quantity']) \
                      + "," + str(row['uom']) + "," + str(row['deliveryOrder']) + "," + str(row['deliveryDate']) + ")"
        update_log_table("New DO", "", description)
        #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
        #               (insertedId, row['partNo'], 0, "New DO", datetime.now()))
        DB.cursor.execute("SELECT id FROM logger ORDER BY id DESC")
        loggerId = DB.cursor.fetchone()
        loggerId = int(loggerId[0])
        DB.cursor.execute("UPDATE delivery_orders SET log_id = %s WHERE id = %s", (loggerId, insertedId))
        DB.conn.commit()
        logger.info("Delivery Order of: (" + str(row['customer']) + "," + str(row['partNo']) + "," + str(row['quantity'])
                    + "," + str(row['uom']) + "," + str(row['deliveryOrder']) + "," + str(row['deliveryDate']) + ") added as Delivery Order ID " + str(insertedId) + ".")
    if processed_do_dataframe.shape[0] > 0:
        process_info.append("\n* Success. " + str(processed_do_dataframe.shape[0]) + " orders are added to the database.")
        logger.info("Success. " + str(processed_do_dataframe.shape[0]) + " orders are added to the database.")

    return process_info, idList, processed_do_dataframe
##############################################################################################################
def fulfill_order(continueFlag, idList, processed_do_dataframe):
    part_list = []
    process_info = []
    complete_part_list = []
    for i in range(len(processed_do_dataframe)):
        conditionPass = True
        partNo = processed_do_dataframe.iloc[[i]].partNo.to_string(index=False)
        update_main_inventory(partNo)
        quantity = int(processed_do_dataframe.iloc[[i]].quantity.to_string(index=False))
        isEarliest = True
        if partNo not in complete_part_list:
            complete_part_list += [partNo]

        DB.cursor.execute("SELECT delivery_date FROM delivery_orders WHERE part_no = %s AND quantity > fulfilled_quantity ORDER BY delivery_date", (partNo,))
        earliestdd = DB.cursor.fetchone()
        DB.cursor.execute("SELECT delivery_date FROM delivery_orders WHERE id = %s", (idList[i],))
        currentdd = DB.cursor.fetchone()

        if earliestdd != currentdd:
            process_info.append("\n* The Part No " + partNo + " has other earlier delivery orders!")
            logger.info("The Part No " + partNo + " has other earlier delivery orders!")
            if partNo not in part_list:
                part_list += [partNo]
            isEarliest = False

        if isEarliest:
            DB.cursor.execute("SELECT old_stock FROM main_inventory WHERE part_no = %s AND total_stock > 0", (partNo,))
            old_stock = DB.cursor.fetchone()
            if not old_stock:
                process_info.append("\n* ERROR: Part No " + partNo + " not found in the inventory!")
                logger.info("ERROR: Part No " + partNo + " not found in the inventory!")
                if partNo not in part_list:
                    part_list += [partNo]
            else:
                old_stock = int(old_stock[0])
                # Checking the old stock first.
                if old_stock > 0 and quantity > 0:
                    DB.cursor.execute("SELECT fulfilled_quantity FROM delivery_orders WHERE id = %s", (idList[i],))
                    memory = DB.cursor.fetchone()
                    memoryFulfilled = int(memory[0])
                    DB.cursor.execute("SELECT quantity FROM delivery_orders WHERE id = %s", (idList[i],))
                    memoryT = DB.cursor.fetchone()
                    memoryTotal = int(memoryT[0])
                    if old_stock >= quantity:
                        process_info.append("\n* NOTE: Tell the packing department that " + str(quantity) + " of the old stock for part " + partNo + " needed to be packed!")
                        logger.info(str(quantity) + " of the old stock for part " + partNo + " is allocated to the delivery order ID " + str(idList[i]) + ".")
                        if memoryFulfilled == 0:
                            DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity + %s, cartons_id = %s WHERE id = %s",
                                           (quantity, "old_stock (" + str(quantity) + ")", idList[i]))
                        else:
                            DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity + %s, cartons_id = CONCAT(COALESCE(cartons_id,''), %s) WHERE id = %s",
                                           (quantity, " | old_stock (" + str(quantity) + ")", idList[i]))
                        description = "(" + str(idList[i]) + "," + str(partNo) + "," + str(quantity) + "/" + str(memoryTotal) + ")"
                        update_log_table("Fulfill Quantity", "", description)
                        #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
                        #               (idList[i],partNo, quantity, "Fulfill Quantity", datetime.now()))
                        DB.cursor.execute("UPDATE main_inventory SET old_stock = old_stock - %s WHERE part_no = %s", (quantity, partNo))
                        DB.conn.commit()
                        old_stock -= quantity
                        quantity -= quantity
                    else:
                        process_info.append("\n* NOTE: Tell the packing department that " + str(old_stock) + " of the old stock for part " + partNo + " needed to be packed!")
                        logger.info(str(old_stock) + " of the old stock for part " + partNo + " is allocated to the delivery order ID " + str(idList[i]) + ".")
                        if memoryFulfilled == 0:
                            DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity + %s, cartons_id = %s WHERE id = %s",
                                           (old_stock, "old_stock (" + str(old_stock) + ")", idList[i]))
                        else:
                            DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity + %s, cartons_id = CONCAT(COALESCE(cartons_id,''), %s) WHERE id = %s",
                                           (old_stock, " | old_stock (" + str(old_stock) + ")", idList[i]))
                        description = "(" + str(idList[i]) + "," + str(partNo) + "," + str(old_stock) + "/" + str(memoryTotal) + ")"
                        update_log_table("Fulfill Quantity", "", description)
                        #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
                        #               (idList[i],partNo, old_stock, "Fulfill Quantity", datetime.now()))
                        DB.cursor.execute("UPDATE main_inventory SET old_stock = 0 WHERE part_no = %s", (partNo,))
                        DB.conn.commit()
                        quantity -= old_stock
                        old_stock = 0
                    update_main_inventory(partNo)

            if partNo not in part_list and quantity > 0:
                DB.cursor.execute("SELECT bundle_qty, stn_qty, uom, cavity, stn_carton FROM part_info WHERE part_no = %s", (partNo,))
                partInfoResults = DB.cursor.fetchone()

                if not partInfoResults:
                    process_info.append("\n* ERROR: Part No " + partNo + " not found in the database! Please fill in the values for that part no.")
                    logger.info("ERROR: Part No " + partNo + " not found in the database! Please fill in the values for that part no.")
                    if partNo not in part_list:
                        part_list += [partNo]
                    conditionPass = False
                else:
                    if int(partInfoResults[0]) == 0 or int(partInfoResults[1]) == 0 or partInfoResults[2] == None or partInfoResults[2] == "" or \
                            (partInfoResults[2] == "PANEL" and partInfoResults[3] == 0) or (partInfoResults[2] == "PNL" and partInfoResults[3] == 0):
                        process_info.append("\n* ERROR: Part No " + partNo + " has missing information for bundleQty/stnQty/uom/cavity! Please fill in the values for that part no.")
                        logger.info("ERROR: Part No " + partNo + " has missing information for bundleQty/stnQty/uom/cavity! Please fill in the values for that part no.")
                        if partNo not in part_list:
                            part_list += [partNo]
                        conditionPass = False

                DB.cursor.execute("SELECT part_no, carton_quantity, sealed_quantity FROM main_inventory WHERE part_no = %s AND total_stock > 0", (partNo,))
                packedResults = DB.cursor.fetchone()

                if not packedResults:
                    process_info.append("\n* ERROR: Part No " + partNo + " not found in the inventory!")
                    logger.info("ERROR: Part No " + partNo + " not found in the inventory!")
                    if partNo not in part_list:
                        part_list += [partNo]
                    conditionPass = False

                if conditionPass:
                    tempdf = {'customer': processed_do_dataframe.iloc[[i]].customer.to_string(index=False),
                              'partNo': partNo,
                              'quantity': quantity,
                              'uom': processed_do_dataframe.iloc[[i]].uom.to_string(index=False),
                              'deliveryOrder': processed_do_dataframe.iloc[[i]].deliveryOrder.to_string(index=False),
                              'deliveryDate': processed_do_dataframe.iloc[[i]].deliveryDate.to_string(index=False),
                              'weightLimit': processed_do_dataframe.iloc[[i]].weightLimit.to_string(index=False)}

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
                                DB.cursor.execute("SELECT id, date_code, remarks, quantity, log_id FROM sealed_inventory WHERE part_no = %s AND quantity > 0 ORDER BY Right(date_code,2), Left(date_code,2), quantity DESC, ID", (partNo,))
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

                            DB.cursor.execute(
                                "INSERT INTO carton_table (part_no, carton_quantity, date_codes, earliest_date_code, remarks, loose_quantity, carton_no, delivery_id, packing_date, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                (partNo, 1, sealedDateCodes, sealed_info[0][1], sealedRemarks, 0 ,partInfoResults[4], 0, date.today().isoformat(), log_id,datetime.now() ,LoginSystem.user_name))
                            DB.conn.commit()
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
                        if partNo not in part_list:
                            part_list += [partNo]
                    else:
                        weightLimit = tempdf['weightLimit']
                        passWeightLimit = True

                        if int(weightLimit) > 0:
                            DB.cursor.execute("SELECT weight FROM part_info WHERE part_no = %s", (partNo,))
                            weight = DB.cursor.fetchone()
                            weight = int(weight[0])
                            if weight == 0:
                                process_info.append("\n* The Part No " + partNo + " has a weight of zero, unable to fulfill cartons with weight limit, please fill in and try again!")
                                logger.info("The Part No " + partNo + " has a weight of zero, unable to fulfill cartons with weight limit, please fill in and try again!")
                            else:
                                if weight * stnQty * 1.01 > int(weightLimit):
                                    process_info.append("\n* This delivery order has a weight limit in which it is lower than the weight of a standard carton, and will be skipped.")
                                    logger.info("This delivery order has a weight limit in which it is lower than the weight of a standard carton, and will be skipped.")
                                    passWeightLimit = False
                        if passWeightLimit:
                            DB.cursor.execute("SELECT fulfilled_quantity, quantity FROM delivery_orders WHERE id = %s", (idList[i],))
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
                                    if int(carton_info[x][3]) > remainingCartonForOrder:
                                        noDecrement = remainingCartonForOrder
                                    else:
                                        noDecrement = int(carton_info[x][3])
                                    if carton_info[x][2] == None:
                                        carton_info[x][2] = ""
                                    noOfCartons += noDecrement
                                    DB.cursor.execute(
                                        "INSERT INTO carton_table (part_no, carton_quantity, date_codes, earliest_date_code, remarks, carton_no, delivery_id, packing_date, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                        (partNo, noDecrement, carton_info[x][1], carton_info[x][5], carton_info[x][2], carton_info[0][4], str(idList[i]), carton_info[x][6], carton_info[x][7, datetime.now() ,LoginSystem.user_name]))
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
                                    process_info.append("\n* " + str(noOfCartons) + " cartons have been allocated for " + partNo + " for the delivery order ID of " + str(idList[i]))
                                    logger.info(str(noOfCartons) + " cartons have been allocated for " + partNo + " for the delivery order ID of " + str(idList[i]))
                                cartonBreak = False
                                if remainingCartonForOrder == 0 and totalLooseQty > 0 and loosePartsAvailable < totalLooseQty and remainingCartonInInventory > 0:
                                    process_info.append("\n* One carton will be broken for part " + partNo + ", with dateCodes of '" + str(carton_info[x][1]) + "', and remarks of '" + str(carton_info[x][2]) +"'.")
                                    logger.info("One carton will be broken for part " + partNo + ", with dateCodes of '" + str(carton_info[x][1]) + "', and remarks of '" + str(carton_info[x][2]) +"'.")
                                    cartonBreak = True
                                    carton_info[x][3] -= 1
                                    loosePartsAvailable += stnQty
                                    if "=" not in carton_info[x][1]:
                                        getDateCode = carton_info[x][1]
                                        getRemark = carton_info[x][2]
                                        DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, getDateCode, getRemark))
                                        sealedResult = DB.cursor.fetchone()
                                        if not sealedResult:
                                            DB.cursor.execute(
                                                "INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                                (partNo, stnQty, getDateCode, getRemark, carton_info[x][7], datetime.now() ,LoginSystem.user_name))
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
                                            DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, getDateCode, getRemark))
                                            sealedResult = DB.cursor.fetchone()
                                            DB.conn.commit()
                                            if not sealedResult:
                                                DB.cursor.execute(
                                                    "INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks,log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                                    (partNo, getQuantity, getDateCode, getRemark, carton_info[x][7], datetime.now() ,LoginSystem.user_name))
                                            else:
                                                DB.cursor.execute(
                                                    "UPDATE sealed_inventory SET quantity = quantity + %s WHERE part_no = %s AND date_code = %s AND remarks = %s AND id = %s",
                                                    (getQuantity, partNo, getDateCode, getRemark, sealedResult[0]))
                                    DB.cursor.execute("UPDATE main_inventory SET carton_quantity = carton_quantity - 1, sealed_quantity = sealed_quantity + stn_qty WHERE part_no = %s", (partNo,))
                                    DB.conn.commit()
                                log_id = 0
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
                                                sealedRemarks += "("
                                                sealedRemarks += sealed_info[y][2]
                                                sealedRemarks += ")="
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
                                            sealedRemarks += "("
                                            sealedRemarks += sealed_info[y][2]
                                            sealedRemarks += ")="
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
                                    DB.cursor.execute(
                                        "INSERT INTO carton_table (part_no, carton_quantity, date_codes, earliest_date_code, remarks, loose_quantity, carton_no, delivery_id, packing_date, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                        (partNo, 1, sealedDateCodes, sealed_info[0][1], sealedRemarks, totalLooseQty ,"L", str(idList[i]), date.today().isoformat(), log_id, datetime.now() ,LoginSystem.user_name))
                                    dateCodeRemarksLoose = str(sealedDateCodes)
                                    if sealedRemarks == "":
                                        dateCodeRemarksLoose += ", N/A"
                                    else:
                                        dateCodeRemarksLoose += ", " + sealedRemarks
                                    DB.conn.commit()
                                    DB.cursor.execute("SELECT id FROM carton_table ORDER BY id DESC")
                                    insertedId = DB.cursor.fetchone()
                                    insertedId = int(insertedId[0])
                                    carton_id += str(insertedId)
                                    for b in range(y):
                                        DB.cursor.execute("UPDATE sealed_inventory SET quantity = %s WHERE id = %s",(sealed_info[b][3],sealed_info[b][0]))
                                        DB.conn.commit()
                                    noLooseCarton += 1
                                if carton_info:
                                    for a in range(len(carton_info)):
                                        DB.cursor.execute("UPDATE carton_table SET carton_quantity = %s WHERE id = %s",(carton_info[a][3],carton_info[a][0]))
                                        DB.conn.commit()
                                DB.cursor.execute("SELECT fulfilled_quantity FROM delivery_orders WHERE id = %s", (idList[i],))
                                memoryAgain = DB.cursor.fetchone()
                                memoryFulfilledAgain = int(memoryAgain[0])
                                DB.cursor.execute("SELECT quantity FROM delivery_orders WHERE id = %s", (idList[i],))
                                memoryT = DB.cursor.fetchone()
                                memoryTotal = int(memoryT[0])
                                if noOfCartons > 0 or loosePartsAvailable >= totalLooseQty:
                                    if remainingCartonForOrder == 0 and totalLooseQty > 0 and loosePartsAvailable >= totalLooseQty:
                                        if memoryFulfilledAgain == 0:
                                            DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = quantity, cartons_id = CONCAT(COALESCE(cartons_id,''), %s) WHERE id = %s",
                                                           (carton_id, idList[i]))
                                        else:
                                            DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = quantity, cartons_id = CONCAT(COALESCE(cartons_id,''), %s) WHERE id = %s",
                                                           (" | " + carton_id, idList[i]))
                                        description = "(" + str(idList[i]) + "," + str(partNo) + "," + str(stnQty * noOfCartons + totalLooseQty) + "/" + str(memoryTotal) + ")"
                                        update_log_table("Fulfill Quantity", "", description)
                                        #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
                                        #               (idList[i],partNo, stnQty * noOfCartons + totalLooseQty, "Fulfill Quantity", datetime.now()))
                                        DB.cursor.execute("UPDATE main_inventory SET carton_quantity = carton_quantity - %s, sealed_quantity = sealed_quantity - %s WHERE part_no = %s", (noOfCartons, totalLooseQty, partNo))
                                    else:
                                        if memoryFulfilledAgain == 0:
                                            DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = %s, cartons_id = CONCAT(COALESCE(cartons_id,''), %s) WHERE id = %s",
                                                           (stnQty * noOfCartons, carton_id, idList[i]))
                                        else:
                                            DB.cursor.execute("UPDATE delivery_orders SET fulfilled_quantity = fulfilled_quantity + %s, cartons_id = CONCAT(COALESCE(cartons_id,''), %s) WHERE id = %s",
                                                           (stnQty * noOfCartons," | " + carton_id, idList[i]))
                                        description = "(" + str(idList[i]) + "," + str(partNo) + "," + str(stnQty * noOfCartons) + "/" + str(memoryTotal) + ")"
                                        update_log_table("Fulfill Quantity", "", description)
                                        #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
                                        #               (idList[i],partNo, stnQty * noOfCartons, "Fulfill Quantity", datetime.now()))
                                        DB.cursor.execute("UPDATE main_inventory SET carton_quantity = carton_quantity - %s WHERE part_no = %s", (noOfCartons, partNo))
                                    update_main_inventory(partNo)
                                    DB.conn.commit()
    if continueFlag:
        process_info_4 = evaluate_part_list(complete_part_list)
        if process_info_4 is not None:
            process_info.extend(process_info_4)
    return process_info
##############################################################################################################
def evaluate_part_list(complete_part_list):
    process_info = []
    for i in complete_part_list:
        DB.cursor.execute("SELECT delivery_date FROM delivery_orders WHERE part_no = %s AND quantity > fulfilled_quantity ORDER BY delivery_date",(i,))
        earliestdd = DB.cursor.fetchone()
        fulfilledIDs = None
        if earliestdd:
            DB.cursor.execute("SELECT id FROM delivery_orders WHERE delivery_date > %s AND part_no = %s AND fulfilled_quantity > 0 ORDER BY delivery_date", (earliestdd[0],i))
            fulfilledIDs = DB.cursor.fetchall()
        if fulfilledIDs:
            fulfilledIDs= list(map(list, fulfilledIDs))
            process_info.append("\n* Fulfilled orders for partNo " + i + " are found. Will be removed and allocated......")
            for x in range(len(fulfilledIDs)):
                remove_cartons(fulfilledIDs[x][0])
            idList, processed_do_dataframe = importPartOrder(i)
            process_info_2 = (False,idList,processed_do_dataframe)
            if process_info_2 is not None:
                process_info.extend(process_info_2)
        # Creating a carton if the sealed quantity for this partNo is above stnQty in total.
        if earliestdd:
            DB.cursor.execute("SELECT sealed_quantity, stn_qty FROM main_inventory WHERE part_no = %s", (i,))
            sealedAboveInfo = DB.cursor.fetchone()
            if sealedAboveInfo:
                if int(sealedAboveInfo[0]) > int(sealedAboveInfo[1]):
                    process_info.append("\n* Sealed quantity for partNo " + i + " is above standard quantity. A carton will be created......")
                    createStnCarton(str(i),int(sealedAboveInfo[1]))
                    idList, processed_do_dataframe = importPartOrder(i)
                    process_info_3 = fulfill_order(False,idList,processed_do_dataframe)
                    if process_info_3 is not None:
                        process_info.extend(process_info_3)
    return process_info
##############################################################################################################
def remove_cartons(ID):
    # Finds the deliveryOrderNo, and then blanks the cartons_ID.
    DB.cursor.execute("SELECT part_no, cartons_id, fulfilled_quantity FROM delivery_orders WHERE id = %s",(ID,))
    deliveryOrderInfo = DB.cursor.fetchone()
    blankCartonsID = ""
    DB.cursor.execute("UPDATE delivery_orders SET cartons_id = %s, fulfilled_quantity = 0 WHERE id = %s",(blankCartonsID,ID))
    DB.conn.commit()
    partNo = str(deliveryOrderInfo[0])
    cartons_ID = str(deliveryOrderInfo[1])
    fulfilledQuantity = int(deliveryOrderInfo[2])
    # Returning standard quantity stock
    DB.cursor.execute("SELECT COUNT(*) FROM carton_table WHERE delivery_id = %s AND loose_quantity = 0", (ID,))
    noOfCartons = DB.cursor.fetchone()
    noOfCartons = int(noOfCartons[0])
    DB.cursor.execute("SELECT carton_quantity, date_codes, remarks, carton_no FROM carton_table WHERE delivery_id = %s AND loose_quantity = 0", (ID,))
    getCartons = DB.cursor.fetchall()
    if getCartons:
        getCartons= list(map(list, getCartons))
        DB.cursor.execute("UPDATE carton_table SET delivery_id = %s WHERE delivery_id = %s AND loose_quantity = 0", (0,ID))
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
            DB.cursor.execute("SELECT part_no FROM main_inventory WHERE part_no = %s", (partNo,))
            findPartNo = DB.cursor.fetchone()
            if not findPartNo:
                DB.cursor.execute(
                    "INSERT INTO main_inventory (part_no, old_stock, total_stock) " "VALUES(%s,%s,%s)",
                    (partNo, old_stock_quantity, old_stock_quantity))
                update_main_inventory(partNo)
            else:
                DB.cursor.execute("UPDATE main_inventory SET old_stock = old_stock + %s, total_stock = total_stock + %s WHERE part_no = %s", (old_stock_quantity, old_stock_quantity, partNo))
            logger.info("Old stock allocated to deleted delivery order ID " + str(ID) + " is sent back to the inventory, quantity of " + str(old_stock_quantity))
            DB.conn.commit()
    # Returning loose quantity stock to sealed inventory
    DB.cursor.execute("SELECT carton_quantity, date_codes, remarks, loose_quantity, carton_no, log_id FROM carton_table WHERE delivery_id = %s AND loose_quantity > 0", (ID,))
    looseQuantityGet = DB.cursor.fetchall()
    if looseQuantityGet:
        looseQuantityGet= list(map(list, looseQuantityGet))
        for y in range(len(looseQuantityGet)):
            if "=" not in looseQuantityGet[y][1]:
                DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, looseQuantityGet[y][1], looseQuantityGet[y][2]))
                sealedResult = DB.cursor.fetchone()
                if not sealedResult:
                    DB.cursor.execute(
                        "INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                        (partNo, int(looseQuantityGet[y][0]) * int(looseQuantityGet[y][3]), looseQuantityGet[y][1], looseQuantityGet[y][2], looseQuantityGet[y][5], datetime.now() ,LoginSystem.user_name))
                else:
                    DB.cursor.execute(
                        "UPDATE sealed_inventory SET quantity = quantity + %s WHERE part_no = %s AND date_code = %s AND remarks = %s AND id = %s",
                        (int(looseQuantityGet[y][0]) * int(looseQuantityGet[y][3]), partNo, looseQuantityGet[y][1], looseQuantityGet[y][2], sealedResult[0]))
                DB.conn.commit()
                logger.info("Loose quantity allocated to delivery order ID " + str(ID) + " is sent back to the inventory, quantity of " + str(int(looseQuantityGet[y][0]) * int(looseQuantityGet[y][3])))
            else:
                dateCodeSplit = looseQuantityGet[y][1].split(" ")
                remarkSplit = looseQuantityGet[y][2].split(")")
                for m in range(len(dateCodeSplit)):
                    getDateCode = dateCodeSplit[m].split("=")[0]
                    getQuantity = dateCodeSplit[m].split("=")[1]
                    getRemark = remarkSplit[m].split("(")[1]

                    DB.cursor.execute("SELECT * FROM sealed_inventory WHERE part_no = %s AND date_code = %s AND remarks = %s", (partNo, getDateCode, getRemark))
                    sealedResult = DB.cursor.fetchone()
                    if not sealedResult:
                        DB.cursor.execute("INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                       (partNo, int(getQuantity), str(getDateCode), getRemark, looseQuantityGet[y][5],datetime.now() ,LoginSystem.user_name))
                    else:
                        DB.cursor.execute(
                            "UPDATE sealed_inventory SET quantity = quantity + %s WHERE part_no = %s AND date_code = %s AND remarks = %s AND id = %s",
                            (getQuantity, partNo, getDateCode, getRemark, sealedResult[0]))
                    DB.conn.commit()
                    logger.info("Loose quantity allocated to delivery order ID " + str(ID) + " is sent back to the inventory, quantity of " + str(int(looseQuantityGet[y][0]) * int(looseQuantityGet[y][3])))
            DB.cursor.execute("DELETE FROM carton_table WHERE delivery_id = %s AND loose_quantity > 0", (ID,))
            DB.conn.commit()
    description = "(" + str(ID) + "," + str(partNo) + "," + str(0-fulfilledQuantity) + ")"
    update_log_table("Removing Cartons", "", description)
    #DB.cursor.execute("INSERT INTO delivery_order_entry_tracker (delivery_order_id, partNo, quantityChange, description, time) " "VALUES (%s,%s,%s,%s,%s)",
    #               (ID,partNo, 0-fulfilledQuantity, "Removing Cartons", datetime.now()))
    update_main_inventory(partNo)
##############################################################################################################
def importPartOrder(partNo):
    # This function is used to check the delivery orders to see if there are any unfulfilled ones, and check if the inventory can fulfill these delivery orders.
    idList = []
    processed_do_dataframe = pd.DataFrame(
        columns=['customer', 'partNo', 'quantity', 'uom', 'deliveryOrder', 'deliveryDate','weightLimit'])
    DB.cursor.execute("SELECT customer, part_no, quantity, uom, delivery_order, delivery_date, weight_limit, id, fulfilled_quantity FROM delivery_orders WHERE quantity > fulfilled_quantity AND part_no = %s ORDER BY part_no, delivery_date, id", (partNo,))
    packedGoods = DB.cursor.fetchall()
    packedGoods= list(map(list, packedGoods))
    for i in range(len(packedGoods)):
        tempdf = {'customer': packedGoods[i][0], 'partNo': packedGoods[i][1], 'quantity': (int(packedGoods[i][2]) - int(packedGoods[i][8])), 'uom': packedGoods[i][3], 'deliveryOrder': packedGoods[i][4],
                  'deliveryDate': packedGoods[i][5], 'weightLimit': packedGoods[i][6]}
        processed_do_dataframe = processed_do_dataframe.append(tempdf, ignore_index=True)
        idList += [int(packedGoods[i][7])]
    return idList, processed_do_dataframe
##############################################################################################################
def refreshDeliveryOrders():
    # This function is used to check all the available unfulfilled delivery orders in the database, and check if the inventory can fulfill these delivery orders.
    reorganizeDeliveryOrders()
    idList = []
    process_info = []
    processed_do_dataframe = pd.DataFrame(
        columns=['customer', 'partNo', 'quantity', 'uom', 'deliveryOrder', 'deliveryDate','weightLimit'])
    DB.cursor.execute("SELECT customer, part_no, quantity, uom, delivery_order, delivery_date, weight_limit, id, fulfilled_quantity FROM delivery_orders WHERE quantity > fulfilled_quantity ORDER BY part_no, delivery_date, delivery_order, quantity")
    packedGoods = DB.cursor.fetchall()
    packedGoods= list(map(list, packedGoods))
    for i in range(len(packedGoods)):
        tempdf = {'customer': packedGoods[i][0], 'partNo': packedGoods[i][1], 'quantity': (int(packedGoods[i][2]) - int(packedGoods[i][8])), 'uom': packedGoods[i][3], 'deliveryOrder': packedGoods[i][4],
                  'deliveryDate': packedGoods[i][5], 'weightLimit': packedGoods[i][6]}
        processed_do_dataframe = processed_do_dataframe.append(tempdf, ignore_index=True)
        idList += [int(packedGoods[i][7])]
    process_info = fulfill_order(False,idList,processed_do_dataframe)
    return process_info
##############################################################################################################
def createStnCarton(partNo, stnQty):
    # This function is used to create a carton.
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
    remainingQuantity = stnQty
    moreThanOneDateCode = False
    sealedDateCodes = ""
    sealedRemarks = ""
    y = 0
    log_id = 0
    while remainingQuantity > 0:
        log_id = sealed_info[y][4]
        if sealed_info[y][4] is None:
            log_id = 0
        if sealed_info[y][2] == None or sealed_info[y][2] == "":
            sealed_info[y][2] = ""
        if int(sealed_info[y][3]) >= remainingQuantity:
            if moreThanOneDateCode:
                sealedDateCodes += str(sealed_info[y][1])
                sealedDateCodes += "="
                sealedDateCodes += str(remainingQuantity)
                sealedRemarks += "("
                sealedRemarks += sealed_info[y][2]
                sealedRemarks += ")="
                sealedRemarks += str(remainingQuantity)
            else:
                sealedDateCodes += str(sealed_info[y][1])
                sealedRemarks += sealed_info[y][2]
            sealed_info[y][3] -= remainingQuantity
            remainingQuantity -= remainingQuantity
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
            remainingQuantity -= sealed_info[y][3]
            sealed_info[y][3] -= sealed_info[y][3]
        y = y + 1
    DB.cursor.execute("SELECT stn_carton FROM part_info WHERE part_no = %s", (partNo,))
    stn_carton = DB.cursor.fetchone()
    DB.cursor.execute(
        "INSERT INTO carton_table (part_no, carton_quantity, date_codes, earliest_date_code, remarks, loose_quantity, carton_no, delivery_id, packing_date, log_id, time_created, user_name) " "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (partNo, 1, sealedDateCodes, sealed_info[0][1], sealedRemarks, 0  ,stn_carton[0], 0, date.today().isoformat(), log_id, datetime.now() ,LoginSystem.user_name))
    DB.conn.commit()
    for b in range(y):
        DB.cursor.execute("UPDATE sealed_inventory SET quantity = %s WHERE id = %s",(sealed_info[b][3],sealed_info[b][0]))
        DB.conn.commit()
    update_main_inventory(partNo)
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
def checkUnfulfilledDeliveryOrdersWithSimilarPartNos():
    # This function finds any unfulfilled delivery orders and returns any partNos to take note.
    DB.cursor.execute("SELECT part_no, quantity, fulfilled_quantity FROM delivery_orders WHERE quantity != fulfilled_quantity")
    delivery_orders = DB.cursor.fetchall()

    similar_part_no_list_1 = []
    similar_part_no_list_2 = []
    process_info = []

    for part_no, quantity, fulfilled_quantity in delivery_orders:
        # Split part_no before the first space and first opening bracket (if exists)

        part_no_split_space = part_no.split(' ', 1)[0]
        part_no_split_bracket = part_no.split('(', 1)[0].rstrip()

        # Check if part_no_split_space is different from part_no
        if part_no_split_space != part_no and part_no not in similar_part_no_list_2:
            DB.cursor.execute("SELECT stn_qty, carton_quantity, sealed_quantity, part_no FROM main_inventory WHERE part_no LIKE %s AND total_stock > 0", ('%' + part_no_split_space + '%',))
            inventory_data = DB.cursor.fetchall()

            if inventory_data:
                for single_inventory_data in inventory_data:
                    stn_qty, carton_quantity, sealed_quantity, inventory_part_no = single_inventory_data

                    # Calculate the remaining quantity needed
                    remaining_quantity = quantity - fulfilled_quantity

                    if remaining_quantity > stn_qty:
                        if carton_quantity > 0 and part_no != inventory_part_no:
                            # Add the part_no_split_space to the similar_part_no_list
                            similar_part_no_list_1.append(inventory_part_no)
                            similar_part_no_list_2.append(part_no)
                    else:
                        if sealed_quantity >= remaining_quantity and part_no != inventory_part_no:
                            # Add the part_no_split_space to the similar_part_no_list
                            similar_part_no_list_1.append(inventory_part_no)
                            similar_part_no_list_2.append(part_no)

        # Check if part_no_split_bracket is different from part_no
        if part_no_split_bracket != part_no_split_space and part_no_split_bracket != part_no and part_no not in similar_part_no_list_2:
            DB.cursor.execute("SELECT stn_qty, carton_quantity, sealed_quantity, part_no FROM main_inventory WHERE part_no LIKE %s AND total_stock > 0", ('%' + part_no_split_bracket + '%',))
            inventory_data = DB.cursor.fetchall()

            if inventory_data:
                for single_inventory_data in inventory_data:
                    stn_qty, carton_quantity, sealed_quantity, inventory_part_no = single_inventory_data

                    # Calculate the remaining quantity needed
                    remaining_quantity = quantity - fulfilled_quantity

                    if remaining_quantity > stn_qty:
                        if carton_quantity > 0 and part_no != inventory_part_no:
                            # Add the part_no_split_bracket to the similar_part_no_list
                            similar_part_no_list_1.append(inventory_part_no)
                            similar_part_no_list_2.append(part_no)
                    else:
                        if sealed_quantity >= remaining_quantity and part_no != inventory_part_no:
                            # Add the part_no_split_bracket to the similar_part_no_list
                            similar_part_no_list_1.append(inventory_part_no)
                            similar_part_no_list_2.append(part_no)

    if similar_part_no_list_1:
        process_info.append("\n Consider transferring stock for fulfillment:")
        for part_no_1, part_no_2 in zip(similar_part_no_list_1, similar_part_no_list_2):
            process_info.append("\n* " + part_no_1 + " -> " + part_no_2)
    return process_info

