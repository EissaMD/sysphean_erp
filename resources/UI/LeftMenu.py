from config import *

class LeftMenu():
    c = {
        "bg": "primary",
        "title_font": ('Arial', 18, "bold"),
    }
    ###############        ###############        ###############        ###############
    def create_menu(self,master):
        c = LeftMenu.c
        LeftMenu.frame=ctk.CTkFrame(master)
        LeftMenu.frame.grid(row=1,column=0,sticky="nswe")
        # title
        LeftMenu.title = t = ctk.CTkLabel(LeftMenu.frame , text="Menu" ,bg_color="transparent",fg_color="transparent" ) ; t.pack(side="top" ,pady= 20)
        ttk.Separator(LeftMenu.frame).pack(fill="x" , pady=10)
        # logo
        ctk.CTkLabel(LeftMenu.frame , image='logo' , text="" ).pack(side="bottom", pady=10)
        LeftMenu.options_frame = f = ctk.CTkFrame(LeftMenu.frame , width=0); f.pack(fill="both")
    ###############        ###############        ###############        ###############
    def update_menu(self,menu_ls={}):
        c = LeftMenu.c
        LeftMenu.options_frame.destroy()
        LeftMenu.options_frame = f = ctk.CTkFrame(LeftMenu.frame); f.pack(fill="both")
        for text,func in menu_ls.items():
            ctk.CTkButton(f,text=text ,command=func,corner_radius=0,fg_color="gray77",text_color="black"  ).pack(fill="x" , pady=2)
    ###############        ###############        ###############        ###############
    def update_title(self,title="Empty"):
        c = LeftMenu.c
        LeftMenu.title.config(text=title)