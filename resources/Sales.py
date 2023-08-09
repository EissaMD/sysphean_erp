import ttkbootstrap as ttk
from .LeftMenu import LeftMenu
from .Page import Page
from .EntriesFrame import EntriesFrame
from .InfoTable import InfoTable
from tksheet import Sheet

class Sales():
    def __init__(self):
        self.page = Page()
        self.page.create_new_page("- - -")
        left_menu = LeftMenu()
        left_menu_ls = {
            "Sales Order"           : SaleOrder,
            "Costumer Management"   : self.costumer_management,
            "Tracking sale"         : self.tracking_sale,
            "Sales Report"          : self.sales_report,
        }
        left_menu.update_menu(left_menu_ls)
    ###############        ###############        ###############        ###############
    def costumer_management(self):
            self.page.create_new_page("Costumer Management")
    ###############        ###############        ###############        ###############    
    def tracking_sale(self):
            self.page.create_new_page("Tracking sale")
    ###############        ###############        ###############        ###############
    def sales_report(self):
            self.page.create_new_page("Sales Report")
##############################################################################################################


class SaleOrder():
        def __init__(self):
                self.page = Page()
                menu_ls = {
                        "Add"   : self.Add_frame,
                        "Edit"  : self.edit_frame,
                        "Delete": self.delete_frame,
                }
                self.page.create_new_page("Sale Order", menu_ls)
        ###############        ###############        ###############        ###############
        def Add_frame(self):
                body_frame = self.page.create_new_body()
                self.page.menu.configure(text="Add")
                entries = ( 
                        ("sale_order_id" , "entry",0,0,None),
                        ("date"          , "date",0,1,None),
                        )
                self.basic_entries = EntriesFrame(body_frame,"Basic Info",entries) ; self.basic_entries.pack() 
                entries = ( 
                        ("costumer_name" , "entry",0,0,None),
                        ("city"          , "entry",0,1,None),
                        ("country"       , "entry",1,0,None),
                        ("address"       , "entry",1,1,None),
                        )
                self.costumer_entries = EntriesFrame(body_frame,"Costumer Info",entries) ; self.costumer_entries.pack() 
                # items = InfoTable(body_frame,("Product/Service","SKU","Description","Quantity","Unit Price")) ; items.pack(fill='x')
                # items.add_btn = lambda : AddProduct(items)
                # items.add_remove_btn()
                frame = ttk.Labelframe(body_frame , text="Products") ; frame.pack(fill="x" , padx=4, pady=4)
                self.sheet = Sheet(frame, show_x_scrollbar=False,height=100,
                           headers=["Product/Service", "SKU", "Description", "Quantity", "Unit Price"],
                           data = [["" , "" , "" , "", ""]],
                           )
                col_size =90
                col_size= [col_size*2.5,col_size,col_size*3,col_size,col_size]
                self.sheet.set_column_widths(column_widths = col_size)
                self.sheet.enable_bindings("ctrl_c", "copy" ,"ctrl_x", "cut","ctrl_v","paste" ,"ctrl_z", "undo","delete_key", "delete", "edit_cell", 
                                        "edit_table", "row_index_drag_drop", "move_rows", "rc_delete_row","delete_rows","rc_insert_row", "rc_add_row",
                                        "row_height_resize", "column_width_resize", "cell_select", "select_all", "row_select", "column_select",  "select", 
                                        "drag_select_cells", "drag_select_rows", "shift_cell_select", "shift_row_select","deselect","all_select_events",
                                        "selectevents", "select_events")
                self.sheet.pack(fill="x", padx=4, pady=4)
        ###############        ###############        ###############        ###############
        def edit_frame(self):
                self.page.create_new_body()
                self.page.menu.configure(text="Edit")
        ###############        ###############        ###############        ###############
        def delete_frame(self):
                self.page.create_new_body()
                self.page.menu.configure(text="Delete")       