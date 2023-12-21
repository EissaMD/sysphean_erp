from config import *
from ..UI import Page, EntriesFrame, SearchWindow
from ..Logics import DB
from .Delivery_Order_Entry_backend import (excel_sheet_to_delivery_order, import_order_to_database,
                                           checkUnfulfilledDeliveryOrdersWithSimilarPartNos, refreshDeliveryOrders)
from .Data_Editor_backend import (addDeliveryOrderNew, editPartNo, editQuantity, editDeliveryDateByDO, editDeliveryDate)
from .Data_Viewer_Backend import (checkCompletelyFulfilledID, checkCompletelyFulfilledNo, archiveDeliveryOrder,
                                  archive_all_orders_by_no, unarchive_delivery_order_by_deliver_order_no, unarchive_delivery_order)
from ..LoginSystem import LoginSystem

class DeliveryOrder(DB,Page):
    def __init__(self):
        menu_ls = {
            "Add (Upload)": self.Add_frame,
            "Add (Manual)": self.Add_manual_frame,
            "Edit/Delete": self.Edit_frame,
            "Track": self.Track_frame,
            "Track (Archived)": self.Track_Archived_frame,
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
        ctk.CTkLabel(master=rwo_color_frame, text=f"                               Not exist in DB                                ", bg_color="#9bfad5", text_color="black"
                               ).grid(row=1, column=0)
        ctk.CTkLabel(master=rwo_color_frame, text=f"                           Unavailable Part No                           ", bg_color="#ffff00",
                               text_color="black"
                               ).grid(row=2, column=0)
        ctk.CTkLabel(master=rwo_color_frame, text=f"                                    Exist in DB                                   ", bg_color="#fcc9c2", text_color="black"
                               ).grid(row=3, column=0, padx=5, pady=(0, 4))

        do_color_frame = ctk.CTkFrame(master=self.frame_left, border_width=1, fg_color=None)
        do_color_frame.grid(row=7, column=0, padx=1)
        ctk.CTkLabel(master=do_color_frame, text=f"Calendar Legend :", width=10
                               ).grid(row=0, column=0, sticky="w", padx=5, pady=1)
        ctk.CTkLabel(master=do_color_frame, text=f"                                 DO Exists                                  ", bg_color="#008101", text_color="black"
                               ).grid(row=1, column=0)
        ctk.CTkLabel(master=do_color_frame, text=f"                                     No DO                                    ", bg_color="#ff0101",
                               text_color="black"
                               ).grid(row=2, column=0)
        self.do_text = StringVar(master=do_color_frame, value="                              No. of DOs: 0                              ")
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
        ctk.CTkButton(master=bottom_frame, text="Upload", width=10, command=self.upload_btn
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
        delivery_orders_dates = DB.select("delivery_orders", ("DATE(time_created) AS time_created",), "time_created IS NOT NULL")
        archived_delivery_orders_dates = DB.select("archived_delivery_orders", ("DATE(time_created)",), "time_created IS NOT NULL")
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
            DB.delete("calendar_exceptions", "id = %s", (id_of_date,))
            messagebox.showinfo("Success", "Date removed from exception!")
        else:
            user_name = LoginSystem.user_name
            DB.insert("calendar_exceptions", ("date", "time_created", "user_name"), (date, datetime.now(), user_name))
            messagebox.showinfo("Success", "Date added to exception!")

        # Refresh the calendar to reflect the changes
        self.refresh_calendar()
    ###############        ###############        ###############        ###############
    def date_selected(self, event):
        selected_date = self.cal.get_date()
        selected_date_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        no_of_ado = DB.select("archived_delivery_orders", ("COUNT(*)",), "DATE(time_created) = %s", (selected_date,))
        if no_of_ado:
            no_of_ado = int(no_of_ado[0][0])
        else:
            no_of_ado = 0
        no_of_do = DB.select("delivery_orders", ("COUNT(*)",), "DATE(time_created) = %s", (selected_date,))
        if no_of_do:
            no_of_do = int(no_of_do[0][0])
        else:
            no_of_do = 0
        total_no_of_do = no_of_ado + no_of_do
        self.do_text.set(f"                              No. of DOs: {str(total_no_of_do)}                              ")
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
        messagebox.showinfo("Process info", process_info)
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
                                            "Delivery Order", "Delivery Date", "Time Created", "User", "Stn Qty", "Total Stock"])
        col_size = 70
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size,
                     col_size, col_size, col_size]
        self.do_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize", "arrowkeys")
        self.do_view_sheet.enable_bindings(binding)
        self.do_view_sheet.pack(fill="x", padx=4, pady=4)
        self.do_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        do_data = DB.select("delivery_orders", (
        "id", "customer", "part_no", "quantity", "fulfilled_quantity", "uom", "cartons_id", "delivery_order",
        "delivery_date", "time_created", "user_name"), "1=1 ORDER BY id")
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
        "delivery_date", "time_created", "user_name"), conditions,("%%" + id + "%%","%%" + part_no + "%%","%%" + customer + "%%","%%" + do_no + "%%"))
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
                                            "Delivery Order", "Delivery Date", "Time Created", "Time Archived", "User", "Archived User"])
        col_size = 70
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size,
                     col_size, col_size, col_size]
        self.do_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
            "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
            "column_height_resize", "row_height_resize", "double_click_row_resize", "arrowkeys")
        self.do_view_sheet.enable_bindings(binding)
        self.do_view_sheet.pack(fill="x", padx=4, pady=4)
        self.do_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        do_data = DB.select("archived_delivery_orders", (
        "id", "customer", "part_no", "quantity", "fulfilled_quantity", "uom", "cartons_id", "delivery_order",
        "delivery_date", "time_created", "time_archived", "user_name", "user_name_archived"), "1=1 ORDER BY id DESC")

        # Insert rows into the sheet
        for row_data in do_data:
            self.do_view_sheet.insert_row(values=row_data)
        if self.table_type == "Unarchive":
            do_archive_filter_frame = ctk.CTkFrame(master=do_view_frame)
            do_archive_filter_frame.pack(side="bottom", fill="x", expand=False)
            self.unarchive_id_text = StringVar(master=do_archive_filter_frame, value="Unarchive ID")
            self.unarchive_do_no_text = StringVar(master=do_archive_filter_frame, value="Unarchive DO No")
            self.unarchive_id_btn = ctk.CTkButton(master=do_archive_filter_frame, textvariable=self.unarchive_id_text,
                                                width=20, command=self.unarchive_id
                                                ).grid(row=0, column=2, padx=(0, 5))
            self.unarchive_do_no_btn = ctk.CTkButton(master=do_archive_filter_frame, textvariable=self.unarchive_do_no_text,
                                                   width=20, command=self.unarchive_do_no
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
        "delivery_date", "time_created","time_archived", "user_name", "user_name_archived"), conditions,("%%" + id + "%%","%%" + part_no + "%%","%%" + customer + "%%","%%" + do_no + "%%"))


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
                                                 "Delivery Date", "Weight Limit", "Time Created", "User"])
        col_size = 100
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.do_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = ("single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize", "column_height_resize", "row_height_resize", "double_click_row_resize", "arrowkeys")
        self.do_view_sheet.enable_bindings(binding)
        self.do_view_sheet.pack(fill="x", padx=4, pady=4)
        self.do_view_sheet.bind("<ButtonRelease-1>", self.cell_select)

        do_data = DB.select("delivery_orders", ("id","customer","part_no","quantity","uom","delivery_order","delivery_date","weight_limit","time_created","user_name"), "1=1 ORDER BY id")
        for row_data in do_data:
            self.do_view_sheet.insert_row(values=row_data)
    ###############        ###############        ###############        ###############
    def filter_view_table(self, keyword):
        # Remove existing data from the table
        total_rows = self.do_view_sheet.get_total_rows()
        for a in range(total_rows - 1, -1, -1):
            self.do_view_sheet.delete_row(a)

        part_info_data = DB.select("delivery_orders", ("id","customer","part_no","quantity","uom","delivery_order","delivery_date","weight_limit","time_created","user_name"), "part_no LIKE %s ORDER BY id", ("%%" + keyword + "%%",))
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
            id_entry = (
                ("id", "entry", (0, 0, 1), None),
            )
            self.id_entries = EntriesFrame(add_do_frame, id_entry);
            self.id_entries.pack()
            customer_entry = (
                ("customer", "entry", (0, 0, 1), None),
            )
            self.customer_entries = EntriesFrame(add_do_frame, customer_entry);
            self.customer_entries.pack()
            part_no_entry = (
                ("part_no", "entry", (0, 0, 1), None),
            )
            self.part_no_edit_entries = EntriesFrame(add_do_frame, part_no_entry);
            self.part_no_edit_entries.pack()
            # add search btn for part no name
            frame = self.part_no_edit_entries.frames["part_no"]
            self.search_part_no = SearchWindow(select_btn=self.select_part_no, layout="Search Part No")
            ctk.CTkButton(frame, image="search_icon", text="", command=self.search_part_no.new_window, width=20).pack(
                side="left")
            entries = (
                ("quantity", "entry", (0, 0, 1), None),
                ("uom", "menu", (1, 0, 1), ("PCS", "PANEL")),
                ("delivery_order", "entry", (2, 0, 1), None),
                ("delivery_date", "date", (3, 0, 1), None),
                ("weight_limit", "entry", (4, 0, 1), None),
            )
            self.edit_delivery_order_entries = EntriesFrame(add_do_frame, entries);
            self.edit_delivery_order_entries.pack()
            misc_entries = (
                ("reason", "menu", (0, 0, 1), ("Just amendment", "Customer request", "QC request", "Marketing request")),
                ("change_all_dates_on_do_no", "seg_btn", (1,0,1), ["No", "Yes"])
            )
            self.misc_entries = EntriesFrame(add_do_frame, misc_entries);
            self.misc_entries.pack()
            self.id_entries.change_value("id", selected_data[0] or "")
            self.id_entries.disable_all()
            self.customer_entries.change_value("customer", selected_data[1] or "")
            self.part_no_edit_entries.change_value("part_no", selected_data[2] or "")
            self.part_no_edit_entries.disable_all()
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
        id_data = self.id_entries.get_data()
        customer_data = self.customer_entries.get_data()
        part_no_data = self.part_no_edit_entries.get_data()
        delivery_order_data = self.edit_delivery_order_entries.get_data()
        misc_data = self.misc_entries.get_data()

        if part_no_data["part_no"] == "":
            messagebox.showinfo("ERROR", "Part No entry is empty!")
            self.do_window.lift()
            return
        # Retrieve data
        edited_data = {
            **dict(id_data),
            **dict(customer_data),
            **dict(part_no_data),
            **dict(delivery_order_data),
            **dict(misc_data)
        }
        self.change_all_dates = False
        if misc_data["change_all_dates_on_do_no"] == "Yes":
            self.change_all_dates = True
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
        old_doi = old_doi[0]
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
                delivery_order_no = delivery_order_no[0][0]
                msg3 = editDeliveryDateByDO(delivery_order_no, doi["delivery_date"], doi["reason"])
            else:
                msg3 = editDeliveryDate(doi["id"], doi["delivery_date"], doi["reason"])
            if msg3:
                msg3 = "Edit Delivery Date: " + " ".join(msg3)
        process_info = "\n\n".join([msg for msg in (msg1, msg2, msg3) if type(msg) is str])
        if process_info:
            messagebox.showinfo("Process info", process_info)

        DB.update("delivery_orders", ("customer","uom","delivery_order","weight_limit"), "id=%s",
                    (doi["customer"],doi["uom"],doi["delivery_order"],doi["weight_limit"],id_of_data))

        messagebox.showinfo("Success", "Delivery Order data updated!")
        self.filter_view_table("")
        close_popup()

    ###############        ###############        ###############        ###############
    def delete_edited_do_data(self, id_of_data, close_popup):
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this delivery order?",
                                        icon="warning")
        if result == "yes":
            DB.delete("delivery_orders", "id=%s", (id_of_data,))
            self.filter_view_table("")
            messagebox.showinfo("Success", "Delivery Order data deleted!")
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
                                            "Delivery Order", "Delivery Date", "Time Created", "Stn Qty", "Total Stock"])
        col_size = 90
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
        self.do_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = (
        "single_select", "row_select", "column_width_resize", "double_click_column_resize", "row_width_resize",
        "column_height_resize", "row_height_resize", "double_click_row_resize", "arrowkeys")
        self.do_view_sheet.enable_bindings(binding)
        self.do_view_sheet.pack(fill="x", padx=4, pady=4)
        self.do_view_sheet.bind("<ButtonRelease-1>", self.cell_select)
        do_data = DB.select("delivery_orders", ("id", "customer", "part_no", "quantity","fulfilled_quantity", "uom","cartons_id", "delivery_order", "delivery_date","time_created","user_name"), "1=1 ORDER BY id")
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
        self.filter_track_table("","","","",False)
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
        self.filter_track_table("", "", "", "", False)
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
        #self.filter_track_table("", "", "", "", False)
    ###############        ###############        ###############        ###############
    def unarchive_do_no(self):
        selected_data = self.do_view_sheet.get_row_data(self.selected_row)
        do_no = selected_data[7]
        process_info = unarchive_delivery_order_by_deliver_order_no(do_no)
        process_info = " ".join(process_info)
        messagebox.showinfo("Process info", process_info)
        #self.filter_track_table("", "", "", "", False)
    ###############        ###############        ###############        ###############
