import sqlite3
from tkinter import messagebox

class DB():
    ###############        ###############        ###############        ###############
    def connect(self):
        try:
            DB.conn = sqlite3.connect(r'./sql.db')
            DB.cursor = DB.conn.cursor()
        except sqlite3.Error as error:
            messagebox.showerror("Error",f"Error in connection to sql database {error}")
    ###############        ###############        ###############        ###############
    def insert(self,table,columns,values):
        col = ", ".join(columns)
        qq = ", ".join(["?" for i in range(len(values))])
        values = tuple(values)
        query = f'INSERT INTO {table} ({col}) VALUES ({qq})'
        try:
            DB.cursor.execute(query, values)
            DB.conn.commit()
        except sqlite3.Error as error:
            messagebox.showerror("Error",f"The system wasn't able to enter this data, {error.args}")


if __name__ == "__main__":
    db = DB()
    db.connect()