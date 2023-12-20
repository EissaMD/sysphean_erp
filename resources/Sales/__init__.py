from ..UI import Page, LeftMenu 
from .SaleOrder import SaleOrder
from .CustomerManagement import CustomerManagement
from .TrackingSale import TrackingSale
from .SaleReport import SaleReport

class Sales(Page):
    def __init__(self):
        self.create_new_page("Sales")
        left_menu = LeftMenu()
        left_menu_ls = {
            "Sales Order"           : SaleOrder,
            "Customer Management"   : CustomerManagement,
            "Tracking Sale"         : TrackingSale,
            "Sales Report"          : SaleReport,
        }
        left_menu.update_menu(left_menu_ls) 