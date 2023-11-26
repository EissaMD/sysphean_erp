import customtkinter as ctk
from tksheet import Sheet
from ..Logics import DB
from .SearchFrame import SearchFrame

class SearchWindow(ctk.CTkToplevel , DB):
    def __init__(self,select_btn=lambda : 0 , layout="Default" ):
        self.window_exist = False
        self.selected_row = None
        self.select_btn = select_btn
        self.layout = layout
        if layout == "Search Customer":
            self.dimension = "1000x310"
        elif layout == "Search Part No":
            self.dimension = "1000x310"
        elif layout == "Search Traveller No":
            self.dimension = "1000x310"
    ###############        ###############        ###############        ###############
    def new_window(self):
        if self.window_exist:
            return
        super().__init__()
        self.title(self.layout)
        self.geometry(self.dimension)
        search_frame = SearchFrame(self,layout=self.layout)
        search_frame.pack(fill="x" )
        self.sheet = search_frame.sheet
        self.sheet.bind("<ButtonPress-1>", self.left_click_sheet)
        ctk.CTkButton(self, text="Select", command=self.select_btn ,width=50).pack( pady=2)
        self.protocol("WM_DELETE_WINDOW", self.close)  # call .close() when window gets closed
        self.window_exist = True
    ###############        ###############        ###############        ###############
    def close(self):
        self.window_exist = False
        self.destroy()
    ###############        ###############        ###############        ###############
    def left_click_sheet(self,event):
            try:
                row = self.sheet.identify_row(event, exclude_index = False, allow_end = True)
                row = self.sheet.get_row_data(row)
                self.selected_row = row
            except: 
                self.selected_row = None
##############################################################################################################

if __name__ == "__main__":
    SearchWindow()