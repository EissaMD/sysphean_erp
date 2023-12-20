from ..UI import Page, LeftMenu 
from .PurchaseRequisition import PurchaseRequisition
from .SupplierManagement import SupplierManagement
from .SupplierQuotation import SupplierQuotation
from .InvoiceMatching import InvoiceMatching

class Procurement(Page):
    def __init__(self):
        self.create_new_page("Procurement")
        left_menu = LeftMenu()
        # Do not have more than 6 menus
        left_menu_ls = {
            "Purchase Requisition"              : PurchaseRequisition,
            "Supplier Management"               : SupplierManagement,
            "Supplier Quotation"                : SupplierQuotation,
            "Invoice Matching"                  : InvoiceMatching,
        }
        left_menu.update_menu(left_menu_ls)
##############################################################################################################