import ttkbootstrap as ttk
from resources import *

class App(ttk.Window):
    def __init__(self):
        super().__init__(
            title="Sysphean ERP",
            themename="flatly",
            size=(1000, 600),
            resizable=(True, False),
        )
        self.configure(bg="#ccc")
        ################## IMAGES #################
                            #Image name in tkinter  ,   file name               ,width  ,height
        image_files = (     ('logo'                 ,   'Sysphean_Logo.png'     ,120    ,100    ),
            )
        self.img_ls = []
        for name, file_name ,w ,h in image_files:
            path = r"./assets/" + file_name # image should be saved in "assets" folder
            img =ttk.Image.open(path).resize((w,h)) if w > 0 else ttk.Image.open(path)
            self.img_ls.append(ttk.ImageTk.PhotoImage(img ,name=name))
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
##############################################################################################################

if __name__ == "__main__":
    app = App()
    app.mainloop()