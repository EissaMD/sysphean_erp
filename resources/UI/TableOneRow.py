from config import *
from ..Logics import DB


class TableOneRow(ctk.CTkFrame):
    def __init__(self,master , layout="Default"):
        super().__init__(master=master)
        self.select_layout(layout)
        self.sheet = Sheet(self, show_x_scrollbar=False, show_y_scrollbar=False, height=50,headers=self.layout["headrs"])
        self.sheet.set_column_widths(column_widths=self.layout["col_size"])
        binding = ("single_select", "row_select",
                   "column_width_resize", "double_click_column_resize", "row_width_resize", "column_height_resize",
                   "row_height_resize", "double_click_row_resize")
        self.sheet.enable_bindings(binding)
        self.sheet.pack(fill="x", padx=4, pady=4)
        self.pack(fill="x", padx=4, pady=4)
    ###############        ###############        ###############        ###############
    def update(self,data):
        data = [list(data)]
        self.sheet.set_sheet_data(data,False)
    ###############        ###############        ###############        ###############
    def update_part_info(self,part_no):
        DB.cursor.execute(
            f"SELECT "
            f"pi.bundle_qty, pi.stn_qty, pi.cavity, pi.uom, pi.customer, pi.paper_label, "
            f"IFNULL(mi.total_stock, '0') AS available_quantity "
            f"FROM part_info AS pi "
            f"LEFT JOIN main_inventory AS mi ON pi.part_no = mi.part_no "
            f"WHERE pi.part_no = %s "
            f"GROUP BY "
            f"pi.bundle_qty, pi.stn_qty, pi.cavity, pi.uom, pi.customer, pi.paper_label, available_quantity;",
            (part_no,)
        )
        part_no_ls = DB.cursor.fetchall()
        # Extract paper_label and available_quantity from the first (and only) row
        if part_no_ls:
            paper_label = "Paper" if part_no_ls[0][-2] == 1 else "Sticker"
            available_quantity = part_no_ls[0][-1]
        else:
            paper_label = '0'
            available_quantity = '0'

        # Calculate total_quantity
        total_quantity = []
        for row in part_no_ls:
            if available_quantity == '0':
                total_quantity.append('0')
            else:
                total_stock = int(available_quantity)  # available_quantity as integer
                DB.cursor.execute("SELECT SUM(fulfilled_quantity) FROM delivery_orders WHERE part_no = %s",
                                (part_no,))
                total_do = DB.cursor.fetchone()
                total_do = int(total_do[0]) if total_do[0] is not None else 0  # Handle the case when total_do is None
                total_quantity.append(str(total_stock + total_do))  # Calculate total_quantity

        # Create part_no_records with the total_quantity column appended
        part_no_records = [list(row[:5]) + [paper_label] + [available_quantity] + [total_quantity[i]] for i, row in
                            enumerate(part_no_ls)]
        self.sheet.set_sheet_data(part_no_records , False)
    ###############        ###############        ###############        ###############
    def select_layout(self,selected_layout):
        if selected_layout == "Default":#####
            col_size = 135
            col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size, col_size, col_size]
            self.layout = { "headrs"   :["Bundle Qty", "Stn Carton", "Stn Qty", "UOM", "Cavity", "Customer", "Single Sided", "Label Type"]            ,
                            "col_size" :col_sizes}
        elif selected_layout == "Part Info":#####
            col_size = 130
            col_sizes = [col_size,col_size,col_size*0.8,col_size*0.8,col_size*1.5,col_size,col_size,col_size]
            self.layout = { "headrs"   :["Bundle Qty", "Standard Qty", "Cavity" , "UoM", "customer" , "Label Material", "Available Qty", "Total Quantity"]            ,
                            "col_size" :col_sizes}
##############################################################################################################

if __name__ == "__main__":
    pass