from config import *

class Page():
    c = {
        "bg": "default",
        "body_bg": "default",
    }
    def init_page(self,master):
        c= Page.c
        Page.main_window = master
        Page.page = ctk.CTkFrame(master)
        Page.page.grid(row=1,column=1,sticky="nswe" , padx=10,pady=10)
        Page.frame = f = ctk.CTkFrame(Page.page); f.pack(fill="both",expand=True)
    ###############        ###############        ###############        ###############
    def create_new_page(self,title="No Title",options={},):
        c= Page.c
        # Page
        Page.frame.destroy()
        Page.frame = f = ctk.CTkFrame(Page.page); f.pack(fill="both",expand=True)
        # header
        header = ctk.CTkFrame(f) ; header.pack(fill="x" , side="top")
        ctk.CTkLabel(header,font=("Times", 25 ,"bold"),text=title).pack(fill="x" ,side="left",pady=2 )
        # body
        Page.body = b = ctk.CTkFrame(f ) ; Page.body.pack(fill="both", expand=True)
        if options:
            options_menu = ctk.CTkSegmentedButton(header, values=list(options.keys()) , command=self.option_clicked)
            options_menu.pack(side="right")
            self.options = options
            first_option = tuple(options.keys())[0]
            options_menu.set(first_option,from_button_callback=True)
        return b
    ###############        ###############        ###############        ###############
    def option_clicked(self,choice):
        self.options[choice]()
    ###############        ###############        ###############        ###############
    def create_new_body(self,):
        c= Page.c
        Page.body.destroy()
        Page.body = b = ctk.CTkFrame(Page.frame  ) ; Page.body.pack(fill="both", expand=True)
        return b
    ###############        ###############        ###############        ###############
    def create_footer(self,footer_btn=lambda :0 , text_btn="Confirm"):
        body = Page.body
        # footer_btn = lambda : messagebox.showinfo("Info","The process was successful!")
        self.footer = ctk.CTkFrame(body ,corner_radius=0) ; self.footer.pack(fill="x" , side="bottom")
        ctk.CTkButton(self.footer,text=text_btn ,command=footer_btn,border_width=0,fg_color="#0aa373",hover_color="#076b4c",corner_radius=0).pack(side="right",padx=2,pady=2)
##############################################################################################################