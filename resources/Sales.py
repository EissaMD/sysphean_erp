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
                        ("delivery_date"        ,"entry"        ,(2,0,1),None),
                        )
                self.basic_entries = EntriesFrame(body_frame,"Order Info",entries) ; self.basic_entries.pack() 
                entries = ( 
                        ("customer_name"        , "entry",(0,0,1),None),
                        ("contact"              , "entry",(0,2,1),None),
                        ("shipping_address"     , "entry",(1,0,3),None),
                        ("billing_address"      , "entry",(2,0,3),None),
                        )
                self.customer_entries = EntriesFrame(body_frame,"customer Info",entries) ; self.customer_entries.pack()
                # add search btn for customer name
                frame = self.customer_entries.frames["customer_name"] 
                ttk.Button(frame ,bootstyle="primary-outline",image="search_icon",command=SearchCustomer).pack(side="left")
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
                self.create_footer()
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
                        ("contact_number"       ,"entry"         ,(0,1,1),None),
                        ("email_address"        ,"entry"        ,(1,0,1),None),
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
                        ("sale_id"             , "entry"       ,(0,0,1),None),
                        ("customer_name"        , "entry"       ,(0,1,1),None),
                        ("added_date"           , "date"        ,(1,0,1),None),
                        ("Delivered_date"       , "date"        ,(1,1,1),None),
                        )
                self.customer_entries = EntriesFrame(body_frame,"customer Info",entries) ; self.customer_entries.pack()
                frame = self.customer_entries.entries_frame 
                ttk.Button(frame ,bootstyle="primary-outline",image="search_icon").grid(row=0,rowspan=2,column=2,sticky="ns")
                # Show sales records on table
                frame = ttk.Labelframe(body_frame , text="Sales records",height=50) ; frame.pack(fill="x" , padx=4, pady=4)
                self.sale_sheet = Sheet(frame, show_x_scrollbar=False,height=200,
                                headers=["Sales ID", "Sales Date", "Sales Representative", "Customer Name", "Sales Status"],
                                data = [["" , "" , "" , "", ""]],
                                )
                col_size =90
                col_size= [col_size*2.5,col_size,col_size*3,col_size,col_size]
                self.sale_sheet.set_column_widths(column_widths = col_size)
                binding = ("row_select", "column_width_resize", "double_click_column_resize", "column_height_resize", "arrowkeys", 
                                "up", "down", "left", "right", "prior", "next", "row_height_resize","double_click_row_resize", 
                                "ctrl_select", "copy", "cut",  "delete", )
                self.sale_sheet.enable_bindings(binding)
                self.sale_sheet.pack(fill="both", padx=4, pady=4,expand=True)
                # show customer info & products detail
                frame = ttk.Frame(body_frame,height=400) ; frame.pack(fill="both", padx=4, pady=4)
                frame.columnconfigure(0,minsize=320) ; frame.columnconfigure(1,weight=1)
                customer = ttk.Labelframe(frame , text="Customer") ; customer.grid(row=0,column=0,sticky="nswe")
                rows = (
                        ("Customer Name:"       ,"name"),
                        ("Customer Contact:"    ,"contact"),
                        ("Customer Email:"      ,"email"),
                )
                self.customer_info = {}
                i = 0
                for label,info in rows:
                        ttk.Label(customer,text=label).grid(row=i,column=0,sticky="nswe", padx=4, pady=4)
                        self.customer_info[info] = ttk.Label(customer,text=info)
                        self.customer_info[info].grid(row=i,column=1,sticky="nswe", padx=(4,0), pady=4)
                        i+=1
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
                # footer
                self.create_footer()
##############################################################################################################