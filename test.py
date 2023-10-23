import customtkinter as ctk
from tkcalendar import Calendar, DateEntry
def abc(choice):
    print(choice)
from resources.UI import EntriesFrame
app = ctk.CTk()
app.geometry("600x500")
app.title("CTk example")

entries = ( 
            ("communication_preferences_checkbox0"    , "entry",(0,0,1),["1","2"]),
            ("shipping_address"             , "entry",(1,0,1),None),
            ("billing_address"              , "entry",(2,0,1),None),
            )
customer_address = EntriesFrame(app,entries) ; customer_address.pack() 
customer_address.entry_dict["communication_preferences"]
data = customer_address.get_data()
print(data)
app.mainloop()

