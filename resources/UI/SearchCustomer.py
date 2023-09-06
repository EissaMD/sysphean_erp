import customtkinter as ctk


class SearchCustomer(ctk.CTkToplevel):
    def __init__(self):
        self = super().__init__(
            title="Customer",
            size=(600, 400),
            resizable=(True, False),
            topmost=True,
        )
        frame = ctk.CTkFrame(self,).pack(fill="x" , padx=4 , pady=4,side="top")
        ctk.CTkLabel(frame, text="Customer Name:").pack(side="left")
        ctk.CTkEntry(frame).pack(side="left", fill="x")
        ctk.CTkButton(frame ,bootstyle="primary-outline",text="s").pack(side="left")

# if __name__ == "__main__":
#     window = ttk.Window(title="Sysphean ERP",
#             themename="flatly",
#             size=(1000, 600),
#             resizable=(True, False),
#         )
#     ctk.CTkButton(window,text="S").pack(side="left", fill="x")
#     SearchCustomer()
#     window.mainloop()