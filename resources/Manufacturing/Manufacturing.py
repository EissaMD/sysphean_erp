from config import *
from ..UI import Page, LeftMenu, EntriesFrame, SearchWindow , ViewFrame , SectionTitle
from ..Logics import DB ,validate_entry
from .SimilarBatchWindow import SimilarBatchWindow
from .Batch_entry_backend import inpro
class Manufacturing(Page):
    def __init__(self):
        self.create_new_page("Manufacturing")
        left_menu = LeftMenu()
        left_menu_ls = {
            "Part No": PartNo,
            "Batch Entry": BatchEntry,
            "Production Entry": ProductionEntry,
        }
        left_menu.update_menu(left_menu_ls)

##############################################################################################################
class PartNo(DB,Page):
    def __init__(self):
        menu_ls = {
            "Add": self.Add_frame,
            "Edit/Delete": self.edit_frame,
        }
        # Initialize a variable to track whether a popup is currently open
        self.popup_open = False
        self.selected_row = None  # To keep track of the selected row
        self.function = "Add"
        self.part_info_columns = ("part_no", "bundle_qty", "stn_carton", "stn_qty", "uom", "cavity", "customer", "single_sided", "paper_label")
        self.table_bindings = ("single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize", "column_height_resize", "row_height_resize", "double_click_row_resize")
        self.create_new_page("Part No", menu_ls)
    ###############        ###############        ###############        ###############
    def Add_frame(self):
        self.function = "Add"
        body_frame = self.create_new_body()

        self.setup_part_no_view_frame(body_frame)

        separator1 = ttk.Separator(body_frame, orient="horizontal")
        separator1.pack(pady=10)  # Add separator line

        # Create a frame to contain the buttons and use the pack geometry manager
        button_frame = ctk.CTkFrame(master=body_frame)
        button_frame.pack(side="top", fill="x", expand=False)

        ctk.CTkButton(master=button_frame, text="Edit/Delete", command=lambda: self.edit_row_frame(body_frame)).pack(
            side="right")
        ctk.CTkButton(master=button_frame, text="Import Excel", command=self.import_excel_btn).pack(side="right")
        ctk.CTkButton(master=button_frame, text="+", command=lambda: self.pop_up_add_part_no(body_frame)).pack(side="right")

        ctk.CTkLabel(master=button_frame, text="Adding Part Nos (For Import Excel, the format is Part No, Customer, Cavity, UOM.)",
                     width=50).pack(side="top", padx=10, pady=10)
        frame = ctk.CTkFrame(body_frame, height=50);
        
        frame.pack(fill="x", padx=4, pady=4)
        self.part_no_sheet = Sheet(frame, show_x_scrollbar=False, height=200,
                                headers=["Part No", "Bundle Qty", "Stn Carton", "Stn Qty", "UOM",
                                         "Cavity", "Customer", "Single Sided", "Label Type"])
        col_size = 115
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.part_no_sheet.set_column_widths(column_widths=col_sizes)
        binding = self.table_bindings
        self.part_no_sheet.enable_bindings(binding)
        self.part_no_sheet.bind("<ButtonRelease-1>", self.cell_select)
        self.part_no_sheet.pack(fill="x", padx=4, pady=4)

        self.create_footer(self.confirm_btn)
    ###############        ###############        ###############        ###############
    def setup_part_no_view_frame(self, body_frame):
        part_no_view_frame = ctk.CTkFrame(master=body_frame)
        part_no_view_filter_frame = ctk.CTkFrame(master=part_no_view_frame)
        part_no_view_filter_frame.pack(side="top", fill="x", expand=False)
        filter_label = ctk.CTkLabel(part_no_view_filter_frame, text="Search Part No:")
        filter_label.pack(side='left', padx=10, pady=10)  # Place label on the left side

        filter_entry = ctk.CTkEntry(part_no_view_filter_frame, width=450)
        filter_entry.pack(side='left', padx=10, pady=10)  # Place entry widget next to the label

        search_button = ctk.CTkButton(part_no_view_filter_frame, text="Search",
                                      command=lambda: self.filter_view_table(filter_entry.get()))
        search_button.pack(side='left')
        if self.function == "Edit":
            edit_button = ctk.CTkButton(master=part_no_view_filter_frame, text="Edit/Delete",
                                        command=lambda: self.edit_row_frame(body_frame))
            edit_button.pack(side='right')
        part_no_view_frame.pack(side="top", fill="x", expand=False)
        self.part_no_view_sheet = Sheet(part_no_view_frame, show_x_scrollbar=False, height=200,
                                        headers=["Part No", "Bundle Qty", "Stn Carton", "Stn Qty", "UOM",
                                                 "Cavity", "Customer", "Single Sided", "Label Type"])
        col_size = 115
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.part_no_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = self.table_bindings
        self.part_no_view_sheet.enable_bindings(binding)
        self.part_no_view_sheet.pack(fill="x", padx=4, pady=4)
        if self.function == "Edit":
            self.part_no_view_sheet.bind("<ButtonRelease-1>", self.cell_select)

        part_info_data = DB.select("part_info", self.part_info_columns)
        for row_data in part_info_data:
            self.part_no_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def filter_view_table(self, keyword):
        # Remove existing data from the table
        total_rows = self.part_no_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.part_no_view_sheet.delete_row(a)

        part_info_data = DB.select("part_info", self.part_info_columns, "part_no LIKE %s", ("%%" + keyword + "%%",))
        for row_data in part_info_data:
            self.part_no_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def cell_select(self, event):
        if self.function == "Add":
            row = self.part_no_sheet.identify_row(event)
            if self.part_no_sheet.total_rows() > 0:
                self.selected_row = row
        else:
            row = self.part_no_view_sheet.identify_row(event)
            if self.part_no_view_sheet.total_rows() > 0:
                self.selected_row = row
    ###############        ###############        ###############        ###############
    def edit_row_frame(self, master):
        if self.selected_row is None:
            messagebox.showinfo("Error", "Please select a row to edit.")
        else:
            self.edit_selected_part_no(master)
    ###############        ###############        ###############        ###############
    def pop_up_add_part_no(self, master):
        if self.popup_open:
            messagebox.showinfo("Error", "The Part No Addition Window is already open!")
            self.add_part_no_window.lift()
        else:
            self.popup_open = True
            # Create a new window (Toplevel) for adding a part number
            self.add_part_no_window = Toplevel(master)
            self.add_part_no_window.title("Add Part Number")
            self.add_part_no_window.lift()

            def close_popup():
                self.add_part_no_window.destroy()
                self.popup_open = False

            # Bind the close_popup function to the window's close button
            self.add_part_no_window.protocol("WM_DELETE_WINDOW", close_popup)

            add_part_no_frame = ctk.CTkFrame(self.add_part_no_window)
            add_part_no_frame.pack()

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
            self.part_no_entries = EntriesFrame(add_part_no_frame, entries);
            self.part_no_entries.pack()
            ctk.CTkButton(master=add_part_no_frame, text="Add",
                          command=lambda: self.confirm_add_table_btn(close_popup)).pack(
                side="bottom", padx=10, pady=10)
    ###############        ###############        ###############        ###############
    def confirm_add_table_btn (self, close_popup):
        # Extract data from EntriesFrame instances
        part_no_data = self.part_no_entries.get_data()

        # Retrieve data
        data = list(part_no_data.values())
        if data[0] == "":
            messagebox.showinfo("Error", f"Part No is empty!")
            self.add_part_no_window.lift()
            return
        same_results = DB.select("part_info", ("part_no",), "part_no = %s", (data[0],))
        if same_results:
            messagebox.showinfo("Error", f"Part No, {data[0]} already exists in the database!")
            self.add_part_no_window.lift()
        else:
            duplicate_part_no_list = self.check_similar_part_nos(data[0])
            dupePass = True
            if duplicate_part_no_list:
                part_no_list_text = '\n'.join([f'* {part_no_similar}' for part_no_similar in duplicate_part_no_list])
                ans = messagebox.askyesno("Warning",
                                          f"This partNo, {data[0]} is similar to the following partNos:\n{part_no_list_text}\nDo you want to proceed?",
                                          icon='warning')
                if not ans:
                    dupePass = False
            if dupePass:
                self.part_no_sheet.insert_row(values=data)
                messagebox.showinfo("Success", f"Part No, {data[0]} is added!")
                self.add_part_no_window.lift()

    ###############        ###############        ###############        ###############
    def import_excel_btn(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if not file_path:
            return

        # Read the Excel data using pandas
        try:
            df = pd.read_excel(file_path, header=None)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read the Excel file: {e}")
            return

        df = df.replace({np.nan: None})
        for i, row in df.iterrows():
            part_no = row.iloc[0]
            same_results = DB.select("part_info", ("part_no",), "part_no = %s", (part_no,))
            if same_results:
                messagebox.showinfo("Error", f"Part No, {part_no} already exists in the database!")
            else:
                duplicate_part_no_list = self.check_similar_part_nos(part_no)
                dupePass = True
                if duplicate_part_no_list:
                    part_no_list_text = '\n'.join([f'* {part_no_similar}' for part_no_similar in duplicate_part_no_list])
                    ans = messagebox.askyesno("Warning",
                                              f"This partNo, {part_no} is similar to the following partNos:\n{part_no_list_text}\nDo you want to proceed?",
                                              icon='warning')
                    if not ans:
                        dupePass = False
                if not pd.isnull(part_no) and dupePass:
                    customer = row.iloc[1]
                    cavity = row.iloc[2]
                    uom = row.iloc[3]
                    if cavity != None and uom != None:
                        if customer == None:
                            customer = ""
                        cavity = int(cavity)
                        self.part_no_sheet.insert_row(values=(part_no,"","","",uom,cavity,customer,"Single","Paper"))
                    else:
                        messagebox.showinfo("Error",
                                            f"\n* PartNo {part_no} has missing information regarding cavity and/or uom. Please recheck your Excel sheet and try again!")
                    #self.add_new_part_no_excel(part_no, customer, cavity, uom)
    ###############        ###############        ###############        ###############
    def check_similar_part_nos(self, part_no):
        part_no_list = []
        part_no_without_spaces = part_no.replace(" ", "")
        part_no_before_bracket = part_no.split("(", 1)[0] if "(" in part_no else None
        part_no_before_space = part_no.split(" ", 1)[0] if " " in part_no else None
        part_no_records = DB.select("part_info", ("part_no",))
        for part_no_to_iterate in part_no_records:
            part_no_iterate = part_no_to_iterate[0]
            part_no_iterate_without_spaces = part_no_iterate.replace(" ", "")
            if (part_no in part_no_iterate or (
                    part_no_without_spaces is not None and part_no_without_spaces in part_no_iterate) or
                    (part_no_before_bracket is not None and part_no_before_bracket in part_no_iterate) or
                    (part_no_before_space is not None and part_no_before_space in part_no_iterate) or
                    part_no in part_no_iterate_without_spaces or (
                            part_no_without_spaces is not None and part_no_without_spaces in part_no_iterate_without_spaces) or
                    (part_no_before_bracket is not None and part_no_before_bracket in part_no_iterate_without_spaces) or
                    (part_no_before_space is not None and part_no_before_space in part_no_iterate_without_spaces)):
                part_no_list.append(part_no_iterate)
        return part_no_list
    ###############        ###############        ###############        ###############
    def edit_selected_part_no(self, master):
        if self.popup_open:
            messagebox.showinfo("Error", "The Part No Edit Window is already open!")
            self.add_part_no_window.lift()
        else:
            self.popup_open = True

            if self.selected_row is None:
                messagebox.showinfo("Error", "Please select a row to edit.")
                self.popup_open = False
                return

            # Create a new window (Toplevel) for editing a part number
            self.add_part_no_window = Toplevel(master)
            self.add_part_no_window.title("Edit Part Number")
            self.add_part_no_window.lift()

            def close_popup():
                self.add_part_no_window.destroy()
                self.popup_open = False

            # Bind the close_popup function to the window's close button
            self.add_part_no_window.protocol("WM_DELETE_WINDOW", close_popup)

            id_of_data = 0
            # Retrieve data from the selected row
            if self.function == "Add":
                selected_data = self.part_no_sheet.get_row_data(self.selected_row)
            else:
                selected_data = self.part_no_view_sheet.get_row_data(self.selected_row)
                id_of_data = DB.select("part_info", ("id",), "part_no=%s", (selected_data[0],))
                id_of_data = id_of_data[0][0]

            add_part_no_frame = ctk.CTkFrame(self.add_part_no_window)
            add_part_no_frame.pack()

            entries = (
                ("part_no", "entry", (0, 0, 3), None),
                ("bundle_qty", "entry", (1, 0, 3), None),
                ("stn_carton", "menu", (2, 0, 3),
                 ("8", "7", "6", "14", "10", "9", "12", "15", "JIG CARTON")),
                ("stn_qty", "entry", (3, 0, 3), None),
                ("uom", "menu", (4, 0, 3), ("PCS", "PANEL")),
                ("cavity", "entry", (5, 0, 3), None),
                ("customer", "entry", (6, 0, 3), None),
                ("single_sided", "menu", (7, 0, 3), ("Single", "Double")),
                ("paper_label", "menu", (8, 0, 3), ("Paper", "Sticker")),
            )
            self.part_no_edit_entries = EntriesFrame(add_part_no_frame, entries)
            self.part_no_edit_entries.pack()
            for i in range(len(entries)):
                if i < 7:
                    self.part_no_edit_entries.change_value(entries[i][0], selected_data[i] or "")
                elif i == 7 and (selected_data[i] is True or selected_data[i] == 1):
                    self.part_no_edit_entries.change_value(entries[i][0], "Single")
                elif i == 7 and (selected_data[i] is False or selected_data[i] == 0):
                    self.part_no_edit_entries.change_value(entries[i][0], "Double")
                elif i == 8 and (selected_data[i] is True or selected_data[i] == 1):
                    self.part_no_edit_entries.change_value(entries[i][0], "Paper")
                elif i == 8 and (selected_data[i] is False or selected_data[i] == 0):
                    self.part_no_edit_entries.change_value(entries[i][0], "Sticker")

            button_frame = ctk.CTkFrame(master=add_part_no_frame)
            button_frame.pack(side="bottom", fill="x", expand=False)
            ctk.CTkButton(master=button_frame, text="Save",
                          command=lambda: self.save_edited_part_no_data(id_of_data,close_popup)).pack(
                side="left", padx=10, pady=10)
            ctk.CTkButton(master=button_frame, text="Delete",
                          command=lambda: self.delete_edited_part_no_data(id_of_data,close_popup)).pack(
                side="right", padx=10, pady=10)

    ###############        ###############        ###############        ###############
    def save_edited_part_no_data(self,id_of_data,close_popup):
        # Extract data from EntriesFrame instances
        part_no_data = self.part_no_edit_entries.get_data()

        # Retrieve data
        edited_data = list(part_no_data.values())

        if edited_data[0] == "":
            messagebox.showinfo("Error", "Part No is empty!")
            self.add_part_no_window.lift()
            return

        # Update the table with the edited data for all 9 columns
        if self.function == "Add":
            for x in range(9):
                self.part_no_sheet.set_cell_data(self.selected_row, x, edited_data[x], True)
        else:
            edited_data.append(id_of_data)
            if edited_data[7] == "Single":
                edited_data[7] = True
            else:
                edited_data[7] = False
            if edited_data[8] == "Paper":
                edited_data[8] = True
            else:
                edited_data[8] = False
            DB.update("part_info", self.part_info_columns,
                        "id=%s", edited_data)
            self.filter_view_table("")

        messagebox.showinfo("Success", "Part No data updated!")
        close_popup()
    ###############        ###############        ###############        ###############
    def delete_edited_part_no_data(self,id_of_data,close_popup):
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this partNo?",
                                        icon="warning")
        if result == "yes":
            if self.function == "Add":
                self.part_no_sheet.delete_row(self.selected_row)
                messagebox.showinfo("Success", "Part No data deleted!")
                close_popup()
            else:
                DB.delete("part_info", "id=%s", (id_of_data,))
                self.filter_view_table("")
                messagebox.showinfo("Success", "Part No data deleted!")
                close_popup()
    ###############        ###############        ###############        ###############
    def confirm_btn(self):
        rows = self.part_no_sheet.get_total_rows()
        rows_to_delete = []
        for x in range(rows):
            part_no_data = self.part_no_sheet.get_row_data(x)

            # Retrieve data
            data = list(part_no_data)
            same_results = DB.select("part_info", ("part_no",), "part_no = %s", (data[0],))
            if same_results:
                messagebox.showinfo("Error", f"Part No, {data[0]} already exists in the database!")
            else:
                duplicate_part_no_list = self.check_similar_part_nos(data[0])
                dupePass = True
                if duplicate_part_no_list:
                    part_no_list_text = '\n'.join([f'* {part_no_similar}' for part_no_similar in duplicate_part_no_list])
                    ans = messagebox.askyesno("Warning",
                                              f"This partNo, {data[0]} is similar to the following partNos:\n{part_no_list_text}\nDo you want to proceed?",
                                              icon='warning')
                    if not ans:
                        dupePass = False
                if dupePass:
                    if data[5] != "" and data[5] != None:
                        if data[7] == "Single":
                            data[7] = True
                        else:
                            data[7] = False
                        if data[8] == "Paper":
                            data[8] = True
                        else:
                            data[8] = False
                        DB.insert("part_info", self.part_info_columns, data)
                        '''
                        stn_qty_for_main_inventory = 0
                        if data[4] == "PCS":
                            stn_qty_for_main_inventory = int(data[3]) * int(data[5])
                        else:
                            stn_qty_for_main_inventory = int(data[3])           
                        DB.insert("main_inventory", ("part_no","carton_quantity","sealed_quantity","stn_qty","total_stock"), (data[0],0,0,stn_qty_for_main_inventory,0))
                        '''
                        messagebox.showinfo("Info", f"The process was successful, partNo {data[0]} is added!")
                        rows_to_delete.append(x)
                    else:
                        messagebox.showinfo("Error",
                                            f"\n* PartNo {data[0]} has missing information regarding cavity and/or uom. Please recheck your Excel sheet and try again!")

        # Delete rows in descending order
        for x in reversed(rows_to_delete):
            self.part_no_sheet.delete_row(x)
    ###############        ###############        ###############        ###############
    def edit_frame(self):
        self.function = "Edit"
        body_frame = self.create_new_body()
        self.setup_part_no_view_frame(body_frame)
    ###############        ###############        ###############        ###############
