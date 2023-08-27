import ttkbootstrap as ttk
from .UI import Page, LeftMenu , EntriesFrame , SearchCustomer
from tksheet import Sheet
from .Logics import DB
from tkinter import messagebox

class Sales(Page):
    def __init__(self):
        self.create_new_page("- - -")
        left_menu = LeftMenu()
        left_menu_ls = {
            "Sales Order"           : SaleOrder,
            "Customer Management"   : customerManagement,
            "Tracking Sale"         : TrackingSale,
            "Sales Report"          : self.sales_report,
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
        ###############        ###############        ###############        ###############
        def Add_frame(self):
                body_frame = self.create_new_body()
                self.menu.configure(text="Add")
                entries = ( 
                        ("order_id"             ,"entry"        ,(0,0,1),None),
                        ("order_date"           ,"date"         ,(0,1,1),None),
                        ("order_status"         ,"menu"         ,(1,0,1),("Open","In Process","Shipped","Completed")),
                        ("sales_representative" ,"entry"        ,(1,1,1),None),
                        ("delivery_date"        ,"date"         ,(2,0,1),None),
                        )
                self.basic_entries = EntriesFrame(body_frame,"Order Info",entries) ; self.basic_entries.pack() 
                last_id = self.get_last_id("sale_order") # DB class
                self.basic_entries.change_and_disable("order_id" ,last_id+1)
                entries = ( 
                        ("customer_name"        , "entry",(0,0,1),None),
                        ("contact"              , "entry",(0,2,1),None),
                        ("shipping_address"     , "entry",(1,0,3),None),
                        ("billing_address"      , "entry",(2,0,3),None),
                        )
                self.customer_entries = EntriesFrame(body_frame,"customer Info",entries) ; self.customer_entries.pack()
                # add search btn for customer name
                # frame = self.customer_entries.frames["customer_name"] 
                # ttk.Button(frame ,bootstyle="primary-outline",image="search_icon",command=SearchCustomer).pack(side="left")
                frame = ttk.Labelframe(body_frame , text="Products") ; frame.pack(fill="x" , padx=4, pady=4)
                self.sheet = Sheet(frame, show_x_scrollbar=False,height=100,
                           headers=["Product/Service", "SKU", "Description", "Quantity", "Unit Price"],
                           data = [["" , "" , "" , "", ""]],
                           )
                col_size =90
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
        ###############        ###############        ###############        ###############
        def edit_frame(self):
                self.create_new_body()
                self.menu.configure(text="Edit")
        ###############        ###############        ###############        ###############
        def delete_frame(self):
                self.create_new_body()
                self.menu.configure(text="Delete")       
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
                self.menu.configure(text="Add")
                entries = ( 
                        ("customer_name"        ,"entry"        ,(0,0,1),None),
                        ("email_address"        ,"entry"        ,(0,1,1),None),
                        ("contact_number"       ,"entry"        ,(1,0,1),None),
                        ("credit_limit"         ,"entry"        ,(1,1,1),None),
                        ("payment_terms"        ,"menu"         ,(2,0,1),("Net 30 days","Cash on delivery")),
                        )
                self.customer_basic = EntriesFrame(body_frame,"customer Info",entries) ; self.customer_basic.pack() 
                entries = ( 
                        ("communication_preferences"    , "entry",(0,0,1),None),
                        ("shipping_address"             , "entry",(1,0,1),None),
                        ("billing_address"              , "entry",(2,0,1),None),
                        )
                self.customer_address = EntriesFrame(body_frame,"Shipping Info",entries) ; self.customer_address.pack() 
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
                self.menu.configure(text="Edit")
        ###############        ###############        ###############        ###############
        def delete_frame(self):
                self.create_new_body()
                self.menu.configure(text="Delete") 
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
                self.search_entries = EntriesFrame(body_frame,"customer Info",entries) ; self.search_entries.pack()
                frame = self.search_entries.entries_frame 
                ttk.Button(frame ,bootstyle="primary-outline",image="search_icon" , command=self.search_btn).grid(row=0,rowspan=2,column=2,sticky="ns")
                # Show sales records on table
                frame = ttk.Labelframe(body_frame , text="Sales records",height=50) ; frame.pack(fill="x" , padx=4, pady=4)
                self.sale_sheet = Sheet(frame, show_x_scrollbar=False,height=200,
                                headers=["Sales ID", "Date Created", "Sales Representative", "Customer Name", "Status" , "Delivery Date"],
                                
                                )
                col_size =96
                col_size= [col_size,col_size,col_size*2,col_size*2,col_size*2]
                self.sale_sheet.set_column_widths(column_widths = col_size)
                binding = ("row_select", "column_width_resize", "double_click_column_resize", "column_height_resize", "arrowkeys","row_select","single_select")
                self.sale_sheet.enable_bindings(binding)
                self.sale_sheet.pack(fill="both", padx=4, pady=4,expand=True)
                self.sale_sheet.bind("<ButtonPress-1>", self.left_click_sheet)
                # show customer info & products detail
                frame = ttk.Frame(body_frame,height=400) ; frame.pack(fill="both", padx=4, pady=4)
                frame.columnconfigure(0,minsize=320) ; frame.columnconfigure(1,weight=1)
                customer = ttk.LabelFrame(frame , text="Info") ; customer.grid(row=0,column=0,sticky="nswe")
                rows = (
                        ("Customer Name:"       ,"customer_name"  ),
                        ("Total Quantity:"      ,"total_quantity" ),
                        ("Total Price:"         ,"total_price"    ),
                )
                self.info = {}
                i = 0
                for label,key in rows:
                        ttk.Label(customer,text=label).grid(row=i,column=0,sticky="w" ,padx=4)
                        self.info[key] = ttk.Label(customer , text="---")
                        self.info[key].grid(row=i,column=1,sticky="nswe", padx=4)
                        i += 1
                # rows = (
                #         ("customer_name"       , "entry"       ,(0,0,1),None),
                #         ("total_quantity"       , "entry"       ,(1,0,1),None),
                #         ("total_price"          , "entry"       ,(3,0,1),None),
                # )
                # self.info = EntriesFrame(frame,"Info",rows) ; self.info.grid(row=0,column=0,sticky="nswe")
                # for entry,__,__,__ in rows:
                #         self.info.change_and_disable(entry,"---")
                product_frame = ttk.Labelframe(frame , text="Product") ; product_frame.grid(row=0,column=1,sticky="nswe")
                self.product_sheet = Sheet(product_frame, show_x_scrollbar=False,height=100,
                                headers=["Product/Service", "Quantity", "Unit Price"],
                                data = [["" , "", ""]],
                                )
                col_size =100
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
                products= []
                for product_id in product_ids:
                        product = self.select("sale_inventory",("product_name","quantity","unit_price"),"id=?",(product_id,))
                        products.append(list(product[0]))
                self.product_sheet.set_sheet_data(products,False)
##############################################################################################################