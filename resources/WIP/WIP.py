from config import *
from ..UI import Page, LeftMenu, EntriesFrame, SearchFrame, SearchWindow, ViewFrame
from ..Logics import DB
import customtkinter as ctk
import tkinter as tk
from tkinter import StringVar, messagebox, filedialog, Toplevel
from tkcalendar import Calendar
from tksheet import Sheet
from datetime import datetime, timedelta
import threading
from cryptography.fernet import Fernet
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .Delivery_Order_Entry_backend import (excel_sheet_to_delivery_order, import_order_to_database,
                                           checkUnfulfilledDeliveryOrdersWithSimilarPartNos, refreshDeliveryOrders)
from .Data_Editor_backend import (addDeliveryOrderNew, editPartNo, editQuantity, editDeliveryDateByDO, editDeliveryDate, transfer_stock,
                                  change_part_no_of_filled_carton, change_part_no_of_sealed_batch, reject_carton, reject_old_stock,
                                  get_old_stock_from_delivery_order, delete_entry_tracker, change_quantity_of_old_stock,
                                  change_quantity_of_filled_carton, change_quantity_of_empty_carton, change_quantity_of_sealed_inventory,
                                  updateMainInventory)
from .Data_Viewer_Backend import (checkCompletelyFulfilledID, checkCompletelyFulfilledNo, archiveDeliveryOrder,
                                  archive_all_orders_by_no, unarchive_delivery_order_by_deliver_order_no, unarchive_delivery_order)
class WIP(Page):
    def __init__(self):
        self.create_new_page("Delivery Order Entry")
        left_menu = LeftMenu()
        left_menu_ls = {
            "Delivery Order": DeliveryOrder,
            "Part No": PartNo,
            "Reject Items": RejectItems,
            "Edit Quantity": EditQuantity,
            "Other Options": OtherOptions,
            "User": User,
            "Inventory": Inventory,
        }
        left_menu.update_menu(left_menu_ls)
