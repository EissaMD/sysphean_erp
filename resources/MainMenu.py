import ttkbootstrap as ttk
from .Sales import Sales
from .Procurement import Procurement
from .EmptyMod import EmptyMod

class MainMenu(ttk.Frame):
    def __init__(self,master):
        background="dark"
        super().__init__(master,bootstyle=background)
        frame = ttk.Frame(self,bootstyle=background); frame.pack()
        s = ttk.Style()
        s.configure(background+".TButton", font=('Arial', 10, "bold"))
        menu_ls = ("Accounting", "Sales" , "Inventory" , "Manufacturing")
        menu = {
            "Procurement"   : Procurement,
            "Sales"         : Sales,
            "Inventory"     : EmptyMod,
            "Manufacturing" : EmptyMod,
        }
        for text,btn in menu.items():
            ttk.Button(frame,text=text, style=background+".TButton",command=btn).pack(side="left")