from resources import DB , CustomerManagement
from resources.UI import TrackFrame ,SearchWindow
import customtkinter as ctk
from tkinter import ttk
from PIL import Image , ImageTk
db = DB()
db.connect()

# cm = CustomerManagement(True)
# cm.confirm_btn(True)

# query = 'INSERT INTO customer (name, email, contact, credit_limit, payment_terms, communication_preferences, shipping_address, billing_address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'
# data = ("customer_test" , "customer_test@example.com" , "0110000000" , "101010" , "Cash" , "Phone" , "MY" , "MY")
# db.cursor.execute(query, data)
# db

image_files = (     ('logo'                 ,   'Sysphean_Logo.png'     ,120   ,100    ),
                    ('search_icon'          ,   'Search.png'            ,20    ,20     ),
            )

app = ctk.CTk()
app.geometry("600x500")
app.title("CTk example")
img_ls = []
for name, file_name ,w ,h in image_files:
    path = r"./assets/" + file_name # image should be saved in "assets" folder
    img =Image.open(path).resize((w,h)) if w > 0 else Image.open(path)
    img_ls.append(ImageTk.PhotoImage(img ,name=name))
sw = SearchWindow()
sw.new_window()

app.mainloop()