##############################################################################################################
class BatchEntry(DB,Page):
    def __init__(self):
        menu_ls = {
            "New Batch": self.new_batch_frame,
            "Extra Labels": self.Extra_frame,
            "Batch Rejection": self.Reject_frame,
            "View": self.Tracker_frame,
        }
        # Initialize a variable to track whether a popup is currently open
        self.popup_open = False
        self.selected_row = None  # To keep track of the selected row
        self.create_new_page("Batch Entry", menu_ls)

    ###############        ###############        ###############        ###############
    def new_batch_frame(self):
        self.function = "Add"
        body_frame = self.create_new_body()
        SectionTitle(body_frame,"Enter New Batch:")
        part_no_entry = (
            ("part_no", "entry", (0, 0, 1), None),
        )
        self.part_no_entries = EntriesFrame(body_frame, part_no_entry);
        self.part_no_entries.pack()
        self.part_no_entries.disable_all()
        # add search btn for part no name
        frame = self.part_no_entries.frames["part_no"]
        self.search_part_no = SearchWindow(select_btn=self.select_part_no, layout="Search Part No")
        ctk.CTkButton(frame, image="search_icon", text="", command=self.search_part_no.new_window, width=20).pack(
            side="left")
        entries = (
            ("quantity" , "entry"   , (1, 0, 1), None),
            ("date_code", "entry"   , (2, 0, 1), None),
            ("remarks"  , "entry"   , (3, 0, 1), None),
        )
        self.manufacturing_entries = EntriesFrame(body_frame, entries)
        self.manufacturing_entries.pack()
        date_entries = (
            ("expiry_date_checkbox0"        , "date", (1, 0, 1), None),
            ("manufacturing_date_checkbox0" , "date", (2, 0, 1), None),
            ("packing_date_checkbox0"       , "date", (3, 0, 1), None),
        )
        self.date_entries = EntriesFrame(body_frame, date_entries)
        self.date_entries.pack()
        correctional_entries = (
            ("correctional_entry", "seg_btn", (1, 0, 1), ["No", "Yes"]),
        )
        self.correctional_entries = EntriesFrame(body_frame, correctional_entries)
        self.correctional_entries.pack()
        SectionTitle(body_frame,"Part Information:")
        self.part_no_select_sheet = Sheet(body_frame, show_x_scrollbar=False, show_y_scrollbar=False, height=50,
                                          headers=["Bundle Qty", "Stn Carton", "Stn Qty", "UOM",
                                                   "Cavity", "Customer", "Single Sided", "Label Type"])
        col_size = 135
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.part_no_select_sheet.set_column_widths(column_widths=col_sizes)
        binding = ("single_select", "row_select",
                   "column_width_resize", "double_click_column_resize", "row_width_resize", "column_height_resize",
                   "row_height_resize", "double_click_row_resize")
        self.part_no_select_sheet.enable_bindings(binding)
        self.part_no_select_sheet.pack(fill="x", padx=4, pady=4)
        ####### Last entered batches
        SectionTitle(body_frame,"Recent batches:")
        self.batch_entry_view_sheet = Sheet(body_frame, show_x_scrollbar=False, height=100,
                                        headers=["Part No", "Quantity", "Date Code", "Remarks", "Additional Info", "Time Added"])
        col_size = 175
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size]
        self.batch_entry_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = ("single_select", "row_select","column_width_resize", "double_click_column_resize", "row_width_resize", 
                   "column_height_resize","row_height_resize", "double_click_row_resize")
        self.batch_entry_view_sheet.enable_bindings(binding)
        self.batch_entry_view_sheet.pack(fill="both",expand=True)

        batch_entry_data = DB.select("entry_tracker", ("part_no", "quantity", "date_code", "remarks", "additional_info", "time"), "1=1 ORDER BY id DESC LIMIT 20")
        for row_data in batch_entry_data:
            self.batch_entry_view_sheet.insert_row(values=row_data)
        self.create_footer(self.new_batch_btn)
    ###############        ###############        ###############        ###############
    def select_part_no(self):
        selected_row = self.search_part_no.selected_row
        if not selected_row:
            return
        self.search_part_no.close()
        entry_names = ("part_no",)
        values = (selected_row[1],)
        for entry_name, value in zip(entry_names, values):
            self.part_no_entries.change_and_disable(entry_name, value)
        if not hasattr(self, 'batch_rejection') and hasattr(self, 'part_no_select_sheet'):
            # Remove existing data from the table
            total_rows = self.part_no_select_sheet.get_total_rows()
            for a in range(total_rows - 1, -1, -1):
                self.part_no_select_sheet.delete_row(a)
            data = DB.select("part_info", ("bundle_qty", "stn_carton", "stn_qty", "uom", "cavity", "customer", "single_sided",
                       "paper_label"), "part_no = %s", (selected_row[1],))
            self.part_no_select_sheet.insert_row(values=data[0])
        if self.popup_open and self.function == "Add":
            rejection_data = DB.select("batch_rejection", ("id", "reason", "time_added"), "part_no = %s", (selected_row[1],))
            if rejection_data:
                rework_options = [f'{id} ({reason}) ({time_added})' for id, reason, time_added in rejection_data]
                self.update_rework_entries(rework_options)
    ###############        ###############        ###############        ###############
    def new_batch_btn(self):
        # Extract data from EntriesFrame instances
        data = {}
        for entries in (self.part_no_entries,self.manufacturing_entries,self.date_entries,self.correctional_entries):
            data.update(entries.get_data())
        # Checker 1: Validate entries
        failed_ls =validate_entry(data,popup_msg=True)
        if len(failed_ls) >0:
            return
        # Checker 2: If there are similar batches
        sbm =SimilarBatchWindow(data)
        if sbm._continue is False:
            return
        # Special Conditions
        conditions_ls = []
        for key,value in data.items():
            if key in ("expiry_date" , "manufacturing_date" , "packing_date") and value != "":
                conditions_ls.append(key.upper()+"="+value)
        conditions = ",".join(conditions_ls)
        qr_code = data["part_no"] + "|" + data["quantity"] + "|" + data["date_code"] + "|" + data["remarks"] + "|" + conditions
        inpro(qr_code) 
    ##############################################################################################################
    def Extra_frame(self):
        body_frame = self.create_new_body()
        part_no_entry = (
            ("part_no", "entry", (0, 0, 1), None),
        )
        self.part_no_entries = EntriesFrame(body_frame, part_no_entry); self.part_no_entries.pack()
        self.part_no_entries.disable_all()
        # add search btn for part no name
        frame = self.part_no_entries.frames["part_no"]
        self.search_part_no = SearchWindow(select_btn=self.select_part_no, layout="Search Part No")
        ctk.CTkButton(frame, image="search_icon", text="", command=self.search_part_no.new_window, width=20).pack(
            side="left")
        entries = (
            ("quantity", "entry", (1, 0, 1), None),
            ("date_code", "entry", (2, 0, 1), None),
            ("remarks", "entry", (3, 0, 1), None),
        )
        self.manufacturing_entries = EntriesFrame(body_frame, entries) ; self.manufacturing_entries.pack()
        date_entries = (
            ("expiry_date_checkbox0", "date", (1, 0, 1), None),
            ("manufacturing_date_checkbox0", "date", (2, 0, 1), None),
            ("packing_date_checkbox0", "date", (3, 0, 1), None),
        )
        self.date_entries = EntriesFrame(body_frame, date_entries);
        self.date_entries.pack()
        correctional_entries = (
            ("correctional_entry", "seg_btn", (1, 0, 1), ["No", "Yes"]),
        )
        self.correctional_entries = EntriesFrame(body_frame, correctional_entries);
        self.correctional_entries.pack()
        label_type_entries = (
            ("label_type", "seg_btn", (1, 0, 1), ["Sealed", "Carton"]),
        )
        self.label_type_entries = EntriesFrame(body_frame, label_type_entries);
        self.label_type_entries.pack()

        self.part_no_select_sheet = Sheet(body_frame, show_x_scrollbar=False, height=150,
                                          headers=["Bundle Qty", "Stn Carton", "Stn Qty", "UOM",
                                                   "Cavity", "Customer", "Single Sided", "Label Type"])
        col_size = 130
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.part_no_select_sheet.set_column_widths(column_widths=col_sizes)
        binding = ("single_select", "row_select",
                   "column_width_resize", "double_click_column_resize", "row_width_resize", "column_height_resize",
                   "row_height_resize", "double_click_row_resize")
        self.part_no_select_sheet.enable_bindings(binding)
        self.part_no_select_sheet.pack(fill="x", padx=4, pady=4)
        self.create_footer(self.confirm_extra_btn)
    ###############        ###############        ###############        ###############
    def confirm_extra_btn(self):
        # Extract data from EntriesFrame instances
        part_no_data = self.part_no_entries.get_data()
        if part_no_data["part_no"] == "":
            messagebox.showinfo("ERROR", "Part No entry is empty!")
            return
        manufacturing_data = self.manufacturing_entries.get_data()
        date_data = self.date_entries.get_data()
        correctional_data = self.correctional_entries.get_data()
        label_data = self.label_type_entries.get_data()

        other_remarks = ""

        if date_data["expiry_date"] != "":
            other_remarks += "EXP=" + str(date_data["expiry_date"]) + " "
        if date_data["manufacturing_date"] != "":
            other_remarks += "MFG=" + str(date_data["manufacturing_date"]) + " "
        if date_data["packing_date"] != "":
            other_remarks += "PKD=" + str(date_data["packing_date"]) + " "
        if correctional_data["correctional_entry"] == "Yes":
            other_remarks += "(CORRECTIONAL ENTRY)" + " "
        other_remarks.strip()

        # Retrieve data
        data = list(part_no_data.values()) + list(manufacturing_data.values())
        data.append(other_remarks)
        data = data + list(label_data.values())
        col_name = ("part_no", "quantity", "date_code", "remarks", "additional_info", "label_type", "time_added")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.append(current_datetime)
        DB.insert("extra_labels", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")
    ##############################################################################################################
    def Reject_frame(self):
        body_frame = self.create_new_body()
        part_no_entry = (
            ("part_no", "entry", (0, 0, 1), None),
        )
        self.part_no_entries = EntriesFrame(body_frame, part_no_entry); self.part_no_entries.pack()
        self.part_no_entries.disable_all()
        # add search btn for part no name
        frame = self.part_no_entries.frames["part_no"]
        self.search_part_no = SearchWindow(select_btn=self.select_part_no, layout="Search Part No")
        ctk.CTkButton(frame, image="search_icon", text="", command=self.search_part_no.new_window, width=20).pack(
            side="left")
        entries = (
            ("traveller_no", "entry", (1, 0, 1), None),
            ("quantity", "entry", (2, 0, 1), None),
            ("uom", "menu", (3, 0, 1), ("PCS", "PANEL")),
            ("reason", "menu", (4, 0, 1), ('BL INCOMPRINT - IN55'     , 'BL MISSING - M17'        , 'BL OVERLAP - OP04'       , 'BL PEELING - P38'    , 'BL REVERSE - R10'        ,
                        'BL SHIFTED - S11'         , 'BL SMEARING - SM18'      , 'BL UNCLEAR - UC58'       , 'BROKEN - BR02'       , 'BURN - BN35'             ,
                        'CARBON INCOMPRINT - CIN49', 'CARBON JAGGED - CJ33'    , 'CARBON SHIFTED - CS26'   , 'CARBON SKIP - CSP50' , 'CARBON SMEARING - CSM48' ,
                        'DIRTY - DY25'             , 'FL INCOMPRINT - IN56'    , 'FL MISSING - M30'        , 'FL OVERLAP - OP36'   , 'FL PEELING - P39'        ,
                        'FL REVERSE - R31'         , 'FL SHIFTED - S37'        , 'FL SMEARING - SM16'      , 'FL UNCLEAR - UC59'   , 'INK HOLE - IH60'         ,
                        'LPSM INCOMPRINT - LP19'   , 'LPSM OVERLAP - LP45'     , 'LPSM OXIDISE - LP44'     , 'LPSM SHIFTED - LP06' , 'LPSM SMEARING - LP08'    ,
                        'LPSM UNEVEN - LP27'       , 'NICK - NK28'             , 'OPEN - OP40'             , 'OVER - OE23'         , 'OVERLAP - EOP51'         ,
                        'OXIDISE FLUX - OXF29'     , 'PIN MARK - PM53'         , 'POOR PLATING - PT24'     , 'PTH OPEN - OP61'     , 'PUNCH C-PAD - CP12'      ,
                        'PUNCH CRACK - CK07'       , 'PUNCH DENTED - DT03'     , 'PUNCH EXTRA - EXN47'     , 'PUNCH REVERSE - PR13', 'PUNCH SHIFTED - PS41'    ,
                        'SCRATCHES - SC01'         , 'SHORT - SR52'            , 'SM INCOMPRINT - IN22'    , 'SM OVERLAP - OP15'   , 'SM OXIDISE - OX05'       ,
                        'SM PEELING - P32'         , 'SM SHIFTED - S20'        , 'SM SMEARING - SM21'      , 'SM UNEVEN - UN27'    , 'STAIN - ST34'            ,
                        'UNDER - OE09'             , 'UNDERSIZE - US54'        , 'VCUT MISSING - VM43'     , 'VCUT SHIFTED - VS14' , 'VCUT SLANTING - VSL57'   ,
                        'VCUT UNEVEN - VUN42')),
            ("date", "date", (5, 0, 1), None),
        )
        self.rejection_entries = EntriesFrame(body_frame, entries) ; self.rejection_entries.pack()

        self.batch_rejection_sheet = Sheet(body_frame, show_x_scrollbar=False, height=150,
                                          headers=["Part No", "Traveller No", "Quantity", "UOM",
                                                   "Reason", "Date", "Time Added"])
        col_size = 150
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.batch_rejection_sheet.set_column_widths(column_widths=col_sizes)
        binding = ("single_select", "row_select",
                   "column_width_resize", "double_click_column_resize", "row_width_resize", "column_height_resize",
                   "row_height_resize", "double_click_row_resize")
        self.batch_rejection_sheet.enable_bindings(binding)
        self.batch_rejection_sheet.pack(fill="x", padx=4, pady=4)

        columns = ("part_no", "traveller_no", "quantity", "uom", "reason", "date", "time_added")
        data = DB.select("batch_rejection", columns, "1=1 ORDER BY id DESC LIMIT 50" )
        for row in data:
            self.batch_rejection_sheet.insert_row(values=row)

        self.create_footer(self.confirm_reject_btn)
    ###############        ###############        ###############        ###############
    def confirm_reject_btn(self):
        # Extract data from EntriesFrame instances
        part_no_data = self.part_no_entries.get_data()
        rejection_data = self.rejection_entries.get_data()

        # Retrieve data
        data = list(part_no_data.values()) + list(rejection_data.values())
        col_name = ("part_no", "traveller_no", "quantity", "uom", "reason", "date", "time_added")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.append(current_datetime)
        DB.insert("batch_rejection", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")
        self.batch_rejection_table.delete(*self.batch_rejection_table.get_children())
        data = DB.select("batch_rejection", ("part_no", "traveller_no", "quantity", "uom", "reason", "date", "time_added"), "1=1 ORDER BY id DESC LIMIT 50")

        # Filter and insert matching rows into the table
        for row in data:
            self.batch_rejection_table.insert("", "end", values=row)
    ##############################################################################################################
    def Tracker_frame(self):
        body_frame = self.create_new_body()
        ViewFrame(body_frame,["Batch Entry","Extra Labels" , "Reject Batch"])
    ##############################################################################################################
##############################################################################################################
class ProductionEntry(DB,Page):
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


