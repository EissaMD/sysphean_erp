import customtkinter as ctk
from tkcalendar import Calendar, DateEntry
import tkinter as tk

class EntriesFrame(ctk.CTkFrame):
    """Create a new Frame with multiple entries in grid format
    Args:
        master (tk): parent frame or window
        title (str): small text on the top left of the frame
        entry_ls (tuple or list): (entry_name , entry_type , row , col , options). Defaults to ().
    """
    def __init__(self,master,entry_ls=(),pack=True):
        self.entry_dict = {}
        super().__init__(master,  height=100)
        if pack:
            self.pack(fill="both" , pady =10, padx=2)
        self.entries_frame = ctk.CTkFrame(self); self.entries_frame.pack(fill="both",expand=True,padx=4,pady=4)
        self.frames= {}
        for entry in entry_ls:
            self.add_entry(entry)
    ###############        ###############        ###############        ###############
    def add_entry(self,entry_info):
        entry_name , entry_type , pos , options=entry_info
        row, col , col_span = pos
        label = entry_name.replace('_',' ').title() + " :"
        label = label.replace('Id','ID')
        self.entries_frame.grid_columnconfigure(col,weight=1)
        frame = ctk.CTkFrame(self.entries_frame,fg_color="transparent")
        frame.grid(sticky="we",row=row,column=col,columnspan=col_span,padx=10)
        self.frames[entry_name]= frame
        ctk.CTkLabel(frame , text=f"{label:<25}" , font=("arial",11), width=130).pack(side="left" ,anchor=ctk.W , padx=10)
        # entry type
        if entry_type == "entry":
            self.entry_dict[entry_name] = ctk.CTkEntry(frame , corner_radius=0)
            self.entry_dict[entry_name].pack(side="left", fill="both" , expand=True)
        elif entry_type == "menu":
            self.entry_dict[entry_name] = ctk.CTkOptionMenu(frame, values=list(options) , fg_color="#565e58",button_color="#565e58",button_hover_color="#3c423e" , corner_radius=0,)
            self.entry_dict[entry_name].pack(side="left", fill="both" , expand=True)
        elif entry_type == "date":
            self.entry_dict[entry_name] = DateEntry(master=frame, width= 16 , foreground= "white",bd=2, locale='en_US', date_pattern='yyyy-mm-dd')
            self.entry_dict[entry_name].pack(side="left", fill="both" , expand=True)
        elif entry_type == "seg_btn":
            self.entry_dict[entry_name] = ctk.CTkSegmentedButton(frame, values=list(options))
            self.entry_dict[entry_name].pack(side="left", fill="both" , expand=True)
            self.entry_dict[entry_name].set(options[0])
    ###############        ###############        ###############        ###############
    def get_data(self):
        data = {}
        for entry_name in self.entry_dict:
            data[entry_name] = self.entry_dict[entry_name].get()
        return data
    ###############        ###############        ###############        ###############
    def change_value(self,entry_name,value):
        if isinstance(self.entry_dict[entry_name] , ctk.CTkEntry):
            self.entry_dict[entry_name].delete(0, ctk.END)
            self.entry_dict[entry_name].insert(ctk.END,value)
        elif isinstance(self.entry_dict[entry_name] , (ctk.CTkOptionMenu,ctk.CTkSegmentedButton)):
            self.entry_dict[entry_name].set(value)
        elif isinstance(self.entry_dict[entry_name] , DateEntry):
            self.entry_dict[entry_name].set_date(value) # YYYY-MM-DD format -> 2020-10-19
    ###############        ###############        ###############        ###############
    def change_and_disable(self,entry_name,value):
        self.entry_dict[entry_name].configure(state=ctk.NORMAL)
        self.change_value(entry_name,value)
        self.entry_dict[entry_name].configure(state=ctk.DISABLED)
    ###############        ###############        ###############        ###############
    def disable_all(self):
        for __ , entry in self.entry_dict.items():
            entry.configure(state=ctk.DISABLED)
##############################################################################################################