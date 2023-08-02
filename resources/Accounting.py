import ttkbootstrap as ttk
from .LeftMenu import LeftMenu
from .BodyFrame import BodyFrame
from .EntriesFrame import EntriesFrame

class Accounting():
    def __init__(self):
        self.body = BodyFrame()
        self.body.create_new_frame("- - -")
        self.left_menu = LeftMenu()
        menu = {
            "Sales Order"           : self.sale_order,
            "Costumer Management"   : self.costumer_management,
            "Tracking sale"         : self.tracking_sale,
            "Sales Report"          : self.sales_report,
        }
        self.left_menu.update_menu(menu)
    ###############        ###############        ###############        ###############
    def sale_order(self):
            body_frame = self.body.create_new_frame(title="Sales Order")
            entries = ( 
                       ("costumer_name" , "entry",0,0,None),
                       ("city"          , "entry",0,1,None),
                       ("country"       , "entry",1,0,None),
                       ("address"       , "entry",1,1,None),
                      )
            costumer_entries = EntriesFrame(body_frame,"Costumer Info",entries) ; costumer_entries.pack() 
    ###############        ###############        ###############        ###############
    def costumer_management(self):
            self.body.create_new_frame("Costumer Management")
    ###############        ###############        ###############        ###############    
    def tracking_sale(self):
            self.body.create_new_frame("Tracking sale")
    ###############        ###############        ###############        ###############
    def sales_report(self):
            self.body.create_new_frame("Sales Report")