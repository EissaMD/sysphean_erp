from config import *
from ..Logics import DB


class DisplayTable(ctk.CTkFrame):
    def __init__(self,master , layout="Default"):
        super().__init__(master=master)
        self.select_layout(layout)
        self.sheet = Sheet(self,headers=self.layout["headrs"])
        self.sheet.set_column_widths(column_widths=self.layout["col_size"])
        binding = ("single_select", "row_select",
                   "column_width_resize", "double_click_column_resize", "row_width_resize", "column_height_resize",
                   "row_height_resize", "double_click_row_resize")
        self.sheet.enable_bindings(binding)
        self.sheet.pack(fill="both", padx=4, pady=4)
        self.pack(fill="both", padx=4, pady=4)
    ###############        ###############        ###############        ###############
    def update(self,data):
        data = [list(ls) for ls in data]
        self.sheet.set_sheet_data(data,False)
    ###############        ###############        ###############        ###############
    def select_layout(self,selected_layout):
        if selected_layout == "Default":#####
            col_size = 135
            col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = { "headrs"   :["Bundle Qty", "Stn Carton", "Stn Qty", "UOM", "Cavity", "Customer", "Single Sided", "Label Type"]            ,
                            "col_size" :col_sizes}
        elif selected_layout == "Batch Rejection":#####
            col_size = 150
            col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = { "headrs"   :["Part No", "Traveller No", "Quantity", "UOM", "Reason", "Date", "Time Added"]            ,
                            "col_size" :col_sizes}
##############################################################################################################

if __name__ == "__main__":
    pass