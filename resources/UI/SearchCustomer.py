import ttkbootstrap as ttk


class SearchCustomer(ttk.Toplevel):
    def __init__(self):
        self = super().__init__(
            title="Customer",
            size=(600, 400),
            resizable=(True, False),
            topmost=True,
        )
        frame = ttk.Frame(self,).pack(fill="x" , padx=4 , pady=4,side="top")
        ttk.Label(frame, text="Customer Name:").pack(side="left")
        ttk.Entry(frame).pack(side="left", fill="x")
        ttk.Button(frame ,bootstyle="primary-outline",text="s").pack(side="left")

if __name__ == "__main__":
    window = ttk.Window(title="Sysphean ERP",
            themename="flatly",
            size=(1000, 600),
            resizable=(True, False),
        )
    ttk.Button(window,text="S").pack(side="left", fill="x")
    SearchCustomer()
    window.mainloop()