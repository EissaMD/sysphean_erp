import customtkinter as ctk
from resources import MainMenu
from resources.UI import LeftMenu , Page
from resources.Logics import DB
from tkinter import ttk
from PIL import Image , ImageTk
ctk.deactivate_automatic_dpi_awareness()
ctk.set_appearance_mode("light")
class App(ctk.CTk):
    WIDTH = 1280
    HEIGHT = 720

    def __init__(self):
        super().__init__()
        self.title("Sysphean ERP")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.minsize(App.WIDTH , App.HEIGHT)
        self.maxsize(App.WIDTH , App.HEIGHT)
        ################## IMAGES #################
                            #Image name in tkinter  ,   file name               ,width ,height
        image_files = (     ('logo'                 ,   'Sysphean_Logo.png'     ,120   ,100    ),
                            ('search_icon'          ,   'Search.png'            ,20    ,20     ),
            )
        self.img_ls = []
        for name, file_name ,w ,h in image_files:
            path = r"./assets/" + file_name # image should be saved in "assets" folder
            img =Image.open(path).resize((w,h)) if w > 0 else Image.open(path)
            self.img_ls.append(ImageTk.PhotoImage(img ,name=name))
        ################## IMAGES #################
        # create the main menu
        self.columnconfigure((1),weight=1)
        main_menu = MainMenu(self)
        main_menu.grid(row=0,column=0, columnspan=2, sticky="nswe" )
        # create secondary menu
        self.rowconfigure((1),weight=1)
        self.columnconfigure((0),minsize=160)
        LeftMenu().create_menu(self)
        # create Body Frame
        Page().init_page(self)
        Page().create_new_page("- - -")
        DB().connect()
##############################################################################################################

if __name__ == "__main__":
    app = App()
    app.mainloop()