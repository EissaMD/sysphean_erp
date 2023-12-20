
from config import *
from ..UI import Page, EntriesFrame , SearchWindow
from ..Logics import DB 

class ProductionEntry(Page):
    def __init__(self):
        menu_ls = {
            "Add": self.Add_frame,
            "View": self.View_frame,
            "Edit/Delete": self.edit_frame,
        }
        # Initialize a variable to track whether a popup is currently open
        self.popup_open = False
        self.selected_row = None  # To keep track of the selected row
        self.table_type = "production_entry_combined"
        self.create_new_page("Production Entry", menu_ls)
    ###############        ###############        ###############        ###############
    def Add_frame(self):
        body_frame = self.create_new_body()
        entries = (
            ("traveller_no", "entry", (0, 0, 3), None),
        )
        part_no_entries = (
            ("part_no", "entry", (0, 0, 3), None),
        )
        production_entries = (
            ("department", "entry", (2, 0, 3), None),
            ("quantity_received", "entry", (3, 0, 3), None),
            ("quantity_output", "entry", (4, 0, 3), None),
            ("quantity_rejected", "entry", (5, 0, 3), None),
            ("remarks", "entry", (6, 0, 3), None),
        )
        self.traveller_entries = EntriesFrame(body_frame, entries);self.traveller_entries.pack()
        self.part_no_entries = EntriesFrame(body_frame, part_no_entries);self.part_no_entries.pack()
        self.production_entries = EntriesFrame(body_frame, production_entries) ; self.production_entries.pack()

        # add search btn for traveller no
        frame = self.traveller_entries.frames["traveller_no"]
        self.search_traveller = SearchWindow(select_btn=self.select_traveller, layout="Search Traveller No")
        ctk.CTkButton(frame, image="search_icon", text="", command=self.search_traveller.new_window, width=20).pack(
            side="left")

        # add search btn for part no name
        frame = self.part_no_entries.frames["part_no"]
        self.search_part_no = SearchWindow(select_btn=self.select_part_no, layout="Search Part No")
        ctk.CTkButton(frame, image="search_icon", text="", command=self.search_part_no.new_window, width=20).pack(
            side="left")

        self.traveller_no_sheet = Sheet(body_frame, show_x_scrollbar=False, height=200,
                                        headers=["ID", "Traveller No", "Part No", "Department",
                                                 "Quantity Received", "Quantity Output", "Quantity Rejected",
                                                 "Quantity Balance", "Remarks", "Time Added"])
        col_size = 110
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.traveller_no_sheet.set_column_widths(column_widths=col_sizes)
        binding = ("single_select", "row_select",
                   "column_width_resize", "double_click_column_resize", "row_width_resize", "column_height_resize",
                   "row_height_resize", "double_click_row_resize")
        self.traveller_no_sheet.enable_bindings(binding)
        self.traveller_no_sheet.pack(fill="x", padx=4, pady=4)

        # Retrieve data from the database and populate the table
        columns = (
        "id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected",
        "quantity_balance", "remarks", "time_added")
        data = DB.select(f"{self.table_type}", columns)
        for row in data:
            self.traveller_no_sheet.insert_row(values=row)

        # Create a horizontal frame to hold filter label and entry
        filter_frame = ctk.CTkFrame(body_frame)
        filter_frame.pack(side='top', fill='x', padx=10, pady=10)

        # Create the traveler filter elements
        filter_traveller_no_label = ctk.CTkLabel(filter_frame, text="Traveller No:")
        filter_traveller_no_label.grid(row=0, column=0, padx=10)

        filter_traveller_no_entry = ctk.CTkEntry(filter_frame, width=400)
        filter_traveller_no_entry.grid(row=0, column=1, padx=10)

        # Create the part filter elements
        filter_part_no_label = ctk.CTkLabel(filter_frame, text="Part No:")
        filter_part_no_label.grid(row=1, column=0, padx=10)

        filter_part_no_entry = ctk.CTkEntry(filter_frame, width=400)
        filter_part_no_entry.grid(row=1, column=1, padx=10)

        # Create the department filter elements
        filter_department_label = ctk.CTkLabel(filter_frame, text="Department:")
        filter_department_label.grid(row=2, column=0, padx=10)

        filter_department_entry = ctk.CTkEntry(filter_frame, width=400)
        filter_department_entry.grid(row=2, column=1, padx=10)

        search_button = ctk.CTkButton(filter_frame, text="Search",
                                      command=lambda: self.filter_table(filter_traveller_no_entry.get(),
                                                                        filter_part_no_entry.get(),
                                                                        filter_department_entry.get()))
        search_button.grid(row=0, column=2, padx=10)
        reset_button = ctk.CTkButton(filter_frame, text="Reset",
                                     command=lambda: self.reset_filters(filter_traveller_no_entry,
                                                                        filter_part_no_entry,
                                                                        filter_department_entry))
        reset_button.grid(row=1, column=2, padx=10)
        switch_button = ctk.CTkButton(filter_frame, text="Switch (Combined)",
                                     command=lambda: self.switch_table(switch_button))
        if self.table_type == "production_entry_combined":
            switch_button.configure(text="Switch (Individual)")
        switch_button.grid(row=2, column=2, padx=10)
        self.create_footer(self.confirm_btn)
    ###############        ###############        ###############        ###############
    def select_traveller(self):
        selected_row = self.search_traveller.selected_row
        if not selected_row:
            return
        self.search_traveller.close()
        entry_names = ("traveller_no","part_no")
        values = (selected_row[1],selected_row[2])
        i = 0
        for entry_name, value in zip(entry_names, values):
            if i == 0:
                self.traveller_entries.change_value(entry_name, value)
            else:
                self.part_no_entries.change_value(entry_name, value)
            i += 1
    ###############        ###############        ###############        ###############
    def select_part_no(self):
        selected_row = self.search_part_no.selected_row
        if not selected_row:
            return
        self.search_part_no.close()
        entry_names = ("part_no",)
        values = (selected_row[1],)
        for entry_name, value in zip(entry_names, values):
            self.part_no_entries.change_value(entry_name, value)

    ###############        ###############        ###############        ###############
    def confirm_btn(self):
        # Extract data from EntriesFrame instances
        traveller_data = self.traveller_entries.get_data()
        part_no_data = self.part_no_entries.get_data()
        production_data = self.production_entries.get_data()

        # Check if the partNo has output quantity lower than the most recent input quantity, if yes, force the user to give the input
        # as to why.
        recent_quantity_balance_same_dept = DB.select("production_entry", ("quantity_balance",), "traveller_no = %s AND department = %s ORDER BY time_added DESC", (str(traveller_data["traveller_no"]), str(production_data["department"])))
        if recent_quantity_balance_same_dept:
            recent_quantity_balance_same_dept = int(recent_quantity_balance_same_dept[0][0])
            if int(production_data["quantity_output"]) + int(production_data["quantity_rejected"]) > recent_quantity_balance_same_dept + int(
                    production_data["quantity_received"]):
                messagebox.showerror("Please fill in the remarks",
                                     f"Quantity output and reject are more than the balance!")
                return

        quantity_balance = 0
        if recent_quantity_balance_same_dept:
            quantity_balance = recent_quantity_balance_same_dept + int(production_data["quantity_received"]) - int(production_data["quantity_output"]) - int(
                production_data["quantity_rejected"])
        else:
            quantity_balance = int(production_data["quantity_received"]) - int(production_data["quantity_output"]) - int(production_data["quantity_rejected"])

        if int(production_data["quantity_rejected"]) > 0 and not production_data["remarks"] == "":
            messagebox.showerror("Please fill in the remarks",
                                 f"{production_data['quantity_rejected']} stock is rejected. Please give a reason in the remarks column as to what happened.")
            return
        col_name = ("traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected", "quantity_balance", "remarks", "time_added")
        # Retrieve data
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = (traveller_data["traveller_no"], part_no_data["part_no"], production_data["department"],
                production_data["quantity_received"], production_data["quantity_output"],
                production_data["quantity_rejected"], quantity_balance, production_data["remarks"], current_datetime)
        DB.insert("production_entry", col_name, data)
        traveller_combined_info = DB.select("production_entry_combined", ("id","quantity_received","quantity_output","quantity_rejected","remarks"), "traveller_no = %s AND part_no = %s AND department = %s",
                                            (traveller_data["traveller_no"], part_no_data["part_no"], production_data["department"]))
        if traveller_combined_info:
            traveller_combined_id = traveller_combined_info[0][0]
            quantity_received = traveller_combined_info[0][1]
            quantity_output = traveller_combined_info[0][2]
            quantity_rejected = traveller_combined_info[0][3]
            remarks = traveller_combined_info[0][4]
            remarks += production_data["remarks"]
            DB.update("production_entry_combined", ("quantity_received", "quantity_output", "quantity_rejected", "quantity_balance", "remarks"), "id = %s",
                        (int(quantity_received + int(production_data['quantity_received'])), int(quantity_output + int(production_data['quantity_output'])),
                         int(quantity_rejected + int(production_data['quantity_rejected'])), quantity_balance, remarks, traveller_combined_id))
        else:
            DB.insert("production_entry_combined", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")
        data = DB.select(f"{self.table_type}", ("id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected", "quantity_balance", "remarks", "time_added"))
        total_rows = self.traveller_no_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.traveller_no_sheet.delete_row(a)
        # Filter and insert matching rows into the table
        for row in data:
            self.traveller_no_sheet.insert_row(values=row)
    ###############        ###############        ###############        ###############
    def View_frame(self):
        body_frame = self.create_new_body()

        # Create a horizontal frame to hold filter label and entry
        filter_frame = ctk.CTkFrame(body_frame)
        filter_frame.pack(side='top', fill='x', padx=10, pady=10)

        # Create the traveler filter elements
        filter_traveller_no_label = ctk.CTkLabel(filter_frame, text="Traveller No:")
        filter_traveller_no_label.grid(row=0, column=0, padx=10)

        filter_traveller_no_entry = ctk.CTkEntry(filter_frame, width=400)
        filter_traveller_no_entry.grid(row=0, column=1, padx=10)

        # Create the part filter elements
        filter_part_no_label = ctk.CTkLabel(filter_frame, text="Part No:")
        filter_part_no_label.grid(row=1, column=0, padx=10)

        filter_part_no_entry = ctk.CTkEntry(filter_frame, width=400)
        filter_part_no_entry.grid(row=1, column=1, padx=10)

        # Create the department filter elements
        filter_department_label = ctk.CTkLabel(filter_frame, text="Department:")
        filter_department_label.grid(row=2, column=0, padx=10)

        filter_department_entry = ctk.CTkEntry(filter_frame, width=400)
        filter_department_entry.grid(row=2, column=1, padx=10)

        search_button = ctk.CTkButton(filter_frame, text="Search",
                                      command=lambda: self.filter_table(filter_traveller_no_entry.get(), filter_part_no_entry.get(), filter_department_entry.get()))
        search_button.grid(row=0, column=2, padx=10)
        reset_button = ctk.CTkButton(filter_frame, text="Reset",
                                      command=lambda: self.reset_filters(filter_traveller_no_entry, filter_part_no_entry, filter_department_entry))
        reset_button.grid(row=1, column=2, padx=10)
        switch_button = ctk.CTkButton(filter_frame, text="Switch (Combined)",
                                      command=lambda: self.switch_table(switch_button))
        if self.table_type == "production_entry":
            switch_button.configure(text="Switch (Individual)")
        switch_button.grid(row=2, column=2, padx=10)

        self.traveller_no_sheet = Sheet(body_frame, show_x_scrollbar=False, height=200,
                                        headers=["ID", "Traveller No", "Part No", "Department",
                                                 "Quantity Received", "Quantity Output", "Quantity Rejected",
                                                 "Quantity Balance", "Remarks", "Time Added"])
        col_size = 110
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.traveller_no_sheet.set_column_widths(column_widths=col_sizes)
        binding = ("single_select", "row_select",
                   "column_width_resize", "double_click_column_resize", "row_width_resize", "column_height_resize",
                   "row_height_resize", "double_click_row_resize")
        self.traveller_no_sheet.enable_bindings(binding)
        self.traveller_no_sheet.pack(fill="x", padx=4, pady=4)

        # Retrieve data from the database and populate the table
        columns = (
            "id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected",
            "quantity_balance", "remarks", "time_added")
        data = DB.select(f"{self.table_type}", columns)
        for row in data:
            self.traveller_no_sheet.insert_row(values=row)
    ###############        ###############        ###############        ###############
    def reset_filters(self, entry1, entry2, entry3):
        # Remove existing data from the table
        total_rows = self.traveller_no_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.traveller_no_sheet.delete_row(a)

        entry1.delete(0, tk.END)
        entry2.delete(0, tk.END)
        entry3.delete(0, tk.END)

        # Get all data from the database
        columns = ("id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected", "quantity_balance", "remarks", "time_added")
        data = DB.select(f"{self.table_type}", columns)
        # Filter and insert matching rows into the table
        for row in data:
            self.traveller_no_sheet.insert_row(values=row)

    ###############        ###############        ###############        ###############
    def filter_table(self, keyword1, keyword2, keyword3):
        # Remove existing data from the table
        total_rows = self.traveller_no_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.traveller_no_sheet.delete_row(a)

        # Get all data from the database
        columns = ("id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected", "quantity_balance", "remarks", "time_added")
        keywords1 = "%%" + keyword1 + "%%"
        keywords2 = "%%" + keyword2 + "%%"
        keywords3 = "%%" + keyword3 + "%%"
        data = DB.select(f"{self.table_type}", columns, "traveller_no LIKE %s AND part_no LIKE %s AND department LIKE %s", (keywords1,keywords2,keywords3))
        # Filter and insert matching rows into the table
        for row in data:
            if keyword1.lower() in row[1].lower() and keyword2.lower() in row[2].lower() and keyword3.lower() in row[3].lower():  # Case-insensitive search in item_description column
                self.traveller_no_sheet.insert_row(values=row)

    ###############        ###############        ###############        ###############
    def switch_table (self, switch_button):
        if self.table_type == "production_entry_combined":
            self.table_type = "production_entry"
            switch_button.configure(text="Switch (Individual)")
        else:
            self.table_type = "production_entry_combined"
            switch_button.configure(text="Switch (Combined)")

        # Remove existing data from the table
        total_rows = self.traveller_no_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.traveller_no_sheet.delete_row(a)

        columns = (
        "id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected",
        "quantity_balance", "remarks", "time_added")
        data = DB.select(f"{self.table_type}", columns)
        # Filter and insert matching rows into the table
        for row in data:
            self.traveller_no_sheet.insert_row(values=row)

    ###############        ###############        ###############        ###############
    def edit_frame(self):
        self.function = "Edit"
        body_frame = self.create_new_body()

        production_entry_view_frame = ctk.CTkFrame(master=body_frame)
        production_entry_view_filter_frame = ctk.CTkFrame(master=production_entry_view_frame)
        production_entry_view_filter_frame.pack(side="top", fill="x", expand=False)
        filter_label_1 = ctk.CTkLabel(production_entry_view_filter_frame, text="Traveller No:")
        filter_label_1.pack(side='left', padx=10, pady=10)  # Place label on the left side

        filter_entry_1 = ctk.CTkEntry(production_entry_view_filter_frame, width=130)
        filter_entry_1.pack(side='left', padx=10, pady=10)  # Place entry widget next to the label

        filter_label_2 = ctk.CTkLabel(production_entry_view_filter_frame, text="Part No:")
        filter_label_2.pack(side='left', padx=10, pady=10)  # Place label on the left side

        filter_entry_2 = ctk.CTkEntry(production_entry_view_filter_frame, width=130)
        filter_entry_2.pack(side='left', padx=10, pady=10)  # Place entry widget next to the label

        filter_label_3 = ctk.CTkLabel(production_entry_view_filter_frame, text="Department:")
        filter_label_3.pack(side='left', padx=10, pady=10)  # Place label on the left side

        filter_entry_3 = ctk.CTkEntry(production_entry_view_filter_frame, width=130)
        filter_entry_3.pack(side='left', padx=10, pady=10)  # Place entry widget next to the label

        search_button = ctk.CTkButton(production_entry_view_filter_frame, text="Search",
                                      command=lambda: self.filter_view_table(filter_entry_1.get(),filter_entry_2.get(),
                                                                             filter_entry_3.get()))
        search_button.pack(side='left')
        reset_button = ctk.CTkButton(production_entry_view_filter_frame, text="Reset",
                                    command=lambda: self.reset_view_filters(filter_entry_1,filter_entry_2,
                                                                             filter_entry_3))
        reset_button.pack(side='left')
        edit_button = ctk.CTkButton(production_entry_view_filter_frame, text="Edit/Delete",
                                    command=lambda: self.edit_row_frame(body_frame))
        edit_button.pack(side='left')
        production_entry_view_frame.pack(side="top", fill="x", expand=False)
        self.production_entry_view_sheet = Sheet(production_entry_view_frame, show_x_scrollbar=False, height=200,
                                        headers=["ID", "Traveller No", "Part No", "Department", "Quantity Received",
                                                 "Quantity Output", "Quantity Rejected", "Quantity Balance", "Remarks", "Time Added"])
        col_size = 100
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.production_entry_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = ("single_select", "row_select",
                   "column_width_resize", "double_click_column_resize", "row_width_resize", "column_height_resize",
                   "row_height_resize", "double_click_row_resize")
        self.production_entry_view_sheet.enable_bindings(binding)
        self.production_entry_view_sheet.pack(fill="x", padx=4, pady=4)
        self.production_entry_view_sheet.bind("<ButtonRelease-1>", self.cell_select)

        part_info_data = DB.select("production_entry", ("id","traveller_no","part_no","department","quantity_received","quantity_output","quantity_rejected",
                                                          "quantity_balance", "remarks", "time_added"))
        for row_data in part_info_data:
            self.production_entry_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def reset_view_filters(self, entry1, entry2, entry3):
        # Remove existing data from the table
        total_rows = self.production_entry_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.production_entry_view_sheet.delete_row(a)

        entry1.delete(0, tk.END)
        entry2.delete(0, tk.END)
        entry3.delete(0, tk.END)

        # Get all data from the database
        columns = ("id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected", "quantity_balance", "remarks", "time_added")
        data = DB.select("production_entry", columns)
        # Filter and insert matching rows into the table
        for row in data:
            self.production_entry_view_sheet.insert_row(values=row)
    ###############        ###############        ###############        ###############
    def filter_view_table(self, traveller_no_keyword, part_no_keyword, department_keyword):
        # Remove existing data from the table
        total_rows = self.production_entry_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.production_entry_view_sheet.delete_row(a)

        production_entry_data = DB.select("production_entry", ("id","traveller_no","part_no","department","quantity_received","quantity_output","quantity_rejected",
                                                          "quantity_balance", "remarks", "time_added"), "traveller_no LIKE %s AND part_no LIKE %s AND department LIKE %s", ("%%" + traveller_no_keyword + "%%",
                                                        "%%" + part_no_keyword + "%%","%%" + department_keyword + "%%"))
        for row_data in production_entry_data:
            self.production_entry_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def cell_select(self, event):
        row = self.production_entry_view_sheet.identify_row(event)
        if self.production_entry_view_sheet.total_rows() > 0:
            self.selected_row = row
    ###############        ###############        ###############        ###############
    def edit_row_frame(self, master):
        if self.selected_row is None:
            messagebox.showinfo("Error", "Please select a row to edit.")
        else:
            self.edit_selected_production_entry(master)
    ###############        ###############        ###############        ###############
    def edit_selected_production_entry(self, master):
        if self.popup_open:
            messagebox.showinfo("Error", "The Production Entry Edit Window is already open!")
            self.add_production_entry_window.lift()
        else:
            self.popup_open = True

            if self.selected_row is None:
                messagebox.showinfo("Error", "Please select a row to edit.")
                self.popup_open = False
                return

            # Create a new window (Toplevel) for editing a production entry
            self.add_production_entry_window = Toplevel(master)
            self.add_production_entry_window.title("Edit Production Entry")
            self.add_production_entry_window.lift()

            def close_popup():
                self.add_production_entry_window.destroy()
                self.popup_open = False

            # Bind the close_popup function to the window's close button
            self.add_production_entry_window.protocol("WM_DELETE_WINDOW", close_popup)
            selected_data = self.production_entry_view_sheet.get_row_data(self.selected_row)
            id_of_data = DB.select("production_entry", ("id",), "id=%s", (selected_data[0],))
            id_of_data = id_of_data[0][0]

            add_production_entry_frame = ctk.CTkFrame(self.add_production_entry_window)
            add_production_entry_frame.pack()

            entries = (
                ("id", "entry", (0, 0, 3), None),
                ("traveller_no", "entry", (1, 0, 3), None),
                ("part_no", "entry", (2, 0, 3), None),
                ("department", "entry", (3, 0, 3), None),
                ("quantity_received", "entry", (4, 0, 3), None),
                ("quantity_output", "entry", (5, 0, 3), None),
                ("quantity_rejected", "entry", (6, 0, 3), None),
                ("quantity_balance", "entry", (7, 0, 3), None),
                ("remarks", "entry", (8, 0, 3), None),
                ("time_added", "entry", (9, 0, 3), None),
            )
            self.production_entries = EntriesFrame(add_production_entry_frame, entries)
            self.production_entries.pack()
            # Create EntryFrame for editing
            self.production_entries.change_and_disable("id", selected_data[0])
            self.production_entries.change_and_disable("traveller_no", selected_data[1])
            self.production_entries.change_and_disable("part_no", selected_data[2])
            self.production_entries.change_and_disable("department", selected_data[3])
            self.production_entries.change_value("quantity_received", selected_data[4])
            self.production_entries.change_value("quantity_output", selected_data[5])
            self.production_entries.change_value("quantity_rejected", selected_data[6])
            self.production_entries.change_and_disable("quantity_balance", selected_data[7])
            self.production_entries.change_value("remarks", selected_data[8])
            self.production_entries.change_and_disable("time_added", selected_data[9])
            button_frame = ctk.CTkFrame(master=add_production_entry_frame)
            button_frame.pack(side="bottom", fill="x", expand=False)
            ctk.CTkButton(master=button_frame, text="Save",
                          command=lambda: self.save_traveller_entry(id_of_data, close_popup)).pack(
                side="left", padx=10, pady=10)
            ctk.CTkButton(master=button_frame, text="Delete",
                          command=lambda: self.delete_traveller_entry(id_of_data, close_popup)).pack(
                side="right", padx=10, pady=10)
    ###############        ###############        ###############        ###############
    def delete_traveller_entry(self, id_of_data,close_popup):
        # Prompt confirmation box before deletion
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this traveller entry?",
                                        icon="warning")
        if result == "yes":
            original_quantities = DB.select("production_entry", ("quantity_received", "quantity_output", "quantity_rejected", "quantity_balance",
                                             "traveller_no", "part_no", "department"), "id = %s", (id_of_data,))

            # Calculate changes (which will be negative values)
            quantity_received_change = -int(original_quantities[0][0])
            quantity_output_change = -int(original_quantities[0][1])
            quantity_rejected_change = -int(original_quantities[0][2])
            quantity_balance_change = int(original_quantities[0][3])
            traveller_no = original_quantities[0][4]
            part_no = original_quantities[0][5]
            department = original_quantities[0][6]
            DB.delete("production_entry", conditions="id=%s", values=(id_of_data,))
            # Get the corresponding entry in production_entry_combined
            traveller_combined_info = DB.select("production_entry_combined", ("id","quantity_received","quantity_output","quantity_rejected",
                "quantity_balance"), ("traveller_no = %s AND part_no = %s AND department = %s"),
                        (traveller_no, part_no, department))
            if traveller_combined_info:
                combined_id = int(traveller_combined_info[0][0])
                DB.update("production_entry_combined", ("quantity_received","quantity_output","quantity_rejected",
                "quantity_balance"), "id = %s", (int(traveller_combined_info[0][1])+int(quantity_received_change),
                int(traveller_combined_info[0][2])+int(quantity_output_change),int(traveller_combined_info[0][3])+int(quantity_rejected_change),
                int(traveller_combined_info[0][4])+int(quantity_balance_change),combined_id))
                traveller_combined_info = DB.select("production_entry_combined", ("quantity_received","quantity_output", "quantity_rejected"), "id = %s",
                            (combined_id,))
                quantity_received_combined, quantity_output_combined, quantity_rejected_combined = traveller_combined_info[0]

                # Check if all quantities are zero, and if so, delete the combined entry
                if quantity_received_combined == 0 and quantity_output_combined == 0 and quantity_rejected_combined == 0:
                    DB.delete("production_entry_combined", "id = %s", (combined_id,))
            messagebox.showinfo("Info", "Traveller Entry deleted successfully")
            data = DB.select("production_entry", (
            "id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected",
            "quantity_balance", "remarks", "time_added"))
            total_rows = self.production_entry_view_sheet.get_total_rows()
            for a in range(total_rows - 1, -1, -1):
                self.production_entry_view_sheet.delete_row(a)
            # Filter and insert matching rows into the table
            for row in data:
                self.production_entry_view_sheet.insert_row(values=row)
            close_popup()
    ###############        ###############        ###############        ###############
    def save_traveller_entry(self, id_of_data,close_popup):
        # Extract data from EntriesFrame instances
        edited_production_data = self.production_entries.get_data()

        recent_quantity_balance_same_dept = DB.select("production_entry", ("quantity_balance",), ("traveller_no = %s AND department = %s AND time_added < %s"), (
            edited_production_data["traveller_no"], edited_production_data["department"], edited_production_data["time_added"]))
        if recent_quantity_balance_same_dept:
            recent_quantity_balance_same_dept = int(recent_quantity_balance_same_dept[0][0])
            if int(edited_production_data["quantity_output"]) + int(edited_production_data["quantity_rejected"]) > recent_quantity_balance_same_dept + int(
                    edited_production_data["quantity_received"]):
                messagebox.showerror("Please fill in the remarks",
                                     f"Quantity output and reject are more than the balance!")
                return

        quantity_balance = 0
        if recent_quantity_balance_same_dept:
            quantity_balance = recent_quantity_balance_same_dept + int(edited_production_data["quantity_received"]) - int(edited_production_data["quantity_output"]) - int(
                edited_production_data["quantity_rejected"])
        else:
            quantity_balance = int(edited_production_data["quantity_received"]) - int(edited_production_data["quantity_output"]) - int(edited_production_data["quantity_rejected"])

        if int(edited_production_data["quantity_rejected"]) > 0 and not edited_production_data["remarks"] == "":
            messagebox.showerror("Please fill in the remarks",
                                 f"{edited_production_data['quantity_rejected']} stock is rejected. Please give a reason in the remarks column as to what happened.")
            return

        # Update the data in the database
        original_quantities = DB.select("production_entry", ("quantity_received", "quantity_output", "quantity_rejected", "quantity_balance"),
                    "id = %s", (id_of_data,))
        quantity_received_change = int(edited_production_data["quantity_received"]) - int(original_quantities[0][0])
        quantity_output_change = int(edited_production_data["quantity_output"]) - int(original_quantities[0][1])
        quantity_rejected_change = int(edited_production_data["quantity_rejected"]) - int(original_quantities[0][2])
        quantity_balance_change = int(quantity_balance) - int(original_quantities[0][3])
        DB.update("production_entry", ("traveller_no","part_no","department","quantity_received","quantity_output",
                                           "quantity_rejected","quantity_balance","remarks"), "id = %s", (edited_production_data["traveller_no"],
            edited_production_data["part_no"], edited_production_data["department"], edited_production_data["quantity_received"],
            edited_production_data["quantity_output"], edited_production_data["quantity_rejected"], quantity_balance, edited_production_data["remarks"], id_of_data))
        traveller_combined_info = DB.select("production_entry_combined", ("id","quantity_received","quantity_output","quantity_rejected",
            "quantity_balance"), ("traveller_no = %s AND part_no = %s AND department = %s"),
                    (edited_production_data["traveller_no"],edited_production_data["part_no"],edited_production_data["department"]))
        if traveller_combined_info:
            traveller_combined_id = traveller_combined_info[0][0]
            quantity_received = traveller_combined_info[0][1]
            quantity_output = traveller_combined_info[0][2]
            quantity_rejected = traveller_combined_info[0][3]
            quantity_balance = traveller_combined_info[0][4]
            DB.update("production_entry_combined", ("quantity_received", "quantity_output", "quantity_rejected",
            "quantity_balance", "remarks"), "id = %s", (int(quantity_received) + int(quantity_received_change),
            int(quantity_output) + int(quantity_output_change), int(quantity_rejected) + int(quantity_rejected_change),
            int(quantity_balance) + int(quantity_balance_change), edited_production_data["remarks"],
                                                       int(traveller_combined_id)))
        else:
            DB.insert("production_entry_combined", ("traveller_no","part_no","department","quantity_received",
            "quantity_output","quantity_rejected","quantity_balance","time_added","remarks"),
            (edited_production_data["traveller_no"],edited_production_data["part_no"],edited_production_data["department"],
            edited_production_data["quantity_received"],edited_production_data["quantity_output"],edited_production_data["quantity_rejected"],
             int(quantity_balance) + int(quantity_balance_change),datetime.now(), edited_production_data["remarks"]))
        messagebox.showinfo("Info", "Traveller Entry updated successfully")
        total_rows = self.production_entry_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.production_entry_view_sheet.delete_row(a)
        # Filter and insert matching rows into the table
        columns = (
        "id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected",
        "quantity_balance", "remarks", "time_added")
        data = DB.select("production_entry", columns)
        for row in data:
            self.production_entry_view_sheet.insert_row(values=row)
        close_popup()