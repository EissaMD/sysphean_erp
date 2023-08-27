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
            DB.cursor.execute(query, tuple(values))
            DB.conn.commit()
        except sqlite3.Error as error:
            messagebox.showerror("Error",f"The process couldn't be completed by the system, {error}")
    ###############        ###############        ###############        ###############
    def select(self,table,columns,conditions="",values=()):
        col = ", ".join(columns)
        query = f"SELECT {col} FROM {table}"
        if conditions:
            query+= " WHERE " +conditions
        try:
            DB.cursor.execute(query+";", tuple(values))
            return DB.cursor.fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Error",f"The process couldn't be completed by the system, {error}")
    ###############        ###############        ###############        ###############
    def update(self,table,columns,conditions,values):
        columns = [column+"=? " for column in columns]
        col = ", ".join(columns)
        query = f"UPDATE {table} SET {col}" + "WHERE " +conditions + ";"
        try:
            DB.cursor.execute(query, tuple(values))
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
            DB.cursor.execute(query, tuple(values))
            DB.conn.commit()
        except sqlite3.Error as error:
            messagebox.showerror("Error",f"The process couldn't be completed by the system, {error}")
    ###############        ###############        ###############        ###############
    def get_last_id(self,table):
        self.cursor.execute(f"SELECT id from {table} order by id DESC limit 1")
        last_id = self.cursor.fetchone()
        return last_id[0] if last_id else 0
##############################################################################################################


if __name__ == "__main__":
    db = DB()
    db.connect()
    # rows = (
    #     ("eissa","eissa@example.com","6000"),
    #     ("aa","aa@example.com","3000"),
    #     ("bb","bb@example.com","4000"),
    # )
    # for row in rows:
    #     db.insert("customer",("name","email","credit_limit"),row)
    # data =db.select("customer",("name",),"credit_limit>? ",(2000,))
    # for row in data:
    #     print(row)
    # db.update("customer",("name",),"name='shawn'",("eissa",))