class class_A:
    var=10
    
    

aa = class_A()
class_A.var = {666:"asaki",}
bb = class_A()
print(aa.var)

import customtkinter as ctk

class RadioButtons():
    def __init__(self):
        self.selected = ""
        self.radio_var = ctk.StringVar(value="")
        self.element_ls = {"": ()}
    def add_button(self,master,name,elements=()):
        ctk.CTkRadioButton(master, text=name,
                            command=self.radiobutton_event, variable= self.radio_var, value=name).pack(side="left")
        self.element_ls[name] = elements
        for element in elements:
            element.configure(state="disabled")
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
        