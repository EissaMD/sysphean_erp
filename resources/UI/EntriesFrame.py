from config import *

class EntriesFrame(ctk.CTkFrame):
    """Create a new Frame with multiple entries in grid format
    Args:
        master (tk): parent frame or window
        title (str): small text on the top left of the frame
        entry_ls (tuple or list): (entry_name , entry_type , row , col , options). Defaults to ().
    """
    def __init__(self,master,entry_ls=(),pack=True):
        self.entry_dict = {}
        self.checkbox_dict = {}
        self.max_row = self.max_col=0
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
        self.max_row = row if row > self.max_row else self.max_row
        self.max_col = col if col > self.max_col else self.max_col
        label = entry_name.replace('_',' ').title() + " :"
        label = label.replace('Id','ID')
        self.entries_frame.grid_columnconfigure(col,weight=1)
        frame = ctk.CTkFrame(self.entries_frame,fg_color="transparent")
        frame.grid(sticky="we",row=row,column=col,columnspan=col_span,padx=10)
        # label or checkbox
        state = tk.NORMAL
        delete_disable = lambda : self.checkbox_func(entry_name)
        if "_checkbox1" in entry_name:
            entry_name = entry_name.replace("_checkbox1", "")
            label = label.replace("_checkbox1", "")
            self.checkbox_dict[entry_name] = ctk.CTkCheckBox(frame , text=f"{label:<25}" , font=("arial",11), width=130 , command=delete_disable)
            self.checkbox_dict[entry_name].pack(side="left" ,anchor=ctk.W , padx=10)
            self.checkbox_dict[entry_name].select()
        elif "_checkbox0" in entry_name:
            state= tk.DISABLED
            entry_name = entry_name.replace("_checkbox0", "")
            label = label.replace(" Checkbox0", "")
            self.checkbox_dict[entry_name] = ctk.CTkCheckBox(frame , text=f"{label:<25}" , font=("arial",11), width=130 , command=delete_disable)
            self.checkbox_dict[entry_name].pack(side="left" ,anchor=ctk.W , padx=10)
        else:
            ctk.CTkLabel(frame , text=f"{label:<25}" , font=("arial",11), width=130).pack(side="left" ,anchor=ctk.W , padx=10)
        # entry type
        if entry_type == "entry":
            self.entry_dict[entry_name] = ctk.CTkEntry(frame , corner_radius=0 , state=state)
            self.entry_dict[entry_name].pack(side="left", fill="both" , expand=True)
        elif entry_type == "menu":
            self.entry_dict[entry_name] = ctk.CTkOptionMenu(frame, values=list(options) , fg_color="#565e58",button_color="#565e58",button_hover_color="#3c423e" , corner_radius=0 , state=state)
            self.entry_dict[entry_name].pack(side="left", fill="both" , expand=True)
        elif entry_type == "date":
            self.entry_dict[entry_name] = DateEntry(master=frame, width= 16 , foreground= "white",bd=2, locale='en_US', date_pattern='yyyy-mm-dd', state=state)
            self.entry_dict[entry_name].pack(side="left", fill="both" , expand=True)
        elif entry_type == "seg_btn":
            self.entry_dict[entry_name] = ctk.CTkSegmentedButton(frame, values=list(options), state=state)
            self.entry_dict[entry_name].pack(side="left", fill="both" , expand=True)
            self.entry_dict[entry_name].set(options[0])
        self.frames[entry_name]= frame # save the frame in dictionary
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
            if value:
                self.entry_dict[entry_name].set_date(value) # YYYY-MM-DD format -> 2020-10-19
            else:
                self.entry_dict[entry_name].delete(0, ctk.END) 
    ###############        ###############        ###############        ###############
    def change_and_disable(self,entry_name,value):
        self.entry_dict[entry_name].configure(state=ctk.NORMAL)
        self.change_value(entry_name,value)
        self.entry_dict[entry_name].configure(state=ctk.DISABLED)
    ###############        ###############        ###############        ###############
    def checkbox_func(self,entry_name):
        checkbox = self.checkbox_dict[entry_name].get()
        if checkbox == 0:
            self.entry_dict[entry_name].configure(state=ctk.NORMAL)
            self.change_and_disable(entry_name,"")
            self.entry_dict[entry_name].configure(state=ctk.DISABLED)
        else:
            self.entry_dict[entry_name].configure(state=ctk.NORMAL)
            if isinstance(self.entry_dict[entry_name] , ctk.CTkOptionMenu):
                first_value = self.entry_dict[entry_name]._values[0]
                self.entry_dict[entry_name].set(first_value)
            elif isinstance(self.entry_dict[entry_name] , ctk.CTkSegmentedButton):
                first_value = self.entry_dict[entry_name]._value_list[0]
                self.entry_dict[entry_name].set(first_value)
            elif isinstance(self.entry_dict[entry_name] , DateEntry):
                self.entry_dict[entry_name].set_date(datetime.now())
    ###############        ###############        ###############        ###############
    def disable_all(self):
        for __ , entry in self.entry_dict.items():
            entry.configure(state=ctk.DISABLED)
##############################################################################################################