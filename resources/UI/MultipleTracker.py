import customtkinter as ctk
from .SearchFrame import SearchFrame

class MultipleTracker(ctk.CTkFrame):
    def __init__(self,master , select_ls=["First" , "Secound" , "Third"]):
        super().__init__(master=master)
        self.pack(fill="both",expand=True)
        if len(select_ls) > 1:
            frame = ctk.CTkFrame(self,fg_color="transparent", border_width=2)
            frame.pack(fill="x" ,pady=5,padx=4)
            ctk.CTkLabel(frame , text=f"Select from menu: " , font=("arial",14), width=200).pack(side="left" ,anchor=ctk.W , pady=4,padx=10)
            self.menu = ctk.CTkOptionMenu(frame, values=select_ls, width=200 , command=self.select_item
                                        , fg_color="#565e58",button_color="#565e58",button_hover_color="#3c423e" , corner_radius=0 )
            self.menu.pack(side="left", fill="x" )
        self.tracker_body = ctk.CTkFrame(self,fg_color="transparent", border_width=2)
        self.tracker_body.pack(fill="both",expand=True ,pady=5,padx=4)
        self.select_item(select_ls[0])
    ###############        ###############        ###############        ###############
    def select_item(self,choice):
        self.tracker_body.destroy()
        self.tracker_body = ctk.CTkFrame(self,fg_color="transparent", border_width=2)
        self.tracker_body.pack(fill="both",expand=True ,pady=5,padx=4)
        SearchFrame(self.tracker_body,choice).pack(fill="both" , expand=True)
##############################################################################################################

if __name__ == "__main__":
    pass