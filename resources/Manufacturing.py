import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter as tk
from .UI import Page, LeftMenu, EntriesFrame
from .Logics import DB
from tkinter import messagebox
from datetime import datetime

class Manufacturing(Page):
    def __init__(self):
        self.create_new_page("Manufacturing")
        left_menu = LeftMenu()
        left_menu_ls = {
            "Part No": PartNo,
            "Batch Entry": Entry,
            "Production Entry": ProductionEntry,
        }
        left_menu.update_menu(left_menu_ls)


##############################################################################################################
class PartNo(DB,Page):
    def __init__(self):
        menu_ls = {
            "Add": self.Add_frame,
            "View": self.View_frame,
            "Edit/Delete": self.edit_frame,
        }
        self.create_new_page("Part No", menu_ls)
    ###############        ###############        ###############        ###############
    def Add_frame(self):
        body_frame = self.create_new_body()
        entries = (
            ("part_no", "entry", (0, 0, 3), None),
            ("bundle_qty", "entry", (1, 0, 3), None),
            ("stn_carton", "menu", (2, 0, 3), ("8", "7", "6", "14", "10", "9", "12", "15", "JIG CARTON")),
            ("stn_qty", "entry", (3, 0, 3), None),
            ("uom", "menu", (4, 0, 3), ("PCS", "PANEL")),
            ("cavity", "entry", (5, 0, 3), None),
            ("customer", "entry", (6, 0, 3), None),
            ("single_sided", "menu", (7, 0, 3), ("Single", "Double")),
            ("paper_label", "menu", (8, 0, 3), ("Paper", "Sticker")),
        )
        self.part_no_entries = EntriesFrame(body_frame, entries) ; self.part_no_entries.pack()
        self.create_footer(self.confirm_btn)
    ###############        ###############        ###############        ###############
    def confirm_btn(self):
        # Extract data from EntriesFrame instances
        part_no_data = self.part_no_entries.get_data()

        # Retrieve data
        data = list(part_no_data.values())
        col_name = ("part_no", "bundle_qty", "stn_carton", "stn_qty", "uom", "cavity", "customer", "single_sided", "paper_label")
        self.insert("part_no", col_name, data)
        stn_qty_for_main_inventory = 0
        if data[4] == "PCS":
            stn_qty_for_main_inventory = int(data[3]) * int(data[5])
        else:
            stn_qty_for_main_inventory = int(data[3])
        self.insert("main_inventory", ("part_no","carton_quantity","sealed_quantity","stn_qty","total_stock"), (data[0],0,0,stn_qty_for_main_inventory,0))
        messagebox.showinfo("Info", "The process was successful!")
    ###############        ###############        ###############        ###############
    def View_frame(self):
        body_frame = self.create_new_body()

        # Create an Entry widget and Search button for filtering
        filter_label = ctk.CTkLabel(body_frame, text="Part No:")
        filter_label.pack()

        filter_entry = ctk.CTkEntry(body_frame)
        filter_entry.pack()

        search_button = ctk.CTkButton(body_frame, text="Search",
                                      command=lambda: self.filter_table(table, filter_entry.get()))
        search_button.pack()

        # Create a Treeview widget to display the data
        columns = ("id", "part_no", "bundle_qty", "stn_carton", "stn_qty", "uom", "cavity", "customer", "single_sided", "paper_label")

        # Create a horizontal scrollbar for the custom view
        x_sroller = ctk.CTkScrollbar(master=body_frame, orientation='horizontal')
        x_sroller.pack(side='bottom')

        table = ttk.Treeview(body_frame, columns=columns, show='headings',xscrollcommand=x_sroller.set )

        style = ttk.Style()

        style.theme_use("default")

        # Configure the Treeview style
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="black",  # Change the foreground color to make text visible
                        rowheight=25,
                        fieldbackground="#ffffff",
                        bordercolor="#000000",
                        borderwidth=1,  # Set border width to 1
                        padding=5)  # Add padding around cell content

        style.map('Treeview', background=[('selected', '#22559b')])

        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat")

        style.map("Treeview.Heading",
                  background=[('active', '#3484F0')])

        # Set column headings and widths
        column_widths = [10, 100, 50, 50, 50, 20, 20, 100, 50, 50]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        # Retrieve data from the database and populate the table
        data = self.select("part_no", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)
    ###############        ###############        ###############        ###############
    def filter_table(self, table, keyword):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = ("id", "part_no", "bundle_qty", "stn_carton", "stn_qty", "uom", "cavity", "customer", "single_sided", "paper_label")
        data = self.select("part_no", columns, "part_no LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)
    ###############        ###############        ###############        ###############
    def edit_frame(self):
        body_frame = self.create_new_body()

        # Create a LabelFrame for selection and editing
        selection_frame = ttk.LabelFrame(body_frame, text="Select Part No to Edit")
        selection_frame.pack(padx=10, pady=10, fill="both", expand=True)

        entries = self.select("part_no", ["part_no"])
        selected_entry = tk.StringVar()
        selected_entry.set("Select an entry")

        # Strip leading/trailing spaces from entry names
        entry_options = [f"{entry[0].strip()}" for entry in entries]

        # Create the Combobox
        self.entry_combobox = ttk.Combobox(selection_frame, values=entry_options, state="readonly", width=75)
        self.entry_combobox.pack(padx=10, pady=10)

        # Create a Button to trigger editing
        edit_button = ttk.Button(selection_frame, text="Edit",
                                 command=lambda: self.edit_part_no(self.entry_combobox.get()))
        edit_button.pack(padx=10, pady=10)

        # Create a Button to trigger deletion
        delete_button = ttk.Button(selection_frame, text="Delete",
                                   command=lambda: self.delete_part_no(self.entry_combobox.get()))
        delete_button.pack(padx=10, pady=10)

        # Create a frame to display entry fields for editing
        self.edit_part_no_frame = ttk.LabelFrame(body_frame, text="Edit Part No")
        self.edit_part_no_frame.pack(padx=10, pady=10, fill="both", expand=True)

    ###############        ###############        ###############        ###############
    def edit_part_no(self, selected_entry):
        if selected_entry.startswith("Select Part No"):
            return

        # Clear previous entry fields
        for widget in self.edit_part_no_frame.winfo_children():
            widget.destroy()

        entry_id = str(selected_entry)
        retrieved_values = self.select("part_no", ["*"], "part_no=?", (entry_id,))
        # Retrieve data for the selected entry
        entry_data = [
            ("part_no", "entry", (0, 0, 3), None),
            ("bundle_qty", "entry", (1, 0, 3), None),
            ("stn_carton", "menu", (2, 0, 3), ("8", "7", "6", "14", "10", "9", "12", "15", "JIG CARTON")),
            ("stn_qty", "entry", (3, 0, 3), None),
            ("uom", "menu", (4, 0, 3), ("PCS", "PANEL")),
            ("cavity", "entry", (5, 0, 3), None),
            ("customer", "entry", (6, 0, 3), None),
            ("single_sided", "menu", (7, 0, 3), ("Single", "Double")),
            ("paper_label", "menu", (8, 0, 3), ("Paper", "Sticker")),
        ]
        self.part_no_entries = EntriesFrame(self.edit_part_no_frame, entry_data)
        self.part_no_entries.pack()

        if entry_data:
            # Create EntryFrame for editing
            self.part_no_entries.change_value("part_no", retrieved_values[0][1])
            self.part_no_entries.change_value("bundle_qty", retrieved_values[0][2])
            self.part_no_entries.change_menu_value("stn_carton", retrieved_values[0][3])
            self.part_no_entries.change_value("stn_qty", retrieved_values[0][4])
            self.part_no_entries.change_menu_value("uom", retrieved_values[0][5])
            self.part_no_entries.change_value("cavity", retrieved_values[0][6])
            self.part_no_entries.change_value("customer", retrieved_values[0][7])
            self.part_no_entries.change_menu_value("single_sided", retrieved_values[0][8])
            self.part_no_entries.change_menu_value("paper_label", retrieved_values[0][9])

            # Create Save button to update the entry
            save_button = ttk.Button(self.edit_part_no_frame, text="Save Changes",
                                     command=lambda: self.save_part_no(entry_id))
            save_button.pack()

    ###############        ###############        ###############        ###############
    def delete_part_no(self, selected_entry):
        if selected_entry.startswith("Select Part No"):
            return

        # Prompt confirmation box before deletion
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this partNo?",
                                        icon="warning")
        if result == "yes":
            entry_id = str(selected_entry)
            self.delete("part_no", conditions="part_no=?", values=(entry_id,))
            messagebox.showinfo("Info", "Part No deleted successfully")

            # Remove deleted entry from the dropdown menu
            self.entry_combobox['values'] = [value for value in self.entry_combobox['values'] if value != selected_entry]
            self.entry_combobox.set("Select Part No")  # Reset the selected entry

            # Clear entry fields after deletion
            for widget in self.edit_part_no_frame.winfo_children():
                widget.destroy()
    ###############        ###############        ###############        ###############
    def save_part_no(self, entry_id):
        # Extract data from EntriesFrame instances
        edited_part_no_data = self.part_no_entries.get_data()

        # Update data in the database
        col_names = list(edited_part_no_data.keys())
        col_values = list(edited_part_no_data.values()) + [entry_id]
        self.update("part_no", col_names, conditions="part_no=?", values=col_values)
        messagebox.showinfo("Info", "Part No updated successfully")
