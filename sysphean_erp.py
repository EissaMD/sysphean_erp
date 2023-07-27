import ttkbootstrap as ttk

class App(ttk.Window):
    def __init__(self):
        super().__init__(
            title="Sysphean ERP",
            themename="superhero",
            size=(1000, 600),
            resizable=(True, False),
        )
        # create the main menu
        self.columnconfigure((0),weight=1)
        menu_ls = ("Accounting", "Sales" , "Inventory" , "Manufacturing")
        main_menu = MainMenu(self,menu_ls)
        main_menu.grid(row=0,column=0, sticky="nswe" )
##############################################################################################################

class MainMenu(ttk.Frame):
    def __init__(self,master,menu_ls):
        super().__init__(master,bootstyle="light")
        for menu in menu_ls:
            ttk.Button(self,text=menu ,bootstyle="light").pack(side="left")
##############################################################################################################

if __name__ == "__main__":
    app = App()
    app.mainloop()