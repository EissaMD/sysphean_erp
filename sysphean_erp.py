import ttkbootstrap as ttk

class App(ttk.Window):
    def __init__(self):
        super().__init__(
            title="Sysphean ERP",
            themename="superhero",
            size=(1000, 600),
            resizable=(True, False),
        )
        image_files = (
            ('logo','Sysphean_Logo.png',100,100),
            )
        self.img_ls = []
        for name, file_name ,w ,h in image_files:
            path = r"./assets/" + file_name
            img =ttk.Image.open(path).resize((w,h)) if w > 0 else ttk.Image.open(path)
            self.img_ls.append(ttk.ImageTk.PhotoImage(img ,name=name))
            # self.img_ls.append(ttk.PhotoImage(name=name, file=img ))
        # create the main menu
        self.columnconfigure((1),weight=1)
        menu_ls = ("Accounting", "Sales" , "Inventory" , "Manufacturing")
        main_menu = MainMenu(self,menu_ls)
        main_menu.grid(row=0,column=0, columnspan=2, sticky="nswe" )
        # create the secondary menu
        self.rowconfigure((1),weight=1)
        self.columnconfigure((0),minsize=160)
        main_menu = LeftMenu(self,menu_ls)
        main_menu.grid(row=1,column=0,sticky="nswe")
        BodyFrame(self)
##############################################################################################################

class MainMenu(ttk.Frame):
    def __init__(self,master,menu_ls=()):
        background="light"
        super().__init__(master,bootstyle=background)
        frame = ttk.Frame(self,bootstyle=background); frame.pack()
        s = ttk.Style()
        s.configure("light.TButton", font=('Arial', 10, "bold"))
        for menu in menu_ls:
            ttk.Button(frame,text=menu, style="light.TButton").pack(side="left")
##############################################################################################################

class LeftMenu(ttk.Frame):
    def __init__(self,master,menu_ls=()):
        background = "secondary"
        super().__init__(master,bootstyle=background)
        # title
        LeftMenu.title = t = ttk.Label(self , text="Welcome" ,bootstyle="inverse-"+background , font=('Arial', 18, "bold") ) ; t.pack(side="top" ,pady= 20)
        # logo
        ttk.Label(self , image='logo' ,bootstyle="inverse-"+background ).pack(side="bottom", pady=10)
        LeftMenu.buttons_frame = f = ttk.Frame(self,bootstyle=background); f.pack(fill="x")
        for menu in menu_ls:
            ttk.Button(f,text=menu ,bootstyle=background).pack(fill="x" , pady=2)
##############################################################################################################

class BodyFrame(ttk.Frame):
    def __init__(self,master):
        super().__init__(master,bootstyle="secondary")
        self.grid(row=1,column=1,sticky="nswe" , padx=10,pady=10)
##############################################################################################################


if __name__ == "__main__":
    app = App()
    app.mainloop()