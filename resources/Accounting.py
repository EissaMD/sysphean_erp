import ttkbootstrap as ttk
from .LeftMenu import LeftMenu
from .BodyFrame import BodyFrame

class Accounting():
    def __init__(self):
        self.body = BodyFrame()
        self.body.create_new_frame("_ _ _")
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
            self.body.create_new_frame(title="Sales Order")
    ###############        ###############        ###############        ###############
    def costumer_management(self):
            self.body.create_new_frame("Costumer Management")
    ###############        ###############        ###############        ###############    
    def tracking_sale(self):
            self.body.create_new_frame("Tracking sale")
    ###############        ###############        ###############        ###############
    def sales_report(self):
            self.body.create_new_frame("Sales Report")