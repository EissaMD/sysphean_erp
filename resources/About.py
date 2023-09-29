from .UI import LeftMenu , Page
import customtkinter as ctk

class About(Page):
    def __init__(self):
        self.create_new_page("- - -")
        self.left_menu = LeftMenu()
        menu = {
        }
        self.left_menu.update_menu(menu)
        self.create_new_page(title="About")
        body_frame = self.create_new_body()
        ctk.CTkLabel(body_frame,text="0.10",font=("Arial", 14, "bold")).pack(fill = "both" , expand = True)
            