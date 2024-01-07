from config import *
from .Sales import Sales
from .Procurement import Procurement
from .Manufacturing import Manufacturing
from .Inventory import Inventory
from .EmptyMod import EmptyMod
from .About import About
from .WIP import WIP
from .DeveloperOptions import DeveloperOptions
from .LoginSystem import LoginSystem
from .Settings import Settings


class MainMenu(ctk.CTkFrame):
    def __init__(self,master):
        super().__init__(master,)
        self.frame = ctk.CTkFrame(self,corner_radius=0); self.frame.place(relx=0.5, rely=0.5, anchor="center")
        frame = ctk.CTkFrame(self , fg_color="transparent",border_width=1) ; frame.pack(side="right")
        frame = ctk.CTkFrame(frame , fg_color="transparent") ; frame.pack(padx=2,pady=2)
        ctk.CTkLabel(frame,text=LoginSystem.user_name).pack(side="left" , padx=4)
        ctk.CTkButton(frame , text="",fg_color=("gray75", "gray30") , image="logout_icon",width=20,
                                command=LoginSystem.start).pack(side="left")
        self.developer_mode = False
    ###############        ###############        ###############        ###############
    def create(self):
        bg = "transparent"
        self.frame.destroy()
        self.frame = ctk.CTkFrame(self,corner_radius=0,fg_color=bg); self.frame.place(relx=0.5, rely=0.5, anchor="center")
        menu = {
            "Sales"             : Sales,
            "Inventory"         : EmptyMod,
            "Manufacturing"     : Manufacturing,
            "Procurement"       : Procurement,
            "Settings"          : Settings,
            "WIP"               : WIP,
            "About"             : About,
        }
        for text,btn in menu.items():
            if LoginSystem.user_info[text] == 1:
                ctk.CTkButton(self.frame,text=text,command=btn,corner_radius=0,fg_color=bg,text_color="black" ,width=10).pack(side="left",pady=2,padx=20)
            else:
                ctk.CTkButton(self.frame,text=text,command=btn,corner_radius=0,fg_color=bg,text_color="black" ,width=10,state="disabled").pack(side="left",pady=2,padx=20)
    ###############        ###############        ###############        ###############
    def dev_popup(self,event):
        if self.developer_mode is False:
            input_popup = ctk.CTkInputDialog(text="Enter Developer Mode password:",title="Developer Mode")
            password = input_popup.get_input()
            if password !="3.14159":
                return
            self.developer_mode = True
            self.create_dev()
        else:
            self.developer_mode = False
            self.create()
    ###############        ###############        ###############        ###############
    def create_dev(self):
        bg = "transparent"
        self.frame.destroy()
        self.frame = ctk.CTkFrame(self,corner_radius=0,fg_color=bg); self.frame.place(relx=0.5, rely=0.5, anchor="center")
        menu = {
            "Sales"             : Sales,
            "Inventory"         : EmptyMod,
            "Manufacturing"     : Manufacturing,
            "Procurement"       : Procurement,
            "Settings"          : Settings,
            "Developer Options" : DeveloperOptions,
            "WIP"               : WIP,
            "About"             : About,
        }
        for text,btn in menu.items():
            if LoginSystem.user_info[text] == 1:
                ctk.CTkButton(self.frame,text=text,command=btn,corner_radius=0,fg_color=bg,text_color="black" ,width=10).pack(side="left",pady=2,padx=20)
            else:
                ctk.CTkButton(self.frame,text=text,command=btn,corner_radius=0,fg_color=bg,text_color="black" ,width=10,state="disabled").pack(side="left",pady=2,padx=20)