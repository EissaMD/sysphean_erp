import ttkbootstrap as ttk
from .LeftMenu import LeftMenu
from .Page import Page

class EmptyMod():
    def __init__(self):
        self.page = Page()
        self.page.create_new_page("- - -")
        self.left_menu = LeftMenu()
        menu = {
            "No Title1"           : self.empty_page,
            "No Title2"           : self.empty_page,
            "No Title3"           : self.empty_page,
        }
        self.left_menu.update_menu(menu)
    ###############        ###############        ###############        ###############
    def empty_page(self):
            self.page.create_new_page(title="No Title")
