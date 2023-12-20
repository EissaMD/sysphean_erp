from config import *
from ..UI import Page, EntriesFrame
from ..Logics import DB 

class PartNo(Page):
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
                                                 "Cavity", "Customer", "Side", "Label Type"])
        col_size = 115
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.part_no_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = self.table_bindings
        self.part_no_view_sheet.enable_bindings(binding)
        self.part_no_view_sheet.pack(fill="x", padx=4, pady=4)
        if self.function == "Edit":
            self.part_no_view_sheet.bind("<ButtonRelease-1>", self.cell_select)

        part_info_data = DB.select("part_info", self.part_info_columns)
        for row_data in part_info_data:
            row_data[-1] = "Paper" if  row_data[-1] else "Sticker"
            row_data[-2] = "Single" if  row_data[-2] else "Double"
            self.part_no_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def filter_view_table(self, keyword):
        # Remove existing data from the table
        total_rows = self.part_no_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.part_no_view_sheet.delete_row(a)

        part_info_data = DB.select("part_info", self.part_info_columns, "part_no LIKE %s", ("%%" + keyword + "%%",))
        for row_data in part_info_data:
            row_data[-1] = "Paper" if  row_data[-1] else "Sticker"
            row_data[-2] = "Single" if  row_data[-2] else "Double"
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
##############################################################################################################
