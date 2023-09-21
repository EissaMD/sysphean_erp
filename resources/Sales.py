import customtkinter as ctk
from .UI import Page, LeftMenu , EntriesFrame , SearchCustomer , RadioButtons , ChartWin
from tksheet import Sheet
from .Logics import DB
from tkinter import messagebox
from datetime import datetime
from dateutil.relativedelta import relativedelta
class Sales(Page):
    def __init__(self):
        self.create_new_page("- - -")
        left_menu = LeftMenu()
        left_menu_ls = {
            "Sales Order"           : SaleOrder,
            "Customer Management"   : customerManagement,
            "Tracking Sale"         : TrackingSale,
            "Sales Report"          : SaleReport,
        }
        left_menu.update_menu(left_menu_ls) 
    ###############        ###############        ###############        ###############
    def sales_report(self):
        self.create_new_page("Sales Report")
##############################################################################################################


class SaleOrder(DB,Page):
        def __init__(self):
                menu_ls = {
                        "Add"   : self.Add_frame,
                        "Edit"  : self.edit_frame,
                        "Delete": self.delete_frame,
                }
                self.create_new_page("Sale Order", menu_ls)
                self.Add_frame()
        ###############        ###############        ###############        ###############
        def Add_frame(self):
                body_frame = self.create_new_body()
                entries = ( 
                        ("order_id"             ,"entry"        ,(0,0,1),None),
                        ("order_date"           ,"date"         ,(0,1,1),None),
                        ("order_status"         ,"menu"         ,(1,0,1),("Open","In Process","Shipped","Completed")),
                        ("sales_representative" ,"entry"        ,(1,1,1),None),
                        ("delivery_date"        ,"date"         ,(2,0,1),None),
                        )
                self.basic_entries = EntriesFrame(body_frame,entries) ; self.basic_entries.pack() 
                last_id = self.get_last_id("sale_order") # DB class
                self.basic_entries.change_and_disable("order_id" ,last_id+1) # last order id plus 1
                entries = ( 
                        ("customer_name"        , "entry",(0,0,1),None),
                        ("contact"              , "entry",(0,2,1),None),
                        ("shipping_address"     , "entry",(1,0,3),None),
                        ("billing_address"      , "entry",(2,0,3),None),
                        )
                self.customer_entries = EntriesFrame(body_frame,entries) ; self.customer_entries.pack()
                self.customer_entries.disable_all()
                # add search btn for customer name
                frame = self.customer_entries.frames["customer_name"] 
                self.search_customer = SearchCustomer(select_btn=self.select_customer)
                ctk.CTkButton(frame ,image="search_icon",text="",command=self.search_customer.new_window , width=20).pack(side="left")
                frame = ctk.CTkFrame(body_frame) ; frame.pack(fill="both" , padx=4, pady=4)
                self.sheet = Sheet(frame, show_x_scrollbar=False,height=200,
                           headers=["Product/Service", "SKU", "Description", "Quantity", "Unit Price"],
                           data = [["" , "" , "" , "", ""]],
                           )
                col_size = 124
                col_size= [col_size*2.5,col_size,col_size*3,col_size,col_size]
                self.sheet.set_column_widths(column_widths = col_size)
                binding = ("single_select", "toggle_select", "drag_select", "select_all", "row_drag_and_drop","column_select", "row_select", "column_width_resize", 
                           "double_click_column_resize", "row_width_resize","column_height_resize", "arrowkeys", "up", "down", "left", "right", "prior", "next", 
                           "row_height_resize","double_click_row_resize", "right_click_popup_menu", "rc_select","rc_insert_row", "rc_delete_row", "ctrl_click_select", 
                           "ctrl_select", "copy", "cut", "paste", "delete", "undo", "edit_cell")
                self.sheet.enable_bindings(binding)
                self.sheet.pack(fill="x", padx=4, pady=4)
                self.create_footer(self.Add_btn)
        ###############        ###############        ###############        ###############
        def Add_btn(self):
                # insert customer info
                customer_entries        = self.customer_entries.get_data()
                self.insert("customer",("name","contact","shipping_address","billing_address"),customer_entries.values())
                customer_id = self.get_last_id("customer")
                # insert product info
                products = self.sheet.get_sheet_data()
                total_quantity = total_price = 0
                product_ids = []
                for product in products:
                        self.insert("sale_inventory",("product_name","SKU","description","quantity","unit_price"),product)
                        total_quantity  += int(product[3])
                        total_price     += int(product[4])*int(product[3])
                        product_ids.append(str(self.cursor.lastrowid))
                product_ids_joined = ",".join(product_ids)
                basic_entries = self.basic_entries.get_data()
                basic_entries.pop("order_id")
                col_name= ("order_date","order_status","sales_representative","delivery_date","customer_name","customer_id","product_ids","total_quantity","total_price")
                value   = list(basic_entries.values()) + [customer_entries["customer_name"],customer_id,product_ids_joined,total_quantity,total_price]
                self.insert("sale_order",col_name,value)
                messagebox.showinfo("Info","The Sale order is been added successfully!")
        ###############        ###############        ###############        ###############
        def select_customer(self):
                selected_row = self.search_customer.selected_row
                if not selected_row:
                        return               
                self.search_customer.close()
                entry_names = ("customer_name" ,"contact" ,"shipping_address" ,"billing_address") 
                values = (selected_row[0],selected_row[2],selected_row[4],selected_row[5])
                for entry_name , value in zip(entry_names,values):
                     self.customer_entries.change_and_disable(entry_name,value)
        ###############        ###############        ###############        ###############
        def edit_frame(self):
                self.create_new_body()
        ###############        ###############        ###############        ###############
        def delete_frame(self):
                self.create_new_body()
