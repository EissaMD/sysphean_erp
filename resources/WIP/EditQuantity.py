from config import *
from ..UI import Page, EntriesFrame
from ..Logics import DB
from .Data_Editor_backend import (change_quantity_of_old_stock,change_quantity_of_filled_carton, change_quantity_of_empty_carton, 
                                  change_quantity_of_sealed_inventory,)
from ..LoginSystem import LoginSystem

class EditQuantity (DB,Page):
    def __init__(self):
        menu_ls = {
            "Empty Cartons": self.Empty_Cartons_frame,
            "Filled Cartons": self.Filled_Cartons_frame,
            "Sealed Parts": self.Sealed_Parts_frame,
            "Old Stock": self.Old_Stock_frame,
        }
        self.table_type = "None"
        self.create_new_page("Edit Quantity", menu_ls)

    ###############        ###############        ###############        ###############
    def Empty_Cartons_frame(self):
        self.table_type = "Empty Cartons"
        body_frame = self.create_new_body()
        self.empty_cartons_sheet = Sheet(body_frame, show_x_scrollbar=False, height=400,
                                   headers=["Carton No", "Quantity"])
        col_size = 300
        col_sizes = [col_size, col_size]
        self.empty_cartons_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize", "arrowkeys")
        self.empty_cartons_sheet.enable_bindings(binding)
        self.empty_cartons_sheet.pack(fill="x", padx=4, pady=4)
        self.empty_cartons_sheet.bind("<ButtonRelease-1>", self.cell_select)
        self.change_empty_cartons_text = StringVar(master=body_frame, value="Change Quantity: ")
        self.empty_cartons_label = ctk.CTkLabel(body_frame, textvariable=self.change_empty_cartons_text)
        self.empty_cartons_label.pack()
        empty_cartons_entry = (
            ("quantity", "entry", (0, 0, 1), None),
        )
        self.empty_cartons_entries = EntriesFrame(body_frame, empty_cartons_entry);
        self.empty_cartons_entries.pack()
        self.change_empty_cartons_btn = ctk.CTkButton(master=body_frame, text="Change", width=20,
                                                  command=self.change_empty_cartons).pack()
        empty_cartons_data = DB.select("carton_info", (
            "carton_no", "quantity"))
        # Insert rows into the sheet
        for row_data in empty_cartons_data:
            self.empty_cartons_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def cell_select(self, event):
        if self.table_type == "Empty Cartons":
            if self.empty_cartons_sheet.total_rows() > 0:
                row = self.empty_cartons_sheet.identify_row(event)
                self.selected_row = row
                selected_data = self.empty_cartons_sheet.get_row_data(self.selected_row)
                entry_names = ("quantity",)
                values = (selected_data[1],)
                for entry_name, value in zip(entry_names, values):
                    self.empty_cartons_entries.change_value(entry_name, value)
                self.change_empty_cartons_text.set(f"Change Quantity: ({selected_data[0]})")
        elif self.table_type == "Filled Cartons":
            if self.carton_view_sheet.total_rows() > 0:
                row = self.carton_view_sheet.identify_row(event)
                self.selected_row = row
                selected_data = self.carton_view_sheet.get_row_data(self.selected_row)
                entry_names = ("quantity",)
                values = (selected_data[2],)
                for entry_name, value in zip(entry_names, values):
                    self.filled_cartons_entries.change_value(entry_name, value)
                self.change_filled_text.set(f"Change Quantity: (ID {selected_data[0]})")
        elif self.table_type == "Sealed Parts":
            if self.sealed_view_sheet.total_rows() > 0:
                row = self.sealed_view_sheet.identify_row(event)
                self.selected_row = row
                selected_data = self.sealed_view_sheet.get_row_data(self.selected_row)
                entry_names = ("quantity",)
                values = (selected_data[2],)
                for entry_name, value in zip(entry_names, values):
                    self.sealed_entries.change_value(entry_name, value)
                self.change_filled_text.set(f"Change Quantity: (ID {selected_data[0]})")
        elif self.table_type == "Old Stock":
            if self.main_inventory_view_sheet.total_rows() > 0:
                row = self.main_inventory_view_sheet.identify_row(event)
                self.selected_row = row
                selected_data = self.main_inventory_view_sheet.get_row_data(self.selected_row)
                entry_names = ("quantity",)
                values = (selected_data[2],)
                for entry_name, value in zip(entry_names, values):
                    self.old_stocks_entries.change_value(entry_name, value)
                self.change_filled_text.set(f"Change Quantity: ({selected_data[1]})")
    ###############        ###############        ###############        ###############
    def change_empty_cartons(self):
        empty_carton_data = self.empty_cartons_entries.get_data()
        selected_data = self.empty_cartons_sheet.get_row_data(self.selected_row)
        carton_no = selected_data[0]
        quantity = empty_carton_data["quantity"]
        if quantity == "" or selected_data[1] == quantity:
            return
        process_info = change_quantity_of_empty_carton(carton_no, quantity)
        process_info = "Empty carton:\n" + " ".join(process_info)
        messagebox.showinfo("Process info", process_info)

    ###############        ###############        ###############        ###############
    def Filled_Cartons_frame(self):
        self.table_type = "Filled Cartons"
        body_frame = self.create_new_body()
        carton_view_frame = ctk.CTkFrame(master=body_frame)
        carton_view_filter_frame = ctk.CTkFrame(master=carton_view_frame)
        carton_view_filter_frame.pack(side="top", fill="x", expand=False)
        carton_view_frame.pack(side="top", fill="x", expand=False)

        part_no_label = ctk.CTkLabel(carton_view_filter_frame, text="Part No:")
        part_no_label.grid(row=0, column=0, padx=10)
        part_no_entry = ctk.CTkEntry(carton_view_filter_frame, width=450)
        part_no_entry.grid(row=0, column=1, padx=10)

        search_button = ctk.CTkButton(carton_view_filter_frame, text="Search",
                                      command=lambda: self.carton_filter_track_table(part_no_entry.get()))
        search_button.grid(row=0, column=2, padx=10)
        self.carton_view_sheet = Sheet(carton_view_frame, show_x_scrollbar=False, height=400,
                                       headers=["ID", "Part No", "Carton Quantity", "Date Codes", "Remarks",
                                                "Packing Date", "Time Added", "User"])
        self.carton_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        col_size = 120
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.carton_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize", "arrowkeys")
        self.carton_view_sheet.enable_bindings(binding)
        self.carton_view_sheet.pack(fill="x", padx=4, pady=4)
        self.carton_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        carton_data = DB.select("carton_table", (
            "id", "part_no", "carton_quantity", "date_codes", "remarks", "packing_date", "time_added", "user_name"),
                                  "loose_quantity = 0 AND (delivery_id = 0 OR delivery_id IS NULL OR CHAR_LENGTH(delivery_id & '') = 0) ORDER BY id DESC")

        # Insert rows into the sheet
        for row_data in carton_data:
            self.carton_view_sheet.insert_row(values=row_data)

        carton_change_filter_frame = ctk.CTkFrame(master=carton_view_frame)
        carton_change_filter_frame.pack(side="bottom", fill="x", expand=False)
        self.change_filled_text = StringVar(master=carton_change_filter_frame, value="Change Quantity:")
        change_filled_label = ctk.CTkLabel(carton_change_filter_frame, textvariable=self.change_filled_text)
        change_filled_label.grid(row=0, column=0, padx=10)
        filled_cartons_entry = (
            ("quantity", "entry", (0, 0, 1), None),
        )
        self.filled_cartons_entries = EntriesFrame(body_frame, filled_cartons_entry);
        self.filled_cartons_entries.pack()
        self.justification_text = StringVar(master=body_frame, value="Justification:")
        justification_label = ctk.CTkLabel(body_frame, textvariable=self.justification_text)
        justification_label.pack()
        justification_reasons = ["Just amendment", "Customer request", "QC request",
                                 "Marketing request"]
        justification_dropdown = ctk.CTkComboBox(body_frame, values=justification_reasons)
        justification_dropdown.pack()

        self.change_filled_carton_btn = ctk.CTkButton(master=body_frame, text="Change",
                                               width=20,
                                               command=lambda: self.change_carton_quantity(justification_dropdown.get())
                                               ).pack()
    ###############        ###############        ###############        ###############
    def carton_filter_track_table(self, part_no):
        # Remove existing data from the table
        total_rows = self.carton_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.carton_view_sheet.delete_row(a)

        carton_data = DB.select("carton_table", (
            "id", "part_no", "carton_quantity", "date_codes", "remarks", "packing_date", "time_added", "user_name"),
                                  "part_no LIKE %s AND loose_quantity = 0 AND (delivery_id = 0 OR delivery_id IS NULL OR CHAR_LENGTH(delivery_id & '') = 0) ORDER BY id DESC",
                                  ("%%" + part_no + "%%",))
        for row_data in carton_data:
            self.carton_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def change_carton_quantity(self,reason):
        selected_data = self.carton_view_sheet.get_row_data(self.selected_row)
        carton_ID = selected_data[0]
        if carton_ID == "None":
            return
        filled_carton_data = self.filled_cartons_entries.get_data()
        quantity = filled_carton_data["quantity"]
        process_info = change_quantity_of_filled_carton(carton_ID, quantity, reason)
        process_info = "filled carton:\n" + " ".join(process_info)
        messagebox.showinfo("Process info", process_info)
        self.carton_filter_track_table("")
    ###############        ###############        ###############        ###############
    def Sealed_Parts_frame(self):
        self.table_type = "Sealed Parts"
        body_frame = self.create_new_body()
        sealed_view_frame = ctk.CTkFrame(master=body_frame)
        sealed_view_filter_frame = ctk.CTkFrame(master=sealed_view_frame)
        sealed_view_filter_frame.pack(side="top", fill="x", expand=False)
        sealed_view_frame.pack(side="top", fill="x", expand=False)

        part_no_label = ctk.CTkLabel(sealed_view_filter_frame, text="Part No:")
        part_no_label.grid(row=0, column=0, padx=10)
        part_no_entry = ctk.CTkEntry(sealed_view_filter_frame, width=450)
        part_no_entry.grid(row=0, column=1, padx=10)

        search_button = ctk.CTkButton(sealed_view_filter_frame, text="Search",
                                      command=lambda: self.sealed_filter_track_table(part_no_entry.get()))
        search_button.grid(row=0, column=2, padx=10)
        self.sealed_view_sheet = Sheet(sealed_view_frame, show_x_scrollbar=False, height=400,
                                       headers=["ID", "Part No", "Quantity", "Date Code", "Remarks", "Additional Info", "Time Added", "User"])
        self.sealed_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        col_size = 120
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.sealed_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize", "arrowkeys")
        self.sealed_view_sheet.enable_bindings(binding)
        self.sealed_view_sheet.pack(fill="x", padx=4, pady=4)
        self.sealed_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        sealed_data = DB.select("sealed_inventory", ("id", "part_no", "quantity", "date_code", "remarks", "additional_info", "time_added", "user_name"), "1=1 ORDER BY id DESC")

        # Insert rows into the sheet
        for row_data in sealed_data:
            self.sealed_view_sheet.insert_row(values=row_data)

        sealed_change_filter_frame = ctk.CTkFrame(master=sealed_view_frame)
        sealed_change_filter_frame.pack(side="bottom", fill="x", expand=False)
        self.change_filled_text = StringVar(master=sealed_change_filter_frame, value="Change Quantity:")
        change_filled_label = ctk.CTkLabel(sealed_change_filter_frame, textvariable=self.change_filled_text)
        change_filled_label.grid(row=0, column=0, padx=10)
        sealed_entry = (
            ("quantity", "entry", (0, 0, 1), None),
        )
        self.sealed_entries = EntriesFrame(body_frame, sealed_entry);
        self.sealed_entries.pack()
        self.justification_text = StringVar(master=body_frame, value="Justification:")
        justification_label = ctk.CTkLabel(body_frame, textvariable=self.justification_text)
        justification_label.pack()
        justification_reasons = ["Just amendment", "Customer request", "QC request",
                                 "Marketing request"]
        justification_dropdown = ctk.CTkComboBox(body_frame, values=justification_reasons)
        justification_dropdown.pack()

        self.change_sealed_btn = ctk.CTkButton(master=body_frame, text="Change",
                                                      width=20,
                                                      command=lambda: self.change_sealed_quantity(
                                                          justification_dropdown.get())
                                                      ).pack()

    ###############        ###############        ###############        ###############
    def sealed_filter_track_table(self, part_no):
        # Remove existing data from the table
        total_rows = self.sealed_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.sealed_view_sheet.delete_row(a)

        sealed_data = DB.select("sealed_inventory", ("id", "part_no", "quantity", "date_code", "remarks", "additional_info", "time_added", "user_name"),
                                  "part_no LIKE %s ORDER BY id DESC",
                                  ("%%" + part_no + "%%",))
        for row_data in sealed_data:
            self.sealed_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def change_sealed_quantity(self, reason):
        selected_data = self.sealed_view_sheet.get_row_data(self.selected_row)
        sealed_ID = selected_data[0]
        if sealed_ID == "None":
            return
        sealed_data = self.sealed_entries.get_data()
        quantity = sealed_data["quantity"]
        process_info = change_quantity_of_sealed_inventory(sealed_ID, quantity, reason)
        process_info = "Reject carton:\n" + " ".join(process_info)
        messagebox.showinfo("Process info", process_info)
        self.sealed_filter_track_table("")
    ###############        ###############        ###############        ###############
    def Old_Stock_frame(self):
        self.table_type = "Old Stock"
        body_frame = self.create_new_body()
        old_stock_view_frame = ctk.CTkFrame(master=body_frame)
        old_stock_view_filter_frame = ctk.CTkFrame(master=old_stock_view_frame)
        old_stock_view_filter_frame.pack(side="top", fill="x", expand=False)
        old_stock_view_frame.pack(side="top", fill="x", expand=False)

        part_no_label = ctk.CTkLabel(old_stock_view_filter_frame, text="Part No:")
        part_no_label.grid(row=0, column=0, padx=10)
        part_no_entry = ctk.CTkEntry(old_stock_view_filter_frame, width=450)
        part_no_entry.grid(row=0, column=1, padx=10)

        # Checkbox for filtering out fulfilled delivery orders
        stock_entry = tk.BooleanVar()
        stock_checkbox = tk.Checkbutton(old_stock_view_filter_frame, text="Has Old Stock", variable=stock_entry)
        stock_checkbox.grid(row=0, column=2, padx=10)

        search_button = ctk.CTkButton(old_stock_view_filter_frame, text="Search",
                                      command=lambda: self.old_stock_filter_track_table(part_no_entry.get(),stock_entry.get()))
        search_button.grid(row=0, column=3, padx=10)
        self.main_inventory_view_sheet = Sheet(old_stock_view_frame, show_x_scrollbar=False, height=400,
                                       headers=["ID", "Part No", "Old Stock"])
        self.main_inventory_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        col_size = 200
        col_sizes = [col_size, col_size, col_size]
        self.main_inventory_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize", "arrowkeys")
        self.main_inventory_view_sheet.enable_bindings(binding)
        self.main_inventory_view_sheet.pack(fill="x", padx=4, pady=4)
        self.main_inventory_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        main_inventory_data = DB.select("main_inventory", (
            "id", "part_no", "old_stock"))

        # Insert rows into the sheet
        for row_data in main_inventory_data:
            self.main_inventory_view_sheet.insert_row(values=row_data)

        old_stock_change_filter_frame = ctk.CTkFrame(master=old_stock_view_frame)
        old_stock_change_filter_frame.pack(side="bottom", fill="x", expand=False)
        self.change_filled_text = StringVar(master=old_stock_change_filter_frame, value="Change Quantity:")
        change_old_stock_label = ctk.CTkLabel(old_stock_change_filter_frame, textvariable=self.change_filled_text)
        change_old_stock_label.grid(row=0, column=0, padx=10)
        old_stock_entry = (
            ("quantity", "entry", (0, 0, 1), None),
        )
        self.old_stocks_entries = EntriesFrame(body_frame, old_stock_entry);
        self.old_stocks_entries.pack()
        self.justification_text = StringVar(master=body_frame, value="Justification:")
        justification_label = ctk.CTkLabel(body_frame, textvariable=self.justification_text)
        justification_label.pack()
        justification_reasons = ["Just amendment", "Customer request", "QC request",
                                 "Marketing request"]
        justification_dropdown = ctk.CTkComboBox(body_frame, values=justification_reasons)
        justification_dropdown.pack()

        self.change_old_stock_btn = ctk.CTkButton(master=body_frame, text="Change",
                                               width=20,
                                               command=lambda: self.change_old_stock_quantity(justification_dropdown.get())
                                               ).pack()
    ###############        ###############        ###############        ###############
    def old_stock_filter_track_table(self, part_no, has_stock):
        # Remove existing data from the table
        total_rows = self.main_inventory_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.main_inventory_view_sheet.delete_row(a)

        conditions = "part_no LIKE %s "
        if has_stock:
            conditions += " AND old_stock > 0"
        conditions += " ORDER BY id"

        old_stock_data = DB.select("main_inventory", ("id", "part_no", "old_stock"),
                                  conditions,
                                  ("%%" + part_no + "%%",))
        for row_data in old_stock_data:
            self.main_inventory_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def change_old_stock_quantity(self, reason):
        selected_data = self.main_inventory_view_sheet.get_row_data(self.selected_row)
        old_stock_data = self.old_stocks_entries.get_data()

        part_no = selected_data[1]
        new_value = old_stock_data["quantity"]
        try:
            new_value = int(new_value)
        except:
            messagebox.showerror("Error", f"Invalid value: {new_value}")
            return
        process_info = change_quantity_of_old_stock(part_no, new_value, reason)
        process_info = "Editing quantity of old stock:\n" + " ".join(process_info)
        messagebox.showinfo("Process info", process_info)
    ###############        ###############        ###############        ###############
##############################################################################################################