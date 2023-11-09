import customtkinter as ctk
from .UI import Page, LeftMenu, EntriesFrame, SearchWindow
from .Logics import DB
import tkinter.ttk as ttk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from tkinter import filedialog
import pandas as pd
import numpy as np

class Manufacturing(Page):
    def __init__(self):
        self.create_new_page("Manufacturing")
        left_menu = LeftMenu()
        left_menu_ls = {
            "Part No": PartNo,
            "Batch Entry": Entry,
            "Production Entry": ProductionEntry,
        }
        left_menu.update_menu(left_menu_ls)


##############################################################################################################
class PartNo(DB,Page):
    def __init__(self):
        menu_ls = {
            "Add (Brief)": self.Add_brief_frame,
            "Add (Full)": self.Add_frame,
            "View": self.View_frame,
            "Edit/Delete": self.edit_frame,
        }
        self.create_new_page("Part No", menu_ls)
    ###############        ###############        ###############        ###############
    def Add_brief_frame(self):
        body_frame = self.create_new_body()
        brief_entries = (
            ("part_no", "entry", (0, 0, 3), None),
            ("uom", "menu", (4, 0, 3), ("PCS", "PANEL")),
            ("cavity", "entry", (5, 0, 3), None),
            ("customer", "entry", (6, 0, 3), None),
        )

        self.part_no_brief_entries = EntriesFrame(body_frame, brief_entries) ; self.part_no_brief_entries.pack()
        ctk.CTkButton(master=body_frame, text="Import Excel", command=self.import_excel_btn).pack(side="top", padx=10,
                                                                                                  pady=10)
        ctk.CTkLabel(master=body_frame, text="(For Import Excel, the format is Part No, Customer, Cavity, UOM.)",
                     width=50).pack(side="top", padx=10, pady=10)

        self.create_footer(self.confirm_brief_btn)
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
            same_results = self.select("part_info", ("part_no",), "part_no = ?", (part_no,))
            if same_results:
                messagebox.showinfo("Error", f"Part No, {part_no} already exists in the database!")
            else:
                duplicate_part_no_list = self.checkSimilarPartNos(part_no)
                dupePass = True
                if duplicate_part_no_list:
                    part_no_list_text = '\n'.join([f'* {part_no_similar}' for part_no_similar in duplicate_part_no_list])
                    ans = messagebox.askyesno("Warning",
                                              f"This partNo, {part_no} is similar to the following partNos:\n{part_no_list_text}\nDo you want to proceed?",
                                              icon='warning')
                    if not ans:
                        dupePass = False
                if not pd.isnull(part_no) and dupePass:
                    customer = row.iloc[1] if len(row) > 1 else ""
                    cavity = row.iloc[2] if len(row) > 2 else ""
                    uom = row.iloc[3] if len(row) > 3 else ""
                    self.add_new_part_no_excel(part_no, customer, cavity, uom)
    ###############        ###############        ###############        ###############
    def add_new_part_no_excel(self, part_no, customer, cavity, uom):
        col_name = ("part_no", "customer", "cavity", "uom")
        if cavity != None and uom != None:
            if customer == None:
                customer = ""
            self.insert("part_info", col_name, (part_no, customer, cavity, uom))
            messagebox.showinfo("Info", f"The process for adding partNo {part_no} was successful!")
        else:
            messagebox.showinfo("Error", f"\n* PartNo {part_no} has missing information regarding cavity and/or uom. Please recheck your Excel sheet and try again!")
    ##############        ###############        ###############        ###############
    def checkSimilarPartNos(self, part_no):
        part_no_list = []
        part_no_without_spaces = part_no.replace(" ", "")
        part_no_before_bracket = part_no.split("(", 1)[0] if "(" in part_no else None
        part_no_before_space = part_no.split(" ", 1)[0] if " " in part_no else None
        part_no_records = self.select("part_info", ("part_no",))
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
    def confirm_brief_btn(self):
        # Extract data from EntriesFrame instances
        part_no_brief_data = self.part_no_brief_entries.get_data()

        # Retrieve data
        data = list(part_no_brief_data.values())
        same_results = self.select("part_info", ("part_no",), "part_no = ?", (data[0],))
        if same_results:
            messagebox.showinfo("Error", f"Part No, {data[0]} already exists in the database!")
        else:
            duplicate_part_no_list = self.checkSimilarPartNos(data[0])
            dupePass = True
            if duplicate_part_no_list:
                part_no_list_text = '\n'.join([f'* {part_no_similar}' for part_no_similar in duplicate_part_no_list])
                ans = messagebox.askyesno("Warning",
                                          f"This partNo, {data[0]} is similar to the following partNos:\n{part_no_list_text}\nDo you want to proceed?",
                                          icon='warning')
                if not ans:
                    dupePass = False
            if dupePass:
                col_name = ("part_no", "uom", "cavity", "customer")
                self.insert("part_info", col_name, data)
                messagebox.showinfo("Info", f"The process for adding part_no {part_no_brief_data['part_no']} was successful!")
    ###############        ###############        ###############        ###############
    def Add_frame(self):
        body_frame = self.create_new_body()
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
        self.part_no_entries = EntriesFrame(body_frame, entries) ; self.part_no_entries.pack()
        self.create_footer(self.confirm_btn)
    ###############        ###############        ###############        ###############
    def confirm_btn(self):
        # Extract data from EntriesFrame instances
        part_no_data = self.part_no_entries.get_data()

        # Retrieve data
        data = list(part_no_data.values())
        same_results = self.select("part_info", ("part_no",), "part_no = ?", (data[0],))
        if same_results:
            messagebox.showinfo("Error", f"Part No, {data[0]} already exists in the database!")
        else:
            duplicate_part_no_list = self.checkSimilarPartNos(data[0])
            dupePass = True
            if duplicate_part_no_list:
                part_no_list_text = '\n'.join([f'* {part_no_similar}' for part_no_similar in duplicate_part_no_list])
                ans = messagebox.askyesno("Warning",
                                          f"This partNo, {data[0]} is similar to the following partNos:\n{part_no_list_text}\nDo you want to proceed?",
                                          icon='warning')
                if not ans:
                    dupePass = False
            if dupePass:
                col_name = ("part_no", "bundle_qty", "stn_carton", "stn_qty", "uom", "cavity", "customer", "single_sided", "paper_label")
                self.insert("part_info", col_name, data)
                stn_qty_for_main_inventory = 0
                if data[4] == "PCS":
                    stn_qty_for_main_inventory = int(data[3]) * int(data[5])
                else:
                    stn_qty_for_main_inventory = int(data[3])
                self.insert("main_inventory", ("part_no","carton_quantity","sealed_quantity","stn_qty","total_stock"), (data[0],0,0,stn_qty_for_main_inventory,0))
                messagebox.showinfo("Info", "The process was successful!")
    ###############        ###############        ###############        ###############
    def View_frame(self):
        body_frame = self.create_new_body()

        # Create a horizontal frame to hold filter label and entry
        filter_frame = ctk.CTkFrame(body_frame)
        filter_frame.pack(side='top', fill='x', padx=10, pady=10)

        filter_label = ctk.CTkLabel(filter_frame, text="Part No:")
        filter_label.pack(side='left', padx=10, pady=10)  # Place label on the left side

        filter_entry = ctk.CTkEntry(filter_frame, width=450)
        filter_entry.pack(side='left', padx=10, pady=10)  # Place entry widget next to the label

        search_button = ctk.CTkButton(filter_frame, text="Search",
                                      command=lambda: self.filter_table(table, filter_entry.get()))
        search_button.pack(side='left')

        # Create a Treeview widget to display the data
        columns = ("id", "part_no", "bundle_qty", "stn_carton", "stn_qty", "uom", "cavity", "customer", "single_sided", "paper_label")

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
        column_widths = [10, 100, 50, 50, 50, 20, 20, 100, 50, 50]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        # Retrieve data from the database and populate the table
        data = self.select("part_info", columns)
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
        columns = ("id", "part_no", "bundle_qty", "stn_carton", "stn_qty", "uom", "cavity", "customer", "single_sided", "paper_label")
        data = self.select("part_info", columns, "part_no LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)
    ###############        ###############        ###############        ###############
    def edit_frame(self):
        body_frame = self.create_new_body()

        # Create a LabelFrame for selection and editing
        filter_frame = ctk.CTkFrame(body_frame)
        filter_frame.pack(side='top', fill='x', padx=10, pady=10)

        part_no_entry = (
            ("part_no", "entry", (0, 0, 1), None),
        )
        self.part_no_entries = EntriesFrame(filter_frame, part_no_entry);
        self.part_no_entries.pack(padx=10, pady=10, side='left')
        self.part_no_entries.disable_all()
        # add search btn for part no name
        frame = self.part_no_entries.frames["part_no"]
        self.search_part_no = SearchWindow(select_btn=self.select_part_no, layout="Search Part No")
        ctk.CTkButton(frame, image="search_icon", text="", command=self.search_part_no.new_window, width=20).pack(
            side="left")

        # Create a Button to trigger editing
        edit_button = ttk.Button(filter_frame, text="Edit",
                                 command=lambda: self.edit_part_no(self.part_no_entries.get_data()["part_no"]))
        edit_button.pack(padx=10, pady=10, side='left')

        # Create a Button to trigger deletion
        delete_button = ttk.Button(filter_frame, text="Delete",
                                   command=lambda: self.delete_part_no(self.part_no_entries.get_data()["part_no"]))
        delete_button.pack(padx=10, pady=10, side='left')

        # Create a frame to display entry fields for editing
        self.edit_part_no_frame = ttk.LabelFrame(body_frame, text="Edit Part No")
        self.edit_part_no_frame.pack(padx=10, pady=10, fill="both", expand=True)

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

    ###############        ###############        ###############        ###############
    def edit_part_no(self, selected_entry):
        # Clear previous entry fields
        for widget in self.edit_part_no_frame.winfo_children():
            widget.destroy()

        entry_id = str(selected_entry)
        retrieved_values = self.select("part_info", ["*"], "part_no=?", (entry_id,))
        # Retrieve data for the selected entry
        entry_data = [
            ("part_no", "entry", (0, 0, 3), None),
            ("bundle_qty", "entry", (1, 0, 3), None),
            ("stn_carton", "menu", (2, 0, 3), ("8", "7", "6", "14", "10", "9", "12", "15", "JIG CARTON")),
            ("stn_qty", "entry", (3, 0, 3), None),
            ("uom", "menu", (4, 0, 3), ("PCS", "PANEL")),
            ("cavity", "entry", (5, 0, 3), None),
            ("customer", "entry", (6, 0, 3), None),
            ("single_sided", "menu", (7, 0, 3), ("Single", "Double")),
            ("paper_label", "menu", (8, 0, 3), ("Paper", "Sticker")),
        ]
        self.part_no_edit_entries = EntriesFrame(self.edit_part_no_frame, entry_data)
        self.part_no_edit_entries.pack()

        if entry_data:
            # Create EntryFrame for editing
            self.part_no_edit_entries.change_value("part_no", retrieved_values[0][1])
            self.part_no_edit_entries.change_value("bundle_qty", retrieved_values[0][2])
            self.part_no_edit_entries.change_value("stn_carton", retrieved_values[0][3])
            self.part_no_edit_entries.change_value("stn_qty", retrieved_values[0][4])
            self.part_no_edit_entries.change_value("uom", retrieved_values[0][5])
            self.part_no_edit_entries.change_value("cavity", retrieved_values[0][6])
            self.part_no_edit_entries.change_value("customer", retrieved_values[0][7])
            self.part_no_edit_entries.change_value("single_sided", retrieved_values[0][8])
            self.part_no_edit_entries.change_value("paper_label", retrieved_values[0][9])

            # Create Save button to update the entry
            save_button = ttk.Button(self.edit_part_no_frame, text="Save Changes",
                                     command=lambda: self.save_part_no(entry_id))
            save_button.pack()

    ###############        ###############        ###############        ###############
    def delete_part_no(self, selected_entry):
        if selected_entry.startswith("Select Part No"):
            return

        # Prompt confirmation box before deletion
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this partNo?",
                                        icon="warning")
        if result == "yes":
            entry_id = str(selected_entry)
            self.delete("part_info", conditions="part_no=?", values=(entry_id,))
            messagebox.showinfo("Info", "Part No deleted successfully")

            # Clear entry fields after deletion
            for widget in self.edit_part_no_frame.winfo_children():
                widget.destroy()
    ###############        ###############        ###############        ###############
    def save_part_no(self, entry_id):
        # Extract data from EntriesFrame instances
        edited_part_no_data = self.part_no_edit_entries.get_data()

        # Update data in the database
        col_names = list(edited_part_no_data.keys())
        col_values = list(edited_part_no_data.values()) + [entry_id]
        self.update("part_info", col_names, conditions="part_no=?", values=col_values)
        messagebox.showinfo("Info", "Part No updated successfully")
