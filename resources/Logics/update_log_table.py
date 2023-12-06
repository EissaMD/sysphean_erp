
from .DB import DB
from config import *

def update_log_table(module_name,process_name, old_description="", new_description="",reason=""):
    if type(new_description) is list or type(new_description) is tuple:
        new_description  = "(" +  ', '.join(map(str, new_description)) + ')'
    if type(old_description) is list or type(old_description) is tuple:
        old_description  = "(" +  ', '.join(map(str, old_description)) + ')'
    DB.cursor.execute("INSERT INTO logger (program, process_name, old_description, new_description, reason, time_added , user_name) " "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                   ("Batch Entry", process_name, old_description, new_description, reason,datetime.now() ,"GlobalVar.user_name")       )
    DB.conn.commit()
    DB.cursor.execute("SELECT id from logger WHERE program = %s AND process_name = %s AND  old_description = %s AND  new_description = %s AND  reason = %s AND  user_name = %s ORDER BY id DESC;",
                   (module_name, process_name, old_description, new_description, reason ,"GlobalVar.user_name") )
    log_id = DB.cursor.fetchone()
    log_id = int(log_id[0]) if log_id else 0
    return log_id