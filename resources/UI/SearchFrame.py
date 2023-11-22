import customtkinter as ctk
from tksheet import Sheet
from ..Logics import DB
from .EntriesFrame import EntriesFrame

class SearchFrame(ctk.CTkFrame , DB):
    def __init__(self,master , layout="Default",new_layout = False):
        if new_layout is True:
            self.layout=layout
        else:
            self.select_layout(layout)
        super().__init__(master=master)
        self.entries = EntriesFrame(self,self.layout["search_entries"]) ; self.entries.pack()
        col , row = self.entries.max_col , self.entries.max_row
        frame = self.entries.entries_frame 
        ctk.CTkButton(frame ,image="search_icon" , text="" , command=self.search_btn,width=50).grid(sticky="nwes",row=0,column=col+1,rowspan=row+1,padx=(0,8),pady=2)
        frame = ctk.CTkFrame(self,); frame.pack(fill="both" , padx=4 , pady=2,expand=True)
        self.sheet = Sheet(frame, show_x_scrollbar=False,height=200,show_top_left=False,
                                headers=self.layout["headrs"],
                                )
        self.sheet.set_column_widths(column_widths = self.layout["col_size"])
        binding = ("row_select", "column_width_resize", "double_click_column_resize", "column_height_resize", "arrowkeys","row_select","single_select")
        self.sheet.enable_bindings(binding)
        self.sheet.pack(fill="both", padx=4, pady=4,expand=True)
        self.window_exist = True
    ###############        ###############        ###############        ###############
    def search_btn(self):
        entries = self.entries.get_data()
        values = tuple(entries.values())
        sql = self.layout["sql"].format(*values)
        self.cursor.execute(sql) 
        records = self.cursor.fetchall() or []
        records = [list(record) for record in records]
        self.sheet.set_sheet_data(records,False)
    ###############        ###############        ###############        ###############
    def select_layout(self,selected_layout):
        if selected_layout == "Default":
            col_size =100
            col_size= [col_size,col_size*1.2,col_size,col_size*1.5,col_size*1.2,col_size*2,col_size*2]
            self.layout = { "search_entries"  :( 
                                        ("customer_name"        ,"entry"        ,(0,0,1),None),
                                        ("email_address"        ,"entry"        ,(0,1,1),None),
                                        )        , 
                            "headrs"   :["ID", "Customer Name", "Email", "Contact", "Credit Limit", "Shipping Address" , "Billing Address"]            ,
                            "sql"      :"SELECT id, name, email, contact, credit_limit, shipping_address , billing_address FROM customer where name LIKE'%{}%' AND email LIKE'%{}%'",
                            "col_size" :col_size}
##############################################################################################################

if __name__ == "__main__":
    pass