
from config import *
from ..UI import Page , EntriesFrame 
from ..Logics import DB

class TrackingSale(Page):
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
                cond = ["id=%s","customer_name=%s","order_date=%s","delivery_date=%s",]
                condition_ls , value_ls = [] , []
                for condition,value in zip(cond,search_entries.values()):
                        if value:
                                condition_ls.append(condition)
                                value_ls.append(value)
                conditions = " AND ".join(condition_ls)
                col_names = ("id","order_date","sales_representative","customer_name","order_status","delivery_date")
                sale_records = DB.select("sale_order",col_names, conditions,value_ls)
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
                record = DB.select("sale_order",("customer_name","total_quantity","total_price","product_ids"),"id=%s",(record_id,))
                record = record[0]
                self.info["customer_name"].configure(text=record[0])
                self.info["total_quantity"].configure(text=record[1])
                self.info["total_price"].configure(text=record[2])
                product_ids = record[3].split(",")
                products , lost_record= [] , 0
                for product_id in product_ids:
                        product = DB.select("sale_inventory",("product_name","quantity","unit_price"),"id=%s",(product_id,))
                        if product:
                                products.append(list(product[0]))
                        else:
                                lost_record +=1
                self.product_sheet.set_sheet_data(products,False)
                if lost_record:
                        messagebox.showerror("ERROR",f"There are {lost_record} product records out of {len(product_ids)} in the inventory been lost.")
##############################################################################################################