
from config import *
from ..UI import Page , EntriesFrame
from ..Logics import DB


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