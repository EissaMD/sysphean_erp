from ..UI import Page, LeftMenu
from .BatchEntry import BatchEntry
from .PartNo import PartNo
from .ProductionEntry import ProductionEntry

class Manufacturing(Page):
    def __init__(self):
        self.create_new_page("Manufacturing")
        left_menu = LeftMenu()
        left_menu_ls = {
            "Part No"           : PartNo,
            "Batch Entry"       : BatchEntry,
            "Production Entry"  : ProductionEntry,
        }
        left_menu.update_menu(left_menu_ls)