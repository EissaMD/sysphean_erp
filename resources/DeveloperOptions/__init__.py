from ..UI import Page, LeftMenu 



class DeveloperOptions(Page):
    def __init__(self):
        self.create_new_page("Developer Options")
        left_menu = LeftMenu()
        left_menu_ls = {
            
        }
        left_menu.update_menu(left_menu_ls) 