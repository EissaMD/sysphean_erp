import ttkbootstrap as ttk

class MainMenu(ttk.Frame):
    def __init__(self,master,menu_ls=()):
        background="light"
        super().__init__(master,bootstyle=background)
        frame = ttk.Frame(self,bootstyle=background); frame.pack()
        s = ttk.Style()
        s.configure("light.TButton", font=('Arial', 10, "bold"))
        for menu in menu_ls:
            ttk.Button(frame,text=menu, style="light.TButton").pack(side="left")