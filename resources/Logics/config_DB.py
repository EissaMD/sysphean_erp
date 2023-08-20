import sqlite3
from tkinter import messagebox
import os

class DB():
    ###############        ###############        ###############        ###############
    def connect(self):
        db_path = r'./sql.db'
        if not os.path.exists(db_path):
            messagebox.showerror("Error",f"The database does not exist, please try to contact Sysphean support.")
            return
        try:
            DB.conn = sqlite3.connect(db_path)
            DB.cursor = DB.conn.cursor()
        except sqlite3.Error as error:
            messagebox.showerror("Error",f"Error in connection to sql database {error}")
    ###############        ###############        ###############        ###############
    def insert(self,table,columns,values):
        col = ", ".join(columns)
        qq = ", ".join(["?" for i in range(len(values))])
        values = tuple(values)
        query = f'INSERT INTO {table} ({col}) VALUES ({qq});'
        try:
            DB.cursor.execute(query, values)
            DB.conn.commit()
        except sqlite3.Error as error:
            messagebox.showerror("Error",f"The process couldn't be completed by the system, {error}")
    ###############        ###############        ###############        ###############
    def select(self,table,columns,conditions="",values=()):
        col = ", ".join(columns)
        query = f"SELECT {col} FROM {table};"
        if conditions:
            query+= " WHERE " +conditions
        try:
            DB.cursor.execute(query, values)
            return DB.cursor.fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Error",f"The process couldn't be completed by the system, {error}")
    ###############        ###############        ###############        ###############
    def update(self,table,columns,conditions,values):
        columns = [column+"=? " for column in columns]
        col = ", ".join(columns)
        query = f"UPDATE {table} SET {col}" + "WHERE " +conditions + ";"
        try:
            DB.cursor.execute(query, values)
            DB.conn.commit()
        except sqlite3.Error as error:
            messagebox.showerror("Error",f"The process couldn't be completed by the system, {error}")
    ###############        ###############        ###############        ###############
    def delete(self,table,conditions,values):
        query = f"DELETE FROM {table}"
        if conditions:
            query = query + " WHERE " + conditions
        query += ";"
        try:
            DB.cursor.execute(query, values)
            DB.conn.commit()
        except sqlite3.Error as error:
            messagebox.showerror("Error",f"The process couldn't be completed by the system, {error}")#
##############################################################################################################


if __name__ == "__main__":
    db = DB()
    db.connect()
    # db.update("customer", ("name",),"name=?",("aid","aad"))
    # db.delete("customer","name=?",("dd",))
    data=db.select("customer",["*"])
    print(data)