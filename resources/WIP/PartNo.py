from config import *
from ..UI import Page, EntriesFrame, SearchWindow
from ..Logics import DB
from .Data_Editor_backend import (transfer_stock,change_part_no_of_filled_carton, change_part_no_of_sealed_batch)
from ..LoginSystem import LoginSystem

class PartNo (DB,Page):
    def __init__(self):
        menu_ls = {
            "Transfer Stock": self.Transfer_Stock_frame,
            "Edit Filled": self.Edit_Filled_frame,
            "Edit Sealed": self.Edit_Sealed_frame,
        }
        self.create_new_page("Part No", menu_ls)
    ###############        ###############        ###############        ###############
    def Transfer_Stock_frame(self):
        body_frame = self.create_new_body()
        part_no_1_entry = (
            ("part_no_1", "entry", (0, 0, 1), None),
        )
        self.part_no_1_entries = EntriesFrame(body_frame, part_no_1_entry);
        self.part_no_1_entries.pack()
        self.part_no_1_entries.disable_all()
        # add search btn for part no name
        frame1 = self.part_no_1_entries.frames["part_no_1"]
        self.search_part_no_1 = SearchWindow(select_btn=self.select_part_no_1, layout="Search Part No")
        ctk.CTkButton(frame1, image="search_icon", text="", command=self.search_part_no_1.new_window, width=20).pack(
            side="left")
        part_no_2_entry = (
            ("part_no_2", "entry", (0, 0, 1), None),
        )
        self.part_no_2_entries = EntriesFrame(body_frame, part_no_2_entry);
        self.part_no_2_entries.pack()
        self.part_no_2_entries.disable_all()
        # add search btn for part no name
        frame2 = self.part_no_2_entries.frames["part_no_2"]
        self.search_part_no_2 = SearchWindow(select_btn=self.select_part_no_2, layout="Search Part No")
        ctk.CTkButton(frame2, image="search_icon", text="", command=self.search_part_no_2.new_window, width=20).pack(
            side="left")
        self.create_footer(self.transfer_stock_btn)
    ###############        ###############        ###############        ###############
    def check_part_no_for_transfer(self, part_no):
        part_information = DB.select("part_info", ("bundle_qty", "stn_carton", "stn_qty", "uom", "cavity", "customer"), "part_no=%s", (part_no,))
        for part_info in part_information[0]:
            if part_info == 0 or part_info == "" or part_info is None:
                return False
        return True
    ###############        ###############        ###############        ###############
    def select_part_no_1(self):
        selected_row = self.search_part_no_1.selected_row
        if not selected_row:
            return
        self.search_part_no_1.close()
        entry_names = ("part_no_1",)
        values = (selected_row[1],)
        if self.check_part_no_for_transfer(selected_row[1]):
            for entry_name, value in zip(entry_names, values):
                self.part_no_1_entries.change_and_disable(entry_name, value)
        else:
            messagebox.showinfo("Error", "Some part information is empty, please fill them before transfer!")
    ###############        ###############        ###############        ###############
    def select_part_no_2(self):
        selected_row = self.search_part_no_2.selected_row
        if not selected_row:
            return
        self.search_part_no_2.close()
        entry_names = ("part_no_2",)
        values = (selected_row[1],)
        if self.check_part_no_for_transfer(selected_row[1]):
            for entry_name, value in zip(entry_names, values):
                self.part_no_2_entries.change_and_disable(entry_name, value)
        else:
            messagebox.showinfo("Error", "Some part information is empty, please fill them before transfer!")
    ###############        ###############        ###############        ###############
    def transfer_stock_btn(self):
        # Extract data from EntriesFrame instances
        part_no_1_data = self.part_no_1_entries.get_data()
        part_no_2_data = self.part_no_2_entries.get_data()
        if not part_no_1_data["part_no_1"] or not part_no_2_data["part_no_2"]:
            messagebox.showinfo("Process info", "Empty Part No")
        process_info=transfer_stock(part_no_1_data["part_no_1"],part_no_2_data["part_no_2"])
        process_info = " ".join(process_info)
        messagebox.showinfo("Process info", process_info)
    ###############        ###############        ###############        ###############
    def Edit_Filled_frame(self):
        self.table_type="Filled"
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
                                   headers=["ID", "Part No", "Carton Quantity", "Date Codes", "Remarks", "Packing Date", "Time Added", "User"])
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
            "id", "part_no", "carton_quantity", "date_codes", "remarks", "packing_date", "time_added", "user_name"), "loose_quantity = 0 AND (delivery_id = 0 OR delivery_id IS NULL OR CHAR_LENGTH(delivery_id & '') = 0) ORDER BY id DESC")

        # Insert rows into the sheet
        for row_data in carton_data:
            self.carton_view_sheet.insert_row(values=row_data)

        carton_change_filter_frame = ctk.CTkFrame(master=carton_view_frame)
        carton_change_filter_frame.pack(side="bottom", fill="x", expand=False)
        self.justification_text = StringVar(master=carton_change_filter_frame, value="Justification:")
        justification_label = ctk.CTkLabel(carton_change_filter_frame, textvariable=self.justification_text)
        justification_label.grid(row=0, column=0, padx=10)
        justification_reasons = ["Just amendment", "Customer request", "QC request",
                                 "Marketing request"]
        justification_dropdown = ctk.CTkComboBox(carton_change_filter_frame, values=justification_reasons)
        justification_dropdown.grid(row=0, column=1, padx=(10, 5))
        change_part_no_label = ctk.CTkLabel(carton_change_filter_frame, text="Change to Part No:")
        change_part_no_label.grid(row=0, column=2, padx=(10, 5))
        part_no_change_list = ["None"]
        self.part_no_change_dropdown = ctk.CTkComboBox(carton_change_filter_frame, values=part_no_change_list)
        self.part_no_change_dropdown.grid(row=0, column=3, padx=(10, 5))
        self.change_carton_text = StringVar(master=carton_change_filter_frame, value="Confirm Changes")
        self.change_carton_btn = ctk.CTkButton(master=carton_change_filter_frame, textvariable=self.change_carton_text,
                                            width=20, command=lambda:self.change_carton_part_no(justification_dropdown.get())
                                            ).grid(row=0, column=4, padx=(0, 5))
    ###############        ###############        ###############        ###############
    def cell_select(self, event):
        hasRow = False
        if self.table_type == "Filled":
            if self.carton_view_sheet.total_rows() > 0:
                row = self.carton_view_sheet.identify_row(event)
                hasRow = True
                self.selected_row = row
                selected_data = self.carton_view_sheet.get_row_data(self.selected_row)
        elif self.table_type == "Sealed":
            if self.sealed_view_sheet.total_rows() > 0:
                row = self.sealed_view_sheet.identify_row(event)
                hasRow = True
                self.selected_row = row
                selected_data = self.sealed_view_sheet.get_row_data(self.selected_row)
        if hasRow:
            self.justification_text.set(f"Justification (ID: {selected_data[0]}): ")
            part_no = selected_data[1]
            part_info = DB.select("part_info", ("bundle_qty","stn_qty","uom","cavity","customer"), "part_no=%s", (part_no,))
            similar_part_no_list = DB.select("part_info", ("part_no",), "bundle_qty = %s AND stn_qty = %s AND uom = %s AND cavity = %s AND customer = %s AND part_no != %s",
                                               (part_info[0][0], part_info[0][1], part_info[0][2], part_info[0][3], part_info[0][4], part_no))
            part_numbers = [item[0] for item in similar_part_no_list]
            self.part_no_change_dropdown.configure(values=part_numbers)
    ###############        ###############        ###############        ###############
    def carton_filter_track_table(self, part_no):
        # Remove existing data from the table
        total_rows = self.carton_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.carton_view_sheet.delete_row(a)

        carton_data = DB.select("carton_table", (
            "id", "part_no", "carton_quantity", "date_codes", "remarks", "packing_date", "time_added", "user_name"), "part_no LIKE %s AND loose_quantity = 0 AND (delivery_id = 0 OR delivery_id IS NULL OR CHAR_LENGTH(delivery_id & '') = 0) ORDER BY id DESC",
                              ("%%" + part_no + "%%",))
        for row_data in carton_data:
            self.carton_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def change_carton_part_no(self, reason):
        selected_data = self.carton_view_sheet.get_row_data(self.selected_row)
        carton_ID = selected_data[0]
        if carton_ID == "None":
            return
        part_no = self.part_no_change_dropdown.get()
        process_info = change_part_no_of_filled_carton(carton_ID, part_no, reason)
        process_info = "Part No:\n" + " ".join(process_info)
        messagebox.showinfo("Process info", process_info)
        self.carton_filter_track_table("")
    ###############        ###############        ###############        ###############
    def Edit_Sealed_frame(self):
        self.table_type="Sealed"
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
        sealed_data = DB.select("sealed_inventory", (
            "id", "part_no", "quantity", "date_code", "remarks", "additional_info", "time_added", "user_name"), "1=1 ORDER BY id DESC")

        # Insert rows into the sheet
        for row_data in sealed_data:
            self.sealed_view_sheet.insert_row(values=row_data)

        sealed_change_filter_frame = ctk.CTkFrame(master=sealed_view_frame)
        sealed_change_filter_frame.pack(side="bottom", fill="x", expand=False)
        self.justification_text = StringVar(master=sealed_change_filter_frame, value="Justification:")
        justification_label = ctk.CTkLabel(sealed_change_filter_frame, textvariable=self.justification_text)
        justification_label.grid(row=0, column=0, padx=10)
        justification_reasons = ["Just amendment", "Customer request", "QC request",
                                 "Marketing request"]
        justification_dropdown = ctk.CTkComboBox(sealed_change_filter_frame, values=justification_reasons)
        justification_dropdown.grid(row=0, column=1, padx=(10, 5))
        change_part_no_label = ctk.CTkLabel(sealed_change_filter_frame, text="Change to Part No:")
        change_part_no_label.grid(row=0, column=2, padx=(10, 5))
        part_no_change_list = ["None"]
        self.part_no_change_dropdown = ctk.CTkComboBox(sealed_change_filter_frame, values=part_no_change_list)
        self.part_no_change_dropdown.grid(row=0, column=3, padx=(10, 5))
        self.change_sealed_text = StringVar(master=sealed_change_filter_frame, value="Confirm Changes")
        self.change_sealed_btn = ctk.CTkButton(master=sealed_change_filter_frame, textvariable=self.change_sealed_text,
                                            width=20, command=lambda:self.change_sealed_part_no(justification_dropdown.get())
                                            ).grid(row=0, column=4, padx=(0, 5))
    ###############        ###############        ###############        ###############
    def sealed_filter_track_table(self, part_no):
        # Remove existing data from the table
        total_rows = self.sealed_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.sealed_view_sheet.delete_row(a)

        sealed_data = DB.select("sealed_inventory", (
            "id", "part_no", "quantity", "date_code", "remarks", "additional_info", "time_added", "user_name"), "part_no LIKE %s ORDER BY id DESC",
                              ("%%" + part_no + "%%",))
        for row_data in sealed_data:
            self.sealed_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def change_sealed_part_no(self, reason):
        selected_data = self.sealed_view_sheet.get_row_data(self.selected_row)
        sealed_ID = selected_data[0]
        if sealed_ID == "None":
            return
        part_no = self.part_no_change_dropdown.get()
        process_info = change_part_no_of_sealed_batch(sealed_ID, part_no, reason)
        process_info = "Part No:\n" + " ".join(process_info)
        messagebox.showinfo("Process info", process_info)
        self.sealed_filter_track_table("")
##############################################################################################################
