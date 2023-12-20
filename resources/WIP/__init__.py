from ..UI import Page, LeftMenu 
from .TravellerNo import TravellerNo
from .DeliveryOrder import DeliveryOrder
from .PartNo import PartNo
from .RejectItems import RejectItems
from .EditQuantity import EditQuantity
from .OtherOptions import OtherOptions
from .Inventory import Inventory

class WIP(Page):
    def __init__(self):
        self.create_new_page("WIP")
        left_menu = LeftMenu()
        left_menu_ls = {
            "Traveller No"      : TravellerNo,
            "Delivery Order"    : DeliveryOrder,
            "Part No"           : PartNo,
            "Reject Items"      : RejectItems,
            "Edit Quantity"     : EditQuantity,
            "Other Options"     : OtherOptions,
            "Inventory"         : Inventory,
        }
        left_menu.update_menu(left_menu_ls) 