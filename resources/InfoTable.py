import ttkbootstrap as ttk


class InfoTable(ttk.Frame):
    def __init__(self,master,headers=()):
        super().__init__(master,)
        self.data = {} # initialize empty tree
        self.treeview = ttk.Treeview(self, columns=headers, show="headings" , bootstyle="primary" , height=3,)
        self.treeview.pack(fill="both",expand=True,side="left")
        for header in headers:
            label = header.replace("_", " ")
            label = label.capitalize()
            self.treeview.heading(header, text=label)
    ###############        ###############        ###############        ###############
    def add_remove_btn(self):
        frame = ttk.Frame(self) ; frame.pack(side="left",fill="both")
        self.add_btn = self.remove_btn = lambda : 0
        ttk.Button(frame,text="+" , bootstyle="outline-primary", command=self.add_btn).pack(fill="both")
        ttk.Button(frame,text="-" , bootstyle="outline-primary", command=self.remove_btn).pack(fill="both")
    ###############        ###############        ###############        ###############
    def clear(self):
        self.data = []
        self.treeview.delete(*self.treeview.get_children())
    ###############        ###############        ###############        ###############
    def add_rows(self,rows=None):
        if rows is not None:
            for row in rows:
                self.treeview.insert('', ttk.END, values=row)
                self.data[self.treeview.get_children()[-1]] = row
    ###############        ###############        ###############        ###############
    def add_new_rows(self,rows=None):
        if rows is not None:
            self.data = {}
            self.clear()
            self.add_rows(rows)
    ###############        ###############        ###############        ###############
    def delete_selection(self):
        for sel_item in self.selection():
            self.treeview.delete(sel_item)
            self.data.pop(sel_item)