import ttkbootstrap as ttk

class App(ttk.Window):
    def __init__(self):
        super().__init__(
            title="Sysphean ERP",
            # themename="journal",
            size=(1000, 600),
            resizable=(True, False),
        )


if __name__ == "__main__":
    app = App()
    app.mainloop()