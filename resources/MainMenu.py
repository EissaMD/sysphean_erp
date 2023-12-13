import customtkinter as ctk
from .Sales import Sales
from .Procurement import Procurement
from .Manufacturing import Manufacturing
from .Inventory import Inventory
from .EmptyMod import EmptyMod
from .About import About
from .WIP import WIP
from .LoginSystem import LoginSystem
class MainMenu(ctk.CTkFrame):
    def __init__(self,master):
        bg = "transparent"
        super().__init__(master,)
        frame = ctk.CTkFrame(self,corner_radius=0,fg_color=bg); frame.place(relx=0.5, rely=0.5, anchor="center")
        menu = {
            "Sales"         : Sales,
            "Inventory"     : EmptyMod,
            "Manufacturing" : Manufacturing,
            "Procurement"   : Procurement,
            "WIP"           : WIP,
            "About"         : About,
        }
        for text,btn in menu.items():
            if LoginSystem.user_info[text] == 1:
                ctk.CTkButton(frame,text=text,command=btn,corner_radius=0,fg_color=bg,text_color="black" ,width=10).pack(side="left",pady=2,padx=20)
            else:
                ctk.CTkButton(frame,text=text,command=btn,corner_radius=0,fg_color=bg,text_color="black" ,width=10,state="disabled").pack(side="left",pady=2,padx=20)
        frame = ctk.CTkFrame(self , fg_color="transparent",border_width=1) ; frame.pack(side="right")
        frame = ctk.CTkFrame(frame , fg_color="transparent") ; frame.pack(padx=2,pady=2)
        ctk.CTkLabel(frame,text=LoginSystem.user_name).pack(side="left" , padx=4)
        ctk.CTkButton(frame , text="",fg_color=("gray75", "gray30") , image="logout_icon",width=20,
                                command=LoginSystem.start).pack(side="left")