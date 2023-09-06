import customtkinter as ctk


class InfoTable(ctk.CTkFrame):
    def __init__(self,master,headers=()):
        super().__init__(master,)
        self.data = {} # initialize empty tree
        self.treeview = ctk.Treeview(self, columns=headers, show="headings" , bootstyle="primary" , height=3,)
        self.treeview.pack(fill="both",side="left")
        for header in headers:
            label = header.replace("_", " ")
            label = label.capitalize()
            self.treeview.heading(header, text=label)
        self.add_btn = self.remove_btn = lambda : 0
    ###############        ###############        ###############        ###############
    def add_remove_btn(self):
        frame = ctk.Frame(self) ; frame.pack(side="left",fill="both")
        ctk.CTkButton(frame,text="+" , bootstyle="outline-primary", command=self.add_btn).pack(fill="both")
        ctk.CTkButton(frame,text="-" , bootstyle="outline-primary", command=self.delete_selection).pack(fill="both")
    ###############        ###############        ###############        ###############
    def clear(self):
        self.data = []
        self.treeview.delete(*self.treeview.get_children())
    ###############        ###############        ###############        ###############
    def add_rows(self,rows=None):
        if rows is not None:
            for row in rows:
                self.treeview.insert('', ctk.END, values=row)
                self.data[self.treeview.get_children()[-1]] = row
    ###############        ###############        ###############        ###############
    def add_new_rows(self,rows=None):
        if rows is not None:
            self.data = {}
            self.clear()
            self.add_rows(rows)
    ###############        ###############        ###############        ###############
    def delete_selection(self):
        for sel_item in self.treeview.selection():
            self.treeview.delete(sel_item)
            self.data.pop(sel_item)