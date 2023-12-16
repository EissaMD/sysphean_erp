from resources import DB , CustomerManagement
from resources.UI import SearchFrame ,EntriesFrame , CheckboxFrame
from config import *
from resources.Manufacturing import SimilarBatchWindow
DB.connect()

# cm = CustomerManagement(True)
# cm.confirm_btn(True)

# query = 'INSERT INTO customer (name, email, contact, credit_limit, payment_terms, communication_preferences, shipping_address, billing_address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'
# data = ("customer_test" , "customer_test@example.com" , "0110000000" , "101010" , "Cash" , "Phone" , "MY" , "MY")
# db.cursor.execute(query, data)
# db

def test():
    data = cb.get_data()
    print(data)
    cb.change_value("op1",True)
    cb.disable()

image_files = (     ('logo'                 ,   'Sysphean_Logo.png'     ,120   ,100    ),
                    ('search_icon'          ,   'Search.png'            ,20    ,20     ),
            )
app = ctk.CTk()
app.geometry("900x600")
app.title("CTk example")
img_ls = []
for name, file_name ,w ,h in image_files:
    path = r"./assets/" + file_name # image should be saved in "assets" folder
    img =Image.open(path).resize((w,h)) if w > 0 else Image.open(path)
    img_ls.append(ImageTk.PhotoImage(img ,name=name))
frame = ctk.CTkFrame(app,fg_color="transparent", border_width=2)
frame.pack()
entry = ("my_options" , ("op1","op2" , "op3") , (1,0,1))
cb = CheckboxFrame(app,entry,)
entries = ( 
                        ("order_id"             ,"entry"        ,(0,0,1),None),
                        ("order_date"           ,"date"         ,(0,1,1),None),
                        ("order_status"         ,"menu"         ,(1,0,1),("Open","In Process","Shipped","Completed")),
                        ("sales_representative" ,"entry"        ,(1,1,1),None),
                        ("delivery_date"        ,"date"         ,(2,0,1),None),
                        )
basic_entries = EntriesFrame(app,entries) ; basic_entries.pack() 
ctk.CTkButton(app,command=test).pack()
app.mainloop()
# columns = ("id", "part_no", "traveller_no", "quantity", "uom", "reason", "date", "time_added")
# print(" , ".join(columns))