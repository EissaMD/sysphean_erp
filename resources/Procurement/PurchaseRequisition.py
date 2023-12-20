
from config import *
from ..UI import Page , EntriesFrame
from ..Logics import DB

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