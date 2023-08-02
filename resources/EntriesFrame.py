import ttkbootstrap as ttk

class EntriesFrame(ttk.Labelframe):
    """Create a new Frame with multiple entries in grid format
    Args:
        master (tk): parent frame or window
        title (str): small text on the top left of the frame
        entry_ls (tuple or list): (entry_name , entry_type , row , col , options). Defaults to ().
    """
    def __init__(self,master,title,entry_ls=()):
        self.entry_dict = {}
        super().__init__(master,text= title,  height=100)
        self.pack(fill="both" , pady =10, padx=2)
        self.entries_frame = ttk.Frame(self); self.entries_frame.pack(fill="both",expand=True,padx=4,pady=4)
        for entry in entry_ls:
            self.add_entry(entry)
    ###############        ###############        ###############        ###############
    def add_entry(self,entry_info):
        entry_name , entry_type , row , col , options=entry_info
        label = entry_name.replace('_',' ').title() + " :"
        self.entries_frame.grid_columnconfigure(col,weight=1)
        frame = ttk.Frame(self.entries_frame)
        frame.grid(sticky="we",row=row,column=col,padx=10)
        ttk.Label(frame , text=f"{label:<10}" , font="arial 10 bold",width=20).pack(side="left" ,anchor="w")
        # entry type
        if entry_type == "entry":
            self.entry_dict[entry_name] = ttk.Entry(frame )
            self.entry_dict[entry_name].pack(side="left", fill="both" , expand=True)
        elif entry_type == "menu":
            self.entry_dict[entry_name] = ttk.StringVar()
            option_menu = ttk.OptionMenu(frame ,self.entry_dict[entry_name] ,options[0], *options , bootstyle="outline")
            option_menu.pack(side="left", fill="both" , expand=True)
            option_menu.config(width=19)
        elif entry_type == "spinbox":
            self.entry_dict[entry_name] = ttk.Spinbox(frame , from_=options[0] , to=options[1])
            self.entry_dict[entry_name].pack(side="left", fill="both" , expand=True)
        elif entry_type == "date":
            DateEntry = ttk.DateEntry(master=frame , dateformat="%d-%m-%Y")
            DateEntry.pack(side="left", fill="both" , expand=True)
            self.entry_dict[entry_name] = DateEntry.entry
    ###############        ###############        ###############        ###############
    def get_data(self):
        data = {}
        for entry_name in self.entry_dict:
            data[entry_name] = self.entry_dict[entry_name].get()
        return data
##############################################################################################################