##############################################################################################################
class Entry(DB,Page):
    def __init__(self):
        menu_ls = {
            "New Batch": self.Add_frame,
            "Batch Tracker": self.View_frame,
            "Extra Labels": self.Extra_frame,
            "Extra Labels Tracker": self.Extra_View_frame,
            "Batch Rejection": self.Reject_frame,
            "Batch Rejection Tracker": self.Reject_View_frame
        }

        self.create_new_page("Batch Entry", menu_ls)

    ###############        ###############        ###############        ###############
    def Add_frame(self):
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
            ("has_expiry_date", "seg_btn", (1, 0 , 1), ["No", "Yes"]),
            ("expiry_date", "date", (2, 0, 1), None),
            ("has_manufacturing_date", "seg_btn", (3, 0, 1), ["No", "Yes"]),
            ("manufacturing_date", "date", (4, 0, 1), None),
            ("has_packing_date", "seg_btn", (5, 0, 1), ["No", "Yes"]),
            ("packing_date", "date", (6, 0, 1), None),
        )
        self.date_entries = EntriesFrame(body_frame, date_entries);
        self.date_entries.pack()
        correctional_entries = (
            ("correctional_entry", "seg_btn", (1, 0, 1), ["No", "Yes"]),
        )
        self.correctional_entries = EntriesFrame(body_frame, correctional_entries);
        self.correctional_entries.pack()

        columns = ("bundle_qty", "stn_carton", "stn_qty", "uom", "cavity", "customer", "single_sided",
                   "paper_label")
        self.part_no_table = ttk.Treeview(body_frame, columns=columns, show='headings')
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
        column_widths = [20, 20, 20, 20, 20, 20, 20, 20]
        for col, width in zip(columns, column_widths):
            self.part_no_table.heading(col, text=col)
            self.part_no_table.column(col, width=width)

        # Reduce the height of the table to show only one row
        self.part_no_table["height"] = 1
        # Pack the table to display
        self.part_no_table.pack(fill="both", expand=True)

        self.create_footer(self.confirm_btn)

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
        # Remove existing data from the table
        if not self.batch_rejection_table:
            self.part_no_table.delete(*self.part_no_table.get_children())
            data = self.select("part_info", ("bundle_qty", "stn_carton", "stn_qty", "uom", "cavity", "customer", "single_sided",
                       "paper_label"), "part_no = ?", (selected_row[1],))
            for row in data:
                self.part_no_table.insert("", "end", values=row)
    ###############        ###############        ###############        ###############
    def confirm_btn(self):
        # Extract data from EntriesFrame instances
        part_no_data = self.part_no_entries.get_data()
        manufacturing_data = self.manufacturing_entries.get_data()
        date_data = self.date_entries.get_data()
        correctional_data = self.correctional_entries.get_data()

        other_remarks = ""

        if date_data["has_expiry_date"] == "Yes":
            other_remarks += "EXP=" + str(date_data["expiry_date"]) + " "
        if date_data["has_manufacturing_date"] == "Yes":
            other_remarks += "MFG=" + str(date_data["manufacturing_date"]) + " "
        if date_data["has_packing_date"] == "Yes":
            other_remarks += "PKD=" + str(date_data["packing_date"]) + " "
        if correctional_data["correctional_entry"] == "Yes":
            other_remarks += "(CORRECTIONAL ENTRY)" + " "
        other_remarks.strip()

        # Retrieve data
        data = list(part_no_data.values()) + list(manufacturing_data.values())
        data.append(other_remarks)
        col_name = ("part_no", "quantity", "date_code", "remarks", "additional_info", "time_added")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.append(current_datetime)
        self.insert("manufacturing", col_name, data)
        part_info = self.select("part_info", ["stn_qty", "uom", "cavity"], "part_no=?", (data[0],))
        total_quantity = int(data[1])
        if part_info[0][1] == "PCS":
            total_quantity *= int(part_info[0][2])
        total_filled_cartons = total_quantity // int(part_info[0][0])
        total_sealed_quantity = total_quantity % int(part_info[0][0])
        main_inventory_data =  self.select("main_inventory", ["carton_quantity", "sealed_quantity", "total_stock"], "part_no=?", (data[0],))
        total_filled_cartons += int(main_inventory_data[0][0])
        total_sealed_quantity += int(main_inventory_data[0][1])
        total_quantity += int(main_inventory_data[0][2])
        while total_sealed_quantity >= int(part_info[0][0]):
            total_sealed_quantity -= int(part_info[0][0])
            total_filled_cartons += 1
        self.update("main_inventory", ["carton_quantity", "sealed_quantity", "total_stock"], "part_no=?", (total_filled_cartons,total_sealed_quantity,total_quantity,data[0]))
        messagebox.showinfo("Info", "The process was successful!")
    ##############################################################################################################
    def View_frame(self):
        body_frame = self.create_new_body()

        # Create a horizontal frame to hold filter label and entry
        filter_frame = ctk.CTkFrame(body_frame)
        filter_frame.pack(side='top', fill='x', padx=10, pady=10)

        filter_label = ctk.CTkLabel(filter_frame, text="Part No:")
        filter_label.pack(side='left', padx=10, pady=10)  # Place label on the left side

        filter_entry = ctk.CTkEntry(filter_frame, width=450)
        filter_entry.pack(side='left', padx=10, pady=10)  # Place entry widget next to the label

        search_button = ctk.CTkButton(filter_frame, text="Search",
                                      command=lambda: self.filter_table(table, filter_entry.get()))
        search_button.pack(side='left')

        # Create a Treeview widget to display the data
        columns = ("id", "part_no", "quantity", "date_code", "remarks", "additional_info", "time_added")

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
        column_widths = [10, 100, 100, 100, 100, 100, 100]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        # Retrieve data from the database and populate the table
        data = self.select("manufacturing", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)

    ##############################################################################################################
    def filter_table(self, table, keyword):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = ("id", "part_no", "quantity", "date_code", "remarks", "additional_info", "time_added")
        data = self.select("manufacturing", columns, "part_no LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)
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
            ("has_expiry_date", "seg_btn", (1, 0 , 1), ["No", "Yes"]),
            ("expiry_date", "date", (2, 0, 1), None),
            ("has_manufacturing_date", "seg_btn", (3, 0, 1), ["No", "Yes"]),
            ("manufacturing_date", "date", (4, 0, 1), None),
            ("has_packing_date", "seg_btn", (5, 0, 1), ["No", "Yes"]),
            ("packing_date", "date", (6, 0, 1), None),
        )
        self.date_entries = EntriesFrame(body_frame, date_entries);
        self.date_entries.pack()
        correctional_entries = (
            ("correctional_entry", "seg_btn", (1, 0, 1), ["No", "Yes"]),
        )
        self.correctional_entries = EntriesFrame(body_frame, correctional_entries);
        self.correctional_entries.pack()
        columns = ("bundle_qty", "stn_carton", "stn_qty", "uom", "cavity", "customer", "single_sided",
                   "paper_label")
        self.part_no_table = ttk.Treeview(body_frame, columns=columns, show='headings')
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
        column_widths = [10, 100, 50, 50, 50, 20, 20, 100, 50, 50]
        for col, width in zip(columns, column_widths):
            self.part_no_table.heading(col, text=col)
            self.part_no_table.column(col, width=width)

        # Reduce the height of the table to show only one row
        self.part_no_table["height"] = 1
        # Pack the table to display
        self.part_no_table.pack(fill="both", expand=True)
        self.create_footer(self.confirm_extra_btn)

    ###############        ###############        ###############        ###############
    def confirm_extra_btn(self):
        # Extract data from EntriesFrame instances
        part_no_data = self.part_no_entries.get_data()
        manufacturing_data = self.manufacturing_entries.get_data()
        date_data = self.date_entries.get_data()
        correctional_data = self.correctional_entries.get_data()

        other_remarks = ""

        if date_data["has_expiry_date"] == "Yes":
            other_remarks += "EXP=" + str(date_data["expiry_date"]) + " "
        if date_data["has_manufacturing_date"] == "Yes":
            other_remarks += "MFG=" + str(date_data["manufacturing_date"]) + " "
        if date_data["has_packing_date"] == "Yes":
            other_remarks += "PKD=" + str(date_data["packing_date"]) + " "
        if correctional_data["correctional_entry"] == "Yes":
            other_remarks += "(CORRECTIONAL ENTRY)" + " "
        other_remarks.strip()

        # Retrieve data
        data = list(part_no_data.values()) + list(manufacturing_data.values())
        data.append(other_remarks)
        col_name = ("part_no", "quantity", "date_code", "remarks", "additional_info", "time_added")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.append(current_datetime)
        self.insert("extra_labels", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")

    ##############################################################################################################
    def Extra_View_frame(self):
        body_frame = self.create_new_body()

        # Create a horizontal frame to hold filter label and entry
        filter_frame = ctk.CTkFrame(body_frame)
        filter_frame.pack(side='top', fill='x', padx=10, pady=10)

        filter_label = ctk.CTkLabel(filter_frame, text="Part No:")
        filter_label.pack(side='left', padx=10, pady=10)  # Place label on the left side

        filter_entry = ctk.CTkEntry(filter_frame, width=450)
        filter_entry.pack(side='left', padx=10, pady=10)  # Place entry widget next to the label

        search_button = ctk.CTkButton(filter_frame, text="Search",
                                      command=lambda: self.filter_extra_table(table, filter_entry.get()))
        search_button.pack(side='left')

        # Create a Treeview widget to display the data
        columns = ("id", "part_no", "quantity", "date_code", "remarks", "additional_info", "time_added")

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
        column_widths = [20, 20, 20, 20, 20, 20, 20, 20]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        # Retrieve data from the database and populate the table
        data = self.select("extra_labels", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)

    ##############################################################################################################
    def filter_extra_table(self, table, keyword):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = ("id", "part_no", "quantity", "date_code", "remarks", "additional_info", "time_added")
        data = self.select("extra_labels", columns, "part_no LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)

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
        columns = ("part_no", "traveller_no", "quantity", "uom", "reason", "date", "time_added")
        self.batch_rejection_table = ttk.Treeview(body_frame, columns=columns, show='headings')
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
        column_widths = [20, 20, 10, 10, 20, 20, 20]
        for col, width in zip(columns, column_widths):
            self.batch_rejection_table.heading(col, text=col)
            self.batch_rejection_table.column(col, width=width)

        # Reduce the height of the table to show only one row
        self.batch_rejection_table["height"] = 5
        # Pack the table to display
        self.batch_rejection_table.pack(fill="both", expand=True)
        data = self.select("batch_rejection", columns, "1=1 ORDER BY id DESC LIMIT 50" )

        # Filter and insert matching rows into the table
        for row in data:
            self.batch_rejection_table.insert("", "end", values=row)
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
        self.insert("batch_rejection", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")
        self.batch_rejection_table.delete(*self.batch_rejection_table.get_children())
        data = self.select("batch_rejection", ("part_no", "traveller_no", "quantity", "uom", "reason", "date", "time_added"), "1=1 ORDER BY id DESC LIMIT 50")

        # Filter and insert matching rows into the table
        for row in data:
            self.batch_rejection_table.insert("", "end", values=row)

    ##############################################################################################################
    def Reject_View_frame(self):
        body_frame = self.create_new_body()

        # Create a horizontal frame to hold filter label and entry
        filter_frame = ctk.CTkFrame(body_frame)
        filter_frame.pack(side='top', fill='x', padx=10, pady=10)

        filter_label = ctk.CTkLabel(filter_frame, text="Part No:")
        filter_label.pack(side='left', padx=10, pady=10)  # Place label on the left side

        filter_entry = ctk.CTkEntry(filter_frame, width=450)
        filter_entry.pack(side='left', padx=10, pady=10)  # Place entry widget next to the label

        search_button = ctk.CTkButton(filter_frame, text="Search",
                                      command=lambda: self.filter_reject_table(table, filter_entry.get()))
        search_button.pack(side='left')

        # Create a Treeview widget to display the data
        columns = ("id", "part_no", "traveller_no", "quantity", "uom", "reason", "date", "time_added")

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
        column_widths = [10, 100, 100, 100, 100, 100, 100, 100]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        # Retrieve data from the database and populate the table
        data = self.select("batch_rejection", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)

    ##############################################################################################################
    def filter_reject_table(self, table, keyword):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = ("id", "part_no", "traveller_no", "quantity", "uom", "reason", "date", "time_added")
        data = self.select("batch_rejection", columns, "part_no LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)

    ##############################################################################################################
    ##############################################################################################################
    #######################################UNUSED FUNCTIONS#######################################################
    ##############################################################################################################
    ##############################################################################################################
    def get_part_no_list(self):
        # Retrieve and format purchase orders from your data source
        entries = self.select("part_info", ["part_no", "stn_qty", "uom", "cavity"], "1=1 ORDER BY part_no")
        purchase_names = [f"{entry[0].strip()} Info: ({entry[1]}/{entry[2]}/{entry[3]})" for entry in
                          entries]
        return purchase_names
    ##############################################################################################################
    def Main_Inventory_frame(self):
        body_frame = self.create_new_body()

        # Create a horizontal frame to hold filter label and entry
        filter_frame = ctk.CTkFrame(body_frame)
        filter_frame.pack(side='top', fill='x', padx=10, pady=10)

        filter_label = ctk.CTkLabel(filter_frame, text="Part No:")
        filter_label.pack(side='left')  # Place label on the left side

        filter_entry = ctk.CTkEntry(filter_frame)
        filter_entry.pack(side='left')  # Place entry widget next to the label

        search_button = ctk.CTkButton(filter_frame, text="Search",
                                      command=lambda: self.filter_main_inventory_table(table, filter_entry.get()))
        search_button.pack(side='left')  # Place search button next to the entry widget

        # Create a Treeview widget to display the data
        columns = ("id", "part_no", "carton_quantity", "sealed_quantity", "stn_qty", "total_stock")

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
        column_widths = [10, 75, 75, 75, 75, 75]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        # Retrieve data from the database and populate the table
        data = self.select("main_inventory", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)
    ##############################################################################################################
    def filter_main_inventory_table(self, table, keyword):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = ("id", "part_no", "carton_quantity", "sealed_quantity", "stn_qty", "total_stock")
        data = self.select("main_inventory", columns, "part_no LIKE ?", ("%%" + keyword + "%%",))

        # Filter and insert matching rows into the table
        for row in data:
            if keyword.lower() in row[1].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)
##############################################################################################################

    # db.insert("purchase_requisition", ("item_description", "quantity", "credit_limit"), ("john", "john@example.com", "2000"), )
class ProductionEntry(DB,Page):
    def __init__(self):
        menu_ls = {
            "Add": self.Add_frame,
            "View": self.View_frame,
            "Edit/Delete": self.edit_frame,
        }
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
        columns = ("id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected", "quantity_balance", "remarks", "time_added")
        self.production_entry_table = ttk.Treeview(body_frame, columns=columns, show='headings')
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
        column_widths = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
        for col, width in zip(columns, column_widths):
            self.production_entry_table.heading(col, text=col)
            self.production_entry_table.column(col, width=width)

        self.production_entry_table["height"] = 3
        # Pack the table to display
        self.production_entry_table.pack(fill="both", expand=True)
        data = self.select(f"{self.table_type}", columns)

        # Filter and insert matching rows into the table
        for row in data:
            self.production_entry_table.insert("", "end", values=row)

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
                                      command=lambda: self.filter_table(self.production_entry_table, filter_traveller_no_entry.get(),
                                                                        filter_part_no_entry.get(),
                                                                        filter_department_entry.get()))
        search_button.grid(row=0, column=2, padx=10)
        reset_button = ctk.CTkButton(filter_frame, text="Reset",
                                     command=lambda: self.reset_filters(self.production_entry_table, filter_traveller_no_entry,
                                                                        filter_part_no_entry,
                                                                        filter_department_entry))
        reset_button.grid(row=1, column=2, padx=10)
        switch_button = ctk.CTkButton(filter_frame, text="Switch (Combined)",
                                     command=lambda: self.switch_table(self.production_entry_table, switch_button))
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
        recent_quantity_balance_same_dept = self.select("production_entry", ("quantity_balance",), "traveller_no = ? AND department = ? ORDER BY time_added DESC", (str(traveller_data["traveller_no"]), str(production_data["department"])))
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
        self.insert("production_entry", col_name, data)
        traveller_combined_info = self.select("production_entry_combined", ("id","quantity_received","quantity_output","quantity_rejected","remarks"), "traveller_no = ? AND part_no = ? AND department = ?",
                                            (traveller_data["traveller_no"], part_no_data["part_no"], production_data["department"]))
        if traveller_combined_info:
            traveller_combined_id = traveller_combined_info[0][0]
            quantity_received = traveller_combined_info[0][1]
            quantity_output = traveller_combined_info[0][2]
            quantity_rejected = traveller_combined_info[0][3]
            remarks = traveller_combined_info[0][4]
            remarks += production_data["remarks"]
            self.update("production_entry_combined", ("quantity_received", "quantity_output", "quantity_rejected", "quantity_balance", "remarks"), "id = ?",
                        (int(quantity_received + int(production_data['quantity_received'])), int(quantity_output + int(production_data['quantity_output'])),
                         int(quantity_rejected + int(production_data['quantity_rejected'])), quantity_balance, remarks, traveller_combined_id))
        else:
            self.insert("production_entry_combined", col_name, data)
        messagebox.showinfo("Info", "The process was successful!")
        data = self.select(f"{self.table_type}", ("id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected", "quantity_balance", "remarks", "time_added"))
        self.production_entry_table.delete(*self.production_entry_table.get_children())
        # Filter and insert matching rows into the table
        for row in data:
            self.production_entry_table.insert("", "end", values=row)
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
                                      command=lambda: self.filter_table(table, filter_traveller_no_entry.get(), filter_part_no_entry.get(), filter_department_entry.get()))
        search_button.grid(row=0, column=2, padx=10)
        reset_button = ctk.CTkButton(filter_frame, text="Reset",
                                      command=lambda: self.reset_filters(table, filter_traveller_no_entry, filter_part_no_entry, filter_department_entry))
        reset_button.grid(row=1, column=2, padx=10)
        switch_button = ctk.CTkButton(filter_frame, text="Switch (Combined)",
                                      command=lambda: self.switch_table(table, switch_button))
        if self.table_type == "production_entry":
            switch_button.configure(text="Switch (Individual)")
        switch_button.grid(row=2, column=2, padx=10)

        # Create a Treeview widget to display the data
        columns = ("id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected", "quantity_balance", "remarks", "time_added")

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
        column_widths = [10, 150, 150, 100, 100, 100, 100, 100, 200, 150]
        for col, width in zip(columns, column_widths):
            table.heading(col, text=col)
            table.column(col, width=width)

        # Retrieve data from the database and populate the table
        data = self.select(f"{self.table_type}", columns)
        for row in data:
            table.insert("", "end", values=row)

        # Pack the table to display
        table.pack(fill="both", expand=True)

        # Attach the scrollbar to the table
        x_sroller.configure(command=table.xview)
    ###############        ###############        ###############        ###############
    def reset_filters(self, table, entry1, entry2, entry3):
        # Remove existing data from the table
        table.delete(*table.get_children())

        entry1.delete(0, tk.END)
        entry2.delete(0, tk.END)
        entry3.delete(0, tk.END)

        # Get all data from the database
        columns = ("id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected", "quantity_balance", "remarks", "time_added")
        data = self.select(f"{self.table_type}", columns)
        # Filter and insert matching rows into the table
        for row in data:
            table.insert("", "end", values=row)

    ###############        ###############        ###############        ###############
    def filter_table(self, table, keyword1, keyword2, keyword3):
        # Remove existing data from the table
        table.delete(*table.get_children())

        # Get all data from the database
        columns = ("id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected", "quantity_balance", "remarks", "time_added")
        keywords1 = "%%" + keyword1 + "%%"
        keywords2 = "%%" + keyword2 + "%%"
        keywords3 = "%%" + keyword3 + "%%"
        data = self.select(f"{self.table_type}", columns, "traveller_no LIKE ? AND part_no LIKE ? AND department LIKE ?", (keywords1,keywords2,keywords3))
        # Filter and insert matching rows into the table
        for row in data:
            if keyword1.lower() in row[1].lower() and keyword2.lower() in row[2].lower() and keyword3.lower() in row[3].lower():  # Case-insensitive search in item_description column
                table.insert("", "end", values=row)

    ###############        ###############        ###############        ###############
    def switch_table (self, table, switch_button):
        if self.table_type == "production_entry_combined":
            self.table_type = "production_entry"
            switch_button.configure(text="Switch (Individual)")
        else:
            self.table_type = "production_entry_combined"
            switch_button.configure(text="Switch (Combined)")
        table.delete(*table.get_children())
        columns = (
        "id", "traveller_no", "part_no", "department", "quantity_received", "quantity_output", "quantity_rejected",
        "quantity_balance", "remarks", "time_added")
        data = self.select(f"{self.table_type}", columns)
        # Filter and insert matching rows into the table
        for row in data:
            table.insert("", "end", values=row)

    ###############        ###############        ###############        ###############
    def edit_frame(self):
        body_frame = self.create_new_body()

        # Create a horizontal frame to hold filter label and entry
        filter_frame = ctk.CTkFrame(body_frame)
        filter_frame.pack(side='top', fill='x', padx=10, pady=10)

        # Create a LabelFrame for selection and editing
        selection_frame = ctk.CTkLabel(filter_frame, text="Select Traveller Entry to Edit")
        selection_frame.pack(side='top', fill='x', padx=10, pady=10)

        entries = self.select("production_entry", ["id","traveller_no","part_no","department","quantity_received","quantity_output","quantity_rejected"])
        selected_entry = tk.StringVar()
        selected_entry.set("Select an entry")

        # Strip leading/trailing spaces from entry names
        entry_options = [f"{entry[0]}/{entry[1]}/{entry[2][:10] + '...' if len(entry[2]) > 10 else entry[2]}/{entry[3]}/{entry[4]}/{entry[5]}/{entry[6]}" for entry in entries]

        # Create the Combobox
        self.entry_combobox = ttk.Combobox(filter_frame, values=entry_options, state="readonly", width=75)
        self.entry_combobox.pack(side='left', padx=10, pady=10)

        # Create a Button to trigger editing
        edit_button = ttk.Button(filter_frame, text="Edit",
                                 command=lambda: self.edit_traveller_entry(self.entry_combobox.get()))
        edit_button.pack(side='left', padx=10, pady=10)

        # Create a Button to trigger deletion
        delete_button = ttk.Button(filter_frame, text="Delete",
                                   command=lambda: self.delete_traveller_entry(self.entry_combobox.get()))
        delete_button.pack(side='left', padx=10, pady=10)

        # Create a frame to display entry fields for editing
        self.edit_traveller_frame = ttk.LabelFrame(body_frame, text="Edit Traveller")
        self.edit_traveller_frame.pack(padx=10, pady=10, fill="both", expand=True)

    ###############        ###############        ###############        ###############
    def edit_traveller_entry(self, selected_entry):
        if selected_entry.startswith("Select Traveller Entry"):
            return

        # Clear previous entry fields
        for widget in self.edit_traveller_frame.winfo_children():
            widget.destroy()

        entry_id = str(selected_entry).split('/')[0]
        retrieved_values = self.select("production_entry", ["*"], "id=?", (entry_id,))
        # Retrieve data for the selected entry
        entry_data = [
            ("traveller_no", "entry", (0, 0, 3), None),
            ("part_no", "entry", (1, 0, 3), None),
            ("department", "entry", (2, 0, 3), None),
            ("quantity_received", "entry", (3, 0, 3), None),
            ("quantity_output", "entry", (4, 0, 3), None),
            ("quantity_rejected", "entry", (5, 0, 3), None),
            ("remarks", "entry", (6, 0, 3), None),
            ("time_added", "entry", (7, 0, 3), None),
        ]
        self.production_entries = EntriesFrame(self.edit_traveller_frame, entry_data)
        self.production_entries.pack()

        if entry_data:
            # Create EntryFrame for editing
            self.production_entries.change_and_disable("traveller_no", retrieved_values[0][1])
            self.production_entries.change_and_disable("part_no", retrieved_values[0][2])
            self.production_entries.change_and_disable("department", retrieved_values[0][3])
            self.production_entries.change_value("quantity_received", retrieved_values[0][4])
            self.production_entries.change_value("quantity_output", retrieved_values[0][5])
            self.production_entries.change_value("quantity_rejected", retrieved_values[0][6])
            self.production_entries.change_value("remarks", retrieved_values[0][8])
            self.production_entries.change_and_disable("time_added", retrieved_values[0][9])

            # Create Save button to update the entry
            save_button = ttk.Button(self.edit_traveller_frame, text="Save Changes",
                                     command=lambda: self.save_traveller_entry(entry_id))
            save_button.pack()

    ###############        ###############        ###############        ###############
    def delete_traveller_entry(self, selected_entry):
        if selected_entry.startswith("Select Traveller Entry"):
            return

        # Prompt confirmation box before deletion
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this traveller entry?",
                                        icon="warning")
        if result == "yes":
            entry_id = str(selected_entry).split('/')[0]
            original_quantities = self.select("production_entry", ("quantity_received", "quantity_output", "quantity_rejected", "quantity_balance",
                                             "traveller_no", "part_no", "department"), "id = ?", (entry_id,))

            # Calculate changes (which will be negative values)
            quantity_received_change = -int(original_quantities[0][0])
            quantity_output_change = -int(original_quantities[0][1])
            quantity_rejected_change = -int(original_quantities[0][2])
            quantity_balance_change = int(original_quantities[0][3])
            traveller_no = original_quantities[0][4]
            part_no = original_quantities[0][5]
            department = original_quantities[0][6]
            self.delete("production_entry", conditions="id=?", values=(entry_id,))
            # Get the corresponding entry in production_entry_combined
            traveller_combined_info = self.select("production_entry_combined", ("id","quantity_received","quantity_output","quantity_rejected",
                "quantity_balance"), ("traveller_no = ? AND part_no = ? AND department = ?"),
                        (traveller_no, part_no, department))
            if traveller_combined_info:
                combined_id = int(traveller_combined_info[0][0])
                self.update("production_entry_combined", ("quantity_received","quantity_output","quantity_rejected",
                "quantity_balance"), "id = ?", (int(traveller_combined_info[0][1])+int(quantity_received_change),
                int(traveller_combined_info[0][2])+int(quantity_output_change),int(traveller_combined_info[0][3])+int(quantity_rejected_change),
                int(traveller_combined_info[0][4])+int(quantity_balance_change),combined_id))
                traveller_combined_info = self.select("production_entry_combined", ("quantity_received","quantity_output", "quantity_rejected"), "id = ?",
                            (combined_id,))
                quantity_received_combined, quantity_output_combined, quantity_rejected_combined = traveller_combined_info[0]

                # Check if all quantities are zero, and if so, delete the combined entry
                if quantity_received_combined == 0 and quantity_output_combined == 0 and quantity_rejected_combined == 0:
                    self.delete("production_entry_combined", "id = ?", (combined_id,))
            messagebox.showinfo("Info", "Traveller Entry deleted successfully")

            # Remove deleted entry from the dropdown menu
            self.entry_combobox['values'] = [value for value in self.entry_combobox['values'] if
                                             value != selected_entry]
            self.entry_combobox.set("Select Traveller Entry")  # Reset the selected entry

            # Clear entry fields after deletion
            for widget in self.edit_traveller_frame.winfo_children():
                widget.destroy()

    ###############        ###############        ###############        ###############
    def save_traveller_entry(self, entry_id):
        # Extract data from EntriesFrame instances
        edited_production_data = self.production_entries.get_data()

        recent_quantity_balance_same_dept = self.select("production_entry", ("quantity_balance",), ("traveller_no = ? AND department = ? AND time_added < ?"), (
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
        original_quantities = self.select("production_entry", ("quantity_received", "quantity_output", "quantity_rejected", "quantity_balance"),
                    "id = ?", (entry_id,))
        quantity_received_change = int(edited_production_data["quantity_received"]) - int(original_quantities[0][0])
        quantity_output_change = int(edited_production_data["quantity_output"]) - int(original_quantities[0][1])
        quantity_rejected_change = int(edited_production_data["quantity_rejected"]) - int(original_quantities[0][2])
        quantity_balance_change = int(quantity_balance) - int(original_quantities[0][3])
        self.update("production_entry", ("traveller_no","part_no","department","quantity_received","quantity_output",
                                           "quantity_rejected","quantity_balance","remarks"), "id = ?", (edited_production_data["traveller_no"],
            edited_production_data["part_no"], edited_production_data["department"], edited_production_data["quantity_received"],
            edited_production_data["quantity_output"], edited_production_data["quantity_rejected"], quantity_balance, edited_production_data["remarks"], entry_id))
        traveller_combined_info = self.select("production_entry_combined", ("id","quantity_received","quantity_output","quantity_rejected",
            "quantity_balance"), ("traveller_no = ? AND part_no = ? AND department = ?"),
                    (edited_production_data["traveller_no"],edited_production_data["part_no"],edited_production_data["department"]))
        if traveller_combined_info:
            traveller_combined_id = traveller_combined_info[0][0]
            quantity_received = traveller_combined_info[0][1]
            quantity_output = traveller_combined_info[0][2]
            quantity_rejected = traveller_combined_info[0][3]
            quantity_balance = traveller_combined_info[0][4]
            self.update("production_entry_combined", ("quantity_received", "quantity_output", "quantity_rejected",
            "quantity_balance", "remarks"), "id = ?", (int(quantity_received) + int(quantity_received_change),
            int(quantity_output) + int(quantity_output_change), int(quantity_rejected) + int(quantity_rejected_change),
            int(quantity_balance) + int(quantity_balance_change), edited_production_data["remarks"],
                                                       int(traveller_combined_id)))
        else:
            self.insert("production_entry_combined", ("traveller_no","part_no","department","quantity_received",
            "quantity_output","quantity_rejected","quantity_balance","time_added","remarks"),
            (edited_production_data["traveller_no"],edited_production_data["part_no"],edited_production_data["department"],
            edited_production_data["quantity_received"],edited_production_data["quantity_output"],edited_production_data["quantity_rejected"],
             int(quantity_balance) + int(quantity_balance_change),datetime.now(), edited_production_data["remarks"]))
        messagebox.showinfo("Info", "Traveller Entry updated successfully")

