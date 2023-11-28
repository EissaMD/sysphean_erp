import customtkinter as ctk
import tkinter.ttk as ttk

class SectionTitle(ctk.CTkFrame):
    def __init__(self,master , text="text"):
        super().__init__(master=master ,fg_color="transparent" )
        self.pack(fill="x")
        frame = ctk.CTkFrame(self,fg_color="transparent"); frame.pack(fill="x")
        ctk.CTkLabel(frame,text=text,font=("Roboto Medium", 15)).pack(side="left" , padx=20)
        ttk.Separator(frame, orient="horizontal").pack(pady=10,fill="x",padx=2 , side="left",expand=True)
##############################################################################################################

if __name__ == "__main__":
    pass