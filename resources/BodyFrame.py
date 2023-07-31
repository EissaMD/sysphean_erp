import ttkbootstrap as ttk

class BodyFrame():
    c = {
        "bg": "secondary",
    }
    def create_body(self,master):
        c= BodyFrame.c
        BodyFrame.main_window = master
        BodyFrame.body = ttk.Frame(master,bootstyle=c["bg"])
        BodyFrame.body.grid(row=1,column=1,sticky="nswe" , padx=10,pady=10)
        BodyFrame.frame = f = ttk.Frame(BodyFrame.body,bootstyle=c["bg"]); f.pack(fill="both",expand=True)
    ###############        ###############        ###############        ###############
    def create_new_frame(self,title="No Title"):
        c= BodyFrame.c
        BodyFrame.frame.destroy()
        BodyFrame.frame = f = ttk.Frame(BodyFrame.body,bootstyle=c["bg"]); f.pack(fill="both",expand=True)
        ttk.Label(f,font=("Times", 25 ,"bold"),bootstyle="light",text=title).pack(fill="x" , anchor="center")
        return f
##############################################################################################################