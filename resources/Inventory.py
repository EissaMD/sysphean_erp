import tkinter as tk
from .UI import Page, LeftMenu, EntriesFrame, SearchWindow
from .Logics import DB
from tksheet import Sheet
from tkinter import messagebox


class Inventory(Page):
    def __init__(self):
        self.create_new_page("- - -")
        left_menu = LeftMenu()
        left_menu_ls = {
            "Inventory": AddInventory,
        }
        left_menu.update_menu(left_menu_ls)


##############################################################################################################
class AddInventory(DB,Page):
    def __init__(self):
        menu_ls = {
            "Add": self.Add_frame,
            "View": self.View_frame
        }
        self.create_new_page("Inventory", menu_ls)

    ###############        ###############        ###############        ###############
    def Add_frame(self):
        body_frame = self.create_new_body()
        self.menu.configure(text="Add")
        entries = (
            ("part_no", "entry", (0, 0, 3), None),
            ("quantity", "entry", (1, 0, 1), None),
            ("reserved_quantity", "entry", (2, 0, 1), None),
            ("total_quantity", "entry", (3, 0, 1), None),
        )
        self.inventory_entries = EntriesFrame(body_frame, "Inventory Information", entries)
        self.create_footer(self.confirm_btn)
    ##############################################################################################################
    def View_frame(self):
        body_frame = self.create_new_body()
        self.menu.configure(text="View")

        # Create a Treeview widget to display the data
        columns = ("id", "name", "quantity", "reserved_quantity", "total_quantity")
        # table = ttk.Treeview(self.body, columns=columns, show='headings')

        # # Set column headings
        # for col in columns:
        #     table.heading(col, text=col)
        #     table.column(col, width=100)  # Adjust column widths as needed

        # # Retrieve data from the database and populate the table
        # db = DB()
        # db.connect()
        # data = db.select("inventory", columns)
        # for row in data:
        #     table.insert("", "end", values=row)

        # # Pack the table to display
        # table.pack(fill="both", expand=True)
    ##############################################################################################################
    def confirm_btn(self):
        # Extract data from EntriesFrame instances
        inventory_data = self.inventory_entries.get_data()

        # Retrieve data
        data = list(inventory_data.values())
        col_name = ("name", "quantity", "reserved_quantity", "total_quantity")
        self.insert("inventory", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")

    # db.insert("purchase_requisition", ("item_description", "quantity", "credit_limit"), ("john", "john@example.com", "2000"), )


