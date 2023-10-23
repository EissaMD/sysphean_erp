import customtkinter as ctk
from tksheet import Sheet
from ..Logics import DB

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
        frame = ctk.CTkFrame(self,border_width=2); frame.pack(fill="x" , padx=4 , pady=4 , )
        ctk.CTkLabel(frame, text=self.layout["label"]).pack(side="left")
        self.entry = ctk.CTkEntry(frame) ; self.entry.pack(side="left", fill="x",expand=True)
        ctk.CTkButton(frame ,image="search_icon" , text="" , command=self.search_btn,width=50).pack(side="left")
        frame = ctk.CTkFrame(self,); frame.pack(fill="both" , padx=4 , pady=2,expand=True)
        self.customer_sheet = Sheet(frame, show_x_scrollbar=False,height=200,show_top_left=False,
                                headers=self.layout["headrs"],
                                )
        self.customer_sheet.bind("<ButtonPress-1>", self.left_click_sheet)
        self.customer_sheet.set_column_widths(column_widths = self.layout["col_size"])
        binding = ("row_select", "column_width_resize", "double_click_column_resize", "column_height_resize", "arrowkeys","row_select","single_select")
        self.customer_sheet.enable_bindings(binding)
        self.customer_sheet.pack(fill="both", padx=4, pady=4,expand=True)
        ctk.CTkButton(self, text="Select", command=self.select_btn ,width=50).pack( pady=2)
        self.protocol("WM_DELETE_WINDOW", self.close)  # call .close() when window gets closed
        self.window_exist = True
    ###############        ###############        ###############        ###############
    def search_btn(self):
        entry = self.entry.get()
        records = self.cursor.execute(self.layout["sql"].format(entry))
        records = [list(record) for record in records]
        self.customer_sheet.set_sheet_data(records,False)
    ###############        ###############        ###############        ###############
    def close(self):
        self.window_exist = False
        self.destroy()
    ###############        ###############        ###############        ###############
    def left_click_sheet(self,event):
            try:
                row = self.customer_sheet.identify_row(event, exclude_index = False, allow_end = True)
                row = self.customer_sheet.get_row_data(row)
                self.selected_row = row
            except: 
                self.selected_row = None
    ###############        ###############        ###############        ###############
    def select_layout(self,selected_layout):
        if selected_layout == "Default":
            col_size =100
            col_size= [col_size,col_size*1.2,col_size,col_size*1.5,col_size*1.2,col_size*2,col_size*2]
            self.layout = { "title"    : "Search"      , 
                            "label"    :"Entry"        , 
                            "dimension":"1000x280"     , 
                            "headrs"   :["ID", "Customer Name", "Email", "Contact", "Credit Limit", "Shipping Address" , "Billing Address"]            ,
                            "sql"      :"SELECT id, name, email, contact, credit_limit, shipping_address , billing_address FROM customer where name LIKE'%{}%'",
                            "col_size" :[col_size,col_size*1.2,col_size,col_size*1.5,col_size*1.2,col_size*2,col_size*2]}
        elif selected_layout == "Search Customer":
            col_size =98
            self.layout = { "title"    :"Search Customer"      , 
                            "label"    :"Customer Name: "        , 
                            "dimension":"1000x280"     , 
                            "headrs"   :["ID", "Customer Name", "Email", "Contact", "Credit Limit", "Shipping Address" , "Billing Address"],
                            "sql"      :"SELECT id, name, email, contact, credit_limit, shipping_address , billing_address FROM customer where name LIKE'%{}%'",
                            "col_size" :[col_size,col_size*1.2,col_size,col_size*1.5,col_size*1.2,col_size*2,col_size*2]}
        elif selected_layout == "Search Part No":
            col_size =98
            col_size= [col_size,col_size,col_size,col_size,col_size,col_size,col_size,col_size,col_size]
            self.layout = { "title"    :"Search Part No"      ,
                            "label"    :"Part No: "        ,
                            "dimension":"1000x280"     ,
                            "headrs"   :["ID", "Part No", "Bundle Qty", "Stn Carton", "UOM", "Cavity" , "Customer", "Sided", "Label Type"],
                            "sql"      :"SELECT id, part_no, bundle_qty, stn_carton, uom, cavity, customer, CASE WHEN single_sided = 1 THEN 'Single' ELSE 'Double' END AS single_sided,"
                                        " CASE WHEN paper_label = 1 THEN 'Paper' ELSE 'Sticker' END AS paper_label FROM part_info WHERE part_no LIKE'%{}%'",
                            "col_size" :col_size}
        elif selected_layout == "Search Traveller No":
            col_size =98
            col_size= [col_size,col_size,col_size]
            self.layout = { "title"    :"Search Traveller No"      ,
                            "label"    :"Part No: "        ,
                            "dimension":"1000x280"     ,
                            "headrs"   :["ID", "Traveller No", "Part No"],
                            "sql"      :"SELECT id, traveller_no, part_no FROM production_entry_combined WHERE part_no LIKE'%{}%'",
                            "col_size" :col_size}
##############################################################################################################

if __name__ == "__main__":
    SearchWindow()