##############################################################################################################

class customerManagement(DB,Page):
        def __init__(self):
                menu_ls = {
                        "Add"   : self.Add_frame,
                        "Edit"  : self.edit_frame,
                        "Delete": self.delete_frame,
                }
                self.create_new_page("Customer Management", menu_ls)
        ###############        ###############        ###############        ###############
        def Add_frame(self):
                body_frame = self.create_new_body()
                entries = ( 
                        ("customer_name"        ,"entry"        ,(0,0,1),None),
                        ("email_address"        ,"entry"        ,(0,1,1),None),
                        ("contact_number"       ,"entry"        ,(1,0,1),None),
                        ("credit_limit"         ,"entry"        ,(1,1,1),None),
                        ("payment_terms"        ,"menu"         ,(2,0,1),("Net 30 days","Cash on delivery")),
                        )
                self.customer_basic = EntriesFrame(body_frame,entries) ; self.customer_basic.pack() 
                entries = ( 
                        ("communication_preferences"    , "entry",(0,0,1),None),
                        ("shipping_address"             , "entry",(1,0,1),None),
                        ("billing_address"              , "entry",(2,0,1),None),
                        )
                self.customer_address = EntriesFrame(body_frame,entries) ; self.customer_address.pack() 
                self.create_footer(self.confirm_btn)
        ###############        ###############        ###############        ###############
        def confirm_btn(self):
                customer_basic = self.customer_basic.get_data()
                customer_address = self.customer_address.get_data()
                data = list(customer_basic.values()) + list(customer_address.values())
                col_name = ("name","email","contact","credit_limit","payment_terms","communication_preferences","shipping_address","billing_address")
                self.insert("customer" , col_name ,data )
                messagebox.showinfo("Info","The process was successful!")
        ###############        ###############        ###############        ###############
        def edit_frame(self):
                self.create_new_body()
        ###############        ###############        ###############        ###############
        def delete_frame(self):
                self.create_new_body()
##############################################################################################################


