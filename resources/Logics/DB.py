import sqlite3
from tkinter import messagebox
import os

class DB():
    ###############        ###############        ###############        ###############
    def connect(self,db_path=r'./sql.db'):
        """Connect to database , Execute this function only one time.

        Args:
            db_path (regexp, optional): Path to database. Defaults to r'./sql.db'.
        """
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
        """insert a new row into the database

        Args:
            table (str): name of the table to insert data
            columns (tuple): name of columns in the table 
            values (tuple): values of the new row , no of columns SHOULD equal number of values
        """
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
        """Get data from the database

        Args:
            table (str): name of the table to get data
            columns (tuple): name of columns in the table 
            conditions (str, optional): to filter records based on conditions. Defaults to "" no filter.
            values (tuple, optional): if there are conditions need values. Defaults to ().

        Returns:
            list: a list of tuples containing selected values
        """
        col = ", ".join(columns)
        query = f"SELECT {col} FROM {table}"
        if conditions:
            query+= " WHERE " +conditions
        try:
            DB.cursor.execute(query+";", tuple(values))
            return [list(record) for record in DB.cursor.fetchall()]
        except sqlite3.Error as error:
            messagebox.showerror("Error",f"The process couldn't be completed by the system, {error}")
            return []
    ###############        ###############        ###############        ###############
    def update(self,table,columns,conditions,values):
        """Update any records in database that meet the conditions

        Args:
            table (str): name of the table to update data
            columns (tuple): name of columns in the table 
            conditions (str): filter out the records
            values (tuple): if there are conditions need values
        """
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
        """Delete any records from database

        Args:
            table (str): name of the table to update data
            conditions (str): filter out the records
            values (tuple): if there are conditions need values
        """
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
        """last id returned from any table

        Args:
            table (str): table name

        Returns:
            int: last ID
        """
        self.cursor.execute(f"SELECT id from {table} order by id DESC limit 1")
        last_id = self.cursor.fetchone()
        return last_id[0] if last_id else 0
##############################################################################################################

def clear_all_data(db_path=r'sysphean_erp\sql.db'):
    # WARNING # All data will be lost # WARNING #
    db = DB()
    db.connect(db_path)
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [name[0] for name in db.cursor.fetchall()]
    for table in tables:
        db.cursor.execute(f'DELETE FROM {table};',);	
    db.conn.commit()
    db.conn.close()
##############################################################################################################
    
if __name__ == "__main__":
    db = DB()
    db.connect()
    customer_name = ''
    # customer_records = db.select("customer",("name", "email", "contact", "credit_limit", "shipping_address" , "billing_address"),"name=?",(customer_name,))
    # db.cursor.execute(f"SELECT * FROM customer where name LIKE'%{customer_name}%'")
    start_date = "2022-01-01"
    end_date = "2023-12-12"
    db.cursor.execute(f"SELECT DISTINCT sales_representative FROM sale_order WHERE delivery_date BETWEEN ? AND ?",(start_date,end_date))
    customer_records = db.cursor.fetchall()
    print(customer_records)