import ttkbootstrap as ttk

class App(ttk.Window):
    def __init__(self):
        super().__init__(
            title="Sysphean ERP",
            themename="superhero",
            size=(1000, 600),
            resizable=(True, False),
        )
        ################## IMAGES #################
        image_files = (
            ('logo','Sysphean_Logo.png',120,100),
            )
        self.img_ls = []
        for name, file_name ,w ,h in image_files:
            path = r"./assets/" + file_name
            img =ttk.Image.open(path).resize((w,h)) if w > 0 else ttk.Image.open(path)
            self.img_ls.append(ttk.ImageTk.PhotoImage(img ,name=name))
        ################## IMAGES #################
        # create the main menu
        self.columnconfigure((1),weight=1)
        menu_ls = ("Accounting", "Sales" , "Inventory" , "Manufacturing")
        main_menu = MainMenu(self,menu_ls)
        main_menu.grid(row=0,column=0, columnspan=2, sticky="nswe" )
        # create secondary menu
        self.rowconfigure((1),weight=1)
        self.columnconfigure((0),minsize=160)
        LeftMenu(self).create_menu(self)

        # create Body Frame
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
    c = {
        "bg": "secondary",
        "title_font": ('Arial', 18, "bold"),
    }
    def create_menu(self,master):
        c = LeftMenu.c
        super().__init__(master,bootstyle=c["bg"])
        self.grid(row=1,column=0,sticky="nswe")
        # title
        LeftMenu.title = t = ttk.Label(self , text="Menu" ,bootstyle="inverse-"+c["bg"] , font=c["title_font"] ) ; t.pack(side="top" ,pady= 20)
        # logo
        ttk.Label(self , image='logo' ,bootstyle="inverse-"+c["bg"] ).pack(side="bottom", pady=10)
        LeftMenu.options_frame = f = ttk.Frame(self,bootstyle=c["bg"]); f.pack(fill="both")
    ###############        ###############        ###############        ###############
    def update_menu(self,menu_ls={}):
        c = LeftMenu.c
        LeftMenu.options_frame.destroy()
        LeftMenu.options_frame = f = ttk.Frame(self,bootstyle=c["bg"]); f.pack(fill="both")
        for text,func in menu_ls.items():
            ttk.Button(f,text=text ,command=func ,bootstyle=c["bg"] ).pack(fill="x" , pady=2)
    ###############        ###############        ###############        ###############
    def update_title(self,title="Empty"):
        c = LeftMenu.c
        LeftMenu.title.destroy()
        LeftMenu.title = t = ttk.Label(self , text="Menu" ,bootstyle="inverse-"+c["bg"] , font=c["title_font"] ) ; t.pack(side="top" ,pady= 20)
##############################################################################################################

class BodyFrame(ttk.Frame):
    def __init__(self,master):
        super().__init__(master,bootstyle="secondary")
        self.grid(row=1,column=1,sticky="nswe" , padx=10,pady=10)
##############################################################################################################


if __name__ == "__main__":
    app = App()
    app.mainloop()