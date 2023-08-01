import ttkbootstrap as ttk
from .LeftMenu import LeftMenu
from .BodyFrame import BodyFrame

class EmptyMod():
    def __init__(self):
        self.body = BodyFrame()
        self.body.create_new_frame("- - -")
        self.left_menu = LeftMenu()
        menu = {
            "No Title1"           : self.empty_page,
            "No Title2"           : self.empty_page,
            "No Title3"           : self.empty_page,
        }
        self.left_menu.update_menu(menu)
    ###############        ###############        ###############        ###############
    def empty_page(self):
            self.body.create_new_frame(title="No Title")
