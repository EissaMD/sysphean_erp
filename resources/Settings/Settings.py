from config import *
from ..UI import Page, LeftMenu , EntriesFrame , CheckboxFrame
from ..Logics import DB

class Settings(Page):
    def __init__(self):
        self.create_new_page("Sales")
        left_menu = LeftMenu()
        left_menu_ls = {
            "User"           : User,
        }
        left_menu.update_menu(left_menu_ls) 
    ###############        ###############        ###############        ###############
    def sales_report(self):
        self.create_new_page("Sales Report")
##############################################################################################################

class User(Page):
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
        permissions_entry = ("user_permissions" ,("admin","sales","inventory","manufacturing","procurement") , (0,0,0,0,0) )
        self.permissions = CheckboxFrame(body_frame,permissions_entry)
        self.create_footer(self.create_user_btn)
    ###############        ###############        ###############        ###############
    def create_user_btn(self):
        u = {} #user data
        for entries in (self.user_entries,self.permissions):
            u.update(entries.get_data())
        user_info = DB.select("user", ("user_name",), "user_name=%s", (u["user_name"],))
        user_name = u["user_name"]
        if user_info:
            messagebox.showinfo("Info",f"User='{user_name}' is already exist in database, please choose unique username!")
            return
        F = Fernet(b'Cgfow1pOUko9As6UAox4FfJSX63kcKXnLJBICAFCnyE=')
        u["password"] = F.encrypt(u["password"].encode()).decode()
        data = (u["user_name"]  ,u["password"]  ,u["first_name"]    ,u["last_name"]     ,u["department"],u["admin"],
                u["sales"]      ,u["inventory"] ,u["manufacturing"] ,u["procurement"]   ,datetime.now())
        ret =DB.insert("user", ("user_name","password","first_name","last_name","department","admin",
                             "sales","inventory","manufacturing","procurement","time_created"), data)
        if ret is True:
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
        "CASE WHEN sales = 1 THEN 'Yes' ELSE 'No' END AS sales",
        "CASE WHEN inventory = 1 THEN 'Yes' ELSE 'No' END AS inventory", #"sales","inventory","manufacturing","procurement","time_created"
        "CASE WHEN manufacturing = 1 THEN 'Yes' ELSE 'No' END AS manufacturing",
        "CASE WHEN procurement = 1 THEN 'Yes' ELSE 'No' END AS procurement"),
                              )
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
        "CASE WHEN sales = 1 THEN 'Yes' ELSE 'No' END AS sales",
        "CASE WHEN inventory = 1 THEN 'Yes' ELSE 'No' END AS inventory",
        "CASE WHEN manufacturing = 1 THEN 'Yes' ELSE 'No' END AS manufacturing",
        "CASE WHEN procurement = 1 THEN 'Yes' ELSE 'No' END AS procurement"),
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
                ("Batch Entry ", "sales"),
                ("Data Editor ", "inventory"),
                ("Data Viewer ", "manufacturing"),
                ("Delivery Order Entry ", "procurement"),
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
        DB.update("user", ("user_name","password","first_name","last_name","department","admin",
                             "sales","inventory","manufacturing","procurement"),
                    "id=%s", edited_data)
        messagebox.showinfo("Info", f"User='{user_name}' has been changed successfully!")
        self.filter_user_view_table("")
        close_popup()
    ###############        ###############        ###############        ###############
    def delete_edited_user_data(self,id_of_data,close_popup):
        result = messagebox.askquestion("Confirm Deletion", "Are you sure you want to delete this user?",
                                        icon="warning")
        if result == "yes":
            DB.delete("user", "id=%s", (id_of_data,))
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
            "CASE WHEN sales = 1 THEN 'Yes' ELSE 'No' END AS sales",
            "CASE WHEN inventory = 1 THEN 'Yes' ELSE 'No' END AS inventory",
            "CASE WHEN manufacturing = 1 THEN 'Yes' ELSE 'No' END AS manufacturing",
            "CASE WHEN procurement = 1 THEN 'Yes' ELSE 'No' END AS procurement"),
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