import ttkbootstrap as ttk

class LeftMenu(ttk.Frame):
    c = {
        "bg": "secondary",
        "title_font": ('Arial', 18, "bold"),
    }
    ###############        ###############        ###############        ###############
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