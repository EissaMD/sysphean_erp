import ttkbootstrap as ttk
from .UI import Page, LeftMenu , EntriesFrame , SearchCustomer
from .Logics import DB
from tksheet import Sheet

class Procurement():
    def __init__(self):
        self.page = Page()
        self.page.create_new_page("- - -")
        left_menu = LeftMenu()
        # Do not have more than 6 menus
        left_menu_ls = {
            "Purchase Requisition"              : PurchaseRequisition,
            "Supplier Management"               : SupplierManagement,
            "Purchase Order"                    : PurchaseOrder,
        }
        left_menu.update_menu(left_menu_ls)
##############################################################################################################
class PurchaseRequisition():
    def __init__(self):
        self.page = Page()
        menu_ls = {
            "Add": self.Add_frame,
            "Edit": self.edit_frame,
            "Delete": self.delete_frame,
        }
        self.page.create_new_page("Purchase Requisition", menu_ls)

    ###############        ###############        ###############        ###############
    def Add_frame(self):
        body_frame = self.page.create_new_body()
        self.page.menu.configure(text="Add")
        entries = (
            ("item_description", "entry", (0, 0, 3), None),
            ("quantity", "entry", (1, 0, 1), None),
            ("unit/packing", "entry", (1, 1, 1), None),
            ("needed_by", "date", (1, 2, 1), None),
            ("balance_(stock)", "entry", (2, 0, 1), None),
            ("last_purchase_date", "date", (2, 1, 1), None),
        )
        self.purchase_entries = EntriesFrame(body_frame, "Purchase Requisition", entries)
        self.purchase_entries.pack()
        entries = (
            ("source_a_(cost_price)", "entry", (0, 0, 1), None),
            ("source_b_(cost_price)", "entry", (0, 1, 1), None),
            ("source_c_(cost_price)", "entry", (0, 2, 1), None),
        )
        self.source_entries = EntriesFrame(body_frame, "Source Entries (For Purchasing Department Only)", entries)
        self.source_entries.pack()
        entries = (
            ("remarks", "entry", (0, 0, 1), None),
        )
        self.remark_entries = EntriesFrame(body_frame, "Remarks", entries)
        
        self.remark_entries.pack()
        self.page.create_footer(self.confirm_btn)

    ###############        ###############        ###############        ###############
    def edit_frame(self):
        self.page.create_new_body()
        self.page.menu.configure(text="Edit")

    ###############        ###############        ###############        ###############
    def delete_frame(self):
        self.page.create_new_body()
        self.page.menu.configure(text="Delete")
    ##############################################################################################################
    def confirm_btn(self):
        # Extract data from EntriesFrame instances
        purchase_data = self.purchase_entries.get_data()
        source_data = self.source_entries.get_data()
        remark_data = self.remark_entries.get_data()

        # Insert data into the database
        db = DB()
        db.connect()

        # Retrieve data
        data = list(purchase_data.values()) + list(source_data.values()) + list(remark_data.values())
        col_name = ("item_description","quantity","unit/packing","needed_by","balance_(stock)","last_purchase_date","source_a_(cost_price)",
                    "source_b_(cost_price)","source_c_(cost_price)","remarks")
        db.insert("purchase_requisition", col_name, data)


    #db.insert("purchase_requisition", ("item_description", "quantity", "credit_limit"), ("john", "john@example.com", "2000"), )
##############################################################################################################
class SupplierManagement():
    def __init__(self):
        self.page = Page()
        menu_ls = {
            "Add": self.Add_frame,
            "Evaluation": self.evaluation_frame,
            "Edit": self.edit_frame,
            "Delete": self.delete_frame,
        }
        self.page.create_new_page("Supplier Management", menu_ls)

    ###############        ###############        ###############        ###############
    def Add_frame(self):
        body_frame = self.page.create_new_body()
        self.page.menu.configure(text="Add")
        entries = (
            ("supplier_name", "entry", (0, 0, 1), None),
            ("address", "entry", (1, 0, 1), None),
            ("e-mail", "entry", (2, 0, 1), None),
            ("phone_no", "entry", (2, 1, 1), None),
        )
        self.contact_info_entries = EntriesFrame(body_frame, "Contact Information", entries)
        self.contact_info_entries.pack()
        entries = (
            ("supplier_ratings/performance", "entry", (0, 0, 1), None),
            ("payment_terms", "entry", (0, 1, 1), None),
            ("lead_time", "entry", (0, 2, 1), None),
        )
        self.supplier_entries = EntriesFrame(body_frame, "Supplier Information", entries)
        self.supplier_entries.pack()
        self.page.create_footer(self.confirm_btn)

    ###############        ###############        ###############        ###############
    def evaluation_frame(self):
        self.page.create_new_body()
        self.page.menu.configure(text="History")

    ###############        ###############        ###############        ###############
    def edit_frame(self):
        self.page.create_new_body()
        self.page.menu.configure(text="Edit")

    ###############        ###############        ###############        ###############
    def delete_frame(self):
        self.page.create_new_body()
        self.page.menu.configure(text="Delete")
    ##############################################################################################################
    def confirm_btn(self):
        # Extract data from EntriesFrame instances
        contact_data = self.contact_info_entries.get_data()
        supplier_data = self.supplier_entries.get_data()

        # Retrieve data
        data = list(contact_data.values()) + list(supplier_data.values())
        col_name = ("supplier_name","address","e-mail","phone_no","supplier_ratings/performance","payment_terms","lead_time")
        self.insert("supplier_management", col_name, data)
