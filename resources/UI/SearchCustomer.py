import customtkinter as ctk
from tksheet import Sheet
from ..Logics import DB

class SearchCustomer(ctk.CTkToplevel , DB):
    def __init__(self,select_btn=lambda : 0):
        self.window_exist = False
        self.selected_row = None
        self.select_btn = select_btn
    ###############        ###############        ###############        ###############
    def new_window(self):
        if self.window_exist:
            return
        super().__init__()
        self.title("Search Customer")
        self.geometry("1000x280")
        frame = ctk.CTkFrame(self,border_width=2); frame.pack(fill="x" , padx=4 , pady=4 , )
        ctk.CTkLabel(frame, text="Customer Name:").pack(side="left")
        self.customer_name = ctk.CTkEntry(frame) ; self.customer_name.pack(side="left", fill="x",expand=True)
        ctk.CTkButton(frame ,image="search_icon" , text="" , command=self.search_btn,width=50).pack(side="left")
        frame = ctk.CTkFrame(self,); frame.pack(fill="both" , padx=4 , pady=2,expand=True)
        self.customer_sheet = Sheet(frame, show_x_scrollbar=False,height=200,show_top_left=False,
                                headers=["ID", "Customer Name", "Email", "Contact", "Credit Limit", "Shipping Address" , "Billing Address"],
                                )
        self.customer_sheet.bind("<ButtonPress-1>", self.left_click_sheet)
        col_size =98
        col_size= [col_size,col_size*1.2,col_size,col_size*1.5,col_size*1.2,col_size*2,col_size*2]
        self.customer_sheet.set_column_widths(column_widths = col_size)
        binding = ("row_select", "column_width_resize", "double_click_column_resize", "column_height_resize", "arrowkeys","row_select","single_select")
        self.customer_sheet.enable_bindings(binding)
        self.customer_sheet.pack(fill="both", padx=4, pady=4,expand=True)
        ctk.CTkButton(self, text="Select", command=self.select_btn ,width=50).pack( pady=2)
        self.protocol("WM_DELETE_WINDOW", self.close)  # call .close() when window gets closed
        self.window_exist = True
    ###############        ###############        ###############        ###############
    def search_btn(self):
        self.winfo_exists
        customer_name = self.customer_name.get()
        customer_records = self.select("customer",("id", "name", "email", "contact", "credit_limit", "shipping_address" , "billing_address"),f"name LIKE'%{customer_name}%'")
        self.customer_sheet.set_sheet_data(customer_records,False)
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
                
##############################################################################################################

if __name__ == "__main__":
    SearchCustomer()