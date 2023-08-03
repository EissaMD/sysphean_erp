import ttkbootstrap as ttk
from .LeftMenu import LeftMenu
from .Page import Page
from .EntriesFrame import EntriesFrame
from .InfoTable import InfoTable

class Accounting():
    def __init__(self):
        self.page = Page()
        self.page.create_new_frame("- - -")
        left_menu = LeftMenu()
        left_menu_ls = {
            "Sales Order"           : self.sale_order,
            "Costumer Management"   : self.costumer_management,
            "Tracking sale"         : self.tracking_sale,
            "Sales Report"          : self.sales_report,
        }
        left_menu.update_menu(left_menu_ls)
    ###############        ###############        ###############        ###############
    def sale_order(self):
            body_frame = self.page.create_new_frame("Sales Order")
            entries = ( 
                       ("sale_order_id" , "entry",0,0,None),
                       ("date"          , "date",0,1,None),
                      )
            self.basic_entries = EntriesFrame(body_frame,"Basic Info",entries) ; self.basic_entries.pack() 
            entries = ( 
                       ("costumer_name" , "entry",0,0,None),
                       ("city"          , "entry",0,1,None),
                       ("country"       , "entry",1,0,None),
                       ("address"       , "entry",1,1,None),
                      )
            self.costumer_entries = EntriesFrame(body_frame,"Costumer Info",entries) ; self.costumer_entries.pack() 
            items = InfoTable(body_frame,("Part No","Date code","Qty")) ; items.pack(fill="x")
            items.add_remove_btn()
    ###############        ###############        ###############        ###############
    def costumer_management(self):
            self.page.create_new_frame("Costumer Management")
    ###############        ###############        ###############        ###############    
    def tracking_sale(self):
            self.page.create_new_frame("Tracking sale")
    ###############        ###############        ###############        ###############
    def sales_report(self):
            self.page.create_new_frame("Sales Report")
##############################################################################################################