##############################################################################################################
class DeliveryOrder(DB,Page):
    def __init__(self):
        menu_ls = {
            "Add": self.Add_frame,
            "Add (Manual)": self.Add_manual_frame,
            "Track": self.Track_frame,
            "Track (Archived)": self.Track_Archived_frame,
            "Edit/Delete": self.Edit_frame,
            "Archive": self.Archive_frame,
            "Unarchive": self.Unarchive_frame,
        }
        self.popup_open = False
        self.table_type = "Track"
        self.create_new_page("Delivery Order", menu_ls)
    ###############        ###############        ###############        ###############
    def create_main_page(self, body_frame):
        self.frame_left = ctk.CTkFrame(master=body_frame)
        self.frame_left.pack(side="left", fill="both", expand=False)

        self.frame_right = ctk.CTkFrame(master=body_frame)
        self.frame_right.pack(side="right", fill="both", expand=True)
        # ============ frame_left ============
        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure(0, minsize=10)  # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(18, weight=1)  # empty row as spacing
        self.frame_left.grid_rowconfigure(18, minsize=20)  # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(21, minsize=10)  # empty row with minsize as spacing

        ctk.CTkLabel(master=self.frame_left, text="Info",).grid(row=1,column=0,pady=10,padx=0)

        rwo_color_frame = ctk.CTkFrame(master=self.frame_left, border_width=1, fg_color=None)
        rwo_color_frame.grid(row=2, column=0, padx=1)
        ctk.CTkLabel(master=rwo_color_frame, text=f"Row color :", width=10
                               ).grid(row=0, column=0, sticky="w", padx=5, pady=1)
        ctk.CTkLabel(master=rwo_color_frame, text=f"Not exist in DB", bg_color="#9bfad5", text_color="black"
                               ).grid(row=1, column=0)
        ctk.CTkLabel(master=rwo_color_frame, text=f"Unavailable Part No", bg_color="#ffff00",
                               text_color="black"
                               ).grid(row=2, column=0)
        ctk.CTkLabel(master=rwo_color_frame, text=f"Exist in DB", bg_color="#fcc9c2", text_color="black"
                               ).grid(row=3, column=0, padx=5, pady=(0, 4))

        do_color_frame = ctk.CTkFrame(master=self.frame_left, border_width=1, fg_color=None)
        do_color_frame.grid(row=7, column=0, padx=1)
        ctk.CTkLabel(master=do_color_frame, text=f"Calendar Legend :", width=10
                               ).grid(row=0, column=0, sticky="w", padx=5, pady=1)
        ctk.CTkLabel(master=do_color_frame, text=f"DO Exists", bg_color="#008101", text_color="black"
                               ).grid(row=1, column=0)
        ctk.CTkLabel(master=do_color_frame, text=f"No DO", bg_color="#ff0101",
                               text_color="black"
                               ).grid(row=2, column=0)
        self.do_text = StringVar(master=do_color_frame, value="No. of DOs: 0")
        ctk.CTkLabel(master=do_color_frame, textvariable=self.do_text, bg_color="#ffffff",
                               text_color="black"
                               ).grid(row=3, column=0)

        # Create a Calendar widget
        self.cal = Calendar(self.frame_left, selectmode="day", date_pattern="yyyy-mm-dd", showothermonthdays=False)
        self.cal.grid(row=11, column=0, padx=4, pady=10, sticky="w")
        self.cal.bind("<<CalendarSelected>>", self.date_selected)

        self.exception_text = StringVar(master=do_color_frame, value="No Exception")
        self.add_exception_button = ctk.CTkButton(master=self.frame_left, textvariable=self.exception_text,
                                                            command=self.add_calendar_exception, state="disabled")
        self.add_exception_button.grid(row=12, column=0, padx=4, pady=5, sticky="w")

        self.refresh_calendar()
        # ============ frame_right ============
        self.frame_right.columnconfigure(0, weight=1)
        self.frame_right.rowconfigure(3, weight=4)
        self.frame_right.rowconfigure(4, weight=1)
        ctk.CTkLabel(master=self.frame_right, text="Delivery Order Entry").grid(row=0, column=0, sticky="nswe", pady=20)

        path_frame = ctk.CTkFrame(master=self.frame_right, border_width=2, fg_color=None)
        path_frame.grid(row=1, column=0, sticky="we")
        path_frame.columnconfigure((0, 1, 2), weight=1)
        path_frame.columnconfigure(1, weight=10)
        ctk.CTkLabel(master=path_frame, text=f"File Path :", width=30
                               ).grid(row=0, column=0, sticky="we", padx=(5, 0), pady=10)
        entry_path = ctk.CTkEntry(master=path_frame, placeholder_text="Click on 'Import' button")
        entry_path.grid(row=0, column=1, sticky="we")

        ctk.CTkButton(master=path_frame, text="Import", width=20, command=lambda: self.import_btn(entry_path)
                                ).grid(row=0, column=2, padx=(0, 5))

        second_frame = ctk.CTkFrame(master=self.frame_right, fg_color=None)
        second_frame.grid(row=2, column=0, sticky="we")
        second_frame.columnconfigure((0, 1), weight=1)
        refresh_frame = ctk.CTkFrame(master=second_frame, fg_color=None)
        refresh_frame.pack()
        ctk.CTkLabel(master=refresh_frame, text=f"Refresh & fulfill all delivery orders :", width=50).pack(side="left")
        ctk.CTkButton(master=refresh_frame, text="Refresh", width=20, command=self.refresh_btn
                                ).pack(side="left")
        # table frame
        self.sheet = Sheet(self.frame_right,
                           headers=["Customer", "Part No", "Qty", "UoM", "Delivery Order No", "Delivery Date",
                                    "Weight"])
        self.sheet.enable_bindings("single_select", "drag_select", "select_all", "column_select", "row_select",
                                   "column_width_resize", "double_click_column_resize", "arrowkeys",
                                   "row_height_resize", "double_click_row_resize")
        self.sheet.grid(row=3, column=0, sticky="nswe", padx=5, pady=5)
        col_size = 138
        col_size = [col_size * 1.5, col_size * 2, col_size * 0.5, col_size * 0.4, col_size, col_size, col_size * 0.5]
        self.sheet.set_column_widths(column_widths=col_size)
        bottom_frame = ctk.CTkFrame(master=self.frame_right, fg_color=None)
        bottom_frame.grid(row=4, column=0)
        ctk.CTkButton(master=bottom_frame, text="Upload", width=20, command=self.upload_btn
                                ).pack(side="left", padx=10)
        self.file_path = None
    ###############        ###############        ###############        ###############
    def refresh_calendar(self):
        # Clear all existing calendar events
        self.cal.calevent_remove('all')

        # Get the current date and time
        current_datetime = datetime.now()
        current_date = current_datetime.date()

        # Get the earliest date from both tables
        delivery_orders_dates = DB.select("delivery_orders", ("DATE(time) AS time_added",), "time IS NOT NULL")
        archived_delivery_orders_dates = DB.select("archived_delivery_orders", ("DATE(time_added)",), "time_added IS NOT NULL")
        combined_dates = [date[0] for date in delivery_orders_dates] + [date[0] for date in archived_delivery_orders_dates]
        combined_dates.sort()

        # Remove duplicates (if any)
        earliest_dates  = list(set(combined_dates))

        calex = DB.select("calendar_exceptions", ("DATE(date)",))
        calendar_exceptions = [row[0] for row in calex]  # Convert to a list of dates

        # Iterate through the days and create calendar events
        for delta in range((current_date - min(earliest_dates)).days + 1):
            current_date_str = (current_date - timedelta(days=delta)).strftime('%Y-%m-%d')
            current_date_date = datetime.strptime(current_date_str, '%Y-%m-%d').date()
            if current_date_date.weekday() in [5, 6]:
                self.cal.calevent_create(current_date_date, 'Weekend', 'gray')
                self.cal.tag_config("gray", background='gray', foreground='black')
            else:
                if current_date_date in earliest_dates or current_date_date in calendar_exceptions:
                    self.cal.calevent_create(current_date_date, 'Uploaded', 'green')
                    self.cal.tag_config("green", background='green', foreground='black')
                else:
                    self.cal.calevent_create(current_date_date, 'Not Uploaded', 'red')
                    self.cal.tag_config("red", background='red', foreground='black')
    ###############        ###############        ###############        ###############
    def add_calendar_exception(self):
        date_str = self.cal.get_date()
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            # Handle invalid date format here
            # You can show an error message to the user
            messagebox.showerror("Error", "Invalid Input")
            return

        # Insert or update the exception in the database
        id_exist = DB.select("calendar_exceptions", ("id",), "date = %s", (date,))
        if id_exist:
            id_of_date = int(id_exist[0][0])
            self.delete("calendar_exceptions", "id = %s", (id_of_date,))
            messagebox.showinfo("Success", "Date removed from exception!")
        else:
            self.insert("calendar_exceptions", ("date", "time_added"), (date, datetime.now()))
            messagebox.showinfo("Success", "Date added to exception!")

        # Refresh the calendar to reflect the changes
        self.refresh_calendar()
    ###############        ###############        ###############        ###############
    def date_selected(self, event):
        selected_date = self.cal.get_date()
        selected_date_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        no_of_ado = DB.select("archived_delivery_orders", ("COUNT(*)",), "DATE(time_added) = %s", (selected_date,))
        if no_of_ado:
            no_of_ado = int(no_of_ado[0][0])
        else:
            no_of_ado = 0
        no_of_do = DB.select("delivery_orders", ("COUNT(*)",), "DATE(time) = %s", (selected_date,))
        if no_of_do:
            no_of_do = int(no_of_do[0][0])
        else:
            no_of_do = 0
        total_no_of_do = no_of_ado + no_of_do
        self.do_text.set(f"No. of DOs: {str(total_no_of_do)}")
        if total_no_of_do == 0:
            calex = DB.select("calendar_exceptions", ("DATE(date)",))
            calendar_exceptions = [row[0] for row in calex]  # Convert to a list of dates
            if selected_date_date not in calendar_exceptions:
                self.add_exception_button.configure(state="normal")
                self.exception_text.set(f"Add Exception ({str(selected_date)})")
            else:
                self.add_exception_button.configure(state="normal")
                self.exception_text.set(f"Remove Exception ({str(selected_date)})")
        else:
            self.add_exception_button.configure(state="disabled")
            self.exception_text.set(f"No Exception")
    ###############        ###############        ###############        ###############
    def import_btn(self,entry_path):
        self.file_path = filedialog.askopenfilename(filetypes=[("Excel files", ".xls")])
        if not self.file_path: return
        entry_path.delete(0, tk.END)
        entry_path.insert(tk.END, str(self.file_path))
        file_condition , _ , delivery_order_ls = excel_sheet_to_delivery_order(self.file_path)
        if not file_condition:
            messagebox.showerror("Error", "The program was not able to load the file")
        green_rows , yellow_rows, red_rows = [] , [], []
        for inx ,record in enumerate(delivery_order_ls):
            record[5]= record[5].date()
            part_no = record[1]
            existing_part_no = DB.select("part_info", ("part_no",), "part_no = %s", (str(part_no),))
            if record[-1]:
                red_rows.append(inx)
            elif not existing_part_no:
                yellow_rows.append(inx)
            else:
                green_rows.append(inx)
            # del record[-1]
        self.sheet.set_sheet_data(delivery_order_ls , False)
        if len(green_rows)>0:
            self.sheet.highlight_rows(rows=green_rows , bg="#9bfad5", fg="black")
        if len(yellow_rows) > 0:
            self.sheet.highlight_rows(rows=yellow_rows, bg="#ffff00", fg="black")
        if len(red_rows)>0:
            self.sheet.highlight_rows(rows=red_rows , bg="#fcc9c2" , fg="black")
    ###############        ###############        ###############        ###############
    def upload_btn(self):
        if not self.file_path: return
        complete,process_info=import_order_to_database(self.file_path)
        process_info =  " ".join(process_info)
        if not complete:
            messagebox.showerror("Error", process_info)
        else:
            messagebox.showinfo("Process info", process_info)
        process_info_2 = checkUnfulfilledDeliveryOrdersWithSimilarPartNos()
        process_info_2 = " ".join(process_info_2)
        if process_info_2:
            messagebox.showinfo("Process info", process_info_2)
    ###############        ###############        ###############        ###############
    def refresh_btn(self):
        process_info=refreshDeliveryOrders()
        process_info =  " ".join(process_info)
        if process_info:
            messagebox.showinfo("Process info", process_info)
        process_info_2 = checkUnfulfilledDeliveryOrdersWithSimilarPartNos()
        process_info_2 = " ".join(process_info_2)
        if process_info_2:
            messagebox.showinfo("Process info", process_info_2)
    ###############        ###############        ###############        ###############
    def stats(self):
        process_info=refreshDeliveryOrders()
        process_info =  " ".join(process_info)
        if process_info:
            messagebox.showinfo("Process info", process_info)
    ###############        ###############        ###############        ###############
    def Add_frame(self):
        body_frame = self.create_new_body()
        self.create_main_page(body_frame)
    ###############        ###############        ###############        ###############
    def Add_manual_frame(self):
        body_frame = self.create_new_body()
        customer_entry = (
            ("customer", "entry", (0, 0, 1), None),
        )
        self.customer_entries = EntriesFrame(body_frame, customer_entry);
        self.customer_entries.pack()
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
            ("quantity", "entry", (0, 0, 1), None),
            ("uom", "menu", (1, 0, 1), ("PCS", "PANEL")),
            ("delivery_order", "entry", (2, 0, 1), None),
            ("delivery_date", "date", (3, 0, 1), None),
            ("weight_limit", "entry", (4, 0, 1), None)
        )
        self.delivery_order_entries = EntriesFrame(body_frame, entries);
        self.delivery_order_entries.pack()
        self.delivery_order_entries.change_value("weight_limit", 0)
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
    ###############        ###############        ###############        ###############
    def confirm_btn(self):
        # Extract data from EntriesFrame instances
        customer_data = self.customer_entries.get_data()
        part_no_data = self.part_no_entries.get_data()
        delivery_order_data = self.delivery_order_entries.get_data()
        if part_no_data["part_no"] == "":
            messagebox.showinfo("ERROR", "Part No entry is empty!")
            return
        # Retrieve data
        data = {
            **dict(customer_data),
            **dict(part_no_data),
            **dict(delivery_order_data)
        }
        # get delivery order entries , doi=delivery order info
        doi = {}
        for entry_name, entry in data.items():
            doi[entry_name] = entry
        # check if Invalid value
        doi_dict_checked = self.check_entry_value(doi.copy())
        error_ls = []
        for key, value in doi_dict_checked.items():
            if value == False:
                error_ls.append(key)
        if len(error_ls) > 0:
            error_text = f"Invalid entry, Please check your entries and try again. \nCheck the following entries={str(error_ls)}"
            messagebox.showerror("Error", error_text)
            return
        process_info = addDeliveryOrderNew(doi["customer"], doi["part_no"], doi["quantity"], doi["uom"],
                                           doi["delivery_order"], doi["delivery_date"], doi["weight_limit"])
    ###############        ###############        ###############        ###############
    def check_entry_value(self,entry_dict={}):
        for key, value in entry_dict.items():
            # check part_no , customer or Delivery Order
            if key in ["part_no" , "customer" , "delivery_order" ]:
                if len(value)<1:
                    entry_dict[key] = False
                else:
                    entry_dict[key] = True
            # check Weight
            if key in ["weight_limit" , "weight" ]:
                try:
                    test=float(value)
                    entry_dict[key] = True
                except:
                    entry_dict[key] = False
            # check uom
            if key == "uom":
                if value.upper() == "PCS" or value.upper() == "PANEL":
                    entry_dict[key] = True
                else:
                    entry_dict[key] = False
            # check quantity
            if key in ["quantity" , "carton_quantity" , "bundle_qty" , "stn_qty"]:
                try:
                    if int(value) <1:
                        raise Exception
                    entry_dict[key] = True
                except:
                    entry_dict[key] = False
            # check integer
            if key in ("cavity"):
                try:
                    test=int(value)
                    entry_dict[key] = True
                except:
                    entry_dict[key] = False
            # check date entry
            if key in ("delivery_date" , "exp" , "mfg" , "pkd","packing_date"):
                try:
                    if value != "":
                        test = datetime.strptime(value, r"%Y-%m-%d")
                    entry_dict[key] = True
                except:
                    entry_dict[key] = False
            # check date_code
            if key in ["date_code","date_code"]:
                if len(value)==4:
                    yy= value[-2:]
                    ww= value[:2]
                    try:
                        test = datetime.strptime(f"{yy}-{ww}-1", r"%y-%W-%w")
                        entry_dict[key] = True
                    except:
                        entry_dict[key] = False
                elif len(value)==6:
                    yy= value[-2:]
                    mm= value[2:4]
                    dd = value[:2]
                    try:
                        test = datetime.strptime(f"{yy}-{mm}-{dd}", r"%y-%m-%d")
                        entry_dict[key] = True
                    except:
                        entry_dict[key] = False
                else:
                    entry_dict[key] = False
            # check if integer
            if key in ["delivery_id","loose_quantity"]:
                try:
                    int(value)
                    entry_dict[key] = True
                except:
                    entry_dict[key] = False
        return entry_dict
    ###############        ###############        ###############        ###############
    def Track_frame(self):
        body_frame = self.create_new_body()
        self.table_type = "Track"
        self.create_view_frame(body_frame)
    ###############        ###############        ###############        ###############
    def create_view_frame(self, body_frame):
        do_view_frame = ctk.CTkFrame(master=body_frame)
        do_view_filter_frame = ctk.CTkFrame(master=do_view_frame)
        do_view_filter_frame.pack(side="top", fill="x", expand=False)
        do_view_frame.pack(side="top", fill="x", expand=False)

        id_label = ctk.CTkLabel(do_view_filter_frame, text="ID:")
        id_label.grid(row=0, column=0, padx=10)
        id_entry = ctk.CTkEntry(do_view_filter_frame, width=450)
        id_entry.grid(row=0, column=1, padx=10)

        part_no_label = ctk.CTkLabel(do_view_filter_frame, text="Part No:")
        part_no_label.grid(row=1, column=0, padx=10)
        part_no_entry = ctk.CTkEntry(do_view_filter_frame, width=450)
        part_no_entry.grid(row=1, column=1, padx=10)

        customer_label = ctk.CTkLabel(do_view_filter_frame, text="Customer:")
        customer_label.grid(row=2, column=0, padx=10)
        customer_entry = ctk.CTkEntry(do_view_filter_frame, width=450)
        customer_entry.grid(row=2, column=1, padx=10)

        do_no_label = ctk.CTkLabel(do_view_filter_frame, text="DO No:")
        do_no_label.grid(row=3, column=0, padx=10)
        do_no_entry = ctk.CTkEntry(do_view_filter_frame, width=450)
        do_no_entry.grid(row=3, column=1, padx=10)

        # Checkbox for filtering out fulfilled delivery orders
        unfulfilled_entry = tk.BooleanVar()
        unfulfilled_checkbox = tk.Checkbutton(do_view_filter_frame, text="Unfulfilled", variable=unfulfilled_entry)
        unfulfilled_checkbox.grid(row=0, column=2, padx=10)

        search_button = ctk.CTkButton(do_view_filter_frame, text="Search",
                                      command=lambda: self.filter_track_table(id_entry.get(), part_no_entry.get(),
                                                                              customer_entry.get(), do_no_entry.get(),
                                                                              unfulfilled_entry.get()))
        search_button.grid(row=1, column=2, padx=10)
        self.do_view_sheet = Sheet(do_view_frame, show_x_scrollbar=False, height=400,
                                   headers=["ID", "Customer", "Part No", "Quantity", "Fulfilled Quantity", "UOM",
                                            "Carton IDs",
                                            "Delivery Order", "Delivery Date", "Time Added", "Stn Qty", "Total Stock"])
        col_size = 90
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size,
                     col_size, col_size]
        self.do_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize")
        self.do_view_sheet.enable_bindings(binding)
        self.do_view_sheet.pack(fill="x", padx=4, pady=4)
        self.do_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        do_data = DB.select("delivery_orders", (
        "id", "customer", "part_no", "quantity", "fulfilled_quantity", "uom", "cartons_id", "delivery_order",
        "delivery_date", "time"), "1=1 ORDER BY id")
        main_inventory = DB.select("main_inventory", ("part_no", "stn_qty", "total_stock"),
                                     "part_no IN (SELECT part_no FROM delivery_orders)", )
        combined_results = {}

        # Process delivery_orders data
        for row in do_data:
            part_no = row[2]
            combined_results[part_no] = row.copy()

        # Process main_inventory data
        for row in main_inventory:
            part_no = row[0]
            if part_no in combined_results:
                combined_results[part_no].extend(row[1:])

        # Insert rows into the sheet
        for row_data in combined_results.values():
            self.do_view_sheet.insert_row(values=row_data)

        if self.table_type == "Archive":
            do_archive_filter_frame = ctk.CTkFrame(master=do_view_frame)
            do_archive_filter_frame.pack(side="bottom", fill="x", expand=False)
            self.archive_id_text = StringVar(master=do_archive_filter_frame, value="Archive ID")
            self.archive_do_no_text = StringVar(master=do_archive_filter_frame, value="Archive DO No")
            self.archive_id_btn = ctk.CTkButton(master=do_archive_filter_frame, textvariable=self.archive_id_text, width=20, command=self.archive_id
                          ).grid(row=0, column=2, padx=(0, 5))
            self.archive_do_no_btn = ctk.CTkButton(master=do_archive_filter_frame, textvariable=self.archive_do_no_text, width=20, command=self.archive_do_no
                          ).grid(row=0, column=3, padx=(0, 5))
            self.do_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
    ###############        ###############        ###############        ###############
    def filter_track_table(self, id, part_no, customer, do_no, unfulfilled):
        # Remove existing data from the table
        total_rows = self.do_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.do_view_sheet.delete_row(a)

        conditions = "id LIKE %s AND part_no LIKE %s AND customer LIKE %s AND delivery_order LIKE %s"
        if unfulfilled:
            conditions += " AND quantity > fulfilled_quantity"
        conditions += " ORDER BY id"

        do_data = DB.select("delivery_orders", (
        "id", "customer", "part_no", "quantity", "fulfilled_quantity", "uom", "cartons_id", "delivery_order",
        "delivery_date", "time"), conditions,("%%" + id + "%%","%%" + part_no + "%%","%%" + customer + "%%","%%" + do_no + "%%"))
        main_inventory = DB.select("main_inventory", ("part_no", "stn_qty", "total_stock"),
                                     "part_no IN (SELECT part_no FROM delivery_orders)", )
        combined_results = {}

        # Process delivery_orders data
        for row in do_data:
            part_no = row[2]
            combined_results[part_no] = row.copy()

        # Process main_inventory data
        for row in main_inventory:
            part_no = row[0]
            if part_no in combined_results:
                combined_results[part_no].extend(row[1:])

        for row_data in combined_results.values():
            self.do_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def create_archived_view_frame(self, body_frame):
        do_view_frame = ctk.CTkFrame(master=body_frame)
        do_view_filter_frame = ctk.CTkFrame(master=do_view_frame)
        do_view_filter_frame.pack(side="top", fill="x", expand=False)
        do_view_frame.pack(side="top", fill="x", expand=False)

        id_label = ctk.CTkLabel(do_view_filter_frame, text="ID:")
        id_label.grid(row=0, column=0, padx=10)
        id_entry = ctk.CTkEntry(do_view_filter_frame, width=450)
        id_entry.grid(row=0, column=1, padx=10)

        part_no_label = ctk.CTkLabel(do_view_filter_frame, text="Part No:")
        part_no_label.grid(row=1, column=0, padx=10)
        part_no_entry = ctk.CTkEntry(do_view_filter_frame, width=450)
        part_no_entry.grid(row=1, column=1, padx=10)

        customer_label = ctk.CTkLabel(do_view_filter_frame, text="Customer:")
        customer_label.grid(row=2, column=0, padx=10)
        customer_entry = ctk.CTkEntry(do_view_filter_frame, width=450)
        customer_entry.grid(row=2, column=1, padx=10)

        do_no_label = ctk.CTkLabel(do_view_filter_frame, text="DO No:")
        do_no_label.grid(row=3, column=0, padx=10)
        do_no_entry = ctk.CTkEntry(do_view_filter_frame, width=450)
        do_no_entry.grid(row=3, column=1, padx=10)

        # Checkbox for filtering out fulfilled delivery orders
        unfulfilled_entry = tk.BooleanVar()
        unfulfilled_checkbox = tk.Checkbutton(do_view_filter_frame, text="Unfulfilled", variable=unfulfilled_entry)
        unfulfilled_checkbox.grid(row=0, column=2, padx=10)

        search_button = ctk.CTkButton(do_view_filter_frame, text="Search",
                                      command=lambda: self.filter_archived_track_table(id_entry.get(),
                                                                                       part_no_entry.get(),
                                                                                       customer_entry.get(),
                                                                                       do_no_entry.get(),
                                                                                       unfulfilled_entry.get()))
        search_button.grid(row=1, column=2, padx=10)
        self.do_view_sheet = Sheet(do_view_frame, show_x_scrollbar=False, height=400,
                                   headers=["ID", "Customer", "Part No", "Quantity", "Fulfilled Quantity", "UOM",
                                            "Carton IDs",
                                            "Delivery Order", "Delivery Date", "Time Added", "Time Archived"])
        col_size = 90
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size,
                     col_size]
        self.do_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize")
        self.do_view_sheet.enable_bindings(binding)
        self.do_view_sheet.pack(fill="x", padx=4, pady=4)
        self.do_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        do_data = DB.select("archived_delivery_orders", (
        "id", "customer", "part_no", "quantity", "fulfilled_quantity", "uom", "cartons_id", "delivery_order",
        "delivery_date", "time_added", "time_archived"), "1=1 ORDER BY id DESC")

        # Insert rows into the sheet
        for row_data in do_data:
            self.do_view_sheet.insert_row(values=row_data)
        if self.table_type == "Unarchive":
            do_archive_filter_frame = ctk.CTkFrame(master=do_view_frame)
            do_archive_filter_frame.pack(side="bottom", fill="x", expand=False)
            self.unarchive_id_text = StringVar(master=do_archive_filter_frame, value="Unarchive ID")
            self.unarchive_do_no_text = StringVar(master=do_archive_filter_frame, value="Unarchive DO No")
            self.unarchive_id_btn = ctk.CTkButton(master=do_archive_filter_frame, textvariable=self.unarchive_id_text,
                                                width=20, command=self.archive_id
                                                ).grid(row=0, column=2, padx=(0, 5))
            self.unarchive_do_no_btn = ctk.CTkButton(master=do_archive_filter_frame, textvariable=self.unarchive_do_no_text,
                                                   width=20, command=self.archive_do_no
                                                   ).grid(row=0, column=3, padx=(0, 5))
            self.do_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
    ###############        ###############        ###############        ###############
    def Track_Archived_frame(self):
        body_frame = self.create_new_body()
        self.table_type = "View"
        self.create_archived_view_frame(body_frame)
    ###############        ###############        ###############        ###############
    def filter_archived_track_table(self, id, part_no, customer, do_no, unfulfilled):
        # Remove existing data from the table
        total_rows = self.do_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.do_view_sheet.delete_row(a)

        conditions = "id LIKE %s AND part_no LIKE %s AND customer LIKE %s AND delivery_order LIKE %s"
        if unfulfilled:
            conditions += " AND quantity > fulfilled_quantity"
        conditions += " ORDER BY id DESC"

        do_data = DB.select("archived_delivery_orders", (
        "id", "customer", "part_no", "quantity", "fulfilled_quantity", "uom", "cartons_id", "delivery_order",
        "delivery_date", "time_added","time_archived"), conditions,("%%" + id + "%%","%%" + part_no + "%%","%%" + customer + "%%","%%" + do_no + "%%"))


        for row_data in do_data:
            self.do_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def Edit_frame(self):
        body_frame = self.create_new_body()
        do_view_frame = ctk.CTkFrame(master=body_frame)
        do_view_filter_frame = ctk.CTkFrame(master=do_view_frame)
        do_view_filter_frame.pack(side="top", fill="x", expand=False)
        filter_label = ctk.CTkLabel(do_view_filter_frame, text="Search Part No:")
        filter_label.pack(side='left', padx=10, pady=10)  # Place label on the left side

        filter_entry = ctk.CTkEntry(do_view_filter_frame, width=450)
        filter_entry.pack(side='left', padx=10, pady=10)  # Place entry widget next to the label

        search_button = ctk.CTkButton(do_view_filter_frame, text="Search",
                                      command=lambda: self.filter_view_table(filter_entry.get()))
        search_button.pack(side='left')
        edit_button = ctk.CTkButton(master=do_view_filter_frame, text="Edit/Delete",
                                    command=lambda: self.edit_row_frame(body_frame))
        edit_button.pack(side='right')
        do_view_frame.pack(side="top", fill="x", expand=False)
        self.do_view_sheet = Sheet(do_view_frame, show_x_scrollbar=False, height=200,
                                        headers=["ID", "Customer", "Part No", "Quantity", "UOM", "Delivery Order",
                                                 "Delivery Date", "Weight Limit", "Time Added"])
        col_size = 115
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.do_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = ("single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize", "column_height_resize", "row_height_resize", "double_click_row_resize")
        self.do_view_sheet.enable_bindings(binding)
        self.do_view_sheet.pack(fill="x", padx=4, pady=4)
        self.do_view_sheet.bind("<ButtonRelease-1>", self.cell_select)

        do_data = DB.select("delivery_orders", ("id","customer","part_no","quantity","uom","delivery_order","delivery_date","weight_limit","time"), "1=1 ORDER BY id")
        for row_data in do_data:
            self.do_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def filter_view_table(self, keyword):
        # Remove existing data from the table
        total_rows = self.do_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.do_view_sheet.delete_row(a)

        part_info_data = DB.select("delivery_orders", ("id","customer","part_no","quantity","uom","delivery_order","delivery_date","weight_limit","time"), "part_no LIKE %s ORDER BY id", ("%%" + keyword + "%%",))
        for row_data in part_info_data:
            self.do_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def cell_select(self, event):
        row = self.do_view_sheet.identify_row(event)
        if self.do_view_sheet.total_rows() > 0:
            self.selected_row = row
        if self.table_type == "Archive":
            selected_data = self.do_view_sheet.get_row_data(self.selected_row)
            self.archive_id_text.set(f"Archive ID ({selected_data[0]})")
            self.archive_do_no_text.set(f"Archive DO No ({selected_data[7]})")
        elif self.table_type == "Unarchive":
            selected_data = self.do_view_sheet.get_row_data(self.selected_row)
            self.unarchive_id_text.set(f"Unarchive ID ({selected_data[0]})")
            self.unarchive_do_no_text.set(f"Unarchive DO No ({selected_data[7]})")
    ###############        ###############        ###############        ###############
    def edit_row_frame(self, master):
        if self.selected_row is None:
            messagebox.showinfo("Error", "Please select a row to edit.")
        else:
            self.edit_selected_do(master)
    ###############        ###############        ###############        ###############
    def edit_selected_do(self, master):
        if self.popup_open:
            messagebox.showinfo("Error", "The DO Edit Window is already open!")
            self.do_window.lift()
        else:
            self.popup_open = True

            if self.selected_row is None:
                messagebox.showinfo("Error", "Please select a row to edit.")
                self.popup_open = False
                return

            # Create a new window (Toplevel) for editing a part number
            self.do_window = Toplevel(master)
            self.do_window.title("Edit Delivery Order")
            self.do_window.lift()

            def close_popup():
                self.do_window.destroy()
                self.popup_open = False

            # Bind the close_popup function to the window's close button
            self.do_window.protocol("WM_DELETE_WINDOW", close_popup)

            id_of_data = 0
            # Retrieve data from the selected row
            selected_data = self.do_view_sheet.get_row_data(self.selected_row)
            id_of_data = DB.select("delivery_orders", ("id",), "id=%s", (selected_data[0],))
            id_of_data = id_of_data[0][0]

            add_do_frame = ctk.CTkFrame(self.do_window)
            add_do_frame.pack()

            customer_entry = (
                ("customer", "entry", (0, 0, 1), None),
            )
            self.customer_entries = EntriesFrame(add_do_frame, customer_entry);
            self.customer_entries.pack()
            part_no_entry = (
                ("part_no", "entry", (0, 0, 1), None),
            )
            self.part_no_entries = EntriesFrame(add_do_frame, part_no_entry);
            self.part_no_entries.pack()
            # add search btn for part no name
            frame = self.part_no_entries.frames["part_no"]
            self.search_part_no = SearchWindow(select_btn=self.select_part_no, layout="Search Part No")
            ctk.CTkButton(frame, image="search_icon", text="", command=self.search_part_no.new_window, width=20).pack(
                side="left")
            entries = (
                ("quantity", "entry", (0, 0, 1), None),
                ("uom", "menu", (1, 0, 1), ("PCS", "PANEL")),
                ("delivery_order", "entry", (2, 0, 1), None),
                ("delivery_date", "date", (3, 0, 1), None),
                ("weight_limit", "entry", (4, 0, 1), None)
            )
            self.edit_delivery_order_entries = EntriesFrame(add_do_frame, entries);
            self.edit_delivery_order_entries.pack()
            self.customer_entries.change_value("customer", selected_data[1] or "")
            self.part_no_entries.change_value("part_no", selected_data[2] or "")
            self.part_no_entries.disable_all()
            for i in range(len(entries)):
                self.edit_delivery_order_entries.change_value(entries[i][0], selected_data[i+3])
            button_frame = ctk.CTkFrame(master=add_do_frame)
            button_frame.pack(side="bottom", fill="x", expand=False)
            ctk.CTkButton(master=button_frame, text="Save",
                          command=lambda: self.save_edited_do_data(id_of_data,close_popup)).pack(
                side="left", padx=10, pady=10)
            ctk.CTkButton(master=button_frame, text="Delete",
                          command=lambda: self.delete_edited_do_data(id_of_data,close_popup)).pack(
                side="right", padx=10, pady=10)
    ###############        ###############        ###############        ###############
    def save_edited_do_data(self, id_of_data, close_popup):
        # Extract data from EntriesFrame instances
        customer_data = self.customer_entries.get_data()
        part_no_data = self.part_no_edit_entries.get_data()
        delivery_order_data = self.edit_delivery_order_entries.get_data()

        if part_no_data["part_no"] == "":
            messagebox.showinfo("ERROR", "Part No entry is empty!")
            self.do_window.lift()
            return
        # Retrieve data
        edited_data = {
            **dict(customer_data),
            **dict(part_no_data),
            **dict(delivery_order_data)
        }

        doi = {}
        for entry_name, entry in edited_data.items():
            doi[entry_name] = entry
        # check if delivery order ID is not selected
        if doi["id"] == "":
            return
        # check if Invalid value
        doi_dict_checked = self.check_entry_value(doi.copy())
        error_ls = []
        for key, value in doi_dict_checked.items():
            if value == False:
                error_ls.append(key)
        if len(error_ls) > 0:
            error_text = f"Invalid entry, Please check your entries and try again. \nCheck the following entries={str(error_ls)}"
            messagebox.showerror("Error", error_text)
            return
        old_doi = DB.select("delivery_orders", ("part_no","quantity","delivery_date"), "id=%s", (doi["id"],))

        msg1 = msg2 = msg3 = None
        if doi["part_no"] != old_doi[0]:
            msg1 = editPartNo(doi["id"], doi["part_no"], doi["reason"])
            if msg1:
                msg1 = "Edit Part No: " + " ".join(msg1)
        if doi["quantity"] != str(old_doi[1]):
            msg2 = editQuantity(doi["id"], int(doi["quantity"]), doi["reason"])
            if msg2:
                msg2 = "Edit quantity: " + " ".join(msg2)
        if doi["delivery_date"] != str(old_doi[2].date()):
            if self.change_all_dates:
                delivery_order_no = DB.select("delivery_orders",("delivery_order",),"id=%s",(doi["id"],))
                msg3 = editDeliveryDateByDO(delivery_order_no, doi["delivery_date"], doi["reason"])
            else:
                msg3 = editDeliveryDate(doi["id"], doi["delivery_date"], doi["reason"])
            if msg3:
                msg3 = "Edit Delivery Date: " + " ".join(msg3)
        process_info = "\n\n".join([msg for msg in (msg1, msg2, msg3) if type(msg) is str])
        if process_info:
            messagebox.showinfo("Process info", process_info)

        self.update("delivery_orders", ("customer","uom","delivery_order","weight_limit"), "id=%s",
                    (doi["customer"],doi["uom"],doi["delivery_order"],doi["weight_limit"],id_of_data))

        messagebox.showinfo("Success", "Part No data updated!")
        self.filter_view_table("")
        close_popup()

    ###############        ###############        ###############        ###############
    def delete_edited_do_data(self, id_of_data, close_popup):
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this partNo?",
                                        icon="warning")
        if result == "yes":
            self.delete("delivery_orders", "id=%s", (id_of_data,))
            self.filter_view_table("")
            messagebox.showinfo("Success", "Part No data deleted!")
            close_popup()
    ###############        ###############        ###############        ###############
    def Archived_frame(self):
        body_frame = self.create_new_body()
        do_view_frame = ctk.CTkFrame(master=body_frame)
        do_view_filter_frame = ctk.CTkFrame(master=do_view_frame)
        do_view_filter_frame.pack(side="top", fill="x", expand=False)
        do_view_frame.pack(side="top", fill="x", expand=False)

        id_label = ctk.CTkLabel(do_view_filter_frame, text="ID:")
        id_label.grid(row=0, column=0, padx=10)
        id_entry = ctk.CTkEntry(do_view_filter_frame, width=450)
        id_entry.grid(row=0, column=1, padx=10)

        part_no_label = ctk.CTkLabel(do_view_filter_frame, text="Part No:")
        part_no_label.grid(row=1, column=0, padx=10)
        part_no_entry = ctk.CTkEntry(do_view_filter_frame, width=450)
        part_no_entry.grid(row=1, column=1, padx=10)

        customer_label = ctk.CTkLabel(do_view_filter_frame, text="Customer:")
        customer_label.grid(row=2, column=0, padx=10)
        customer_entry = ctk.CTkEntry(do_view_filter_frame, width=450)
        customer_entry.grid(row=2, column=1, padx=10)

        do_no_label = ctk.CTkLabel(do_view_filter_frame, text="DO No:")
        do_no_label.grid(row=3, column=0, padx=10)
        do_no_entry = ctk.CTkEntry(do_view_filter_frame, width=450)
        do_no_entry.grid(row=3, column=1, padx=10)

        # Checkbox for filtering out fulfilled delivery orders
        unfulfilled_entry = tk.BooleanVar()
        unfulfilled_checkbox = tk.Checkbutton(do_view_filter_frame, text="Unfulfilled", variable=unfulfilled_entry)
        unfulfilled_checkbox.grid(row=0, column=2, padx=10)

        search_button = ctk.CTkButton(do_view_filter_frame, text="Search",
                                      command=lambda: self.filter_track_table(id_entry.get(), part_no_entry.get(),
                                    customer_entry.get(), do_no_entry.get(), unfulfilled_entry.get()))
        search_button.grid(row=1, column=2, padx=10)
        self.do_view_sheet = Sheet(do_view_frame, show_x_scrollbar=False, height=400,
                                   headers=["ID", "Customer", "Part No", "Quantity", "Fulfilled Quantity", "UOM", "Carton IDs",
                                            "Delivery Order", "Delivery Date", "Time Added", "Stn Qty", "Total Stock"])
        col_size = 90
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.do_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
        "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
        "column_height_resize", "row_height_resize", "double_click_row_resize")
        self.do_view_sheet.enable_bindings(binding)
        self.do_view_sheet.pack(fill="x", padx=4, pady=4)
        self.do_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        do_data = DB.select("delivery_orders", ("id", "customer", "part_no", "quantity","fulfilled_quantity", "uom","cartons_id", "delivery_order", "delivery_date","time"), "1=1 ORDER BY id")
        main_inventory = DB.select("main_inventory", ("part_no","stn_qty","total_stock"), "part_no IN (SELECT part_no FROM delivery_orders)",)
        combined_results = {}

        # Process delivery_orders data
        for row in do_data:
            part_no = row[2]
            combined_results[part_no] = row.copy()

        # Process main_inventory data
        for row in main_inventory:
            part_no = row[0]
            if part_no in combined_results:
                combined_results[part_no].extend(row[1:])

        # Insert rows into the sheet
        for row_data in combined_results.values():
            self.do_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def Archive_frame(self):
        body_frame = self.create_new_body()
        self.table_type = "Archive"
        self.create_view_frame(body_frame)
    ###############        ###############        ###############        ###############
    def archive_id(self):
        selected_data = self.do_view_sheet.get_row_data(self.selected_row)
        do_id = selected_data[0]
        notFulfilled = checkCompletelyFulfilledID(do_id)
        if notFulfilled:
            # Ask for confirmation before archiving
            confirm = messagebox.askyesno("Confirm Archival",
                                          "This delivery order is not completely fulfilled. Do you want to archive it anyway?")
            if not confirm:
                return  # User canceled archiving
        archiveDeliveryOrder(do_id)
        process_info = "Delivery Order ID " + str(do_id) + " archival is successful!"
        messagebox.showinfo("Process info", process_info)
    ###############        ###############        ###############        ###############
    def archive_do_no(self):
        selected_data = self.do_view_sheet.get_row_data(self.selected_row)
        do_no = selected_data[7]
        notFulfilled = checkCompletelyFulfilledNo(do_no)
        if notFulfilled:
            # Ask for confirmation before archiving
            confirm = messagebox.askyesno("Confirm Archival",
                                          "At least one of the delivery orders is not completely fulfilled. Do you want to archive it anyway?")
            if not confirm:
                return  # User canceled archiving
        process_info = archive_all_orders_by_no(do_no)
        process_info = " ".join(process_info)
        messagebox.showinfo("Process info", process_info)
    ###############        ###############        ###############        ###############
    def Unarchive_frame(self):
        body_frame = self.create_new_body()
        self.table_type = "Unarchive"
        self.create_archived_view_frame(body_frame)
    ###############        ###############        ###############        ###############
    def unarchive_id(self):
        selected_data = self.do_view_sheet.get_row_data(self.selected_row)
        do_id = selected_data[0]
        process_info = unarchive_delivery_order(do_id)
        process_info = "Delivery Order ID " + str(do_id) + " Un-archival is successful!"
        messagebox.showinfo("Process info", process_info)
    ###############        ###############        ###############        ###############
    def unarchive_do_no(self):
        selected_data = self.do_view_sheet.get_row_data(self.selected_row)
        do_no = selected_data[7]
        process_info = unarchive_delivery_order_by_deliver_order_no(do_no)
        process_info = " ".join(process_info)
        messagebox.showinfo("Process info", process_info)
    ###############        ###############        ###############        ###############
