
from config import *
from ..UI import Page , EntriesFrame
from ..Logics import DB

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
