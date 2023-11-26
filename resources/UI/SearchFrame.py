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
        if selected_layout == "Default":#####
            col_size =100
            col_size= [col_size,col_size*1.2,col_size,col_size*1.5,col_size*1.2,col_size*2,col_size*2]
            self.layout = { "search_entries"  :(("customer_name"        ,"entry"        ,(0,0,1),None),
                                                ("email_address"        ,"entry"        ,(0,1,1),None),
                                                )        , 
                            "headrs"   :["ID", "Customer Name", "Email", "Contact", "Credit Limit", "Shipping Address" , "Billing Address"]            ,
                            "sql"      :"SELECT id, name, email, contact, credit_limit, shipping_address , billing_address FROM customer where name LIKE'%{}%' AND email LIKE'%{}%'",
                            "col_size" :col_size}
        elif selected_layout == "Search Customer":#####
            col_size =98
            self.layout = { "search_entries"  :( 
                                        ("customer_name"        ,"entry"        ,(0,0,1),None),
                                        )      , 
                            "headrs"   :["ID", "Customer Name", "Email", "Contact", "Credit Limit", "Shipping Address" , "Billing Address"],
                            "sql"      :"SELECT id, name, email, contact, credit_limit, shipping_address , billing_address FROM customer where name LIKE'%{}%'",
                            "col_size" :[col_size,col_size*1.2,col_size,col_size*1.5,col_size*1.2,col_size*2,col_size*2]}
        elif selected_layout == "Search Part No":#####
            col_size =98
            col_size= [col_size,col_size,col_size,col_size,col_size,col_size,col_size,col_size,col_size]
            self.layout = { "search_entries"  :( 
                                        ("part_no"        ,"entry"        ,(0,0,1),None),
                                        )      , 
                            "headrs"   :["ID", "Part No", "Bundle Qty", "Stn Carton", "UOM", "Cavity" , "Customer", "Sided", "Label Type"],
                            "sql"      :"SELECT id, part_no, bundle_qty, stn_carton, uom, cavity, customer, CASE WHEN single_sided = 1 THEN 'Single' ELSE 'Double' END AS single_sided,"
                                        " CASE WHEN paper_label = 1 THEN 'Paper' ELSE 'Sticker' END AS paper_label FROM part_info WHERE part_no LIKE'%{}%'",
                            "col_size" :col_size}
        elif selected_layout == "Search Traveller No":#####
            col_size =98
            col_size= [col_size,col_size,col_size]
            self.layout = { "search_entries"  :( 
                                        ("part_no"        ,"entry"        ,(0,0,1),None),
                                        )      , 
                            "headrs"   :["ID", "Traveller No", "Part No"],
                            "sql"      :"SELECT id, traveller_no, part_no FROM production_entry_combined WHERE part_no LIKE'%{}%'",
                            "col_size" :col_size}
        elif selected_layout == "Batch Entry":#####
            col_size =140
            col_size= [col_size*.5, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = { "search_entries"  :( ("part_no"      ,"entry"    ,(0,0,1),None),
                                                )        , 
                            "headrs"   :["ID", "Part No", "Quantity", "Date Code", "Remarks", "Additional Info", "Time Added", "User"] ,
                            "sql"      :"SELECT id , part_no , quantity , date_code , remarks , additional_info , time , user_name FROM entry_tracker where part_no LIKE'%{}%'",
                            "col_size" :col_size}
        elif selected_layout == "Extra Labels":#####
            col_size =140
            col_size= [col_size*.5, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = { "search_entries"  :(("part_no"      ,"entry"    ,(0,0,1),None),
                                                ("date_code"    ,"entry"    ,(0,1,1),None),
                                                )        , 
                            "headrs"   :["ID", "Part No", "Quantity", "Date Code","Remarks", "Additional Info", "Label Type", "Time Added"]            ,
                            "sql"      :"SELECT id , part_no , quantity , date_code , remarks , additional_info , label_type , time_added FROM extra_labels where part_no LIKE'%{}%' AND date_code LIKE'%{}%'",
                            "col_size" :col_size}
        elif selected_layout == "Reject Batch":#####
            col_size =140
            col_size= [col_size*.5, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = { "search_entries"  :(("part_no"      ,"entry"    ,(0,0,1),None),
                                                )        , 
                            "headrs"   :["ID", "Part No", "Traveller No", "Quantity", "UOM", "Reason", "Date", "Time Added"]            ,
                            "sql"      :"SELECT id , part_no , traveller_no , quantity , uom , reason , date , time_added FROM batch_rejection where part_no LIKE'%{}%'",
                            "col_size" :col_size}

##############################################################################################################

if __name__ == "__main__":
    pass