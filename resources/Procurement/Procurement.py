from config import *
from ..UI import Page, LeftMenu , EntriesFrame
from ..Logics import DB

class Procurement(Page):
    def __init__(self):
        self.create_new_page("Procurement")
        left_menu = LeftMenu()
        # Do not have more than 6 menus
        left_menu_ls = {
            "Purchase Requisition"              : PurchaseRequisition,
            "Supplier Management"               : SupplierManagement,
            "Supplier Quotation"                : SupplierQuotation,
            "Invoice Matching"                  : InvoiceMatching,
        }
        left_menu.update_menu(left_menu_ls)
##############################################################################################################
class PurchaseRequisition(Page):
    def __init__(self):
        menu_ls = {
            "Add": self.Add_frame,
            "View": self.View_frame,
            "Edit/Delete": self.edit_frame,
        }
        self.create_new_page("Purchase Requisition", menu_ls)

    ###############        ###############        ###############        ###############
    def Add_frame(self):
        body_frame = self.create_new_body()
        entries = (
            ("item_description", "entry", (0, 0, 3), None),
            ("quantity", "entry", (1, 0, 1), None),
            ("unit_packing", "entry", (1, 1, 1), None),
            ("balance_stock", "entry", (2, 0, 1), None),
            ("needed_by", "date", (3, 0, 1), None),
            ("last_purchase_date", "date", (3, 1, 1), None),
        )
        self.purchase_entries = EntriesFrame(body_frame, entries) ; self.purchase_entries.pack()
        entries = (
            ("source_a_cost_price", "entry", (0, 0, 1), None),
            ("source_b_cost_price", "entry", (0, 1, 1), None),
            ("source_c_cost_price", "entry", (0, 2, 1), None),
        )
        self.source_entries = EntriesFrame(body_frame,  entries) ; self.source_entries.pack()
        entries = (
            ("remarks", "entry", (0, 0, 1), None),
        )
        self.remark_entries = EntriesFrame(body_frame, entries) ; self.remark_entries.pack()
        self.create_footer(self.Add_btn)

    ###############        ###############        ###############        ###############
    def Add_btn(self):
        # Extract data from EntriesFrame instances
        purchase_data = self.purchase_entries.get_data()
        source_data = self.source_entries.get_data()
        remark_data = self.remark_entries.get_data()

        # Retrieve data
        data = list(purchase_data.values()) + list(source_data.values()) + list(remark_data.values())
        col_name = ("item_description","quantity","unit_packing","needed_by","balance_stock","last_purchase_date","source_a_cost_price",
                    "source_b_cost_price","source_c_cost_price","remarks","time_added")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.append(current_datetime)
        DB.insert("purchase_requisition", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")
    ###############        ###############        ###############        ###############
    def View_frame(self):
        body_frame = self.create_new_body()

        # Create an Entry widget and Search button for filtering
        filter_label = ctk.CTkLabel(body_frame, text="Item Description:")
        filter_label.pack()

        filter_entry = ctk.CTkEntry(body_frame)
        filter_entry.pack()

        search_button = ctk.CTkButton(body_frame, text="Search",
                                      command=lambda: self.filter_table(table, filter_entry.get()))
        search_button.pack()
        # Create a Treeview widget to display the data
        columns = ("id", "item_description", "quantity", "unit_packing", "needed_by", "balance_stock",
                   "last_purchase_date", "source_a_cost_price", "source_b_cost_price", "source_c_cost_price",
                   "remarks","time_added")

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
        column_widths = [10, 100, 50, 75, 75, 80, 125, 125, 125, 125, 150, 100]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)


        data = DB.select("purchase_requisition", columns)
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
        columns = (
            "id", "item_description", "quantity", "unit_packing", "needed_by", "balance_stock",
            "last_purchase_date", "source_a_cost_price", "source_b_cost_price", "source_c_cost_price",
            "remarks","time_added"
        )
        data = DB.select("purchase_requisition", columns, "item_description LIKE ?",("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)

    ###############        ###############        ###############        ###############
    def edit_frame(self):
        body_frame = self.create_new_body()

        # Create a LabelFrame for selection and editing
        selection_frame = ttk.LabelFrame(body_frame, text="Select Entry to Edit")
        selection_frame.pack(padx=10, pady=10, fill="both", expand=True)

        entries = DB.select("purchase_requisition", ["id", "item_description"])
        selected_entry = tk.StringVar()
        selected_entry.set("Select an entry")

        # Strip leading/trailing spaces from entry names
        entry_options = [f"{entry[1].strip()} (ID: {entry[0]})" for entry in entries]

        # Create the Combobox
        self.entry_combobox = ttk.Combobox(selection_frame, values=entry_options, state="readonly", width=75)
        self.entry_combobox.pack(padx=10, pady=10)

        # Create a Button to trigger editing
        edit_button = ttk.Button(selection_frame, text="Edit Entry",
                                 command=lambda: self.edit_selected_entry(self.entry_combobox.get()))
        edit_button.pack(padx=10, pady=10)

        # Create a Button to trigger deletion
        delete_button = ttk.Button(selection_frame, text="Delete Entry",
                                   command=lambda: self.delete_selected_entry(self.entry_combobox.get()))
        delete_button.pack(padx=10, pady=10)

        # Create a frame to display entry fields for editing
        self.edit_entries_frame = ttk.LabelFrame(body_frame, text="Edit Entry Details")
        self.edit_entries_frame.pack(padx=10, pady=10, fill="both", expand=True)

    ###############        ###############        ###############        ###############
    def edit_selected_entry(self, selected_entry):
        if selected_entry.startswith("Select an entry"):
            return

        # Clear previous entry fields
        for widget in self.edit_entries_frame.winfo_children():
            widget.destroy()

        entry_id = int(selected_entry.split("(ID:")[1].split(")")[0].strip())
        retrieved_values = DB.select("purchase_requisition", ["*"], "id=?", (entry_id,))
        # Retrieve data for the selected entry
        entry_data = [
            ("item_description", "entry", (0, 0, 3), None),
            ("quantity", "entry", (1, 0, 1), None),
            ("unit_packing", "entry", (1, 1, 1), None),
            ("balance_stock", "entry", (2, 0, 1), None),
            ("needed_by", "date", (3, 0, 1), None),
            ("last_purchase_date", "date", (3, 1, 1), None),
        ]
        self.purchase_entries = EntriesFrame(self.edit_entries_frame, entry_data)
        self.purchase_entries.pack()

        entry_data = [
            ("source_a_cost_price", "entry", (0, 0, 1), None),
            ("source_b_cost_price", "entry", (0, 1, 1), None),
            ("source_c_cost_price", "entry", (0, 2, 1), None),
        ]
        self.source_entries = EntriesFrame(self.edit_entries_frame, entry_data)
        self.source_entries.pack()

        entry_data = [
            ("remarks", "entry", (0, 0, 1), None),
        ]
        self.remark_entries = EntriesFrame(self.edit_entries_frame,  entry_data)
        self.remark_entries.pack()
        if entry_data:
            # Create EntryFrame for editing

            self.purchase_entries.change_value("item_description", retrieved_values[0][1])
            self.purchase_entries.change_value("quantity", retrieved_values[0][2])
            self.purchase_entries.change_value("unit_packing", retrieved_values[0][3])
            self.purchase_entries.change_value("needed_by", retrieved_values[0][4])
            self.purchase_entries.change_value("balance_stock", retrieved_values[0][5])
            self.purchase_entries.change_value("last_purchase_date", retrieved_values[0][6])
            self.source_entries.change_value("source_a_cost_price", retrieved_values[0][7])
            self.source_entries.change_value("source_b_cost_price", retrieved_values[0][8])
            self.source_entries.change_value("source_c_cost_price", retrieved_values[0][9])
            self.remark_entries.change_value("remarks", retrieved_values[0][10])


            # Create Save button to update the entry
            save_button = ttk.Button(self.edit_entries_frame, text="Save Changes",
                                     command=lambda: self.save_edited_entry(entry_id))
            save_button.pack(padx=10, pady=10)

    ###############        ###############        ###############        ###############
    def delete_selected_entry(self, selected_entry):
        if selected_entry.startswith("Select an entry"):
            return

        # Prompt confirmation box before deletion
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this entry?",
                                        icon="warning")
        if result == "yes":
            entry_id = int(selected_entry.split("(ID:")[1].split(")")[0].strip())
            DB.delete("purchase_requisition", conditions="id=?", values=(entry_id,))
            messagebox.showinfo("Info", "Entry deleted successfully")

            # Remove deleted entry from the dropdown menu
            self.entry_combobox['values'] = [value for value in self.entry_combobox['values'] if value != selected_entry]
            self.entry_combobox.set("Select an entry")  # Reset the selected entry

            # Clear entry fields after deletion
            for widget in self.edit_entries_frame.winfo_children():
                widget.destroy()
    ###############        ###############        ###############        ###############
    def save_edited_entry(self, entry_id):
        # Extract data from EntriesFrame instances
        edited_purchase_data = self.purchase_entries.get_data()
        edited_source_data = self.source_entries.get_data()
        edited_remark_data = self.remark_entries.get_data()

        # Update data in the database
        col_names = list(edited_purchase_data.keys()) + list(edited_source_data.keys()) + list(edited_remark_data.keys())
        col_values = list(edited_purchase_data.values()) + list(edited_source_data.values()) + list(
            edited_remark_data.values()) + [entry_id]
        DB.update("purchase_requisition", col_names, conditions="id=?", values=col_values)
        messagebox.showinfo("Info", "Entry updated successfully")

    ##############################################################################################################
    #db.insert("purchase_requisition", ("item_description", "quantity", "credit_limit"), ("john", "john@example.com", "2000"), )
##############################################################################################################
class SupplierManagement(Page):
    def __init__(self):
        menu_ls = {
            "Add": self.Add_frame,
            "View": self.View_frame,
            "Edit/Delete": self.edit_frame,
            "Performance Evaluation": self.Evaluation_frame,
            "View Evaluation": self.View_Evaluation_frame,
            "Edit/Delete Evaluation": self.Edit_Evaluation_frame,
        }
        self.create_new_page("Supplier Management", menu_ls)

    ###############        ###############        ###############        ###############
    def Add_frame(self):
        body_frame = self.create_new_body()
        entries = (
            ("supplier_name", "entry", (0, 0, 1), None),
            ("email_address", "entry", (1, 0, 1), None),
            ("contact_number", "entry", (2, 0, 1), None),
            ("address_details", "entry", (3, 0, 1), None),
            ("company_address", "entry", (4, 0, 1), None),
        )
        self.contact_info_entries = EntriesFrame(body_frame, entries) ; self.contact_info_entries.pack()
        self.create_footer(self.Add_btn)

    ###############        ###############        ###############        ###############
    def Add_btn(self):
        # Extract data from EntriesFrame instances
        contact_data = self.contact_info_entries.get_data()

        # Retrieve data
        data = list(contact_data.values())
        col_name = ("supplier_name","email_address","contact_number","address_details","company_address","time_added")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.append(current_datetime)
        DB.insert("supplier_management", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")
    ###############        ###############        ###############        ###############

    def View_frame(self):
        body_frame = self.create_new_body()

        # Create an Entry widget and Search button for filtering
        filter_label = ctk.CTkLabel(body_frame, text="Supplier:")
        filter_label.pack()

        filter_entry = ctk.CTkEntry(body_frame)
        filter_entry.pack()

        search_button = ctk.CTkButton(body_frame, text="Search",
                                      command=lambda: self.filter_table(table, filter_entry.get()))
        search_button.pack()
        # Create a Treeview widget to display the data
        columns = ("id", "supplier_name", "email_address", "contact_number", "address_details","company_address","time_added")

        # Create a horizontal scrollbar for the custom view
        x_sroller = ctk.CTkScrollbar(master=body_frame, orientation='horizontal')
        x_sroller.pack(side='bottom')

        table = ttk.Treeview(body_frame, columns=columns, show='headings', xscrollcommand=x_sroller.set)

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
        column_widths = [10, 100, 100, 100, 200, 200, 100]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        data = DB.select("supplier_management", columns)
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
        columns = ("id", "supplier_name", "email_address", "contact_number", "address_details","company_address","time_added")

        data = DB.select("supplier_management", columns, "supplier_name LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)

    ###############        ###############        ###############        ###############
    def edit_frame(self):
        body_frame = self.create_new_body()

        # Create a LabelFrame for selection and editing
        selection_frame = ttk.LabelFrame(body_frame, text="Select Entry to Edit")
        selection_frame.pack(padx=10, pady=10, fill="both", expand=True)

        entries = DB.select("supplier_management", ["id", "supplier_name"])
        selected_entry = tk.StringVar()
        selected_entry.set("Select an entry")

        # Strip leading/trailing spaces from entry names
        entry_options = [f"{entry[1].strip()} (ID: {entry[0]})" for entry in entries]

        # Create the Combobox
        self.entry_combobox = ttk.Combobox(selection_frame, values=entry_options, state="readonly", width=75)
        self.entry_combobox.pack(padx=10, pady=10)

        # Create a Button to trigger editing
        edit_button = ttk.Button(selection_frame, text="Edit Entry",
                                 command=lambda: self.edit_selected_entry(self.entry_combobox.get()))
        edit_button.pack(padx=10, pady=10)

        # Create a Button to trigger deletion
        delete_button = ttk.Button(selection_frame, text="Delete Entry",
                                   command=lambda: self.delete_selected_entry(self.entry_combobox.get()))
        delete_button.pack(padx=10, pady=10)

        # Create a frame to display entry fields for editing
        self.edit_entries_frame = ttk.LabelFrame(body_frame, text="Edit Entry Details")
        self.edit_entries_frame.pack(padx=10, pady=10, fill="both", expand=True)

    ###############        ###############        ###############        ###############
    def edit_selected_entry(self, selected_entry):
        if selected_entry.startswith("Select an entry"):
            return

        # Clear previous entry fields
        for widget in self.edit_entries_frame.winfo_children():
            widget.destroy()

        entry_id = int(selected_entry.split("(ID:")[1].split(")")[0].strip())
        retrieved_values = DB.select("supplier_management", ["*"], "id=?", (entry_id,))
        # Retrieve data for the selected entry
        entry_data = [
            ("supplier_name", "entry", (0, 0, 1), None),
            ("email_address", "entry", (1, 0, 1), None),
            ("contact_number", "entry", (2, 0, 1), None),
            ("address_details", "entry", (3, 0, 1), None),
            ("company_address", "entry", (4, 0, 1), None)
        ]
        self.contact_info_entries = EntriesFrame(self.edit_entries_frame, entry_data)
        self.contact_info_entries.pack()

        if entry_data:
            # Create EntryFrame for editing

            self.contact_info_entries.change_value("supplier_name", retrieved_values[0][1])
            self.contact_info_entries.change_value("email_address", retrieved_values[0][2])
            self.contact_info_entries.change_value("contact_number", retrieved_values[0][3])
            self.contact_info_entries.change_value("address_details", retrieved_values[0][4])
            self.contact_info_entries.change_value("company_address", retrieved_values[0][5])

            # Create Save button to update the entry
            save_button = ttk.Button(self.edit_entries_frame, text="Save Changes",
                                     command=lambda: self.save_edited_entry(entry_id))
            save_button.pack(padx=10, pady=10)

    ###############        ###############        ###############        ###############
    def delete_selected_entry(self, selected_entry):
        if selected_entry.startswith("Select an entry"):
            return

        # Prompt confirmation box before deletion
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this entry?",
                                        icon="warning")
        if result == "yes":
            entry_id = int(selected_entry.split("(ID:")[1].split(")")[0].strip())
            DB.delete("supplier_management", conditions="id=?", values=(entry_id,))
            messagebox.showinfo("Info", "Entry deleted successfully")

            # Remove deleted entry from the dropdown menu
            self.entry_combobox['values'] = [value for value in self.entry_combobox['values'] if
                                             value != selected_entry]
            self.entry_combobox.set("Select an entry")  # Reset the selected entry

            # Clear entry fields after deletion
            for widget in self.edit_entries_frame.winfo_children():
                widget.destroy()

    ###############        ###############        ###############        ###############
    def save_edited_entry(self, entry_id):
        # Extract data from EntriesFrame instances
        edited_contact_info_data = self.contact_info_entries.get_data()

        # Update data in the database
        col_names = list(edited_contact_info_data.keys())
        col_values = list(edited_contact_info_data.values()) + [entry_id]
        DB.update("supplier_management", col_names, conditions="id=?", values=col_values)
        messagebox.showinfo("Info", "Entry updated successfully")
    ##############################################################################################################
    def Evaluation_frame(self):
        body_frame = self.create_new_body()

        entries = (
            ("supplier_name", "menu", (0, 0, 3), self.get_supplier_names()),  # Include supplier selection here
            ("delivery_time_rating", "menu", (1, 0, 1), ("1*", "2*", "3*", "4*", "5*")),
            ("quality_rating", "menu", (1, 1, 1), ("1*", "2*", "3*", "4*", "5*")),
            ("price_rating", "menu", (1, 2, 1), ("1*", "2*", "3*", "4*", "5*")),
            ("remarks", "entry", (2, 0, 3), None),
        )
        self.evaluation_entries = EntriesFrame(body_frame, entries) ;   self.evaluation_entries.pack()
        self.create_footer(self.Add_Evaluation_btn)
    ##############################################################################################################
    def get_supplier_names(self):
        # Retrieve and format supplier names from your data source
        entries = DB.select("supplier_management", ["supplier_name"])
        supplier_names = [f"{entry[0].strip()}" for entry in entries]
        return supplier_names
    ###############        ###############        ###############        ###############
    def Add_Evaluation_btn(self):
        # Extract data from EntriesFrame instances
        evaluation_data = self.evaluation_entries.get_data()

        # Retrieve data
        data = list(evaluation_data.values())

        # Add the current date and time to the data
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.append(current_datetime)

        col_name = ("supplier_name","delivery_time_rating","quality_rating","price_rating","remarks", "datetime")
        DB.insert("supplier_evaluation", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")
    ###############        ###############        ###############        ###############
    def View_Evaluation_frame(self):
        body_frame = self.create_new_body()

        # Create an Entry widget and Search button for filtering
        filter_label = ctk.CTkLabel(body_frame, text="Supplier:")
        filter_label.pack()

        filter_entry = ctk.CTkEntry(body_frame)
        filter_entry.pack()

        search_button = ctk.CTkButton(body_frame, text="Search",
                                      command=lambda: self.filter_evaluation_table(table, filter_entry.get()))
        search_button.pack()
        # Create a Treeview widget to display the data
        columns = ("id", "supplier_name", "delivery_time_rating", "quality_rating", "price_rating", "remarks", "datetime")

        # Create a horizontal scrollbar for the custom view
        x_sroller = ctk.CTkScrollbar(master=body_frame, orientation='horizontal')
        x_sroller.pack(side='bottom')

        table = ttk.Treeview(body_frame, columns=columns, show='headings', xscrollcommand=x_sroller.set)

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
        column_widths = [10, 100, 75, 50, 50, 200, 50]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        data = DB.select("supplier_evaluation", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)
    ###############        ###############        ###############        ###############
    def filter_evaluation_table(self, table, keyword):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = ("id", "supplier_name","delivery_time_rating","quality_rating","price_rating","remarks", "datetime")

        data = DB.select("supplier_evaluation", columns, "supplier_name LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)

    ###############        ###############        ###############        ###############
    def Edit_Evaluation_frame(self):
        body_frame = self.create_new_body()

        # Create a LabelFrame for selection and editing
        selection_frame = ttk.LabelFrame(body_frame, text="Select Evaluation to Edit")
        selection_frame.pack(padx=10, pady=10, fill="both", expand=True)

        entries = DB.select("supplier_evaluation", ["id", "supplier_name"])
        selected_entry = tk.StringVar()
        selected_entry.set("Select an entry")

        # Strip leading/trailing spaces from entry names
        entry_options = [f"{entry[1].strip()} (ID: {entry[0]})" for entry in entries]

        # Create the Combobox
        self.entry_combobox = ttk.Combobox(selection_frame, values=entry_options, state="readonly", width=75)
        self.entry_combobox.pack(padx=10, pady=10)

        # Create a Button to trigger editing
        edit_button = ttk.Button(selection_frame, text="Edit Evaluation",
                                 command=lambda: self.edit_selected_evaluation(self.entry_combobox.get()))
        edit_button.pack(padx=10, pady=10)

        # Create a Button to trigger deletion
        delete_button = ttk.Button(selection_frame, text="Delete Evaluation",
                                   command=lambda: self.delete_selected_evaluation(self.entry_combobox.get()))
        delete_button.pack(padx=10, pady=10)

        # Create a frame to display entry fields for editing
        self.edit_entries_frame = ttk.LabelFrame(body_frame, text="Edit Evaluation Details")
        self.edit_entries_frame.pack(padx=10, pady=10, fill="both", expand=True)

    ###############        ###############        ###############        ###############
    def edit_selected_evaluation(self, selected_entry):
        if selected_entry.startswith("Select an entry"):
            return

        # Clear previous entry fields
        for widget in self.edit_entries_frame.winfo_children():
            widget.destroy()

        entry_id = int(selected_entry.split("(ID:")[1].split(")")[0].strip())
        retrieved_values = DB.select("supplier_evaluation", ["*"], "id=?", (entry_id,))
        # Retrieve data for the selected entry
        entry_data = [
            ("supplier_name", "entry", (0, 0, 3), None),
            ("delivery_time_rating", "menu", (1, 0, 1), ("1*", "2*", "3*", "4*", "5*")),
            ("quality_rating", "menu", (1, 1, 1), ("1*", "2*", "3*", "4*", "5*")),
            ("price_rating", "menu", (1, 2, 1), ("1*", "2*", "3*", "4*", "5*")),
            ("remarks", "entry", (2, 0, 3), None),
        ]
        self.evaluation_entries = EntriesFrame(self.edit_entries_frame, entry_data)
        self.evaluation_entries.pack()

        if entry_data:
            # Create EntryFrame for editing
            self.evaluation_entries.change_and_disable("supplier_name", retrieved_values[0][1])
            self.evaluation_entries.change_menu_value("delivery_time_rating", retrieved_values[0][2])
            self.evaluation_entries.change_menu_value("quality_rating", retrieved_values[0][3])
            self.evaluation_entries.change_menu_value("price_rating", retrieved_values[0][4])
            self.evaluation_entries.change_value("remarks", retrieved_values[0][5])

            # Create Save button to update the entry
            save_button = ttk.Button(self.edit_entries_frame, text="Save Changes",
                                     command=lambda: self.save_edited_evaluation(entry_id))
            save_button.pack(padx=10, pady=10)

    ###############        ###############        ###############        ###############
    def delete_selected_evaluation(self, selected_entry):
        if selected_entry.startswith("Select an evaluation"):
            return

        # Prompt confirmation box before deletion
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this evaluation?",
                                        icon="warning")
        if result == "yes":
            entry_id = int(selected_entry.split("(ID:")[1].split(")")[0].strip())
            DB.delete("supplier_evaluation", conditions="id=?", values=(entry_id,))
            messagebox.showinfo("Info", "Evaluation deleted successfully")

            # Remove deleted entry from the dropdown menu
            self.entry_combobox['values'] = [value for value in self.entry_combobox['values'] if
                                             value != selected_entry]
            self.entry_combobox.set("Select an evaluation")  # Reset the selected entry

            # Clear entry fields after deletion
            for widget in self.edit_entries_frame.winfo_children():
                widget.destroy()

    ###############        ###############        ###############        ###############
    def save_edited_evaluation(self, entry_id):
        # Extract data from EntriesFrame instances
        edited_evaluation_data = self.evaluation_entries.get_data()

        # Update data in the database
        col_names = list(edited_evaluation_data.keys())
        col_values = list(edited_evaluation_data.values()) + [entry_id]
        DB.update("supplier_evaluation", col_names, conditions="id=?", values=col_values)
        messagebox.showinfo("Info", "Evaluation updated successfully")
##############################################################################################################
class SupplierQuotation(Page):
    def __init__(self):
        menu_ls = {
            "Creation": self.Creation_frame,
            "View Creation": self.View_frame,
            "Edit/Delete Creation": self.edit_frame,
            "Approval": self.Approval_frame,
            "View Approval": self.View_Approval_frame,
            "Edit/Delete Approval": self.Edit_Approval_frame,
            "Order Tracking": self.Order_frame,
            "View Orders": self.View_Order_frame,
            "Edit/Delete Orders": self.Edit_Order_frame,
            "Goods Receipt": self.Goods_frame,
            "View Goods Receipts": self.View_Goods_frame,
            "Edit/Delete Goods Receipts": self.Edit_Goods_frame,
        }
        self.create_new_page("Supplier Quotation", menu_ls)

    ###############        ###############        ###############        ###############
    def Creation_frame(self):
        body_frame = self.create_new_body()
        entries = (
            ("supplier_name", "menu", (0, 0, 3), self.get_supplier_names()),
            ("order_date", "date", (1, 0, 2), None),
            ("item_ordered", "entry", (2, 0, 2), None),
            ("quantity", "entry", (3, 0, 1), None),
            ("unit_price", "entry", (3, 1, 1), None),
            ("total_amount", "entry", (3, 2, 1), None),
            ("delivery_date", "date", (4, 0, 2), None),
            ("ship_to_address", "entry", (5, 0, 3), None),
            ("company_address", "entry", (6, 0, 3), None),
        )
        self.order_entries = EntriesFrame(body_frame, entries)
        self.order_entries.pack()
        self.create_footer(self.confirm_quotation_btn)

    ###############        ###############        ###############        ###############
    def get_supplier_names(self):
        # Retrieve and format supplier names from your data source
        entries = DB.select("supplier_management", ["supplier_name"])
        supplier_names = [f"{entry[0].strip()}" for entry in entries]
        return supplier_names
    ###############        ###############        ###############        ###############
    def confirm_quotation_btn(self):
        # Extract data from EntriesFrame instances
        order_data = self.order_entries.get_data()

        # Retrieve data
        data = list(order_data.values())
        col_name = ("supplier_name", "order_date", "item_ordered", "quantity", "unit_price", "total_amount",
                    "delivery_date", "ship_to_address", "company_address", "time_added")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.append(current_datetime)
        DB.insert("purchase_creation", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")

    ###############        ###############        ###############        ###############
    def View_frame(self):
        body_frame = self.create_new_body()

        # Create an Entry widget and Search button for filtering
        filter_label = ctk.CTkLabel(body_frame, text="Supplier Name:")
        filter_label.pack()

        filter_entry = ctk.CTkEntry(body_frame)
        filter_entry.pack()

        search_button = ctk.CTkButton(body_frame, text="Search",
                                      command=lambda: self.filter_table(table, filter_entry.get()))
        search_button.pack()

        # Create a Treeview widget to display the data
        columns = ("id", "supplier_name", "order_date", "item_ordered", "quantity", "unit_price",
                   "total_amount", "delivery_date", "ship_to_address", "company_address", "time_added")

        # Create a horizontal scrollbar for the custom view
        x_sroller = ctk.CTkScrollbar(master=body_frame, orientation='horizontal')
        x_sroller.pack(side='bottom')

        table = ttk.Treeview(body_frame, columns=columns, show='headings', xscrollcommand=x_sroller.set)

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
        column_widths = [10, 150, 100, 200, 75, 75, 100, 100, 200, 200, 100]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        data = DB.select("purchase_creation", columns)
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
        columns = ("id", "supplier_name", "order_date", "item_ordered", "quantity", "unit_price",
                   "total_amount", "delivery_date", "ship_to_address", "company_address", "time_added")
        data = DB.select("purchase_creation", columns, "supplier_name LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in supplier_name column
                table.insert("", "end", values=row)

    ###############        ###############        ###############        ###############
    def edit_frame(self):
        body_frame = self.create_new_body()

        # Create a LabelFrame for selection and editing
        selection_frame = ttk.LabelFrame(body_frame, text="Select Entry to Edit")
        selection_frame.pack(padx=10, pady=10, fill="both", expand=True)

        entries = DB.select("purchase_creation", ["id", "supplier_name"])
        selected_entry = tk.StringVar()
        selected_entry.set("Select an entry")

        # Strip leading/trailing spaces from entry names
        entry_options = [f"{entry[1].strip()} (ID: {entry[0]})" for entry in entries]

        # Create the Combobox
        self.entry_combobox = ttk.Combobox(selection_frame, values=entry_options, state="readonly", width=75)
        self.entry_combobox.pack(padx=10, pady=10)

        # Create a Button to trigger editing
        edit_button = ttk.Button(selection_frame, text="Edit Entry",
                                 command=lambda: self.edit_selected_entry(self.entry_combobox.get()))
        edit_button.pack(padx=10, pady=10)

        # Create a Button to trigger deletion
        delete_button = ttk.Button(selection_frame, text="Delete Entry",
                                   command=lambda: self.delete_selected_entry(self.entry_combobox.get()))
        delete_button.pack(padx=10, pady=10)

        # Create a frame to display entry fields for editing
        self.edit_entries_frame = ttk.LabelFrame(body_frame, text="Edit Entry Details")
        self.edit_entries_frame.pack(padx=10, pady=10, fill="both", expand=True)

    ###############        ###############        ###############        ###############
    def edit_selected_entry(self, selected_entry):
        if selected_entry.startswith("Select an entry"):
            return

        # Clear previous entry fields
        for widget in self.edit_entries_frame.winfo_children():
            widget.destroy()

        entry_id = int(selected_entry.split("(ID:")[1].split(")")[0].strip())
        retrieved_values = DB.select("purchase_creation", ["*"], "id=?", (entry_id,))
        # Retrieve data for the selected entry
        entry_data = [
            ("supplier_name", "entry", (0, 0, 3), None),
            ("order_date", "date", (1, 0, 2), None),
            ("item_ordered", "entry", (2, 0, 2), None),
            ("quantity", "entry", (3, 0, 1), None),
            ("unit_price", "entry", (3, 1, 1), None),
            ("total_amount", "entry", (3, 2, 1), None),
            ("delivery_date", "date", (4, 0, 2), None),
            ("ship_to_address", "entry", (5, 0, 3), None),
            ("company_address", "entry", (6, 0, 3), None),
        ]
        self.order_entries = EntriesFrame(self.edit_entries_frame, entry_data)
        self.order_entries.pack()

        if entry_data:
            # Create EntryFrame for editing
            self.order_entries.change_value("supplier_name", retrieved_values[0][1])
            self.order_entries.change_value("order_date", retrieved_values[0][2])
            self.order_entries.change_value("item_ordered", retrieved_values[0][3])
            self.order_entries.change_value("quantity", retrieved_values[0][4])
            self.order_entries.change_value("unit_price", retrieved_values[0][5])
            self.order_entries.change_value("total_amount", retrieved_values[0][6])
            self.order_entries.change_value("delivery_date", retrieved_values[0][7])
            self.order_entries.change_value("ship_to_address", retrieved_values[0][8])
            self.order_entries.change_value("company_address", retrieved_values[0][9])

            # Create Save button to update the entry
            save_button = ttk.Button(self.edit_entries_frame, text="Save Changes",
                                     command=lambda: self.save_edited_entry(entry_id))
            save_button.pack(padx=10, pady=10)

    ###############        ###############        ###############        ###############
    def delete_selected_entry(self, selected_entry):
        if selected_entry.startswith("Select an entry"):
            return

        # Prompt confirmation box before deletion
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this entry?",
                                        icon="warning")
        if result == "yes":
            entry_id = int(selected_entry.split("(ID:")[1].split(")")[0].strip())
            DB.delete("purchase_creation", conditions="id=?", values=(entry_id,))
            messagebox.showinfo("Info", "Entry deleted successfully")

            # Remove deleted entry from the dropdown menu
            self.entry_combobox['values'] = [value for value in self.entry_combobox['values'] if
                                             value != selected_entry]
            self.entry_combobox.set("Select an entry")  # Reset the selected entry

            # Clear entry fields after deletion
            for widget in self.edit_entries_frame.winfo_children():
                widget.destroy()

    ###############        ###############        ###############        ###############
    def save_edited_entry(self, entry_id):
        # Extract data from EntriesFrame instances
        edited_order_data = self.order_entries.get_data()

        # Update data in the database
        col_names = list(edited_order_data.keys())
        col_values = list(edited_order_data.values()) + [entry_id]
        DB.update("purchase_creation", col_names, conditions="id=?", values=col_values)
        messagebox.showinfo("Info", "Entry updated successfully")
    ###############        ###############        ###############        ###############
    def Approval_frame(self):
        body_frame = self.create_new_body()
        entries = (
            ("purchase_order", "menu", (0, 0, 3), self.get_purchase_orders_for_approval()),
            ("approver", "entry", (1, 0, 3), None),
            ("approval_status", "menu", (2, 0, 3), ("Pending", "Approved", "Rejected")),
            ("approval_date", "date", (3, 0, 3), None),
            ("comments", "entry", (4, 0, 3), None)
        )
        self.approval_entries = EntriesFrame(body_frame, entries)
        self.approval_entries.pack()
        self.create_footer(self.confirm_approval_btn)
    ###############        ###############        ###############        ###############
    def get_purchase_orders_for_approval(self):
        # Retrieve and format purchase orders from your data source
        entries = DB.select("purchase_creation", ["supplier_name", "order_date", "item_ordered"])
        purchase_names = [f"{entry[0].strip()}/{entry[1]}/{entry[2][:20] + '...' if len(entry[2]) > 20 else entry[2]}" for entry in
                          entries]
        return purchase_names

    ###############        ###############        ###############        ###############
    def confirm_approval_btn(self):
        # Extract data from EntriesFrame instances
        approval_data = self.approval_entries.get_data()

        # Retrieve data
        data = list(approval_data.values())
        col_name = ("purchase_order", "approver", "approval_status", "approval_date", "comments", "time_added")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.append(current_datetime)
        DB.insert("purchase_approval", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")

    ###############        ###############        ###############        ###############
    def View_Approval_frame(self):
        body_frame = self.create_new_body()

        # Create an Entry widget and Search button for filtering
        filter_label = ctk.CTkLabel(body_frame, text="Purchase Order:")
        filter_label.pack()

        filter_entry = ctk.CTkEntry(body_frame)
        filter_entry.pack()

        search_button = ctk.CTkButton(body_frame, text="Search",
                                      command=lambda: self.filter_approval_table(table, filter_entry.get()))
        search_button.pack()

        # Create a Treeview widget to display the data
        columns = ("id", "purchase_order", "approver", "approval_status", "approval_date", "comments", "time_added")

        # Create a horizontal scrollbar for the custom view
        x_sroller = ctk.CTkScrollbar(master=body_frame, orientation='horizontal')
        x_sroller.pack(side='bottom')

        table = ttk.Treeview(body_frame, columns=columns, show='headings', xscrollcommand=x_sroller.set)

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
        column_widths = [10, 150, 100, 200, 75, 75, 100, 100, 200, 100]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        data = DB.select("purchase_approval", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)

    ###############        ###############        ###############        ###############
    def filter_approval_table(self, table, keyword):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = ("id", "purchase_order","approver","approval_status","approval_date","comments", "time_added")

        data = DB.select("purchase_approval", columns, "purchase_order LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)

    ###############        ###############        ###############        ###############
    def Edit_Approval_frame(self):
        body_frame = self.create_new_body()

        # Create a LabelFrame for selection and editing
        selection_frame = ttk.LabelFrame(body_frame, text="Select Approval Entry to Edit")
        selection_frame.pack(padx=10, pady=10, fill="both", expand=True)

        entries = DB.select("purchase_approval", ["id", "purchase_order"])
        selected_entry = tk.StringVar()
        selected_entry.set("Select an entry")

        # Strip leading/trailing spaces from entry names
        entry_options = [f"{entry[0]}/{entry[1].strip()} " for entry in entries]

        # Create the Combobox for selecting an entry to edit
        self.entry_combobox = ttk.Combobox(selection_frame, values=entry_options, state="readonly", width=75)
        self.entry_combobox.pack(padx=10, pady=10)

        # Create a Button to trigger editing
        edit_button = ttk.Button(selection_frame, text="Edit Approval",
                                 command=lambda: self.edit_selected_approval(self.entry_combobox.get()))
        edit_button.pack(padx=10, pady=10)

        # Create a Button to trigger deletion
        delete_button = ttk.Button(selection_frame, text="Delete Approval",
                                   command=lambda: self.delete_selected_approval(self.entry_combobox.get()))
        delete_button.pack(padx=10, pady=10)

        # Create a frame to display entry fields for editing
        self.edit_entries_frame = ttk.LabelFrame(body_frame, text="Edit Approval Entry Details")
        self.edit_entries_frame.pack(padx=10, pady=10, fill="both", expand=True)
    ###############        ###############        ###############        ###############
    def edit_selected_approval(self, selected_entry):
        if selected_entry.startswith("Select an entry"):
            return

        # Clear previous entry fields
        for widget in self.edit_entries_frame.winfo_children():
            widget.destroy()

        entry_id = str(selected_entry).split('/')[0]
        retrieved_values = DB.select("purchase_approval", ["*"], "id=?", (entry_id,))
        # Retrieve data for the selected entry

        # Define the entry fields for editing
        entry_data = [
            ("purchase_order", "entry", (0, 0, 3), None),
            ("approver", "entry", (1, 0, 3), None),
            ("approval_status", "menu", (2, 0, 3), ("Pending", "Approved", "Rejected")),
            ("approval_date", "date", (3, 0, 3), None),
            ("comments", "entry", (4, 0, 3), None),
        ]

        # Create EntryFrame for editing
        self.edit_approvals = EntriesFrame(self.edit_entries_frame, entry_data)
        self.edit_approvals.pack()

        if entry_data:
            # Populate entry fields with retrieved values
            self.edit_approvals.change_and_disable("purchase_order", retrieved_values[0][1])
            self.edit_approvals.change_value("approver", retrieved_values[0][2])
            self.edit_approvals.change_menu_value("approval_status", retrieved_values[0][3])
            self.edit_approvals.change_value("approval_date", retrieved_values[0][4])
            self.edit_approvals.change_value("comments", retrieved_values[0][5])

            # Create Save button to update the entry
            save_button = ttk.Button(self.edit_entries_frame, text="Save Changes",
                                     command=lambda: self.save_selected_approval(entry_id))
            save_button.pack(padx=10, pady=10)

    ###############        ###############        ###############        ###############
    def save_selected_approval(self, entry_id):
        # Extract data from EntriesFrame instances
        edited_approval_data = self.edit_approvals.get_data()

        # Update data in the database
        col_names = list(edited_approval_data.keys())
        col_values = list(edited_approval_data.values()) + [entry_id]
        DB.update("purchase_approval", col_names, conditions="id=?", values=col_values)
        messagebox.showinfo("Info", "Approval entry updated successfully")
    ###############        ###############        ###############        ###############
    def delete_selected_approval(self, selected_entry):
        if selected_entry.startswith("Select an approval"):
            return

        # Prompt confirmation box before deletion
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this approval?",
                                        icon="warning")
        if result == "yes":
            entry_id = str(selected_entry).split('/')[0]
            DB.delete("purchase_approval", conditions="id=?", values=(entry_id,))
            messagebox.showinfo("Info", "Approval deleted successfully")

            # Remove deleted entry from the dropdown menu
            self.entry_combobox['values'] = [value for value in self.entry_combobox['values'] if
                                             value != selected_entry]
            self.entry_combobox.set("Select an approval")  # Reset the selected entry

            # Clear entry fields after deletion
            for widget in self.edit_entries_frame.winfo_children():
                widget.destroy()
    ###############        ###############        ###############        ###############
    def Order_frame(self):
        body_frame = self.create_new_body()
        entries = (
            ("purchase_order", "menu", (0, 0, 3), self.get_purchase_approvals()),
            ("order_status", "menu", (1, 0, 3), ("Pending", "Creation", "Receipt")),
            ("estimated_delivery_date", "date", (2, 0, 3), None),
            ("actual_delivery_date", "date", (3, 0, 3), None),
            ("shipment_tracking_number", "entry", (4, 0, 3), None)
        )
        self.purchase_order_entries = EntriesFrame(body_frame, entries)
        self.purchase_order_entries.pack()
        self.create_footer(self.confirm_order_btn)
    ###############        ###############        ###############        ###############
    def get_purchase_approvals(self):
        # Retrieve and format purchase orders from your data source
        entries = DB.select("purchase_approval", ["id", "purchase_order"])
        purchase_names = [f"(ID: {entry[0]}) {entry[1].strip()}" for entry in
                          entries]
        return purchase_names
    ###############        ###############        ###############        ###############
    def confirm_order_btn(self):
        # Extract data from EntriesFrame instances
        order_data = self.purchase_order_entries.get_data()

        # Retrieve data
        data = list(order_data.values())
        col_name = ("purchase_order", "order_status", "estimated_delivery_date", "actual_delivery_date", "shipment_tracking_number")
        DB.insert("order_tracking", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")

    ###############        ###############        ###############        ###############
    def View_Order_frame(self):
        body_frame = self.create_new_body()

        # Create an Entry widget and Search button for filtering
        filter_label = ctk.CTkLabel(body_frame, text="Purchase Order:")
        filter_label.pack()

        filter_entry = ctk.CTkEntry(body_frame)
        filter_entry.pack()

        search_button = ctk.CTkButton(body_frame, text="Search",
                                      command=lambda: self.filter_order_table(table, filter_entry.get()))
        search_button.pack()

        # Create a Treeview widget to display the data
        columns = ("id", "purchase_order", "order_status", "estimated_delivery_date", "actual_delivery_date", "shipment_tracking_number")

        # Create a horizontal scrollbar for the custom view
        x_sroller = ctk.CTkScrollbar(master=body_frame, orientation='horizontal')
        x_sroller.pack(side='bottom')

        table = ttk.Treeview(body_frame, columns=columns, show='headings', xscrollcommand=x_sroller.set)

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
        column_widths = [10, 100, 100, 100, 100, 100]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        data = DB.select("order_tracking", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)

    ###############        ###############        ###############        ###############
    def filter_order_table(self, table, keyword):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = ("id", "purchase_order", "order_status", "estimated_delivery_date", "actual_delivery_date", "shipment_tracking_number")

        data = DB.select("order_tracking", columns, "purchase_order LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)

    ###############        ###############        ###############        ###############
    def Edit_Order_frame(self):
        body_frame = self.create_new_body()

        # Create a LabelFrame for selection and editing
        selection_frame = ttk.LabelFrame(body_frame, text="Select Order to Edit")
        selection_frame.pack(padx=10, pady=10, fill="both", expand=True)

        entries = DB.select("order_tracking", ["id", "purchase_order"])
        selected_entry = tk.StringVar()
        selected_entry.set("Select an entry")

        # Strip leading/trailing spaces from entry names
        entry_options = [f"(Order ID: {entry[0]}) {entry[1].strip()} " for entry in entries]

        # Create the Combobox for selecting an entry to edit
        self.entry_combobox = ttk.Combobox(selection_frame, values=entry_options, state="readonly", width=75)
        self.entry_combobox.pack(padx=10, pady=10)

        # Create a Button to trigger editing
        edit_button = ttk.Button(selection_frame, text="Edit Order",
                                 command=lambda: self.edit_selected_order(self.entry_combobox.get()))
        edit_button.pack(padx=10, pady=10)

        # Create a Button to trigger deletion
        delete_button = ttk.Button(selection_frame, text="Delete Order",
                                   command=lambda: self.delete_selected_order(self.entry_combobox.get()))
        delete_button.pack(padx=10, pady=10)

        # Create a frame to display entry fields for editing
        self.edit_entries_frame = ttk.LabelFrame(body_frame, text="Edit Order Details")
        self.edit_entries_frame.pack(padx=10, pady=10, fill="both", expand=True)

    ###############        ###############        ###############        ###############
    def edit_selected_order(self, selected_entry):
        if selected_entry.startswith("Select an order"):
            return

        # Clear previous entry fields
        for widget in self.edit_entries_frame.winfo_children():
            widget.destroy()

        entry_id = int(selected_entry.split("(Order ID:")[1].split(")")[0].strip())
        retrieved_values = DB.select("order_tracking", ["*"], "id=?", (entry_id,))
        # Retrieve data for the selected entry

        # Define the entry fields for editing
        entry_data = [
            ("purchase_order", "entry", (0, 0, 3), None),
            ("order_status", "menu", (1, 0, 3), ("Pending", "Creation", "Receipt")),
            ("estimated_delivery_date", "date", (2, 0, 3), None),
            ("actual_delivery_date", "date", (3, 0, 3), None),
            ("shipment_tracking_number", "entry", (4, 0, 3), None)
        ]

        # Create EntryFrame for editing
        self.edit_orders = EntriesFrame(self.edit_entries_frame, entry_data)
        self.edit_orders.pack()

        if entry_data:
            # Populate entry fields with retrieved values
            self.edit_orders.change_and_disable("purchase_order", retrieved_values[0][1])
            self.edit_orders.change_menu_value("order_status", retrieved_values[0][2])
            self.edit_orders.change_value("estimated_delivery_date", retrieved_values[0][3])
            self.edit_orders.change_value("actual_delivery_date", retrieved_values[0][4])
            self.edit_orders.change_value("shipment_tracking_number", retrieved_values[0][5])

            # Create Save button to update the entry
            save_button = ttk.Button(self.edit_entries_frame, text="Save Changes",
                                     command=lambda: self.save_selected_order(entry_id))
            save_button.pack(padx=10, pady=10)

    ###############        ###############        ###############        ###############
    def save_selected_order(self, entry_id):
        # Extract data from EntriesFrame instances
        edited_order_data = self.edit_orders.get_data()

        # Update data in the database
        col_names = list(edited_order_data.keys())
        col_values = list(edited_order_data.values()) + [entry_id]
        DB.update("order_tracking", col_names, conditions="id=?", values=col_values)
        messagebox.showinfo("Info", "Order updated successfully")

    ###############        ###############        ###############        ###############
    def delete_selected_order(self, selected_entry):
        if selected_entry.startswith("Select an order"):
            return

        # Prompt confirmation box before deletion
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this order?",
                                        icon="warning")
        if result == "yes":
            entry_id = int(selected_entry.split("(Order ID:")[1].split(")")[0].strip())
            DB.delete("order_tracking", conditions="id=?", values=(entry_id,))
            messagebox.showinfo("Info", "Order deleted successfully")

            # Remove deleted entry from the dropdown menu
            self.entry_combobox['values'] = [value for value in self.entry_combobox['values'] if
                                             value != selected_entry]
            self.entry_combobox.set("Select an approval")  # Reset the selected entry

            # Clear entry fields after deletion
            for widget in self.edit_entries_frame.winfo_children():
                widget.destroy()

    ###############        ###############        ###############        ###############
    def Goods_frame(self):
        body_frame = self.create_new_body()
        entries = (
            ("purchase_order", "menu", (0, 0, 3), self.get_purchase_orders_for_goods()),
            ("quantity_received", "entry", (1, 0, 3), None),
            ("inspection_status", "menu", (2, 0, 3), ("Excellent", "Okay", "Poor")),
            ("received_date", "date", (3, 0, 3), None),
        )
        self.goods_receipt_entries = EntriesFrame(body_frame, entries)
        self.goods_receipt_entries.pack()
        self.create_footer(self.confirm_goods_btn)

    ###############        ###############        ###############        ###############
    def get_purchase_orders_for_goods(self):
        # Retrieve and format purchase orders from your data source
        entries = DB.select("order_tracking", ["id", "purchase_order"])
        purchase_names = [f"(Order Track ID: {entry[0]}) {entry[1].strip()}" for entry in
                          entries]
        return purchase_names

    ###############        ###############        ###############        ###############
    def confirm_goods_btn(self):
        # Extract data from EntriesFrame instances
        goods_data = self.goods_receipt_entries.get_data()

        # Retrieve data
        data = list(goods_data.values())
        col_name = ("purchase_order", "quantity_received", "inspection_status", "received_date")
        DB.insert("goods_receipt", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")

    ###############        ###############        ###############        ###############
    def View_Goods_frame(self):
        body_frame = self.create_new_body()

        # Create an Entry widget and Search button for filtering
        filter_label = ctk.CTkLabel(body_frame, text="Purchase Order:")
        filter_label.pack()

        filter_entry = ctk.CTkEntry(body_frame)
        filter_entry.pack()

        search_button = ctk.CTkButton(body_frame, text="Search",
                                      command=lambda: self.filter_goods_receipt_table(table, filter_entry.get()))
        search_button.pack()

        # Create a Treeview widget to display the data
        columns = ("id", "purchase_order", "quantity_received", "inspection_status", "received_date")

        # Create a horizontal scrollbar for the custom view
        x_sroller = ctk.CTkScrollbar(master=body_frame, orientation='horizontal')
        x_sroller.pack(side='bottom')

        table = ttk.Treeview(body_frame, columns=columns, show='headings', xscrollcommand=x_sroller.set)

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
        column_widths = [10, 100, 100, 100, 100]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        data = DB.select("goods_receipt", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)

    ###############        ###############        ###############        ###############
    def filter_goods_receipt_table(self, table, keyword):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = ("id", "purchase_order", "quantity_received", "inspection_status", "received_date")

        data = DB.select("goods_receipt", columns, "purchase_order LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)

    ###############        ###############        ###############        ###############
    def Edit_Goods_frame(self):
        body_frame = self.create_new_body()

        # Create a LabelFrame for selection and editing
        selection_frame = ttk.LabelFrame(body_frame, text="Select Goods receipt to Edit")
        selection_frame.pack(padx=10, pady=10, fill="both", expand=True)

        entries = DB.select("goods_receipt", ["id", "purchase_order"])
        selected_entry = tk.StringVar()
        selected_entry.set("Select an entry")

        # Strip leading/trailing spaces from entry names
        entry_options = [f"(Goods Receipt ID: {entry[0]}) {entry[1].strip()} " for entry in entries]

        # Create the Combobox for selecting an entry to edit
        self.entry_combobox = ttk.Combobox(selection_frame, values=entry_options, state="readonly", width=75)
        self.entry_combobox.pack(padx=10, pady=10)

        # Create a Button to trigger editing
        edit_button = ttk.Button(selection_frame, text="Edit Goods Receipt",
                                 command=lambda: self.edit_selected_goods_receipt(self.entry_combobox.get()))
        edit_button.pack(padx=10, pady=10)

        # Create a Button to trigger deletion
        delete_button = ttk.Button(selection_frame, text="Delete Goods Receipt",
                                   command=lambda: self.delete_selected_goods_receipt(self.entry_combobox.get()))
        delete_button.pack(padx=10, pady=10)

        # Create a frame to display entry fields for editing
        self.edit_entries_frame = ttk.LabelFrame(body_frame, text="Edit Goods Receipt")
        self.edit_entries_frame.pack(padx=10, pady=10, fill="both", expand=True)

    ###############        ###############        ###############        ###############
    def edit_selected_goods_receipt(self, selected_entry):
        if selected_entry.startswith("Select a goods receipt"):
            return

        # Clear previous entry fields
        for widget in self.edit_entries_frame.winfo_children():
            widget.destroy()

        entry_id = int(selected_entry.split("(Goods Receipt ID:")[1].split(")")[0].strip())
        retrieved_values = DB.select("goods_receipt", ["*"], "id=?", (entry_id,))
        # Retrieve data for the selected entry

        # Define the entry fields for editing
        entry_data = [
            ("purchase_order", "entry", (0, 0, 3), None),
            ("quantity_received", "entry", (1, 0, 3), None),
            ("inspection_status", "menu", (2, 0, 3), ("Excellent", "Okay", "Poor")),
            ("received_date", "date", (3, 0, 3), None),
        ]

        # Create EntryFrame for editing
        self.edit_goods_receipt = EntriesFrame(self.edit_entries_frame, entry_data)
        self.edit_goods_receipt.pack()

        if entry_data:
            # Populate entry fields with retrieved values
            self.edit_goods_receipt.change_and_disable("purchase_order", retrieved_values[0][1])
            self.edit_goods_receipt.change_value("quantity_received", retrieved_values[0][2])
            self.edit_goods_receipt.change_menu_value("inspection_status", retrieved_values[0][3])
            self.edit_goods_receipt.change_value("received_date", retrieved_values[0][4])

            # Create Save button to update the entry
            save_button = ttk.Button(self.edit_entries_frame, text="Save Changes",
                                     command=lambda: self.save_selected_goods_receipt(entry_id))
            save_button.pack(padx=10, pady=10)

    ###############        ###############        ###############        ###############
    def save_selected_goods_receipt(self, entry_id):
        # Extract data from EntriesFrame instances
        edited_goods_receipt_data = self.edit_goods_receipt.get_data()

        # Update data in the database
        col_names = list(edited_goods_receipt_data.keys())
        col_values = list(edited_goods_receipt_data.values()) + [entry_id]
        DB.update("goods_receipt", col_names, conditions="id=?", values=col_values)
        messagebox.showinfo("Info", "Order updated successfully")

    ###############        ###############        ###############        ###############
    def delete_selected_goods_receipt(self, selected_entry):
        if selected_entry.startswith("Select a goods receipt"):
            return

        # Prompt confirmation box before deletion
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this goods receipt?",
                                        icon="warning")
        if result == "yes":
            entry_id = int(selected_entry.split("(Goods Receipt ID:")[1].split(")")[0].strip())
            DB.delete("goods_receipt", conditions="id=?", values=(entry_id,))
            messagebox.showinfo("Info", "Goods Receipt deleted successfully")

            # Remove deleted entry from the dropdown menu
            self.entry_combobox['values'] = [value for value in self.entry_combobox['values'] if
                                             value != selected_entry]
            self.entry_combobox.set("Select a goods receipt")  # Reset the selected entry

            # Clear entry fields after deletion
            for widget in self.edit_entries_frame.winfo_children():
                widget.destroy()
    ##############################################################################################################
##############################################################################################################
class InvoiceMatching( Page):
    def __init__(self):
        menu_ls = {
            "Add": self.Add_frame,
            "View": self.View_frame,
            "Edit/Delete": self.edit_frame,
        }
        self.create_new_page("Invoice Matching", menu_ls)

    ###############        ###############        ###############        ###############
    def Add_frame(self):
        body_frame = self.create_new_body()
        entries = (
            ("order_reference", "menu", (0, 0, 3), self.get_purchase_orders_for_invoice()),
            ("goods_receipt_reference", "menu", (1, 0, 3), self.get_goods_receipts()),
            ("invoice_date", "date", (2, 0, 3), None),
            ("invoice_amount", "entry", (3, 0, 3), None),
            ("payment_due_date", "date", (4, 0, 3), None),
        )
        self.invoice_entries = EntriesFrame(body_frame, entries);
        self.invoice_entries.pack()
        self.create_footer(self.Add_btn)

    ###############        ###############        ###############        ###############
    def get_purchase_orders_for_invoice(self):
        # Retrieve and format purchase orders from your data source
        entries = DB.select("purchase_creation", ["id", "supplier_name", "order_date", "item_ordered"])
        purchase_names = [f"{entry[1].strip()} (ID: {entry[0]}) (Date: {entry[2]}) (Item: {entry[3]})" for entry in
                          entries]
        return purchase_names
    ###############        ###############        ###############        ###############
    def get_goods_receipts(self):
        # Retrieve and format purchase orders from your data source
        entries = DB.select("goods_receipt", ["id", "purchase_order"])
        goods_receipts_names = [f"(ID: {entry[0]}) {entry[1].strip()}" for entry in
                          entries]
        return goods_receipts_names
    ###############        ###############        ###############        ###############
    def Add_btn(self):
        # Extract data from EntriesFrame instances
        invoice_data = self.invoice_entries.get_data()

        # Retrieve data
        data = list(invoice_data.values())
        col_name = ("order_reference", "goods_receipt_reference", "invoice_date", "invoice_amount", "payment_due_date")
        DB.insert("invoice_matching", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")

    ###############        ###############        ###############        ###############
    def View_frame(self):
        body_frame = self.create_new_body()

        # Create an Entry widget and Search button for filtering
        filter_label_1 = ctk.CTkLabel(body_frame, text="Purchase Order Reference:")
        filter_label_1.pack()

        filter_entry_1 = ctk.CTkEntry(body_frame)
        filter_entry_1.pack()

        filter_label_2 = ctk.CTkLabel(body_frame, text="Goods Receipt Reference:")
        filter_label_2.pack()

        filter_entry_2 = ctk.CTkEntry(body_frame)
        filter_entry_2.pack()

        search_button = ctk.CTkButton(body_frame, text="Search",
                                      command=lambda: self.filter_table(table, filter_entry_1.get(), filter_entry_2.get()))
        search_button.pack()
        # Create a Treeview widget to display the data
        columns = ("id", "order_reference", "goods_receipt_reference", "invoice_date", "invoice_amount", "payment_due_date")

        # Create a horizontal scrollbar for the custom view
        x_sroller = ctk.CTkScrollbar(master=body_frame, orientation='horizontal')
        x_sroller.pack(side='bottom')

        table = ttk.Treeview(body_frame, columns=columns, show='headings', xscrollcommand=x_sroller.set)

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
        column_widths = [10, 100, 100, 100, 100, 100]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        data = DB.select("invoice_matching", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)

    ###############        ###############        ###############        ###############
    def filter_table(self, table, keyword_1, keyword_2):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = (
            "id", "order_reference", "goods_receipt_reference", "invoice_date", "invoice_amount", "payment_due_date"
        )
        data = DB.select("invoice_matching", columns, "order_reference LIKE ? AND goods_receipt_reference LIKE ?", ("%%" + keyword_1 + "%%","%%" + keyword_2 + "%%"))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword_1.lower() in row[1].lower() and keyword_2.lower() in row[2].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)

    ###############        ###############        ###############        ###############
    def edit_frame(self):
        body_frame = self.create_new_body()

        # Create a LabelFrame for selection and editing
        selection_frame = ttk.LabelFrame(body_frame, text="Select Invoice to Edit")
        selection_frame.pack(padx=10, pady=10, fill="both", expand=True)

        entries = DB.select("invoice_matching", ["id", "order_reference", "goods_receipt_reference"])
        selected_entry = tk.StringVar()
        selected_entry.set("Select an entry")

        # Strip leading/trailing spaces from entry names
        entry_options = [f" (ID: {entry[0]}) (Order: {entry[1].strip()}) (GR: {entry[2].strip()})" for entry in entries]

        # Create the Combobox
        self.entry_combobox = ttk.Combobox(selection_frame, values=entry_options, state="readonly", width=75)
        self.entry_combobox.pack(padx=10, pady=10)

        # Create a Button to trigger editing
        edit_button = ttk.Button(selection_frame, text="Edit Entry",
                                 command=lambda: self.edit_selected_entry(self.entry_combobox.get()))
        edit_button.pack(padx=10, pady=10)

        # Create a Button to trigger deletion
        delete_button = ttk.Button(selection_frame, text="Delete Entry",
                                   command=lambda: self.delete_selected_entry(self.entry_combobox.get()))
        delete_button.pack(padx=10, pady=10)

        # Create a frame to display entry fields for editing
        self.edit_entries_frame = ttk.LabelFrame(body_frame, text="Edit Entry Details")
        self.edit_entries_frame.pack(padx=10, pady=10, fill="both", expand=True)

    ###############        ###############        ###############        ###############
    def edit_selected_entry(self, selected_entry):
        if selected_entry.startswith("Select an entry"):
            return

        # Clear previous entry fields
        for widget in self.edit_entries_frame.winfo_children():
            widget.destroy()

        entry_id = int(selected_entry.split("(ID:")[1].split(")")[0].strip())
        retrieved_values = DB.select("invoice_matching", ["*"], "id=?", (entry_id,))
        # Retrieve data for the selected entry
        entry_data = [
            ("order_reference", "entry", (0, 0, 3), None),
            ("goods_receipt_reference", "entry", (1, 0, 3), None),
            ("invoice_date", "date", (2, 0, 3), None),
            ("invoice_amount", "entry", (3, 0, 3), None),
            ("payment_due_date", "date", (4, 0, 3), None),
        ]
        self.invoice_entries = EntriesFrame(self.edit_entries_frame, entry_data)
        self.invoice_entries.pack()

        if entry_data:
            # Create EntryFrame for editing

            self.invoice_entries.change_and_disable("order_reference", retrieved_values[0][1])
            self.invoice_entries.change_and_disable("goods_receipt_reference", retrieved_values[0][2])
            self.invoice_entries.change_value("invoice_date", retrieved_values[0][3])
            self.invoice_entries.change_value("invoice_amount", retrieved_values[0][4])
            self.invoice_entries.change_value("payment_due_date", retrieved_values[0][5])

            # Create Save button to update the entry
            save_button = ttk.Button(self.edit_entries_frame, text="Save Changes",
                                     command=lambda: self.save_edited_entry(entry_id))
            save_button.pack(padx=10, pady=10)

    ###############        ###############        ###############        ###############
    def delete_selected_entry(self, selected_entry):
        if selected_entry.startswith("Select an invoice"):
            return

        # Prompt confirmation box before deletion
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this invoice?",
                                        icon="warning")
        if result == "yes":
            entry_id = int(selected_entry.split("(ID:")[1].split(")")[0].strip())
            DB.delete("invoice_matching", conditions="id=?", values=(entry_id,))
            messagebox.showinfo("Info", "Invoice deleted successfully")

            # Remove deleted entry from the dropdown menu
            self.entry_combobox['values'] = [value for value in self.entry_combobox['values'] if
                                             value != selected_entry]
            self.entry_combobox.set("Select an entry")  # Reset the selected entry

            # Clear entry fields after deletion
            for widget in self.edit_entries_frame.winfo_children():
                widget.destroy()

    ###############        ###############        ###############        ###############
    def save_edited_entry(self, entry_id):
        # Extract data from EntriesFrame instances
        edited_invoice_data = self.invoice_entries.get_data()

        # Update data in the database
        col_names = list(edited_invoice_data.keys())
        col_values = list(edited_invoice_data.values()) + [entry_id]
        DB.update("invoice_matching", col_names, conditions="id=?", values=col_values)
        messagebox.showinfo("Info", "Invoice updated successfully")

    ##############################################################################################################