##############################################################################################################
class Entry(DB,Page):
    def __init__(self):
        menu_ls = {
            "Add Entry": self.Add_frame,
            "Entry Tracker": self.View_frame,
            "Main Inventory": self.Main_Inventory_frame,
        }
        self.create_new_page("Entry", menu_ls)

    ###############        ###############        ###############        ###############
    def Add_frame(self):
        body_frame = self.create_new_body()
        entries = (
            ("part_no", "menu", (0, 0, 3), self.get_part_no_list()),
            ("quantity", "entry", (1, 0, 1), None),
            ("date_code", "entry", (2, 0, 1), None),
            ("remarks", "entry", (3, 0, 1), None),
            ("additional_info", "entry", (4, 0, 1), None),
        )
        self.manufacturing_entries = EntriesFrame(body_frame, entries) ; self.manufacturing_entries.pack()
        self.create_footer(self.confirm_btn)

    ###############        ###############        ###############        ###############
    def get_part_no_list(self):
        # Retrieve and format purchase orders from your data source
        entries = self.select("part_no", ["part_no", "stn_qty", "uom", "cavity"], "1=1 ORDER BY part_no")
        purchase_names = [f"{entry[0].strip()} Info: ({entry[1]}/{entry[2]}/{entry[3]})" for entry in
                          entries]
        return purchase_names
    ##############################################################################################################
    def View_frame(self):
        body_frame = self.create_new_body()

        # Create an Entry widget and Search button for filtering
        filter_label = ctk.CTkLabel(body_frame, text="Part No:")
        filter_label.pack()

        filter_entry = ctk.CTkEntry(body_frame)
        filter_entry.pack()

        search_button = ctk.CTkButton(body_frame, text="Search",
                                      command=lambda: self.filter_table(table, filter_entry.get()))
        search_button.pack()

        # Create a Treeview widget to display the data
        columns = ("id", "part_no", "quantity", "date_code", "remarks", "additional_info", "time_added")

        # Create a horizontal scrollbar for the custom view
        x_sroller = ctk.CTkScrollbar(master=body_frame, orientation='horizontal')
        x_sroller.pack(side='bottom')

        table = ttk.Treeview(body_frame, columns=columns, show='headings',xscrollcommand=x_sroller.set )

        style = ttk.Style()

        style.theme_use("default")

        # Configure the Treeview style
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="black",  # Change the foreground color to make text visible
                        rowheight=25,
                        fieldbackground="#ffffff",
                        bordercolor="#000000",
                        borderwidth=1,  # Set border width to 1
                        padding=5)  # Add padding around cell content

        style.map('Treeview', background=[('selected', '#22559b')])

        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat")

        style.map("Treeview.Heading",
                  background=[('active', '#3484F0')])

        # Set column headings and widths
        column_widths = [10, 100, 100, 100, 100, 100, 100]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        # Retrieve data from the database and populate the table
        data = self.select("manufacturing", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)
    ##############################################################################################################
    def filter_table(self, table, keyword):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = ("id", "part_no", "quantity", "date_code", "remarks", "additional_info", "time_added")
        data = self.select("manufacturing", columns, "part_no LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)
    ##############################################################################################################
    def confirm_btn(self):
        # Extract data from EntriesFrame instances
        manufacturing_data = self.manufacturing_entries.get_data()

        # Retrieve data
        data = list(manufacturing_data.values())
        data[0] = data[0].split(" Info:")[0].strip()
        col_name = ("part_no", "quantity", "date_code", "remarks", "additional_info", "time_added")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.append(current_datetime)
        self.insert("manufacturing", col_name, data)
        part_info = self.select("part_no", ["stn_qty", "uom", "cavity"], "part_no=?", (data[0],))
        total_quantity = int(data[1])
        if part_info[0][1] == "PCS":
            total_quantity *= int(part_info[0][2])
        total_filled_cartons = total_quantity // int(part_info[0][0])
        total_sealed_quantity = total_quantity % int(part_info[0][0])
        main_inventory_data =  self.select("main_inventory", ["carton_quantity", "sealed_quantity", "total_stock"], "part_no=?", (data[0],))
        total_filled_cartons += int(main_inventory_data[0][0])
        total_sealed_quantity += int(main_inventory_data[0][1])
        total_quantity += int(main_inventory_data[0][2])
        while total_sealed_quantity >= int(part_info[0][0]):
            total_sealed_quantity -= int(part_info[0][0])
            total_filled_cartons += 1
        self.update("main_inventory", ["carton_quantity", "sealed_quantity", "total_stock"], "part_no=?", (total_filled_cartons,total_sealed_quantity,total_quantity,data[0]))
        messagebox.showinfo("Info", "The process was successful!")
    ##############################################################################################################
    def Main_Inventory_frame(self):
        body_frame = self.create_new_body()

        # Create an Entry widget and Search button for filtering
        filter_label = ctk.CTkLabel(body_frame, text="Part No:")
        filter_label.pack()

        filter_entry = ctk.CTkEntry(body_frame)
        filter_entry.pack()

        search_button = ctk.CTkButton(body_frame, text="Search",
                                      command=lambda: self.filter_main_inventory_table(table, filter_entry.get()))
        search_button.pack()

        # Create a Treeview widget to display the data
        columns = ("id", "part_no", "carton_quantity", "sealed_quantity", "stn_qty", "total_stock")

        # Create a horizontal scrollbar for the custom view
        x_sroller = ctk.CTkScrollbar(master=body_frame, orientation='horizontal')
        x_sroller.pack(side='bottom')

        table = ttk.Treeview(body_frame, columns=columns, show='headings',xscrollcommand=x_sroller.set )

        style = ttk.Style()

        style.theme_use("default")

        # Configure the Treeview style
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="black",  # Change the foreground color to make text visible
                        rowheight=25,
                        fieldbackground="#ffffff",
                        bordercolor="#000000",
                        borderwidth=1,  # Set border width to 1
                        padding=5)  # Add padding around cell content

        style.map('Treeview', background=[('selected', '#22559b')])

        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat")

        style.map("Treeview.Heading",
                  background=[('active', '#3484F0')])

        # Set column headings and widths
        column_widths = [10, 75, 75, 75, 75, 75]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        # Retrieve data from the database and populate the table
        data = self.select("main_inventory", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)
    ##############################################################################################################
    def filter_main_inventory_table(self, table, keyword):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = ("id", "part_no", "carton_quantity", "sealed_quantity", "stn_qty", "total_stock")
        data = self.select("main_inventory", columns, "part_no LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)
##############################################################################################################

    # db.insert("purchase_requisition", ("item_description", "quantity", "credit_limit"), ("john", "john@example.com", "2000"), )
class ProductionEntry(DB,Page):
    def __init__(self):
        menu_ls = {
            "Add": self.Add_frame,
            "View": self.View_frame,
            "Edit/Delete": self.edit_frame,
        }
        self.create_new_page("Production Entry", menu_ls)
    ###############        ###############        ###############        ###############
    def Add_frame(self):
        body_frame = self.create_new_body()
        entries = (
            ("traveller_no", "entry", (0, 0, 3), None),
            ("part_no", "entry", (1, 0, 3), None),
            ("department", "entry", (2, 0, 3), None),
            ("quantity_received", "entry", (3, 0, 3), None),
            ("quantity_output", "entry", (4, 0, 3), None),
            ("quantity_rejected", "entry", (5, 0, 3), None),
            ("remarks", "entry", (6, 0, 3), None),
        )
        self.production_entries = EntriesFrame(body_frame, entries) ; self.production_entries.pack()
        self.create_footer(self.confirm_btn)
    ###############        ###############        ###############        ###############
    def confirm_btn(self):
        # Extract data from EntriesFrame instances
        production_data = self.production_entries.get_data()

        # Retrieve data
        data = list(production_data.values())
        col_name = ("traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected", "remarks", "time_added")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.append(current_datetime)
        self.insert("production_entry", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")
    ###############        ###############        ###############        ###############
    def View_frame(self):
        body_frame = self.create_new_body()

        # Create an Entry widget and Search button for filtering
        filter_label = ctk.CTkLabel(body_frame, text="Traveller No:")
        filter_label.pack()

        filter_entry = ctk.CTkEntry(body_frame)
        filter_entry.pack()

        search_button = ctk.CTkButton(body_frame, text="Search",
                                      command=lambda: self.filter_table(table, filter_entry.get()))
        search_button.pack()

        # Create a Treeview widget to display the data
        columns = ("id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected", "remarks", "time_added")

        # Create a horizontal scrollbar for the custom view
        x_sroller = ctk.CTkScrollbar(master=body_frame, orientation='horizontal')
        x_sroller.pack(side='bottom')

        table = ttk.Treeview(body_frame, columns=columns, show='headings',xscrollcommand=x_sroller.set )

        style = ttk.Style()

        style.theme_use("default")

        # Configure the Treeview style
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="black",  # Change the foreground color to make text visible
                        rowheight=25,
                        fieldbackground="#ffffff",
                        bordercolor="#000000",
                        borderwidth=1,  # Set border width to 1
                        padding=5)  # Add padding around cell content

        style.map('Treeview', background=[('selected', '#22559b')])

        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat")

        style.map("Treeview.Heading",
                  background=[('active', '#3484F0')])

        # Set column headings and widths
        column_widths = [10, 150, 150, 100, 100, 100, 100, 200, 150]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        # Retrieve data from the database and populate the table
        data = self.select("production_entry", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)
    ###############        ###############        ###############        ###############
    def filter_table(self, table, keyword):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = ("id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected", "remarks", "time_added")
        data = self.select("production_entry", columns, "part_no LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)

    ###############        ###############        ###############        ###############
    def edit_frame(self):
        body_frame = self.create_new_body()

        # Create a LabelFrame for selection and editing
        selection_frame = ttk.LabelFrame(body_frame, text="Select Traveller Entry to Edit")
        selection_frame.pack(padx=10, pady=10, fill="both", expand=True)

        entries = self.select("production_entry", ["id","traveller_no","part_no","department","quantity_received","quantity_output","quantity_rejected"])
        selected_entry = tk.StringVar()
        selected_entry.set("Select an entry")

        # Strip leading/trailing spaces from entry names
        entry_options = [f"{entry[0]}/{entry[1]}/{entry[2][:10] + '...' if len(entry[2]) > 10 else entry[2]}/{entry[3]}/{entry[4]}/{entry[5]}/{entry[6]}" for entry in entries]

        # Create the Combobox
        self.entry_combobox = ttk.Combobox(selection_frame, values=entry_options, state="readonly", width=75)
        self.entry_combobox.pack(padx=10, pady=10)

        # Create a Button to trigger editing
        edit_button = ttk.Button(selection_frame, text="Edit",
                                 command=lambda: self.edit_traveller_entry(self.entry_combobox.get()))
        edit_button.pack(padx=10, pady=10)

        # Create a Button to trigger deletion
        delete_button = ttk.Button(selection_frame, text="Delete",
                                   command=lambda: self.delete_traveller_entry(self.entry_combobox.get()))
        delete_button.pack(padx=10, pady=10)

        # Create a frame to display entry fields for editing
        self.edit_traveller_frame = ttk.LabelFrame(body_frame, text="Edit Traveller")
        self.edit_traveller_frame.pack(padx=10, pady=10, fill="both", expand=True)

    ###############        ###############        ###############        ###############
    def edit_traveller_entry(self, selected_entry):
        if selected_entry.startswith("Select Traveller Entry"):
            return

        # Clear previous entry fields
        for widget in self.edit_traveller_frame.winfo_children():
            widget.destroy()

        entry_id = str(selected_entry).split('/')[0]
        retrieved_values = self.select("production_entry", ["*"], "id=?", (entry_id,))
        # Retrieve data for the selected entry
        entry_data = [
            ("traveller_no", "entry", (0, 0, 3), None),
            ("part_no", "entry", (1, 0, 3), None),
            ("department", "entry", (2, 0, 3), None),
            ("quantity_received", "entry", (3, 0, 3), None),
            ("quantity_output", "entry", (4, 0, 3), None),
            ("quantity_rejected", "entry", (5, 0, 3), None),
            ("remarks", "entry", (6, 0, 3), None),
        ]
        self.production_entries = EntriesFrame(self.edit_traveller_frame, entry_data)
        self.production_entries.pack()

        if entry_data:
            # Create EntryFrame for editing
            self.production_entries.change_value("traveller_no", retrieved_values[0][1])
            self.production_entries.change_value("part_no", retrieved_values[0][2])
            self.production_entries.change_value("department", retrieved_values[0][3])
            self.production_entries.change_value("quantity_received", retrieved_values[0][4])
            self.production_entries.change_value("quantity_output", retrieved_values[0][5])
            self.production_entries.change_value("quantity_rejected", retrieved_values[0][6])
            self.production_entries.change_value("remarks", retrieved_values[0][7])

            # Create Save button to update the entry
            save_button = ttk.Button(self.edit_traveller_frame, text="Save Changes",
                                     command=lambda: self.save_traveller_entry(entry_id))
            save_button.pack()

    ###############        ###############        ###############        ###############
    def delete_traveller_entry(self, selected_entry):
        if selected_entry.startswith("Select Traveller Entry"):
            return

        # Prompt confirmation box before deletion
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this traveller entry?",
                                        icon="warning")
        if result == "yes":
            entry_id = str(selected_entry).split('/')[0]
            self.delete("production_entry", conditions="id=?", values=(entry_id,))
            messagebox.showinfo("Info", "Traveller Entry deleted successfully")

            # Remove deleted entry from the dropdown menu
            self.entry_combobox['values'] = [value for value in self.entry_combobox['values'] if
                                             value != selected_entry]
            self.entry_combobox.set("Select Traveller Entry")  # Reset the selected entry

            # Clear entry fields after deletion
            for widget in self.edit_traveller_frame.winfo_children():
                widget.destroy()

    ###############        ###############        ###############        ###############
    def save_traveller_entry(self, entry_id):
        # Extract data from EntriesFrame instances
        edited_production_data = self.production_entries.get_data()

        # Update data in the database
        col_names = list(edited_production_data.keys())
        col_values = list(edited_production_data.values()) + [entry_id]
        self.update("production_entry", col_names, conditions="id=?", values=col_values)
        messagebox.showinfo("Info", "Traveller Entry updated successfully")


