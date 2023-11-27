import customtkinter as ctk
import tkinter.ttk as ttk

class SectionTitle(ctk.CTkFrame):
    def __init__(self,master , text="text",separator_top=False,separator_bottom=False,side="top"):
        super().__init__(master=master ,fg_color="transparent" )
        self.pack(fill="x")
        if separator_top:
            ttk.Separator(self, orient="horizontal").pack(pady=(4,0),fill="x",padx=2)
        frame = ctk.CTkFrame(self,fg_color="transparent"); frame.pack(fill="x")
        ctk.CTkLabel(frame,text=text,font=("Roboto Medium", 15)).pack(side=side , padx=20)
        if separator_bottom:
            ttk.Separator(self, orient="horizontal").pack(pady=(0,4),fill="x",padx=2)
##############################################################################################################

if __name__ == "__main__":
    pass