class TrackingSale(DB,Page):
        def __init__(self):
                self.tracking_sale()
        ###############        ###############        ###############        ###############
        def tracking_sale(self):
                self.create_new_page("Tracking sale")
                body_frame = self.create_new_body()
                # Search form
                entries = ( 
                        ("sale_id"              , "entry"       ,(0,0,1),None),
                        ("customer_name"        , "entry"       ,(0,1,1),None),
                        ("Created_date"         , "date"        ,(1,0,1),None),
                        ("Delivered_date"       , "date"        ,(1,1,1),None),
                        )
                self.search_entries = EntriesFrame(body_frame,entries) ; self.search_entries.pack()
                frame = self.search_entries.entries_frame 
                ctk.CTkButton(frame ,image="search_icon" , text="" , command=self.search_btn,width=50).grid(row=0,column=2,sticky="ns")
                ctk.CTkButton(frame , text="clear" ,text_color="black", command=self.clear_btn,width=50).grid(row=1,column=2,sticky="ns")
                # Show sales records on table
                frame = ctk.CTkFrame(body_frame ,height=50) ; frame.pack(fill="x" , padx=4, pady=4)
                self.sale_sheet = Sheet(frame, show_x_scrollbar=False,height=200,
                                headers=["Sales ID", "Date Created", "Sales Representative", "Customer Name", "Status" , "Delivery Date"],
                                
                                )
                col_size =160
                col_size= [col_size,col_size,col_size*1.5,col_size*1.2,col_size,col_size]
                self.sale_sheet.set_column_widths(column_widths = col_size)
                binding = ("row_select", "column_width_resize", "double_click_column_resize", "column_height_resize", "arrowkeys","row_select","single_select")
                self.sale_sheet.enable_bindings(binding)
                self.sale_sheet.pack(fill="both", padx=4, pady=4,expand=True)
                self.sale_sheet.bind("<ButtonPress-1>", self.left_click_sheet)
                # show customer info & products detail
                frame = ctk.CTkFrame(body_frame,height=400) ; frame.pack(fill="both", padx=4, pady=4,)
                frame.columnconfigure(0,minsize=320) ; frame.columnconfigure(1,weight=1)
                customer = ctk.CTkFrame(frame , border_width=2) ; customer.grid(row=0,column=0,sticky="nswe")
                customer = ctk.CTkFrame(customer) ; customer.pack(fill="both",expand=True ,padx=4, pady=4)
                rows = (
                        ("Customer Name:"       ,"customer_name"  ),
                        ("Total Quantity:"      ,"total_quantity" ),
                        ("Total Price:"         ,"total_price"    ),
                )
                self.info = {}
                i = 0
                for label,key in rows:
                        ctk.CTkLabel(customer,text=label).grid(row=i,column=0,sticky="w" ,padx=4)
                        self.info[key] = ctk.CTkLabel(customer , text="---")
                        self.info[key].grid(row=i,column=1,sticky="nswe", padx=4)
                        i += 1
                product_frame = ctk.CTkFrame(frame, border_width=2) ; product_frame.grid(row=0,column=1,sticky="nswe")
                product_frame = ctk.CTkFrame(product_frame) ; product_frame.pack(fill="both",expand=True ,padx=4, pady=4)
                self.product_sheet = Sheet(product_frame, show_x_scrollbar=False,height=100,
                                headers=["Product/Service", "Quantity", "Unit Price"],
                                )
                col_size =130
                col_size= [col_size*2.4,col_size,col_size]
                self.product_sheet.set_column_widths(column_widths = col_size)
                self.product_sheet.enable_bindings(binding)
                self.product_sheet.pack(fill="both", padx=4, pady=4)
        ###############        ###############        ###############        ###############
        def search_btn(self):
                search_entries = self.search_entries.get_data()
                cond = ["id=?","customer_name=?","order_date=?","delivery_date=?",]
                condition_ls , value_ls = [] , []
                for condition,value in zip(cond,search_entries.values()):
                        if value:
                                condition_ls.append(condition)
                                value_ls.append(value)
                conditions = " AND ".join(condition_ls)
                col_names = ("id","order_date","sales_representative","customer_name","order_status","delivery_date")
                sale_records = self.select("sale_order",col_names, conditions,value_ls)
                sale_records = [list(record) for record in sale_records]
                self.sale_sheet.set_sheet_data(sale_records,False)
        ###############        ###############        ###############        ###############
        def clear_btn(self):
                search_entries = self.search_entries.entry_dict
                for _,entry in search_entries.items():
                        entry.delete(0, "end")
                self.sale_sheet.set_sheet_data([],False)
                self.sale_sheet.select_all()
                self.product_sheet.set_sheet_data([],False)
                self.product_sheet.select_all()
                for _,label in self.info.items():
                        label.configure(text="---")
        ###############        ###############        ###############        ###############
        def left_click_sheet(self,event):
                try:
                        row = self.sale_sheet.identify_row(event, exclude_index = False, allow_end = True)
                        row = self.sale_sheet.get_row_data(row)
                except: return
                record_id = row[0]
                record = self.select("sale_order",("customer_name","total_quantity","total_price","product_ids"),"id=?",(record_id,))
                record = record[0]
                self.info["customer_name"].configure(text=record[0])
                self.info["total_quantity"].configure(text=record[1])
                self.info["total_price"].configure(text=record[2])
                product_ids = record[3].split(",")
                products , lost_record= [] , 0
                for product_id in product_ids:
                        product = self.select("sale_inventory",("product_name","quantity","unit_price"),"id=?",(product_id,))
                        if product:
                                products.append(list(product[0]))
                        else:
                                lost_record +=1
                self.product_sheet.set_sheet_data(products,False)
                if lost_record:
                        messagebox.showerror("ERROR",f"There are {lost_record} product records out of {len(product_ids)} in the inventory been lost.")
