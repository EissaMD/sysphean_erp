import ttkbootstrap as ttk

class Page():
    c = {
        "bg": "default",
    }
    def init_page(self,master):
        c= Page.c
        Page.main_window = master
        Page.page = ttk.Frame(master,bootstyle=c["bg"])
        Page.page.grid(row=1,column=1,sticky="nswe" , padx=10,pady=10)
        Page.frame = f = ttk.Frame(Page.page,bootstyle=c["bg"]); f.pack(fill="both",expand=True)
    ###############        ###############        ###############        ###############
    def create_new_frame(self,title="No Title",options=None):
        c= Page.c
        Page.frame.destroy()
        Page.frame = f = ttk.Frame(Page.page); f.pack(fill="both",expand=True)
        s = ttk.Style()
        s.configure('header.TFrame', background='#ccc')
        header = ttk.Frame(f ,style='header.TFrame') ; header.pack(fill="x" , side="top")
        ttk.Label(header,font=("Times", 25 ,"bold"),text=title,background="#ccc").pack(fill="x" ,side="left" )
        return f
##############################################################################################################