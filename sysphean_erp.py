import babel.numbers
from config import *
from resources import MainMenu , LoginSystem
from resources.UI import LeftMenu , Page
from resources.Logics import DB
ctk.set_default_color_theme("green")
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
        self.main_frame = ctk.CTkFrame(self,fg_color="transparent")
        ################## IMAGES #################
                    #Image name in tkinter  ,   file name               ,width ,height
        image_files = (     ('logo'                 ,   'Sysphean_Logo.png'     ,120   ,100    ),
                            ('search_icon'          ,   'Search.png'            ,20    ,20     ),
                            ('user_icon'            ,   'user.png'              ,100   ,100    ),
                            ('logout_icon'          ,   'logout.png'            ,20    ,20     ),
                            ('popup_icon'           ,   'popup.png'             ,20    ,20     ),
                            ('background'           ,   'background.png'        ,App.WIDTH    ,App.HEIGHT     ),
            )
        self.img_ls = []
        for name, file_name ,w ,h in image_files:
            path = r"./assets/" + file_name # image should be saved in "assets" folder
            img =Image.open(path).resize((w,h)) if w > 0 else Image.open(path)
            self.img_ls.append(ImageTk.PhotoImage(img ,name=name))
        ################## IMAGES #################
        DB.connect()
        login = LoginSystem(self.create_empty_frame,self.create_main_frame)
        LoginSystem.start()
        # self.create_main_frame()
    ###############        ###############        ###############        ###############
    def create_empty_frame(self):
        self.main_frame.destroy()
        self.main_frame = ctk.CTkFrame(self,fg_color="transparent")
        self.main_frame.pack(fill="both",expand=True)
        return self.main_frame
    ###############        ###############        ###############        ###############
    def create_main_frame(self):
        self.create_empty_frame()
        # create the main menu
        self.main_frame.columnconfigure((1),weight=1)
        main_menu = MainMenu(self.main_frame)
        main_menu.grid(row=0,column=0, columnspan=2, sticky="nswe" )
        # create secondary menu
        self.main_frame.rowconfigure((1),weight=1)
        self.main_frame.columnconfigure((0),minsize=160)
        LeftMenu().create_menu(self.main_frame)
        # create Body Frame
        Page().init_page(self.main_frame)
        Page().create_new_page("- - -")
##############################################################################################################

if __name__ == "__main__":
    app = App()
    app.mainloop()