##############################################################################################################
class PurchaseOrder():
    def __init__(self):
        self.page = Page()
        menu_ls = {
            "Quotation": self.Quotation_frame,
            "Creation": self.Creation_frame,
            "Completion": self.Completion_frame,
            "Viewing": self.Viewing_frame,
        }
        self.page.create_new_page("Purchase Order", menu_ls)

    ###############        ###############        ###############        ###############
    def Quotation_frame(self):
        body_frame = self.page.create_new_body()
        self.page.menu.configure(text="Quotation")
        entries = (
            ("supplier_name", "entry", (0, 0, 3), None),
            ("quotation_date", "date", (0, 1, 1), None),
            ("quoted_items/services", "entry", (1, 0, 3), None),
            ("quotation_amount", "entry", (2, 0, 1), None),
        )
        self.quotation_entries = EntriesFrame(body_frame, "Quotation Information", entries)
        self.quotation_entries.pack()
        entries = (
            ("validity_period", "entry", (0, 0, 1), None),
            ("terms_and_conditions", "entry", (1, 0, 1), None),
        )
        self.quotation_terms_entries = EntriesFrame(body_frame, "Quotation Terms", entries)
        self.quotation_terms_entries.pack()
        self.page.create_footer(self.confirm_btn_1)

    ###############        ###############        ###############        ###############
    def confirm_btn_1(self):
        # Extract data from EntriesFrame instances
        quotation_data = self.quotation_entries.get_data()
        quotation_terms_data = self.quotation_terms_entries.get_data()

        # Retrieve data
        data = list(quotation_data.values()) + list(quotation_terms_data.values())
        col_name = ("supplier_name","quotation_date","quoted_items/services","quotation_amount","validity_period","terms_and_conditions")
        self.insert("purchase_quotation", col_name, data)
    ###############        ###############        ###############        ###############
    def Creation_frame(self):
        body_frame = self.page.create_new_body()
        self.page.menu.configure(text="Creation")
        entries = (
            ("supplier_name", "entry", (0, 0, 2), None),
            ("order_date", "date", (0, 1, 1), None),
            ("items_ordered", "entry", (1, 0, 1), None),
            ("quantity", "entry", (2, 0, 1), None),
            ("unit_price", "entry", (2, 1, 1), None),
            ("total_amount", "entry", (2, 2, 1), None),
        )
        self.order_entries = EntriesFrame(body_frame, "Order Information", entries)
        self.order_entries.pack()
        entries = (
            ("delivery_date", "date", (0, 0, 1), None),
            ("ship_to_address", "entry", (1, 0, 1), None),
            ("payment_terms", "entry", (2, 0, 1), None),
        )
        self.delivery_terms_entries = EntriesFrame(body_frame, "Delivery Terms", entries)
        self.delivery_terms_entries.pack()
        self.page.create_footer(self.confirm_btn_2)

    ###############        ###############        ###############        ###############
    def confirm_btn_2(self):
        # Extract data from EntriesFrame instances
        order_data = self.order_entries.get_data()
        delivery_terms_data = self.delivery_terms_entries.get_data()

        # Retrieve data
        data = list(order_data.values()) + list(delivery_terms_data.values())
        col_name = ("supplier_name","order_date","items_ordered","quantity","unit_price","total_amount","delivery_date","ship_to_address","payment_terms")
        self.insert("purchase_creation", col_name, data)
    ##############################################################################################################
    def Completion_frame(self):
        body_frame = self.page.create_new_body()
        self.page.menu.configure(text="Completion")
        entries = (
            ("order_reference", "entry", (0, 0, 1), None),
            ("goods_receipt_reference", "entry", (0, 1, 1), None)
        )
        self.reference_entries = EntriesFrame(body_frame, "Reference Information", entries)
        self.reference_entries.pack()
        entries = (
            ("invoice_date", "date", (0, 0, 1), None),
            ("invoice_amount", "entry", (0, 1, 1), None),
            ("payment_due_date", "date", (0, 2, 1), None),
        )
        self.invoice_entries = EntriesFrame(body_frame, "Invoice Information", entries)
        self.invoice_entries.pack()
        self.page.create_footer(self.confirm_btn_3)
    ##############################################################################################################
    def confirm_btn_3(self):
        # Extract data from EntriesFrame instances
        reference_data = self.reference_entries.get_data()
        invoice_data = self.invoice_entries.get_data()

        # Retrieve data
        data = list(reference_data.values()) + list(invoice_data.values())
        col_name = ("order_reference","goods_receipt_reference","invoice_date","invoice_amount","payment_due_date")
        self.insert("purchase_completion", col_name, data)
    ##############################################################################################################
    def Viewing_frame(self):
        body_frame = self.page.create_new_body()
        self.page.menu.configure(text="Viewing")
    ##############################################################################################################