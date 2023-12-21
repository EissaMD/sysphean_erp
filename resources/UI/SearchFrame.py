from config import *
from ..Logics import DB
from .EntriesFrame import EntriesFrame

class SearchFrame(ctk.CTkFrame):
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
        DB.cursor.execute(sql) 
        records = DB.cursor.fetchall() or []
        records = [list(record) for record in records]
        self.sheet.set_sheet_data(records,False)
    ###############        ###############        ###############        ###############
    def select_layout(self,selected_layout):
        if selected_layout == "Default": ##############
            col_size =100
            col_size= [col_size,col_size*1.2,col_size,col_size*1.5,col_size*1.2,col_size*2,col_size*2]
            self.layout = { "search_entries"  :(("customer_name"        ,"entry"        ,(0,0,1),None),
                                                ("email_address"        ,"entry"        ,(0,1,1),None),
                                                )        , 
                            "headrs"   :["ID", "Customer Name", "Email", "Contact", "Credit Limit", "Shipping Address" , "Billing Address"]            ,
                            "sql"      :"SELECT id, name, email, contact, credit_limit, shipping_address , billing_address FROM customer where name LIKE'%{}%' AND email LIKE'%{}%'",
                            "col_size" :col_size}
        elif selected_layout == "Search Customer": ##############
            col_size =98
            self.layout = { "search_entries"  :( 
                                        ("customer_name"        ,"entry"        ,(0,0,1),None),
                                        )      , 
                            "headrs"   :["ID", "Customer Name", "Email", "Contact", "Credit Limit", "Shipping Address" , "Billing Address"],
                            "sql"      :"SELECT id, name, email, contact, credit_limit, shipping_address , billing_address FROM customer where name LIKE'%{}%'",
                            "col_size" :[col_size,col_size*1.2,col_size,col_size*1.5,col_size*1.2,col_size*2,col_size*2]}
        elif selected_layout == "Search Part No": ##############
            col_size =98
            col_size= [col_size,col_size,col_size,col_size,col_size,col_size,col_size,col_size,col_size]
            self.layout = { "search_entries"  :( 
                                        ("part_no"        ,"entry"        ,(0,0,1),None),
                                        )      , 
                            "headrs"   :["ID", "Part No", "Bundle Qty", "Stn Carton", "UOM", "Cavity" , "Customer", "Sided", "Label Type"],
                            "sql"      :"SELECT id, part_no, bundle_qty, stn_carton, uom, cavity, customer, CASE WHEN single_sided = 1 THEN 'Single' ELSE 'Double' END AS single_sided,"
                                        " CASE WHEN paper_label = 1 THEN 'Paper' ELSE 'Sticker' END AS paper_label FROM part_info WHERE part_no LIKE'%{}%'",
                            "col_size" :col_size}
        elif selected_layout == "Search Traveller No": ##############
            col_size =98
            col_size= [col_size,col_size,col_size]
            self.layout = { "search_entries"  :( 
                                        ("part_no"        ,"entry"        ,(0,0,1),None),
                                        )      , 
                            "headrs"   :["ID", "Traveller No", "Part No"],
                            "sql"      :"SELECT id, traveller_no, part_no FROM production_entry_combined WHERE part_no LIKE'%{}%'",
                            "col_size" :col_size}
        elif selected_layout == "Batch Entry": ##############
            col_size =140
            col_size= [col_size*.5, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = { "search_entries"  :( ("part_no"      ,"entry"    ,(0,0,1),None),
                                                )        , 
                            "headrs"   :["ID", "Part No", "Quantity", "Date Code", "Remarks", "Additional Info", "Time Added", "User"] ,
                            "sql"      :"SELECT id , part_no , quantity , date_code , remarks , additional_info , time_created , user_name FROM entry_tracker where part_no LIKE'%{}%' ORDER BY id DESC",
                            "col_size" :col_size}
        elif selected_layout == "Extra Labels": ##############
            col_size =140
            col_size= [col_size*.5, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = { "search_entries"  :(("part_no"      ,"entry"    ,(0,0,1),None),
                                                ("date_code"    ,"entry"    ,(0,1,1),None),
                                                )        , 
                            "headrs"   :["ID", "Part No", "Quantity", "Date Code","Remarks", "Additional Info", "Label Type", "Time Added"]            ,
                            "sql"      :"SELECT id , part_no , quantity , date_code , remarks , additional_info , label_type , time_created FROM extra_labels where part_no LIKE'%{}%' AND date_code LIKE'%{}%' ORDER BY id DESC",
                            "col_size" :col_size}
        elif selected_layout == "Reject Batch": ##############
            col_size =140
            col_size= [col_size*.5, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = { "search_entries"  :(("part_no"      ,"entry"    ,(0,0,1),None),
                                                )        , 
                            "headrs"   :["ID", "Part No", "Traveller No", "Quantity", "UOM", "Reason", "Date", "Time Added"]            ,
                            "sql"      :"SELECT id , part_no , traveller_no , quantity , uom , reason , date , time_created FROM batch_rejection where part_no LIKE'%{}%' ORDER BY id DESC",
                            "col_size" :col_size}
        elif selected_layout == "Search Entry Tracker":##############
            col_size =98
            col_size= [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = {"search_entries"  :(("part_no"      ,"entry"    ,(0,0,1),None),
                                                )        ,
                            "headrs"   :["ID", "Part No", "Quantity", "Date Code", "Remarks", "Time Added", "Additional Info", "User Name"]            ,
                            "sql"      :"SELECT id , part_no , quantity , date_code , remarks , time , additional_info , user_name FROM entry_tracker where part_no LIKE'%{}%' ORDER BY id DESC",
                            "col_size" :col_size}
        elif selected_layout == "Search Delivery Order": ##############
            col_size =98
            col_size= [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = {"search_entries"  :(("id"      ,"entry"    ,(0,0,1),None),
                                            ("part_no", "entry", (1, 0, 1), None),
                                            ("customer", "entry", (0, 1, 1), None),
                                            ("delivery_order", "entry", (1, 1, 1), None),
                                                )        ,
                            "headrs"   :["ID", "Customer", "Part No", "Quantity", "Fulfilled", "UoM", "Carton IDs", "Delivery Order", "Delivery Date", "Added Time"]            ,
                            "sql"      :"SELECT id , customer, part_no , quantity , fulfilled_quantity , uom , cartons_id , delivery_order , delivery_date, time_created FROM delivery_orders "
                                        "where id LIKE'%{}%' AND part_no LIKE'%{}%' AND customer LIKE'%{}%' AND delivery_order LIKE'%{}%' ORDER BY id",
                            "col_size" :col_size}
        elif selected_layout == "Main Inventory":  ##############
            col_size = 140
            col_size = [col_size * .5, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = {"search_entries": (("part_no", "entry", (0, 0, 1), None),
                                            ),
                        "headrs": ["ID", "Part No", "Carton Quantity", "Sealed Quantity", "Standard Quantity",
                                    "New Stock", "Old Stock", "Total Stock"],
                        "sql": "SELECT id , part_no , carton_quantity , sealed_quantity , stn_qty , new_stock , old_stock , total_stock FROM main_inventory where part_no LIKE'%{}%' ORDER BY id",
                        "col_size": col_size}
        elif selected_layout == "Carton Table":  ##############
            col_size = 140
            col_size = [col_size * .5, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = {"search_entries": (("part_no", "entry", (0, 0, 1), None),
                                            ),
                        "headrs": ["ID", "Part No", "Carton Quantity", "Loose Quantity", "Date Codes", "Remarks",
                                    "Delivery ID", "Packing Date"],
                        "sql": "SELECT id , part_no , carton_quantity , loose_quantity , date_codes , remarks , delivery_id , packing_date FROM carton_table where part_no LIKE'%{}%' ORDER BY id",
                        "col_size": col_size}
        elif selected_layout == "Archived Carton Table":  ##############
            col_size = 140
            col_size = [col_size * .5, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = {"search_entries": (("part_no", "entry", (0, 0, 1), None),
                                            ),
                        "headrs": ["ID", "Part No", "Carton Quantity", "Loose Quantity", "Date Codes", "Remarks",
                                    "Delivery ID", "Packing Date"],
                        "sql": "SELECT id , part_no , carton_quantity , loose_quantity , date_codes , remarks , delivery_id , packing_date FROM archived_carton_table where part_no LIKE'%{}%' ORDER BY id",
                        "col_size": col_size}
        elif selected_layout == "Sealed Inventory":  ##############
            col_size = 140
            col_size = [col_size * .5, col_size, col_size, col_size, col_size, col_size]
            self.layout = {"search_entries": (("part_no", "entry", (0, 0, 1), None),
                                            ),
                        "headrs": ["ID", "Part No", "Quantity", "Date Codes", "Remarks", "Additional Info"],
                        "sql": "SELECT id , part_no , quantity , date_code , remarks , additional_info FROM sealed_inventory where part_no LIKE'%{}%' ORDER BY id",
                        "col_size": col_size}
##############################################################################################################

if __name__ == "__main__":
    pass