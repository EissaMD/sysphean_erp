from config import *
from ..UI import Page, EntriesFrame, SearchWindow
from ..Logics import DB
from .Data_Editor_backend import (reject_carton, reject_old_stock,get_old_stock_from_delivery_order, delete_entry_tracker)
from ..LoginSystem import LoginSystem

class RejectItems(DB,Page):
    def __init__(self):
        menu_ls = {
            "Reject Carton": self.Reject_Carton_frame,
            "Reject Old Stock": self.Reject_Old_Stock_frame,
            "References for Entry": self.References_Entry_frame,
            "Delete Entry": self.Delete_Entry_frame,
        }
        self.popup_open = False
        self.table_type = None
        self.create_new_page("Reject Items", menu_ls)
    ###############        ###############        ###############        ###############
    def Reject_Carton_frame(self):
        self.table_type = "Carton"
        body_frame = self.create_new_body()
        carton_view_frame = ctk.CTkFrame(master=body_frame)
        do_view_filter_frame = ctk.CTkFrame(master=carton_view_frame)
        do_view_filter_frame.pack(side="top", fill="x", expand=False)
        carton_view_frame.pack(side="top", fill="x", expand=False)

        delivery_order_entry = (
            ("delivery_order_id", "entry", (0, 0, 1), None),
        )
        self.delivery_order_entries = EntriesFrame(do_view_filter_frame, delivery_order_entry);
        self.delivery_order_entries.pack()
        self.delivery_order_entries.disable_all()
        frame = self.delivery_order_entries.frames["delivery_order_id"]
        self.search_delivery_order = SearchWindow(select_btn=self.select_delivery_order, layout="Search Delivery Order")
        ctk.CTkButton(frame, image="search_icon", text="", command=self.search_delivery_order.new_window, width=20).pack(
            side="right")

        self.carton_view_sheet = Sheet(carton_view_frame, show_x_scrollbar=False, height=400,
                                   headers=["ID", "Part No", "Carton Quantity", "Loose Quantity", "Date Codes",
                                            "Remarks", "Packing Date"])
        col_size = 120
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.carton_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize", "arrowkeys")
        self.carton_view_sheet.enable_bindings(binding)
        self.carton_view_sheet.pack(fill="x", padx=4, pady=4)
        self.carton_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        self.reject_carton_text = StringVar(master=body_frame, value="Reject Carton ID: ")
        self.reject_carton_label = ctk.CTkLabel(body_frame, textvariable=self.reject_carton_text)
        self.reject_carton_label.pack()

        self.reject_carton_btn = ctk.CTkButton(master=body_frame, text="Reject", width=20,
                                            command=self.reject_carton).pack()
    ###############        ###############        ###############        ###############
    def select_delivery_order(self):
        selected_row = self.search_delivery_order.selected_row
        if not selected_row:
            return
        self.search_delivery_order.close()
        entry_names = ("delivery_order_id",)
        values = (selected_row[0],)
        for entry_name, value in zip(entry_names, values):
            self.delivery_order_entries.change_and_disable(entry_name, value)
        # Remove existing data from the table
        total_rows = self.carton_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.carton_view_sheet.delete_row(a)
        carton_data = DB.select("carton_table",("id", "part_no", "carton_quantity", "loose_quantity", "date_codes", "remarks", "packing_date"),
                    "delivery_id=%s", (selected_row[0],))
        for row_data in carton_data:
            self.carton_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def cell_select(self, event):
        if self.table_type == "Carton":
            if self.carton_view_sheet.total_rows() > 0:
                row = self.carton_view_sheet.identify_row(event)
                self.selected_row = row
                selected_data = self.carton_view_sheet.get_row_data(self.selected_row)
                self.reject_carton_text.set(f"Reject Carton ID:  ({selected_data[0]})")
        elif self.table_type == "Old Stock":
            if self.do_view_sheet.total_rows() > 0:
                row = self.do_view_sheet.identify_row(event)
                self.selected_row = row
                selected_data = self.do_view_sheet.get_row_data(self.selected_row)
                self.old_stock_entries.change_value("old_stock", get_old_stock_from_delivery_order(selected_data[0]))
        elif self.table_type == "Delete Entry":
            if self.entry_view_sheet.total_rows() > 0:
                row = self.entry_view_sheet.identify_row(event)
                self.selected_row = row
                selected_data = self.entry_view_sheet.get_row_data(self.selected_row)
                self.delete_entry_text.set(f"Delete Entry ID:  ({selected_data[0]})")
    ###############        ###############        ###############        ###############
    def reject_carton(self):
        selected_data = self.carton_view_sheet.get_row_data(self.selected_row)
        carton_ID = selected_data[0]
        # check if carton ID is not selected
        if carton_ID == "None":
            return
        process_info = reject_carton(carton_ID)
        process_info = "Reject carton:\n" + " ".join(process_info)
        messagebox.showinfo("Process info", process_info)
    ###############        ###############        ###############        ###############
    def Reject_Old_Stock_frame(self):
        self.table_type = "Old Stock"
        body_frame = self.create_new_body()
        self.do_view_sheet = Sheet(body_frame, show_x_scrollbar=False, height=400,
                                   headers=["ID", "Customer", "Part No", "Quantity", "Fulfilled Quantity", "UOM",
                                            "Carton IDs",
                                            "Delivery Order", "Delivery Date", "Time Added"])
        col_size = 100
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.do_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize", "arrowkeys")
        self.do_view_sheet.enable_bindings(binding)
        self.do_view_sheet.pack(fill="x", padx=4, pady=4)
        self.do_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        self.reject_old_stock_label = ctk.CTkLabel(body_frame, text="Change Old Stock: ")
        self.reject_old_stock_label.pack()
        old_stock_entry = (
            ("old_stock", "entry", (0, 0, 1), None),
        )
        self.old_stock_entries = EntriesFrame(body_frame, old_stock_entry);
        self.old_stock_entries.pack()
        self.reject_old_stock_btn = ctk.CTkButton(master=body_frame, text="Change", width=20,
                                            command=self.reject_old_stock).pack()
        do_data = DB.select("delivery_orders", (
            "id", "customer", "part_no", "quantity", "fulfilled_quantity", "uom", "cartons_id", "delivery_order",
            "delivery_date", "time","user_name"), "cartons_id LIKE %s ORDER BY id", ("%" + "old_stock" + "%",))
        # Insert rows into the sheet
        for row_data in do_data:
            self.do_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def reject_old_stock(self):
        selected_data = self.do_view_sheet.get_row_data(self.selected_row)
        delivery_order_ID = selected_data[0]
        current_value = get_old_stock_from_delivery_order(selected_data[0])
        old_stock_data = self.old_stock_entries.get_data()
        new_value = old_stock_data["old_stock"]
        # check if new_value is not entered
        if new_value == "":
            return
        try:
            if int(new_value) > int(current_value):
                raise Exception
        except:
            messagebox.showerror("Error",
                                 f"Entered value: {new_value} \nInvalid value or the entered value is greater than the current value")
            return
        deducted_quantity = int(current_value) - int(new_value)
        process_info = reject_old_stock(delivery_order_ID, deducted_quantity)
        process_info = "Reject carton:\n" + " ".join(process_info)
        messagebox.showinfo("Process info", process_info)
    ###############        ###############        ###############        ###############
    def References_Entry_frame(self):
        self.table_type = "References"
        body_frame = self.create_new_body()
        reference_view_frame = ctk.CTkFrame(master=body_frame)
        search_view_filter_frame = ctk.CTkFrame(master=reference_view_frame)
        search_view_filter_frame.pack(side="top", fill="x", expand=False)
        reference_view_frame.pack(side="top", fill="x", expand=False)

        entry_tracker_entry = (
            ("entry_id", "entry", (0, 0, 1), None),
        )
        self.entry_tracker_entries = EntriesFrame(search_view_filter_frame, entry_tracker_entry);
        self.entry_tracker_entries.pack()
        self.entry_tracker_entries.disable_all()
        frame = self.entry_tracker_entries.frames["entry_id"]
        self.search_entry_tracker = SearchWindow(select_btn=self.select_entry_tracker, layout="Search Entry Tracker")
        ctk.CTkButton(frame, image="search_icon", text="", command=self.search_entry_tracker.new_window,
                      width=20).pack(
            side="right")

        self.carton_view_sheet = Sheet(search_view_filter_frame, show_x_scrollbar=False, height=200,
                                       headers=["DO ID", "ID", "Part No", "Carton Quantity", "Loose Quantity", "Date Codes",
                                                "Remarks", "Packing Date"])
        col_size = 120
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.carton_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize", "arrowkeys")
        self.carton_view_sheet.enable_bindings(binding)
        self.carton_view_sheet.pack(fill="x", padx=4, pady=4)

        self.sealed_view_sheet = Sheet(search_view_filter_frame, show_x_scrollbar=False, height=200,
                                       headers=["ID", "Part No", "Quantity", "Date Code", "Remarks"])
        col_size = 200
        col_sizes = [col_size, col_size, col_size, col_size, col_size]
        self.sealed_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize", "arrowkeys")
        self.sealed_view_sheet.enable_bindings(binding)
        self.sealed_view_sheet.pack(fill="x", padx=4, pady=4)


    ###############        ###############        ###############        ###############
    def select_entry_tracker(self):
        selected_row = self.search_entry_tracker.selected_row
        if not selected_row:
            return
        self.search_entry_tracker.close()
        entry_names = ("entry_id",)
        values = (selected_row[0],)
        for entry_name, value in zip(entry_names, values):
            self.entry_tracker_entries.change_and_disable(entry_name, value)
        if self.table_type == "References":
            # Remove existing data from the table
            total_rows = self.carton_view_sheet.get_total_rows()
            for a in range(total_rows - 1, -1, -1):
                self.carton_view_sheet.delete_row(a)
            entry_information = DB.select("entry_tracker", ("part_no","date_code","remarks"), "id=%s ORDER BY id DESC", (selected_row[0],))
            carton_data = DB.select("carton_table", ("delivery_id",
            "id", "part_no", "carton_quantity", "loose_quantity", "date_codes", "remarks", "packing_date"),
                                      "part_no = %s AND date_codes LIKE %s AND remarks LIKE %s ORDER BY id", (entry_information[0][0],entry_information[0][1],entry_information[0][2]))
            for row_data in carton_data:
                self.carton_view_sheet.insert_row(values=row_data)

            total_rows = self.sealed_view_sheet.get_total_rows()
            for a in range(total_rows - 1, -1, -1):
                self.sealed_view_sheet.delete_row(a)
            sealed_data = DB.select("sealed_inventory", ("id", "part_no", "quantity", "date_code", "remarks"),
                                      "part_no = %s AND date_code LIKE %s AND remarks LIKE %s ORDER BY id",
                                      (entry_information[0][0],entry_information[0][1], entry_information[0][2]))
            for row_data in sealed_data:
                self.sealed_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def Delete_Entry_frame(self):
        self.table_type = "Delete Entry"
        body_frame = self.create_new_body()
        reference_view_frame = ctk.CTkFrame(master=body_frame)
        search_view_filter_frame = ctk.CTkFrame(master=reference_view_frame)
        search_view_filter_frame.pack(side="top", fill="x", expand=False)
        reference_view_frame.pack(side="top", fill="x", expand=False)

        part_no_label = ctk.CTkLabel(search_view_filter_frame, text="Part No:")
        part_no_label.grid(row=0, column=0, padx=10)
        part_no_entry = ctk.CTkEntry(search_view_filter_frame, width=450)
        part_no_entry.grid(row=0, column=1, padx=10)

        search_button = ctk.CTkButton(search_view_filter_frame, text="Search",
                                      command=lambda: self.entry_filter_track_table(part_no_entry.get()))
        search_button.grid(row=0, column=2, padx=10)

        self.entry_view_sheet = Sheet(reference_view_frame, show_x_scrollbar=False, height=200,
                                       headers=["ID", "Part No", "Quantity", "Date Code", "Remarks", "Time", "Additional Info", "Customer", "User Name"])
        col_size = 100
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.entry_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize", "arrowkeys")
        self.entry_view_sheet.enable_bindings(binding)
        self.entry_view_sheet.pack(fill="x", padx=4, pady=4)
        self.entry_view_sheet.bind("<ButtonRelease-1>", self.cell_select)

        entry_data = DB.select("entry_tracker", (
            "id", "part_no", "quantity", "date_code", "remarks", "time", "additional_info", "customer", "user_name"), "1=1 ORDER BY id DESC")
        for row_data in entry_data:
            self.entry_view_sheet.insert_row(values=row_data)
        self.delete_entry_text = StringVar(master=body_frame, value="Delete Entry ID: ")
        self.delete_entry_label = ctk.CTkLabel(body_frame, textvariable=self.delete_entry_text)
        self.delete_entry_label.pack()
        self.justification_text = StringVar(master=body_frame, value="Justification:")
        justification_label = ctk.CTkLabel(body_frame, textvariable=self.justification_text)
        justification_label.pack()
        justification_reasons = ["Just amendment", "Customer request", "QC request",
                                 "Marketing request"]
        justification_dropdown = ctk.CTkComboBox(body_frame, values=justification_reasons)
        justification_dropdown.pack()
        self.delete_entry_btn = ctk.CTkButton(master=body_frame, text="Delete",
                                               width=20,
                                               command=lambda: self.delete_entry_tracker(justification_dropdown.get())
                                               ).pack()
    ###############        ###############        ###############        ###############
    def entry_filter_track_table(self, part_no):
        # Remove existing data from the table
        total_rows = self.entry_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.entry_view_sheet.delete_row(a)

        entry_data = DB.select("entry_tracker", (
            "id", "part_no", "quantity", "date_code", "remarks", "time", "additional_info", "customer", "user_name"),
                                 "part_no LIKE %s ORDER BY id DESC", ("%%" + part_no + "%%",))
        for row_data in entry_data:
            self.entry_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def delete_entry_tracker(self, reason):
        selected_data = self.entry_view_sheet.get_row_data(self.selected_row)
        entry_ID = selected_data[0]
        if entry_ID == "None":
            return
        process_info = delete_entry_tracker(entry_ID, reason)
        process_info = "Delete Entry:\n" + " ".join(process_info)
        messagebox.showinfo("Process info", process_info)
        #self.entry_filter_track_table("")
    ##############################################################################################################
