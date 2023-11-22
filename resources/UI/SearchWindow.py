import customtkinter as ctk
from tksheet import Sheet
from ..Logics import DB
from .SearchFrame import SearchFrame

class SearchWindow(ctk.CTkToplevel , DB):
    def __init__(self,select_btn=lambda : 0 , layout="Default" ):
        self.window_exist = False
        self.selected_row = None
        self.select_btn = select_btn
        self.select_layout(layout)
    ###############        ###############        ###############        ###############
    def new_window(self):
        if self.window_exist:
            return
        super().__init__()
        self.title(self.layout["title"])
        self.geometry(self.layout["dimension"])
        search_frame = SearchFrame(self,layout=self.layout,new_layout=True)
        search_frame.pack(fill="x" )
        self.sheet = search_frame.sheet
        self.sheet.bind("<ButtonPress-1>", self.left_click_sheet)
        self.sheet.set_column_widths(column_widths = self.layout["col_size"])
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
    ###############        ###############        ###############        ###############
    def select_layout(self,selected_layout):
        if selected_layout == "Default":
            col_size =100
            col_size= [col_size,col_size*1.2,col_size,col_size*1.5,col_size*1.2,col_size*2,col_size*2]
            self.layout = { "title"    : "Search"      , 
                            "search_entries"  :( 
                                        ("customer_name"        ,"entry"        ,(0,0,1),None),
                                        )      , 
                            "dimension":"1000x305"     , 
                            "headrs"   :["ID", "Customer Name", "Email", "Contact", "Credit Limit", "Shipping Address" , "Billing Address"]            ,
                            "sql"      :"SELECT id, name, email, contact, credit_limit, shipping_address , billing_address FROM customer where name LIKE'%{}%'",
                            "col_size" :col_size}
        elif selected_layout == "Search Customer":
            col_size =98
            self.layout = { "title"    :"Search Customer" ,
                            "search_entries"  :( 
                                        ("customer_name"        ,"entry"        ,(0,0,1),None),
                                        )      , 
                            "dimension":"1000x310"     , 
                            "headrs"   :["ID", "Customer Name", "Email", "Contact", "Credit Limit", "Shipping Address" , "Billing Address"],
                            "sql"      :"SELECT id, name, email, contact, credit_limit, shipping_address , billing_address FROM customer where name LIKE'%{}%'",
                            "col_size" :[col_size,col_size*1.2,col_size,col_size*1.5,col_size*1.2,col_size*2,col_size*2]}
        elif selected_layout == "Search Part No":
            col_size =98
            col_size= [col_size,col_size,col_size,col_size,col_size,col_size,col_size,col_size,col_size]
            self.layout = { "title"    :"Search Part No"      ,
                            "search_entries"  :( 
                                        ("part_no"        ,"entry"        ,(0,0,1),None),
                                        )      , 
                            "dimension":"1000x310"     ,
                            "headrs"   :["ID", "Part No", "Bundle Qty", "Stn Carton", "UOM", "Cavity" , "Customer", "Sided", "Label Type"],
                            "sql"      :"SELECT id, part_no, bundle_qty, stn_carton, uom, cavity, customer, CASE WHEN single_sided = 1 THEN 'Single' ELSE 'Double' END AS single_sided,"
                                        " CASE WHEN paper_label = 1 THEN 'Paper' ELSE 'Sticker' END AS paper_label FROM part_info WHERE part_no LIKE'%{}%'",
                            "col_size" :col_size}
        elif selected_layout == "Search Traveller No":
            col_size =98
            col_size= [col_size,col_size,col_size]
            self.layout = { "title"    :"Search Traveller No"      ,
                            "search_entries"  :( 
                                        ("part_no"        ,"entry"        ,(0,0,1),None),
                                        )      , 
                            "dimension":"1000x310"     ,
                            "headrs"   :["ID", "Traveller No", "Part No"],
                            "sql"      :"SELECT id, traveller_no, part_no FROM production_entry_combined WHERE part_no LIKE'%{}%'",
                            "col_size" :col_size}
##############################################################################################################

if __name__ == "__main__":
    SearchWindow()