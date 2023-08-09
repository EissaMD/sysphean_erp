import ttkbootstrap as ttk
from tkinter import messagebox

class Page():
    c = {
        "bg": "default",
        "body_bg": "default",
    }
    def init_page(self,master):
        c= Page.c
        Page.main_window = master
        Page.page = ttk.Frame(master,bootstyle=c["bg"])
        Page.page.grid(row=1,column=1,sticky="nswe" , padx=10,pady=10)
        Page.frame = f = ttk.Frame(Page.page,bootstyle=c["bg"]); f.pack(fill="both",expand=True)
        s = ttk.Style()
        s.configure('header.TFrame', background='#ccc')
    ###############        ###############        ###############        ###############
    def create_new_page(self,title="No Title",options={}):
        c= Page.c
        # Page
        Page.frame.destroy()
        Page.frame = f = ttk.Frame(Page.page,bootstyle=c["bg"]); f.pack(fill="both",expand=True)
        # header
        header = ttk.Frame(f ,style='header.TFrame') ; header.pack(fill="x" , side="top")
        ttk.Label(header,font=("Times", 25 ,"bold"),text=title,background="#ccc").pack(fill="x" ,side="left" )
        if options:
            self.menu = ttk.Menubutton(header,text="Options") ; self.menu.pack(side="right")
            inside_menu = ttk.Menu(self.menu)
            for txt,func in options.items():
                inside_menu.add_radiobutton(label=txt , command=func)
            self.menu["menu"] = inside_menu
        # body
        Page.body = b = ttk.Frame(f , bootstyle=c["body_bg"]) ; Page.body.pack(fill="both", expand=True)
        return b
    ###############        ###############        ###############        ###############
    def create_new_body(self,):
        c= Page.c
        Page.body.destroy()
        Page.body = b = ttk.Frame(Page.frame , bootstyle=c["body_bg"]) ; Page.body.pack(fill="both", expand=True)
        return b
    ###############        ###############        ###############        ###############
    def create_footer(self,footer_btn=lambda :0):
        body = Page.body
        footer_btn = lambda : messagebox.showinfo("Info","The process was successful!")
        footer = ttk.Frame(body,borderwidth=2 ,bootstyle="secondary") ; footer.pack(fill="x" , side="bottom")
        ttk.Button(footer,text="Confirm" , bootstyle="success",command=footer_btn).pack(side="right")
##############################################################################################################