##############################################################################################################
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
    def select_part_no_1(self):
        selected_row = self.search_part_no_1.selected_row
        if not selected_row:
            return
        self.search_part_no_1.close()
        entry_names = ("part_no_1",)
        values = (selected_row[1],)
        for entry_name, value in zip(entry_names, values):
            self.part_no_1_entries.change_and_disable(entry_name, value)
    ###############        ###############        ###############        ###############
    def select_part_no_2(self):
        selected_row = self.search_part_no_2.selected_row
        if not selected_row:
            return
        self.search_part_no_2.close()
        entry_names = ("part_no_2",)
        values = (selected_row[1],)
        for entry_name, value in zip(entry_names, values):
            self.part_no_2_entries.change_and_disable(entry_name, value)
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
                                   headers=["ID", "Part No", "Carton Quantity", "Date Codes", "Remarks", "Packing Date"])
        self.carton_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        col_size = 130
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size]
        self.carton_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize")
        self.carton_view_sheet.enable_bindings(binding)
        self.carton_view_sheet.pack(fill="x", padx=4, pady=4)
        self.carton_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        carton_data = DB.select("carton_table", (
            "id", "part_no", "carton_quantity", "date_codes", "remarks", "packing_date"), "loose_quantity = 0 AND (delivery_id = 0 OR delivery_id IS NULL OR CHAR_LENGTH(delivery_id & '') = 0) ORDER BY id DESC")

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
        part_no_change_list = ["None"]
        self.part_no_change_dropdown = ctk.CTkComboBox(carton_change_filter_frame, values=part_no_change_list)
        self.part_no_change_dropdown.grid(row=0, column=2, padx=(10, 5))
        self.change_carton_text = StringVar(master=carton_change_filter_frame, value="Confirm Changes")
        self.change_carton_btn = ctk.CTkButton(master=carton_change_filter_frame, textvariable=self.change_carton_text,
                                            width=20, command=lambda:self.change_carton_part_no(justification_dropdown.get())
                                            ).grid(row=0, column=3, padx=(0, 5))
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
            "id", "part_no", "carton_quantity", "date_codes", "remarks", "packing_date"), "part_no LIKE %s AND loose_quantity = 0 AND (delivery_id = 0 OR delivery_id IS NULL OR CHAR_LENGTH(delivery_id & '') = 0) ORDER BY id DESC",
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
                                   headers=["ID", "Part No", "Quantity", "Date Code", "Remarks", "Additional Info"])
        self.sealed_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        col_size = 130
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size]
        self.sealed_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize")
        self.sealed_view_sheet.enable_bindings(binding)
        self.sealed_view_sheet.pack(fill="x", padx=4, pady=4)
        self.sealed_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        sealed_data = DB.select("sealed_inventory", (
            "id", "part_no", "quantity", "date_code", "remarks", "additional_info"), "1=1 ORDER BY id DESC")

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
        part_no_change_list = ["None"]
        self.part_no_change_dropdown = ctk.CTkComboBox(sealed_change_filter_frame, values=part_no_change_list)
        self.part_no_change_dropdown.grid(row=0, column=2, padx=(10, 5))
        self.change_sealed_text = StringVar(master=sealed_change_filter_frame, value="Confirm Changes")
        self.change_sealed_btn = ctk.CTkButton(master=sealed_change_filter_frame, textvariable=self.change_sealed_text,
                                            width=20, command=lambda:self.change_sealed_part_no(justification_dropdown.get())
                                            ).grid(row=0, column=3, padx=(0, 5))
    ###############        ###############        ###############        ###############
    def sealed_filter_track_table(self, part_no):
        # Remove existing data from the table
        total_rows = self.sealed_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.sealed_view_sheet.delete_row(a)

        sealed_data = DB.select("sealed_inventory", (
            "id", "part_no", "quantity", "date_code", "remarks", "additional_info"), "part_no LIKE %s ORDER BY id DESC",
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
##############################################################################################################
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
            "column_height_resize", "row_height_resize", "double_click_row_resize")
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
        col_size = 120
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.do_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize")
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
            "delivery_date", "time"), "cartons_id LIKE %s ORDER BY id", ("%" + "old_stock" + "%",))
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
            "column_height_resize", "row_height_resize", "double_click_row_resize")
        self.carton_view_sheet.enable_bindings(binding)
        self.carton_view_sheet.pack(fill="x", padx=4, pady=4)

        self.sealed_view_sheet = Sheet(search_view_filter_frame, show_x_scrollbar=False, height=200,
                                       headers=["ID", "Part No", "Quantity", "Date Code", "Remarks"])
        col_size = 200
        col_sizes = [col_size, col_size, col_size, col_size, col_size]
        self.sealed_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize")
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
            "column_height_resize", "row_height_resize", "double_click_row_resize")
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
    ##############################################################################################################
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
            "column_height_resize", "row_height_resize", "double_click_row_resize")
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
        if not self.selected_row or self.selected_row == 0:
            return
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
                                                "Packing Date"])
        self.carton_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        col_size = 130
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size]
        self.carton_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize")
        self.carton_view_sheet.enable_bindings(binding)
        self.carton_view_sheet.pack(fill="x", padx=4, pady=4)
        self.carton_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        carton_data = DB.select("carton_table", (
            "id", "part_no", "carton_quantity", "date_codes", "remarks", "packing_date"),
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
            "id", "part_no", "carton_quantity", "date_codes", "remarks", "packing_date"),
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
                                       headers=["ID", "Part No", "Quantity", "Date Code", "Remarks", "Additional Info"])
        self.sealed_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        col_size = 130
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size]
        self.sealed_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize")
        self.sealed_view_sheet.enable_bindings(binding)
        self.sealed_view_sheet.pack(fill="x", padx=4, pady=4)
        self.sealed_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        sealed_data = DB.select("sealed_inventory", ("id", "part_no", "quantity", "date_code", "remarks", "additional_info"), "1=1 ORDER BY id DESC")

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

        sealed_data = DB.select("sealed_inventory", ("id", "part_no", "quantity", "date_code", "remarks", "additional_info"),
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
            "column_height_resize", "row_height_resize", "double_click_row_resize")
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
class OtherOptions(DB,Page):
    def __init__(self):
        menu_ls = {
            "Auto Update Inventory": self.Auto_Update_frame,
        }
        self.starting = False
        self.create_new_page("Other Options", menu_ls)
    ###############        ###############        ###############        ###############
    def Auto_Update_frame(self):
        body_frame = self.create_new_body()
        textbox = tk.Text(master=body_frame, bg="gray90")
        textbox.grid(row=1, column=0, columnspan=len([i for i in range(4)]), sticky="nwe", pady=10, padx=20)
        ctk.CTkButton(master=body_frame, text="Start Update Inventory",
                                command=lambda: self.auto_update_btn(textbox), height=35
                                ).grid(row=2, column=1, pady=10)

        def stop_btn():
            self.starting = False

        ctk.CTkButton(master=body_frame, text="Stop", command=stop_btn, height=35).grid(row=2, column=2,pady=10)
    ###############        ###############        ###############        ###############
    def auto_update_btn(self, textbox):
        if self.starting == True:
            return
        self.starting = True
        def updating():
            part_no_ls = DB.select("part_info", ("part_no",))
            textbox.delete(1.0, tk.END)
            i = 1
            for part_no in part_no_ls:
                if not self.starting:  # stop the loop
                    return
                updateMainInventory(part_no[0])
                line = f"\n{i}. part_no: {part_no[0]} successfully updated!"
                textbox.insert(tk.END, line)
                textbox.see(tk.END)
                i += 1
            messagebox.showinfo("Process info", "The main inventory is successfully updated!")
            self.starting = False
        threading.Thread(target=updating).start()
    ###############        ###############        ###############        ###############
