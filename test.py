import customtkinter as ctk

def abc():
    print(seg.get())

app = ctk.CTk()
app.geometry("600x500")
app.title("CTk example")

seg = ctk.CTkSegmentedButton(app, values=["Yearly", "Monthly", "Weekly", "Daily"]) ; seg.pack()

ctk.CTkButton(app,command=abc).pack()

app.mainloop()