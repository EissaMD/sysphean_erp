import customtkinter as ctk
from tkcalendar import Calendar, DateEntry
def abc():
    print(seg.get())

app = ctk.CTk()
app.geometry("600x500")
app.title("CTk example")

seg = ctk.CTkSegmentedButton(app, values=["Yearly", "Monthly", "Weekly", "Daily"]) ; seg.pack()

ctk.CTkButton(app,command=abc).pack()

date = DateEntry(master=app, width= 16 , foreground= "white",bd=2, locale='en_US', date_pattern='yyyy-mm-dd')
date.pack()
date.set_date("2020-1-02")
# print(date.get_date())
app.mainloop()