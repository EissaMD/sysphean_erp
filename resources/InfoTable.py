import ttkbootstrap as ttk


class InfoTable(ttk.Treeview):
    def __init__(self,master,headers=()):
        self.data = {} # initialize empty tree
        super().__init__(master, columns=headers, show="headings" , bootstyle="primary" , height=3,)
        for header in headers:
            label = header.replace("_", " ")
            label = label.capitalize()
            self.heading(header, text=label)
    ###############        ###############        ###############        ###############
    def clear(self):
        self.data = []
        self.delete(*self.get_children())
    ###############        ###############        ###############        ###############
    def add_rows(self,rows=None):
        if rows is not None:
            for row in rows:
                self.insert('', ttk.END, values=row)
                self.data[self.get_children()[-1]] = row
    ###############        ###############        ###############        ###############
    def add_new_rows(self,rows=None):
        if rows is not None:
            self.data = {}
            self.clear()
            self.add_rows(rows)
    ###############        ###############        ###############        ###############
    def delete_selection(self):
        for sel_item in self.selection():
            self.delete(sel_item)
            self.data.pop(sel_item)