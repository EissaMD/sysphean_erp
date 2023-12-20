from config import *
from ..UI import Page , EntriesFrame , SearchWindow 
from ..Logics import DB ,validate_entry

class SaleOrder(Page):
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
                entries = ( 
                        ("order_id"             ,"entry"        ,(0,0,1),None),
                        ("order_date"           ,"date"         ,(0,1,1),None),
                        ("order_status"         ,"menu"         ,(1,0,1),("Open","In Process","Shipped","Completed")),
                        ("sales_representative" ,"entry"        ,(1,1,1),None),
                        ("delivery_date"        ,"date"         ,(2,0,1),None),
                        )
                self.basic_entries = EntriesFrame(body_frame,entries) ; self.basic_entries.pack() 
                self.last_id = DB.get_last_id("sale_order") # DB class
                self.basic_entries.change_and_disable("order_id" ,self.last_id+1) # last order id plus 1
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
                self.search_customer = SearchWindow(self.select_customer ,"Search Customer" )
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
                # insert product info
                products = self.sheet.get_sheet_data() or []
                total_quantity = total_price = 0
                product_ids = []
                for product in products:
                        product.append(self.last_id+1)
                        DB.insert("sale_inventory",("product_name","SKU","description","quantity","unit_price","sale_id"),product,False)
                        total_quantity  += int(product[3])
                        total_price     += int(product[4])*int(product[3])
                        product_ids.append(str(DB.cursor.lastrowid))
                product_ids_joined = ",".join(product_ids)
                basic_entries = self.basic_entries.get_data()
                basic_entries.pop("order_id")
                col_name= ("order_date","order_status","sales_representative","delivery_date","customer_name","customer_id","product_ids","total_quantity","total_price")
                value   = list(basic_entries.values()) + [self.customer_info["name"],self.customer_info["id"],product_ids_joined,total_quantity,total_price]
                DB.insert("sale_order",col_name,value)
                messagebox.showinfo("Info","The Sale order is been added successfully!")
                self.Add_frame()
        ###############        ###############        ###############        ###############
        def select_customer(self):
                selected_row = self.search_customer.selected_row
                if not selected_row:
                        return               
                self.search_customer.close()
                entry_names = ("customer_name" ,"contact" ,"shipping_address" ,"billing_address") 
                values = (selected_row[1],selected_row[3],selected_row[5],selected_row[6])
                for entry_name , value in zip(entry_names,values):
                     self.customer_entries.change_and_disable(entry_name,value)
                self.customer_info = {"id": selected_row[0] , "name": selected_row[1]}
        ###############        ###############        ###############        ###############
        def edit_frame(self):
                self.create_new_body()
        ###############        ###############        ###############        ###############
        def delete_frame(self):
                self.create_new_body()
##############################################################################################################