##############################################################################################################
class User(DB,Page):
    def __init__(self):
        menu_ls = {
            "Create New User": self.Create_frame,
            "Edit/Delete User": self.Edit_frame,
            "User Report": self.Report_frame,
        }
        self.popup_open = False
        self.selected_row = None
        self.create_new_page("User", menu_ls)
    ###############        ###############        ###############        ###############
    def Create_frame(self):
        body_frame = self.create_new_body()
        entries = (
            ("user_name", "entry", (0, 0, 1), None),
            ("password", "entry", (1, 0, 1), None),
            ("first_name", "entry", (2, 0, 1), None),
            ("last_name", "entry", (3, 0, 1), None),
            ("department", "menu", (4, 0, 1), ('Marketing','QC','Packing','Other')),
        )
        self.user_entries = EntriesFrame(body_frame, entries);
        self.user_entries.pack()
        ctk.CTkLabel(master=body_frame, text="User Permissions :", width=50).pack()
        permissions_frame = ctk.CTkFrame(master=body_frame, height=20)
        permissions_frame.pack()
        widget_infos = (
            # label                     , entry name
            ("admin privileges ", "admin"),
            ("Batch Entry ", "batch_entry"),
            ("Data Editor ", "data_editor"),
            ("Data Viewer ", "data_viewer"),
            ("Delivery Order Entry ", "delivery_order_entry"),
        )
        self.user_checkbox_entries = {}
        for label, entry_name in widget_infos:
            self.user_checkbox_entries[entry_name] = ctk.CTkCheckBox(master=permissions_frame, text=label)
            self.user_checkbox_entries[entry_name].pack(side=tk.LEFT, padx=10)
        self.create_footer(self.create_user_btn)
    ###############        ###############        ###############        ###############
    def create_user_btn(self):
        user_data = self.user_entries.get_data()
        user_info = DB.select("user", ("user_name",), "user_name=%s", (user_data["user_name"],))
        user_name = user_data["user_name"]
        if user_info:
            messagebox.showinfo("Info",
                                f"User='{user_name}' is already exist in database, please choose unique username!")
            return
        F = Fernet(b'Cgfow1pOUko9As6UAox4FfJSX63kcKXnLJBICAFCnyE=')
        user_data["password"] = F.encrypt(user_data["password"].encode()).decode()
        data = list(user_data.values())
        # Append checkbox values
        for checkbox_name, checkbox in self.user_checkbox_entries.items():
            data.append(checkbox.get())
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.append(current_datetime)
        self.insert("user", ("user_name","password","first_name","last_name","department","admin",
                             "batch_entry","data_editor","data_viewer","delivery_order_entry","time_created"), data)
        messagebox.showinfo("Info", f"User='{user_name}' is created successfully!")
    ###############        ###############        ###############        ###############
    def Edit_frame(self):
        body_frame = self.create_new_body()
        user_view_frame = ctk.CTkFrame(master=body_frame)
        user_view_filter_frame = ctk.CTkFrame(master=user_view_frame)
        user_view_filter_frame.pack(side="top", fill="x", expand=False)
        filter_label = ctk.CTkLabel(user_view_filter_frame, text="Search User:")
        filter_label.pack(side='left', padx=10, pady=10)  # Place label on the left side

        filter_entry = ctk.CTkEntry(user_view_filter_frame, width=450)
        filter_entry.pack(side='left', padx=10, pady=10)  # Place entry widget next to the label

        search_button = ctk.CTkButton(user_view_filter_frame, text="Search",
                                      command=lambda: self.filter_user_view_table(filter_entry.get()))
        search_button.pack(side='left')
        edit_button = ctk.CTkButton(master=user_view_filter_frame, text="Edit/Delete",
                                    command=lambda: self.edit_row_frame(body_frame))
        edit_button.pack(side='right')
        user_view_frame.pack(side="top", fill="x", expand=False)
        self.user_view_sheet = Sheet(user_view_frame, show_x_scrollbar=False, height=200,
                                   headers=["ID", "User Name", "First Name", "Last Name", "Department", "Admin",
                                            "Batch Entry", "Data Editor", "Data Viewer", "Delivery Order Entry"])
        col_size = 100
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.user_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
        "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
        "column_height_resize", "row_height_resize", "double_click_row_resize")
        self.user_view_sheet.enable_bindings(binding)
        self.user_view_sheet.pack(fill="x", padx=4, pady=4)
        self.user_view_sheet.bind("<ButtonRelease-1>", self.cell_select)

        user_data = DB.select("user", (
        "id", "user_name", "first_name", "last_name", "department", "CASE WHEN admin = 1 THEN 'Yes' ELSE 'No' END AS admin",
        "CASE WHEN batch_entry = 1 THEN 'Yes' ELSE 'No' END AS batch_entry",
        "CASE WHEN data_editor = 1 THEN 'Yes' ELSE 'No' END AS data_editor",
        "CASE WHEN data_viewer = 1 THEN 'Yes' ELSE 'No' END AS data_viewer",
        "CASE WHEN delivery_order_entry = 1 THEN 'Yes' ELSE 'No' END AS delivery_order_entry"),
                              "1=1 ORDER BY id")
        for row_data in user_data:
            self.user_view_sheet.insert_row(values=row_data)

    ###############        ###############        ###############        ###############
    def filter_user_view_table(self, keyword):
        # Remove existing data from the table
        total_rows = self.user_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.user_view_sheet.delete_row(a)

        user_data = DB.select("user", (
        "id", "user_name", "first_name", "last_name", "department", "CASE WHEN admin = 1 THEN 'Yes' ELSE 'No' END AS admin",
        "CASE WHEN batch_entry = 1 THEN 'Yes' ELSE 'No' END AS batch_entry",
        "CASE WHEN data_editor = 1 THEN 'Yes' ELSE 'No' END AS data_editor",
        "CASE WHEN data_viewer = 1 THEN 'Yes' ELSE 'No' END AS data_viewer",
        "CASE WHEN delivery_order_entry = 1 THEN 'Yes' ELSE 'No' END AS delivery_order_entry"),
                                     "user_name LIKE %s ORDER BY id", ("%%" + keyword + "%%",))
        for row_data in user_data:
            self.user_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def cell_select(self, event):
        row = self.user_view_sheet.identify_row(event)
        if self.user_view_sheet.total_rows() > 0:
            self.selected_row = row
    ###############        ###############        ###############        ###############
    def edit_row_frame(self,master):
        if self.popup_open:
            messagebox.showinfo("Error", "The User Edit Window is already open!")
            self.add_user_window.lift()
        else:
            self.popup_open = True

            if self.selected_row is None:
                messagebox.showinfo("Error", "Please select a row to edit.")
                self.popup_open = False
                return

            # Create a new window (Toplevel) for editing user
            self.add_user_window = Toplevel(master)
            self.add_user_window.title("Edit User")
            self.add_user_window.lift()

            def close_popup():
                self.add_user_window.destroy()
                self.popup_open = False

            # Bind the close_popup function to the window's close button
            self.add_user_window.protocol("WM_DELETE_WINDOW", close_popup)

            # Retrieve data from the selected row
            selected_data = self.user_view_sheet.get_row_data(self.selected_row)
            id_of_data = selected_data[0]

            add_user_frame = ctk.CTkFrame(self.add_user_window)
            add_user_frame.pack()

            entries = (
                ("user_name", "entry", (0, 0, 1), None),
                ("password", "entry", (1, 0, 1), None),
                ("first_name", "entry", (2, 0, 1), None),
                ("last_name", "entry", (3, 0, 1), None),
                ("department", "menu", (4, 0, 1), ('Marketing', 'QC', 'Packing', 'Other')),
            )
            self.user_edit_entries = EntriesFrame(add_user_frame, entries)
            self.user_edit_entries.pack()
            for i in range(len(entries)):
                if i == 0:
                    self.user_edit_entries.change_value(entries[i][0], selected_data[i+1] or "")
                elif i > 1:
                    self.user_edit_entries.change_value(entries[i][0], selected_data[i] or "")
            ctk.CTkLabel(master=add_user_frame, text="User Permissions :", width=50).pack()
            permissions_frame = ctk.CTkFrame(master=add_user_frame, height=20)
            permissions_frame.pack()
            widget_infos = (
                # label                     , entry name
                ("admin privileges ", "admin"),
                ("Batch Entry ", "batch_entry"),
                ("Data Editor ", "data_editor"),
                ("Data Viewer ", "data_viewer"),
                ("Delivery Order Entry ", "delivery_order_entry"),
            )
            self.user_checkbox_entries = {}
            counter = 5
            for label, entry_name in widget_infos:
                self.user_checkbox_entries[entry_name] = ctk.CTkCheckBox(master=permissions_frame, text=label)
                self.user_checkbox_entries[entry_name].pack(side=tk.LEFT, padx=10)
                if selected_data[counter] == "Yes":
                    self.user_checkbox_entries[entry_name].select()
                counter += 1


            button_frame = ctk.CTkFrame(master=add_user_frame)
            button_frame.pack(side="bottom", fill="x", expand=False)
            ctk.CTkButton(master=button_frame, text="Save",
                          command=lambda: self.save_edited_user_data(id_of_data,close_popup)).pack(
                side="left", padx=10, pady=10)
            ctk.CTkButton(master=button_frame, text="Delete",
                          command=lambda: self.delete_edited_user_data(id_of_data,close_popup)).pack(
                side="right", padx=10, pady=10)

    ###############        ###############        ###############        ###############
    def save_edited_user_data(self, id_of_data, close_popup):
        # Extract data from EntriesFrame instances
        user_data = self.user_edit_entries.get_data()
        # Retrieve data
        edited_data = list(user_data.values())
        user_name = user_data["user_name"]

        if user_data["password"] != "":
            F = Fernet(b'Cgfow1pOUko9As6UAox4FfJSX63kcKXnLJBICAFCnyE=')
            user_data["password"] = F.encrypt(user_data["password"].encode()).decode()

        # Append checkbox values
        for checkbox_name, checkbox in self.user_checkbox_entries.items():
            edited_data.append(checkbox.get())
        edited_data.append(id_of_data)
        self.update("user", ("user_name","password","first_name","last_name","department","admin",
                             "batch_entry","data_editor","data_viewer","delivery_order_entry"),
                    "id=%s", edited_data)
        messagebox.showinfo("Info", f"User='{user_name}' has been changed successfully!")
        self.filter_user_view_table("")
        close_popup()
    ###############        ###############        ###############        ###############
    def delete_edited_user_data(self,id_of_data,close_popup):
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this user?",
                                        icon="warning")
        if result == "yes":
            self.delete("user", "id=%s", (id_of_data,))
            self.filter_user_view_table("")
            messagebox.showinfo("Success", "User data deleted!")
            close_popup()
    ###############        ###############        ###############        ###############
    def Report_frame(self):
        body_frame = self.create_new_body()
        self.user_view_frame = ctk.CTkFrame(master=body_frame)
        user_view_filter_frame = ctk.CTkFrame(master=self.user_view_frame)
        user_view_filter_frame.pack(side="top", fill="x", expand=False)
        filter_label = ctk.CTkLabel(user_view_filter_frame, text="Search User:")
        filter_label.pack(side='left', padx=10, pady=10)  # Place label on the left side

        filter_entry = ctk.CTkEntry(user_view_filter_frame, width=450)
        filter_entry.pack(side='left', padx=10, pady=10)  # Place entry widget next to the label

        search_button = ctk.CTkButton(user_view_filter_frame, text="Search",
                                      command=lambda: self.filter_user_view_table(filter_entry.get()))
        search_button.pack(side='left')
        edit_button = ctk.CTkButton(master=user_view_filter_frame, text="User Report",
                                    command=lambda: self.user_report_frame(body_frame))
        edit_button.pack(side='right')
        self.user_view_frame.pack(side="top", fill="x", expand=False)
        self.user_view_sheet = Sheet(self.user_view_frame, show_x_scrollbar=False, height=200,
                                     headers=["ID", "User Name", "First Name", "Last Name", "Department", "Admin",
                                              "Batch Entry", "Data Editor", "Data Viewer", "Delivery Order Entry"])
        col_size = 100
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.user_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize")
        self.user_view_sheet.enable_bindings(binding)
        self.user_view_sheet.pack(fill="x", padx=4, pady=4)
        self.user_view_sheet.bind("<ButtonRelease-1>", self.cell_select)

        user_data = DB.select("user", (
            "id", "user_name", "first_name", "last_name", "department",
            "CASE WHEN admin = 1 THEN 'Yes' ELSE 'No' END AS admin",
            "CASE WHEN batch_entry = 1 THEN 'Yes' ELSE 'No' END AS batch_entry",
            "CASE WHEN data_editor = 1 THEN 'Yes' ELSE 'No' END AS data_editor",
            "CASE WHEN data_viewer = 1 THEN 'Yes' ELSE 'No' END AS data_viewer",
            "CASE WHEN delivery_order_entry = 1 THEN 'Yes' ELSE 'No' END AS delivery_order_entry"),
                                "1=1 ORDER BY id")
        for row_data in user_data:
            self.user_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def user_report_frame(self, master):
        # Retrieve data from the selected row
        selected_data = self.user_view_sheet.get_row_data(self.selected_row)
        user_name = selected_data[1]

        # Find and clear existing pie chart frames only
        for widget in master.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != self.user_view_frame:
                if widget.winfo_children():
                    widget.destroy()

        dump_data = (("Batch Entry", 88, 5), ("Data Editor", 63, 2),
                     ("Data Viewer", 42, 0), ("Delivery Order Entry", 57, 9),
                     )
        data = [["Batch Entry", 0, 0], ["Data Editor", 0, 0],
                ["Data Viewer", 0, 0], ["Delivery Order Entry", 0, 0], ]
        # counting the total records of the user in each program
        old_description_ls = DB.select("logger", ("program",), "user_name=%s", (user_name,))
        for record in old_description_ls:
            if record[0] == "Batch Entry":
                data[0][1] += 1
            elif record[0] == 'Data Editor':
                data[1][1] += 1
            elif record[0] == "Data Viewer":
                data[2][1] += 1
            elif record[0] == "Delivery Order Entry":
                data[3][1] += 1
        for block in data.copy():
            if block[1] == 0:
                data.remove(block)
        if data == []:
            frame = ctk.CTkFrame(master)
            frame.pack(expand=True, fill="both", side="left")
            ctk.CTkLabel(frame, width=500, height=300, text="No records were found").pack()
            return

        # check if there is an error
        old_description_ls = DB.select("logger", ("old_description",), "old_description LIKE %s",
                                         ("%%" + user_name + "%%",))
        id_ls = [record[0].split(" | ")[0] for record in old_description_ls]
        id_ls = ", ".join(id_ls)
        Detected_error_ls = DB.select("logger", ("program",), "id IN (%s) AND reason=%s",
                                        (id_ls, "Just amendment"))
        for record in Detected_error_ls:
            if record[0] == "Batch Entry":
                data[0][2] += 1
            elif record[0] == 'Data Editor':
                data[1][2] += 1
            elif record[0] == "Data Viewer":
                data[2][2] += 1
            elif record[0] == "Delivery Order Entry":
                data[3][2] += 1

        self.create_user_report(master, data)

    ###############        ###############        ###############        ###############
    def create_pie_chart(self, master, data):
        title, total_input, error_input = data
        # frame to display the title , chart , total_input , error_input
        pie_chart_frame = ctk.CTkFrame(master)
        pie_chart_frame.pack(expand=True, fill="both", side="left", pady=4, padx=4)
        # display title
        ctk.CTkLabel(pie_chart_frame, text=title).pack(padx=4)
        # data to display
        labels = ('Total Input', 'Error Input')
        values = (total_input, error_input)
        # Pie chart
        fig = Figure(figsize=(1.7, 1.7), facecolor='gray')  # create a figure object
        ax = fig.add_subplot(111)  # add an Axes to the figure
        ax.pie(values, radius=1, autopct='%0.1f%%', shadow=True, )
        ax.legend(loc='upper right', bbox_to_anchor=(0.8, 1.21), labels=labels)
        chart = FigureCanvasTkAgg(fig, pie_chart_frame)
        chart.get_tk_widget().pack()
        # info at the bottom
        frame = ctk.CTkFrame(pie_chart_frame, corner_radius=0)
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(frame, text=labels[0] + ": ", width=0).pack(
            anchor='w', padx=4, side="left")
        ctk.CTkLabel(frame, text=total_input, width=0).pack(anchor='w', padx=4,
                                                                                  side="left")
        frame = ctk.CTkFrame(pie_chart_frame, corner_radius=0)
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(frame, text=labels[1] + ": ", width=0).pack(
            anchor='w', padx=4, side="left")
        ctk.CTkLabel(frame, text=error_input, width=0).pack(anchor='w', padx=4,
                                                                                  side="left")
    ###############        ###############        ###############        ###############
    def create_user_report(self, master,data_ls=()):
        for data in data_ls:
            frame = ctk.CTkFrame(master,border_width=4)
            frame.pack(expand=True, fill="both", side="left", padx=4)
            self.create_pie_chart(frame, data)
##############################################################################################################
class Inventory(DB,Page):
    def __init__(self):
        menu_ls = {
            "Main Inventory": self.Main_Inventory_frame,
            "Inventory Tracker": self.Inventory_Tracker_frame,
        }
        self.create_new_page("Inventory", menu_ls)
    ###############        ###############        ###############        ###############
    # TODO: Needs to have checkbox for whether it has stock or not!
    def Main_Inventory_frame(self):
        body_frame = self.create_new_body()
        SearchFrame(body_frame, "Main Inventory").pack(fill="both", expand=True)
    ###############        ###############        ###############        ###############
    def Inventory_Tracker_frame(self):
        body_frame = self.create_new_body()
        ViewFrame(body_frame,["Carton Table","Archived Carton Table" , "Sealed Inventory"])

