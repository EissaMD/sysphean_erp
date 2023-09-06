import customtkinter as ctk
from .Sales import Sales
from .EmptyMod import EmptyMod

class MainMenu(ctk.CTkFrame):
    def __init__(self,master):
        bg = "transparent"
        super().__init__(master,)
        frame = ctk.CTkFrame(self,corner_radius=0,fg_color=bg); frame.pack()
        menu = {
            "Sales"         : Sales,
            "Inventory"     : EmptyMod,
            "Manufacturing" : EmptyMod,
        }
        for text,btn in menu.items():
            ctk.CTkButton(frame,text=text,command=btn,width=90,corner_radius=0,fg_color=bg,text_color="black").pack(side="left",pady=2)