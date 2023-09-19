import customtkinter as ctk


class RadioButtons():
    def __init__(self):
        self.selected = ""
        self.radio_var = ctk.StringVar(value="")
        self.element_ls = {"": ()}
    ###############        ###############        ###############        ###############
    def add_button(self,master,name,label,elements=()):
        ctk.CTkRadioButton(master, text=label,
                            command=self.radiobutton_event, variable= self.radio_var, value=name).pack(side="left",padx=4)
        self.element_ls[name] = elements
        # for element in elements:
        #     element.configure(state="disabled")
    ###############        ###############        ###############        ###############
    def radiobutton_event(self):
        # disable pervious elements
        elements = self.element_ls[self.selected]
        for element in elements:
            element.configure(state="disabled")
        # enable current elements
        self.selected = self.radio_var.get()
        elements = self.element_ls[self.selected]
        for element in elements:
            element.configure(state="normal")
    ###############        ###############        ###############        ###############
    def disable_all_elements(self):
        for name,elements in self.element_ls.items():
            for element in elements:
                for element in elements:
                    element.configure(state="disabled")
##############################################################################################################