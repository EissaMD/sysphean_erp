import ttkbootstrap as ttk
from .LeftMenu import LeftMenu
from .Page import Page
from .EntriesFrame import EntriesFrame
from .InfoTable import InfoTable
from tksheet import Sheet

class Sales():
    def __init__(self):
        self.page = Page()
        self.page.create_new_page("- - -")
        left_menu = LeftMenu()
        left_menu_ls = {
            "Sales Order"           : SaleOrder,
            "Costumer Management"   : CostumerManagement,
            "Tracking sale"         : self.tracking_sale,
            "Sales Report"          : self.sales_report,
        }
        left_menu.update_menu(left_menu_ls)
    ###############        ###############        ###############        ###############
    def costumer_management(self):
            self.page.create_new_page("Costumer Management")
    ###############        ###############        ###############        ###############    
    def tracking_sale(self):
            self.page.create_new_page("Tracking sale")
    ###############        ###############        ###############        ###############
    def sales_report(self):
            self.page.create_new_page("Sales Report")
##############################################################################################################


class SaleOrder():
        def __init__(self):
                self.page = Page()
                menu_ls = {
                        "Add"   : self.Add_frame,
                        "Edit"  : self.edit_frame,
                        "Delete": self.delete_frame,
                }
                self.page.create_new_page("Sale Order", menu_ls)
        ###############        ###############        ###############        ###############
        def Add_frame(self):
                body_frame = self.page.create_new_body()
                self.page.menu.configure(text="Add")
                entries = ( 
                        ("order_id"             ,"entry"        ,(0,0,1),None),
                        ("order_date"           ,"date"         ,(0,1,1),None),
                        ("order_status"         ,"menu"         ,(1,0,1),("Open","In Process","Shipped","Completed")),
                        ("sales_representative" ,"entry"        ,(1,1,1),None),
                        ("delivery_date"        ,"entry"        ,(2,0,1),None),
                        )
                self.basic_entries = EntriesFrame(body_frame,"Order Info",entries) ; self.basic_entries.pack() 
                entries = ( 
                        ("costumer_name"        , "entry",(0,0,1),None),
                        ("contact"              , "entry",(0,1,1),None),
                        ("shipping_address"     , "entry",(1,0,2),None),
                        ("billing_address"      , "entry",(2,0,2),None),
                        )
                self.costumer_entries = EntriesFrame(body_frame,"Costumer Info",entries) ; self.costumer_entries.pack() 
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
                self.page.create_footer()
        ###############        ###############        ###############        ###############
        def edit_frame(self):
                self.page.create_new_body()
                self.page.menu.configure(text="Edit")
        ###############        ###############        ###############        ###############
        def delete_frame(self):
                self.page.create_new_body()
                self.page.menu.configure(text="Delete")       
##############################################################################################################

class CostumerManagement():
        def __init__(self):
                self.page = Page()
                menu_ls = {
                        "Add"   : self.Add_frame,
                        "Edit"  : self.edit_frame,
                        "Delete": self.delete_frame,
                }
                self.page.create_new_page("Costumer Management", menu_ls)
        ###############        ###############        ###############        ###############
        def Add_frame(self):
                body_frame = self.page.create_new_body()
                self.page.menu.configure(text="Add")
                entries = ( 
                        ("customer_name"        ,"entry"        ,(0,0,1),None),
                        ("contact_number"       ,"date"         ,(0,1,1),None),
                        ("email_address"        ,"entry"         ,(1,0,1),None),
                        ("Credit Limit"         ,"entry"        ,(1,1,1),None),
                        ("Payment Terms"        ,"menu"         ,(2,0,1),("Net 30 days","Cash on delivery")),
                        )
                self.basic_entries = EntriesFrame(body_frame,"Costumer Info",entries) ; self.basic_entries.pack() 
                entries = ( 
                        ("communication_preferences"    , "entry",(0,0,1),None),
                        ("shipping_address"             , "entry",(1,0,1),None),
                        ("billing_address"              , "entry",(2,0,1),None),
                        )
                self.costumer_entries = EntriesFrame(body_frame,"Shipping Info",entries) ; self.costumer_entries.pack() 
                self.page.create_footer()
        ###############        ###############        ###############        ###############
        def edit_frame(self):
                self.page.create_new_body()
                self.page.menu.configure(text="Edit")
        ###############        ###############        ###############        ###############
        def delete_frame(self):
                self.page.create_new_body()
                self.page.menu.configure(text="Delete") 
##############################################################################################################