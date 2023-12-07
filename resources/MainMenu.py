import customtkinter as ctk
from .Sales import Sales
from .Procurement import Procurement
from .Manufacturing import Manufacturing
from .Inventory import Inventory
from .EmptyMod import EmptyMod
from .About import About
from .WIP import WIP
class MainMenu(ctk.CTkFrame):
    def __init__(self,master):
        bg = "transparent"
        super().__init__(master,)
        frame = ctk.CTkFrame(self,corner_radius=0,fg_color=bg); frame.pack()
        menu = {
            "Sales"         : Sales,
            "Inventory"     : EmptyMod,
            "Manufacturing" : Manufacturing,
            "Procurement"   : Procurement,
            "WIP"           : WIP,
            "About"         : About,
        }
        for text,btn in menu.items():
            ctk.CTkButton(frame,text=text,command=btn,corner_radius=0,fg_color=bg,text_color="black" ,width=10).pack(side="left",pady=2,padx=20)