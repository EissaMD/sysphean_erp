from config import *
from ..UI import Page, SearchFrame, ViewFrame
from ..Logics import DB
from ..LoginSystem import LoginSystem

class Inventory(DB,Page):
    def __init__(self):
        menu_ls = {
            "Main Inventory": self.Main_Inventory_frame,
            "Inventory Tracker": self.Inventory_Tracker_frame,
        }
        self.create_new_page("Inventory", menu_ls)
    ###############        ###############        ###############        ###############
    # TODO: Needs to have checkbox for whether it has stock or not!
    def Main_Inventory_frame(self):
        body_frame = self.create_new_body()
        SearchFrame(body_frame, "Main Inventory").pack(fill="both", expand=True)
    ###############        ###############        ###############        ###############
    def Inventory_Tracker_frame(self):
        body_frame = self.create_new_body()
        ViewFrame(body_frame,["Carton Table","Archived Carton Table" , "Sealed Inventory"])

