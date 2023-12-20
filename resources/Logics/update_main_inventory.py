from .DB import DB

def update_main_inventory(part_no=""):
    """ update Main inventory from sealed_inventory and carton table
    """
    if part_no =="":
        return
    DB.cursor.execute("DELETE FROM carton_table WHERE carton_quantity = %s AND loose_quantity = %s AND part_no = %s",(0,0,part_no))
    DB.conn.commit()
    DB.cursor.execute("DELETE FROM sealed_inventory WHERE quantity = %s AND part_no = %s" ,(0,part_no))
    DB.conn.commit()
    # check if part_no is present in main_inventory
    DB.cursor.execute("SELECT * from main_inventory WHERE part_no = %s",(part_no,))
    part_no_exist = DB.cursor.fetchone()
    if not part_no_exist:# if there is no record in main_inventory
        DB.cursor.execute("INSERT INTO main_inventory (part_no) VALUES (%s)", (part_no,))#create new record 
    # get standard quantity
    stn_qty = 0
    DB.cursor.execute("SELECT stn_qty , uom , cavity FROM part_info WHERE part_no = %s", (part_no,))
    sdQ = DB.cursor.fetchone()
    if sdQ:
        stn_qty , uom , cavity = remove_none( sdQ[0],"i") , remove_none( sdQ[1]) , remove_none( sdQ[2],"i")
        if uom.upper() == "PCS" and cavity>1 :
            stn_qty = stn_qty * cavity
    # get old_stock
    old_stock = 0 
    DB.cursor.execute("SELECT old_stock from main_inventory WHERE part_no = %s",(part_no,))
    oS = DB.cursor.fetchone()
    if oS:
        old_stock = remove_none( oS[0],"i")
    # check carton_table (Standard carton)
    DB.cursor.execute("SELECT SUM(carton_quantity) FROM carton_table WHERE part_no = %s AND loose_quantity = %s AND (delivery_id = %s OR delivery_id IS NULL)",(part_no,0,0))
    cQ = DB.cursor.fetchone()
    carton_quantity = remove_none( cQ[0],"i")
    # check sealed_inventory
    DB.cursor.execute("SELECT SUM(quantity) FROM sealed_inventory WHERE part_no = %s",(part_no,))
    sQ = DB.cursor.fetchone()
    sealed_quantity = remove_none(sQ[0],"i")
    
    new_stock = (carton_quantity * stn_qty) + sealed_quantity 
    total_stock = old_stock +new_stock
    DB.cursor.execute("UPDATE main_inventory SET carton_quantity = %s, sealed_quantity = %s, stn_qty = %s, new_stock = %s, total_stock = %s WHERE part_no = %s;",
                       (carton_quantity,  sealed_quantity, stn_qty, new_stock,total_stock, part_no))
    DB.conn.commit()
##############################################################################################################

def remove_none(var , data_type="s"):
    if data_type.lower() == "s":#string
        return  str(var) if var != None else ""
    elif data_type.lower() == "i":#integer
        return int(var) if var != None else 0
    elif data_type.lower() == "f":#float
        return float(var) if var != None else 0
##############################################################################################################