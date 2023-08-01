import ttkbootstrap as ttk
from .Accounting import Accounting
from .EmptyMod import EmptyMod

class MainMenu(ttk.Frame):
    def __init__(self,master):
        background="light"
        super().__init__(master,bootstyle=background)
        frame = ttk.Frame(self,bootstyle=background); frame.pack()
        s = ttk.Style()
        s.configure("light.TButton", font=('Arial', 10, "bold"))
        menu_ls = ("Accounting", "Sales" , "Inventory" , "Manufacturing")
        menu = {
            "Accounting"    : Accounting,
            "Sales"         : EmptyMod,
            "Inventory"     : EmptyMod,
            "Manufacturing" : EmptyMod,
        }
        for text,btn in menu.items():
            ttk.Button(frame,text=text, style="light.TButton",command=btn).pack(side="left")