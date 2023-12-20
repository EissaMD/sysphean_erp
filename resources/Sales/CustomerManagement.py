
from config import *
from ..UI import Page , EntriesFrame
from ..Logics import DB

class CustomerManagement(Page):
        def __init__(self,test=False):
                if not test:
                        menu_ls = {
                                "Add"   : self.Add_frame,
                                "Edit"  : self.edit_frame,
                                "Delete": self.delete_frame,
                        }
                        self.create_new_page("Customer Management", menu_ls)
        ###############        ###############        ###############        ###############
        def Add_frame(self):
                body_frame = self.create_new_body()
                entries = ( 
                        ("customer_name"        ,"entry"        ,(0,0,1),None),
                        ("email_address"        ,"entry"        ,(0,1,1),None),
                        ("contact_number"       ,"entry"        ,(1,0,1),None),
                        ("credit_limit"         ,"entry"        ,(1,1,1),None),
                        ("payment_terms"        ,"menu"         ,(2,0,1),("Net 30 days","Cash on delivery")),
                        )
                self.customer_basic = EntriesFrame(body_frame,entries) ; self.customer_basic.pack() 
                entries = ( 
                        ("communication_preferences"    , "entry",(0,0,1),None),
                        ("shipping_address"             , "entry",(1,0,1),None),
                        ("billing_address"              , "entry",(2,0,1),None),
                        )
                self.customer_address = EntriesFrame(body_frame,entries) ; self.customer_address.pack() 
                self.create_footer(self.confirm_btn)
        ###############        ###############        ###############        ###############
        def confirm_btn(self,test=False):
                if test :
                        data = ("customer_test" , "customer_test@example.com" , "0110000000" , "101010" , "Cash" , "Phone" , "MY" , "MY")
                else:
                        customer_basic = self.customer_basic.get_data()
                        customer_address = self.customer_address.get_data()
                        data = list(customer_basic.values()) + list(customer_address.values())
                col_name = ("name","email","contact","credit_limit","payment_terms","communication_preferences","shipping_address","billing_address")
                complete = DB.insert("customer" , col_name ,data )
                if not complete:
                        return
                messagebox.showinfo("Info","The process was successful!")
        ###############        ###############        ###############        ###############
        def edit_frame(self):
                self.create_new_body()
        ###############        ###############        ###############        ###############
        def delete_frame(self):
                self.create_new_body()
##############################################################################################################