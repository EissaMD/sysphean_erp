import ttkbootstrap as ttk

class App(ttk.Window):
    def __init__(self):
        super().__init__(
            title="Sysphean ERP",
            themename="superhero",
            size=(1000, 600),
            resizable=(True, False),
        )
        s = ttk.Style()
        s.configure("light.TButton", font=('Helvetica', 12))
        # create the main menu
        self.columnconfigure((1),weight=1)
        menu_ls = ("Accounting", "Sales" , "Inventory" , "Manufacturing")
        main_menu = MainMenu(self,menu_ls)
        main_menu.grid(row=0,column=0, columnspan=2, sticky="nswe" )
        # create the secondary menu
        self.rowconfigure((1),weight=1)
        self.columnconfigure((0),minsize=160)
        main_menu = LeftMenu(self)
        main_menu.grid(row=1,column=0,sticky="nswe")
        ttk.Frame(self, bootstyle="secondary").grid(row=1,column=1,sticky="nswe" , padx=10,pady=10)
##############################################################################################################

class MainMenu(ttk.Frame):
    def __init__(self,master,menu_ls=()):
        background="light"
        super().__init__(master,bootstyle=background)
        frame = ttk.Frame(self,bootstyle=background); frame.pack()
        s = ttk.Style()
        s.configure("light.TButton", font=('Arial', 10, "bold"))
        for menu in menu_ls:
            ttk.Button(frame,text=menu ,bootstyle=background , style="light.TButton").pack(side="left")
##############################################################################################################

class LeftMenu(ttk.Frame):
    def __init__(self,master,menu_ls=()):
        super().__init__(master,bootstyle="secondary")
        
        for menu in menu_ls:
            ttk.Button(self,text=menu ,bootstyle="secondary").pack(fill="x" , pady=4)
##############################################################################################################

class BodyFrame(ttk.Frame):
    def __init__(self,master,menu_ls=()):
        super().__init__(master,bootstyle="secondary")
        
        for menu in menu_ls:
            ttk.Button(self,text=menu ,bootstyle="secondary").pack(fill="x" , pady=4)
##############################################################################################################


if __name__ == "__main__":
    app = App()
    app.mainloop()