from config import *

class CheckboxFrame(ctk.CTkFrame):
    """Create a new Frame with multiple entries in grid format
    Args:
        master (tk): parent frame or window
        title (str): small text on the top left of the frame
        entry_info (tuple or list): (entry_name , options , values). Defaults to ().
    """
    def __init__(self,master,entry_info=(),pack=True,border_width=2):
        self.checkbox_ls = {}
        super().__init__(master,  height=100 ,fg_color="transparent" , border_width=border_width)
        if pack:
            self.pack(fill="both" , pady =10, padx=2)
        frame = ctk.CTkFrame(self,fg_color="transparent"); frame.pack(fill="both",expand=True,padx=4,pady=4)
        entry_name , options , values = entry_info
        # create label
        if entry_name:
            label = entry_name.replace('_',' ').title() + " :"
            label = label.replace('Id','ID')
            ctk.CTkLabel(frame , text=f"{label:<25}" , font=("arial",11), width=130).pack(side="left" ,anchor=ctk.W , padx=10)
        for option, value in zip(options,values):
            self.checkbox_ls[option] = ctk.CTkCheckBox(frame,text=option)
            self.checkbox_ls[option].pack(side="left")
            if   value ==1:
                self.checkbox_ls[option].select()
            elif value ==0:
                self.checkbox_ls[option].deselect()
    ###############        ###############        ###############        ###############
    def get_data(self):
        data = {}
        for option,widget in self.checkbox_ls.items():
            data[option] = widget.get()
        return data
    ###############        ###############        ###############        ###############
    def change_value(self,option,value):
        if value:
            self.checkbox_ls[option].select()
        else:
            self.checkbox_ls[option].deselect()
    ###############        ###############        ###############        ###############
    def disable(self):
        for _,widget in self.checkbox_ls.items():
            widget.configure(state="disabled")
    ###############        ###############        ###############        ###############
    def enable(self):
        for _,widget in self.checkbox_ls.items():
            widget.configure(state="normal")
##############################################################################################################