##############################################################################################################

class SaleReport(DB,Page):
        def __init__(self):
                self.create_new_page("Sale Report")
                self.sale_report()
        ###############        ###############        ###############        ###############
        def sale_report(self):
                self.create_new_body()
                body_frame = self.create_new_body()
                frame = ctk.CTkFrame(body_frame,fg_color="transparent") ; frame.pack(fill="x" ,pady=8)
                ctk.CTkLabel(frame,text="Select a range and one of the options below to generate sale report:",font=("Arial", 14, "bold")).pack(padx=10,pady=15 ,side ="left")
                # Date form
                entries = ( 
                        ("start_date"   , "date"       ,(0,0,1),None),
                        ("end_date"     , "date"       ,(0,1,1),None),
                        )
                self.date_range = EntriesFrame(body_frame,entries) ; self.date_range.pack()
                self.radio_btns = RadioButtons()
                # Time period form
                frame = ctk.CTkFrame(body_frame,fg_color="transparent") ; frame.pack(fill="x",pady=8)
                entries = ( 
                        ("time_period"  , "seg_btn"    ,(0,0,1),["Yearly", "Monthly", "Weekly", "Daily"]),
                        )
                self.time_period = EntriesFrame(frame,entries,False)
                self.radio_btns.add_button(frame,"time_period","Sales over time period: ",tuple(self.time_period.entry_dict.values()))
                self.time_period.pack(side="left",fill="x",expand=True)
                # sellers_rank form
                frame = ctk.CTkFrame(body_frame,fg_color="transparent") ; frame.pack(fill="x" ,pady=8)
                entries = ( 
                        ("top"  , "seg_btn"    ,(0,0,1),["3", "5", "10", "15", "20", "25","30"]),
                        )
                self.top_seller = EntriesFrame(frame,entries,False)
                self.radio_btns.add_button(frame,"sellers_rank","Sales Rep: Best seller (Ranks on graph).",tuple(self.top_seller.entry_dict.values()))
                self.top_seller.pack(side="left",fill="x",expand=True)
                # sale_revenue form
                frame = ctk.CTkFrame(body_frame,fg_color="transparent") ; frame.pack(fill="x" ,pady=8)
                entries = ( 
                        ("top"  , "seg_btn"    ,(0,0,1),["3", "5", "10", "15", "20", "25","30"]),
                        )
                self.sale_revenue = EntriesFrame(frame,entries,False)
                self.radio_btns.add_button(frame,"sale_revenue","Sales Revenue: The total amount of revenue generated from each sale.",tuple(self.sale_revenue.entry_dict.values()))
                self.sale_revenue.pack(side="left",fill="x",expand=True)
                # sellers_rank form
                frame = ctk.CTkFrame(body_frame,fg_color="transparent") ; frame.pack(fill="x" ,pady=8)
                self.radio_btns.add_button(frame,"quantity_rank","Sales Quantity Sold: The number of units sold for each product.")
                # sellers_rank form
                frame = ctk.CTkFrame(body_frame,fg_color="transparent") ; frame.pack(fill="x" ,pady=8)
                self.radio_btns.add_button(frame,"products","Sales by Product: Best selling items, Categories Product,")
                ####
                self.radio_btns.disable_all_elements()
                self.create_footer(self.generate_btn,"Generate")
        ###############        ###############        ###############        ###############
        def generate_btn(self):
                report_name = self.radio_btns.selected
                if not report_name:
                        messagebox.showerror("ERROR",f"Please select one of the options to generate sale report.")
                        return
                date = self.date_range.get_data()
                date_range = (datetime.strptime(date["start_date"], "%Y-%m-%d").date() , datetime.strptime(date["end_date"], "%Y-%m-%d").date())
                if date_range[0]>= date_range[1]:
                        messagebox.showerror("ERROR",f"The End Date should be greater than the Start Date")
                        return
                if report_name == "time_period":
                        self.time_period_btn(date_range)
                elif report_name == "sellers_rank":
                        self.sellers_rank_btn(date_range)
        ###############        ###############        ###############        ###############
        def time_period_btn(self,date_range=(datetime.today(),datetime.today())):
                start_date , end_date = date_range
                start_year , end_year = start_date.year , end_date.year
                years_diffs = end_year - start_year
                time_period = self.time_period.get_data()["time_period"]
                total_price_ls = []
                if time_period == "Yearly" :
                        years_ls = [] 
                        for i in range(years_diffs+1):
                                year = start_year+i
                                years_ls.append(year)
                                self.cursor.execute(f"SELECT sum(total_price) FROM sale_order WHERE delivery_date BETWEEN '{year}-01-01' AND '{year}-12-31'")
                                total_price_ls.append(self.cursor.fetchone()[0] or 0)
                        ChartWin().create_plt("Time Period (Yearly)",("Year","MYR"),(years_ls,total_price_ls))
                elif time_period == "Monthly" :
                        months_diff = (years_diffs*12) + (end_date.month - start_date.month)
                        months_ls = []
                        current_date = start_date
                        for i in range(months_diff+1):
                                if i: current_date = current_date + relativedelta(months=1)
                                year , month=current_date.year , str(current_date.month).zfill(2)
                                months_ls.append(f"{year}-{month}")
                                self.cursor.execute(f"SELECT sum(total_price) FROM sale_order WHERE delivery_date BETWEEN '{year}-{month}-01' AND '{year}-{month}-31'")
                                total_price_ls.append(self.cursor.fetchone()[0] or 0)
                        ChartWin().create_plt("Time Period (Monthly)",("Month","MYR"),(months_ls,total_price_ls))
                elif time_period == "Weekly" :
                        start_week = start_date - relativedelta(days=start_date.isocalendar()[2]-1)
                        end_week = end_date + relativedelta(days=7-start_date.isocalendar()[2])
                        weeks_diff = end_week.isocalendar()[1] - start_week.isocalendar()[1]
                        current_date = start_week
                        weeks_ls = []
                        for i in range(weeks_diff+1):
                                if i: current_date = current_date + relativedelta(weeks=1)
                                year ,month , day , last_day = current_date.year , str(current_date.month).zfill(2), str(current_date.day).zfill(2), str(current_date.day+6).zfill(2)
                                week = current_date.isocalendar()[1]
                                weeks_ls.append(f"{year}-{week}")
                                self.cursor.execute(f"SELECT sum(total_price) FROM sale_order WHERE delivery_date BETWEEN '{year}-{month}-{day}' AND '{year}-{month}-{last_day}'")
                                total_price_ls.append(self.cursor.fetchone()[0] or 0)
                        ChartWin().create_plt("Time Period (Weekly)",("Week","MYR"),(weeks_ls,total_price_ls),True)
                elif time_period == "Daily" :
                        days_diff = (end_date-start_date).days
                        if days_diff >  30:
                                messagebox.showerror("ERROR",f"Daily report: The number of days should not exceed 30 days.")
                                return
                        day_ls = []
                        current_date = start_date
                        for i in range(days_diff+1):
                                if i: current_date = current_date + relativedelta(days=1)
                                current_date_str = "{}-{}-{}".format(current_date.year , str(current_date.month).zfill(2), str(current_date.day).zfill(2))
                                day_ls.append(current_date_str)
                                self.cursor.execute(f"SELECT sum(total_price) FROM sale_order WHERE delivery_date = ?",(current_date_str,))
                                total_price_ls.append(self.cursor.fetchone()[0] or 0)
                        ChartWin().create_plt("Time Period (Daily)",("Day","MYR"),(day_ls,total_price_ls),True)
        ###############        ###############        ###############        ###############
        def sellers_rank_btn(self,date_range=(datetime.today(),datetime.today())):
                start_date , end_date = date_range
                start_date = "{}-{}-{}".format(start_date.year , str(start_date.month).zfill(2), str(start_date.day).zfill(2))
                end_date = "{}-{}-{}".format(end_date.year , str(end_date.month).zfill(2), str(end_date.day).zfill(2))
                self.cursor.execute(f"SELECT DISTINCT sales_representative FROM sale_order WHERE delivery_date BETWEEN ? AND ?",(start_date,end_date))
                seller_ls = [i[0] for i in self.cursor.fetchall()]
                ls = []
                for seller in seller_ls:
                        self.cursor.execute(f"SELECT sum(total_price) FROM sale_order WHERE sales_representative = ? AND delivery_date BETWEEN ? AND ?",(seller,start_date,end_date))
                        ls.append((seller,self.cursor.fetchone()[0] or 0))
                ls =sorted(ls, key = lambda x: x[1], reverse = True)
                top = self.top_seller.get_data()
                top = int(top["top"])
                seller_ls , total_price_ls = [] , []
                i = 1
                for seller,total_price in ls:
                        seller_ls.append(seller)
                        total_price_ls.append(total_price)
                        if i == top:
                                break
                        i+=1
                ChartWin().create_bar("Top sellers",("Seller","MYR"),(seller_ls,total_price_ls))