import ttkbootstrap as ttk
from resources import *

class App(ttk.Window):
    def __init__(self):
        super().__init__(
            title="Sysphean ERP",
            themename="superhero",
            size=(1280, 720),
            resizable=(True, False),
        )
        ################## IMAGES #################
        image_files = (
            ('logo','Sysphean_Logo.png',120,100),
            )
        self.img_ls = []
        for name, file_name ,w ,h in image_files:
            path = r"./assets/" + file_name
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
        BodyFrame().create_body(self)
        BodyFrame().create_new_frame("_ _ _")
##############################################################################################################

if __name__ == "__main__":
    app = App()
    app.mainloop()