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
    print(data)

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
data = ('eissa', 'gAAAAABlfsl9Xu4n9jRQZo6yy1OEiP2eaFNY-8a2EdMWJ521nmsm7cTq9LkB69QPBlY4lU15uAg6_ztS8NVuDUNaikt4PzjqdA==', 'Eissa', 'moh', 'QC', 0, 0, 1, 1, 0, datetime.now())
app.mainloop()
# columns = ("id", "part_no", "traveller_no", "quantity", "uom", "reason", "date", "time_added")
# print(" , ".join(columns))