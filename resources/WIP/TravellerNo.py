from config import *
from ..UI import Page, EntriesFrame, ViewFrame
from ..Logics import DB
from ..LoginSystem import LoginSystem

class TravellerNo(DB, Page):
    def __init__(self):
        menu_ls = {
            "Add": self.Add_frame,
            "View":self.View_frame,
        }
        self.create_new_page("Traveller No", menu_ls)
    ###############        ###############        ###############        ###############
    def Add_frame(self):
        body_frame = self.create_new_body()
        import_button = ctk.CTkButton(body_frame, text="Import from Excel",
                                      command=lambda: self.import_excel())
        import_button.pack()
        basic_information_entry = (
            ("customer", "entry", (0, 0, 1), None),
            ("part_no", "entry", (1, 0, 1), None),
            ("issued_revision", "entry", (2, 0, 1), None),
        )
        self.basic_information_entries = EntriesFrame(body_frame, basic_information_entry);
        traveller_no_entry = (
            ("traveller_no", "entry", (0, 0, 1), None),
        )
        self.traveller_no_entries = EntriesFrame(body_frame, traveller_no_entry);

        production_quantity_entry = (
            ("production_quantity", "entry", (0, 0, 2), None),
            ("production_unit", "menu", (0,2,1), ('PCS','PANEL')),
        )
        self.production_quantity_entries = EntriesFrame(body_frame, production_quantity_entry);

        process_entry = (
            ("process_1", "entry", (0, 0, 1), None),
            ("process_2", "entry", (1, 0, 1), None),
            ("process_3", "entry", (2, 0, 1), None),
            ("process_4", "entry", (3, 0, 1), None),
            ("process_5", "entry", (4, 0, 1), None),
            ("process_6", "entry", (5, 0, 1), None),
            ("process_7", "entry", (0, 1, 1), None),
            ("process_8", "entry", (1, 1, 1), None),
            ("process_9", "entry", (2, 1, 1), None),
            ("process_10", "entry", (3, 1, 1), None),
            ("process_11", "entry", (4, 1, 1), None),
            ("process_12", "entry", (5, 1, 1), None),
            ("process_13", "entry", (0, 2, 1), None),
            ("process_14", "entry", (1, 2, 1), None),
            ("process_15", "entry", (2, 2, 1), None),
            ("process_16", "entry", (3, 2, 1), None),
            ("process_17", "entry", (4, 2, 1), None),
            ("process_18", "entry", (5, 2, 1), None),
        )
        self.process_entries = EntriesFrame(body_frame, process_entry);

        self.create_footer(self.confirm_btn)
    ###############        ###############        ###############        ###############
    def import_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[('Excel', '*.xls')])
        if not file_path:
            return

        # Open the workbook using xlrd
        workbook = xlrd.open_workbook(file_path)

        # Assuming there is only one sheet, you might need to modify this if you have multiple sheets
        sheet = workbook.sheet_by_index(0)

        # Get values from specific cells
        customer = sheet.cell_value(8, 2)  # C9
        part_no = sheet.cell_value(10, 3)  # D11
        issued_revision = sheet.cell_value(9, 8)  # I10

        self.basic_information_entries.change_value("customer", customer or "")
        self.basic_information_entries.change_value("part_no", part_no or "")
        self.basic_information_entries.change_value("issued_revision", issued_revision or "")

        # Check if any of the required cells is empty
        if any(value == '' for value in [customer, part_no]):
            messagebox.showerror("Error", "Some required cells are empty.")
            return

        # Iterate through the B column to get the list of processes
        processes = []
        start_processing = False

        for row in range(sheet.nrows):
            if sheet.cell_value(row, 1) == 'CUTTING':
                start_processing = True
                processes.append(sheet.cell_value(row, 1))
            elif sheet.cell_value(row, 1) == 'PACKING':
                processes.append(sheet.cell_value(row, 1))
                break  # Stop when reaching PACKING
            elif start_processing:
                processes.append(sheet.cell_value(row, 1))

        for i in range(len(processes)):
            self.process_entries.change_value(f"process_{i+1}", processes[i] or "")

        # Close the workbook
        workbook.release_resources()
    ###############        ###############        ###############        ###############
    def confirm_btn(self):
        basic_information_data = self.basic_information_entries.get_data()
        traveller_no_data = self.traveller_no_entries.get_data()
        process_data = self.process_entries.get_data()
        production_quantity_data = self.production_quantity_entries.get_data()
        if basic_information_data["customer"] == "" or basic_information_data["part_no"] == ""\
                or traveller_no_data["traveller_no"] == "" or process_data["process_1"] == ""\
                or production_quantity_data["production_quantity"] == "":
            messagebox.showinfo("ERROR", "Some information is empty!")
            return
        if len(traveller_no_data["traveller_no"]) != 3:
            messagebox.showinfo("ERROR", "Only input the last 3 digits of the traveller no in the entry.")
            return

        current_year = datetime.now().strftime("%y")
        current_month = datetime.now().strftime("%m")
        traveller_no = traveller_no_data["traveller_no"]
        traveller_no_string = f"{current_year}{current_month}0000{traveller_no.zfill(3)}"
        exist_traveller_no = DB.select("traveller_no_inputs", ("id",), "traveller_no=%s", (traveller_no_string,))
        if exist_traveller_no:
            messagebox.showinfo("ERROR", f"Traveller No {traveller_no_string} already exists in the database!")
            return

        part_no = basic_information_data["part_no"]
        basic_information_info = basic_information_data["customer"] + "|" + basic_information_data["part_no"] + (basic_information_data["issued_revision"] or "")
        production_quantity = production_quantity_data["production_quantity"]
        production_unit = production_quantity_data["production_unit"]
        process_list = ""

        for i in range(len(process_data)):
            process_list += process_data[f"process_{i+1}"] or ""
            if i != len(process_data) - 1:
                process_list += "|"

        user_name = LoginSystem.user_name
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        DB.insert("bom_inputs", ("part_no","basic_information_info","process_entry_info","time_created","user_name"), (part_no, basic_information_info, process_list, current_datetime, user_name))
        DB.insert("traveller_no_inputs", ("part_no","traveller_no","production_qty","production_unit","time_created","user_name"), (part_no, traveller_no_string, production_quantity, production_unit, current_datetime, user_name))
        messagebox.showinfo("Info", f"Traveller No {traveller_no_string} added successfully!")

    ###############        ###############        ###############        ###############
    def View_frame(self):
        body_frame = self.create_new_body()
        ViewFrame(body_frame, ["BOM Inputs", "Traveller No Inputs"])
##############################################################################################################
