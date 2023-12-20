from config import *
from ..UI import Page, EntriesFrame, SearchWindow , ViewFrame , SectionTitle , TableOneRow , DisplayTable
from ..Logics import DB ,validate_entry , update_log_table , update_main_inventory
from ..LoginSystem import LoginSystem

class BatchEntry(Page):
    def __init__(self):
        menu_ls = {
            "New Batch": self.new_batch_frame,
            "Extra Labels": self.extra_labels_frame,
            "Batch Rejection": self.Reject_frame,
            "View": self.view_frame,
        }
        # Initialize a variable to track whether a popup is currently open
        self.popup_open = False
        self.selected_row = None  # To keep track of the selected row
        self.create_new_page("Batch Entry", menu_ls)

    ###############        ###############        ###############        ###############
    def new_batch_frame(self):
        self.function = "new_batch"
        body_frame = self.create_new_body()
        SectionTitle(body_frame,"Enter New Batch:")
        part_no_entry = (
            ("part_no", "entry", (0, 0, 1), None),
        )
        self.part_no_entries = EntriesFrame(body_frame, part_no_entry)
        self.part_no_entries.pack()
        self.part_no_entries.disable_all()
        # add search btn for part no name
        frame = self.part_no_entries.frames["part_no"]
        self.search_part_no = SearchWindow(select_btn=self.select_part_no, layout="Search Part No")
        ctk.CTkButton(frame, image="search_icon", text="", command=self.search_part_no.new_window, width=20).pack(
            side="left")
        entries = (
            ("quantity" , "entry"   , (1, 0, 1), None),
            ("date_code", "entry"   , (2, 0, 1), None),
            ("remarks"  , "entry"   , (3, 0, 1), None),
        )
        self.manufacturing_entries = EntriesFrame(body_frame, entries)
        self.manufacturing_entries.pack()
        date_entries = (
            ("expiry_date_checkbox0"        , "date", (1, 0, 1), None),
            ("manufacturing_date_checkbox0" , "date", (2, 0, 1), None),
            ("packing_date_checkbox0"       , "date", (3, 0, 1), None),
        )
        self.date_entries = EntriesFrame(body_frame, date_entries)
        self.date_entries.pack()
        correctional_entries = (
            ("correctional_entry", "seg_btn", (1, 0, 1), ["No", "Yes"]),
        )
        self.correctional_entries = EntriesFrame(body_frame, correctional_entries)
        self.correctional_entries.pack()
        SectionTitle(body_frame,"Part Information:")
        self.part_no_select_sheet = TableOneRow(body_frame,"Part Info")
        ####### Last entered batches
        SectionTitle(body_frame,"Recent batches:")
        self.batch_entry_view_sheet = Sheet(body_frame, show_x_scrollbar=False, height=100,
                                        headers=["Part No", "Quantity", "Date Code", "Remarks", "Additional Info", "Time Added"])
        col_size = 175
        col_sizes = [col_size, col_size, col_size, col_size, col_size, col_size]
        self.batch_entry_view_sheet.set_column_widths(column_widths=col_sizes)
        binding = ("single_select", "row_select","column_width_resize", "double_click_column_resize", "row_width_resize", 
                   "column_height_resize","row_height_resize", "double_click_row_resize")
        self.batch_entry_view_sheet.enable_bindings(binding)
        self.batch_entry_view_sheet.pack(fill="both",expand=True)

        batch_entry_data = DB.select("entry_tracker", ("part_no", "quantity", "date_code", "remarks", "additional_info", "time"), "1=1 ORDER BY id DESC LIMIT 20")
        for row_data in batch_entry_data:
            self.batch_entry_view_sheet.insert_row(values=row_data)
        self.create_footer(self.new_batch_btn)
    ###############        ###############        ###############        ###############
    def select_part_no(self):
        selected_row = self.search_part_no.selected_row
        if not selected_row:
            return
        self.search_part_no.close()
        entry_names = ("part_no",)
        values = (selected_row[1],)
        for entry_name, value in zip(entry_names, values):
            self.part_no_entries.change_and_disable(entry_name, value)
        if self.function == "new_batch":
            self.part_no_select_sheet.update_part_info(selected_row[1])
            return
        if not hasattr(self, 'batch_rejection') and hasattr(self, 'part_no_select_sheet'):
            # Remove existing data from the table
            total_rows = self.part_no_select_sheet.get_total_rows()
            for a in range(total_rows - 1, -1, -1):
                self.part_no_select_sheet.delete_row(a)
            data = DB.select("part_info", ("bundle_qty", "stn_carton", "stn_qty", "uom", "cavity", "customer", "single_sided",
                       "paper_label"), "part_no = %s", (selected_row[1],))
            self.part_no_select_sheet.insert_row(values=data[0])
        if self.popup_open and self.function == "Add":
            rejection_data = DB.select("batch_rejection", ("id", "reason", "time_added"), "part_no = %s", (selected_row[1],))
            if rejection_data:
                rework_options = [f'{id} ({reason}) ({time_added})' for id, reason, time_added in rejection_data]
                self.update_rework_entries(rework_options)
    ###############        ###############        ###############        ###############
    def new_batch_btn(self):
        # Extract data from EntriesFrame instances
        data = {}
        for entries in (self.part_no_entries,self.manufacturing_entries,self.date_entries,self.correctional_entries):
            data.update(entries.get_data())
        # Checker 1: Validate entries
        failed_ls =validate_entry(data,popup_msg=True)
        if len(failed_ls) >0:
            return
        # Checker 2: If there are similar batches
        sbm =SimilarBatchWindow(data)
        if sbm._continue is False:
            return
        # Special Conditions
        terms = {
            "expiry_date"       :"EXP",
            "manufacturing_date":"MFG",
            "packing_date"      :"PKD",
        }
        conditions_ls = []
        for key,value in data.items():
            if key in ("expiry_date" , "manufacturing_date" , "packing_date") and value != "":
                conditions_ls.append(terms[key]+"="+value)
        conditions = ",".join(conditions_ls)
        qr_code = data["part_no"] + "|" + data["quantity"] + "|" + data["date_code"] + "|" + data["remarks"] + "|" + conditions
        ret0 =inpro(qr_code) 
        if ret0 is True:
            self.new_batch_frame()
    ###############        ###############        ###############        ###############
    def extra_labels_frame(self):
        body_frame = self.create_new_body()
        SectionTitle(body_frame,"Extra Labels:")
        part_no_entry = (
            ("part_no", "entry", (0, 0, 1), None),
        )
        self.part_no_entries = EntriesFrame(body_frame, part_no_entry); self.part_no_entries.pack()
        self.part_no_entries.disable_all()
        # add search btn for part no name
        frame = self.part_no_entries.frames["part_no"]
        self.search_part_no = SearchWindow(select_btn=self.select_part_no, layout="Search Part No")
        ctk.CTkButton(frame, image="search_icon", text="", command=self.search_part_no.new_window, width=20).pack(
            side="left")
        entries = (
            ("quantity", "entry", (1, 0, 1), None),
            ("date_code", "entry", (2, 0, 1), None),
            ("remarks", "entry", (3, 0, 1), None),
        )
        self.manufacturing_entries = EntriesFrame(body_frame, entries) ; self.manufacturing_entries.pack()
        date_entries = (
            ("expiry_date_checkbox0", "date", (1, 0, 1), None),
            ("manufacturing_date_checkbox0", "date", (2, 0, 1), None),
            ("packing_date_checkbox0", "date", (3, 0, 1), None),
        )
        self.date_entries = EntriesFrame(body_frame, date_entries);
        self.date_entries.pack()
        label_type_entries = (
            ("label_type", "seg_btn", (1, 0, 1), ["Sealed", "Carton","Single Carton"]),
        )
        self.label_type_entries = EntriesFrame(body_frame, label_type_entries);
        self.label_type_entries.pack()
        # display part info
        SectionTitle(body_frame,"Part Information:")
        self.part_no_select_sheet = TableOneRow(body_frame,"Part Info")
        self.create_footer(self.extra_labels_btn,"Generate Labels")
    ###############        ###############        ###############        ###############
    def extra_labels_btn(self):
        # Extract data from EntriesFrame instances
        data = {}
        for entries in (self.part_no_entries,self.manufacturing_entries,self.date_entries,self.label_type_entries):
            data.update(entries.get_data())
        # Checker 1: Validate entries
        failed_ls =validate_entry(data,popup_msg=True)
        if len(failed_ls) >0:
            return
        # Special Conditions
        terms = {
            "expiry_date"       :"EXP",
            "manufacturing_date":"MFG",
            "packing_date"      :"PKD",
        }
        conditions_ls = []
        for key,value in data.items():
            if key in ("expiry_date" , "manufacturing_date" , "packing_date") and value != "":
                conditions_ls.append(terms[key]+"="+value)
        conditions = ",".join(conditions_ls)
        sm = SealedManager(data["part_no"]) # for processing sealed records
        if data["label_type"] == "Sealed":# ------------------------------Sealed Labels------------------------#
            part_info = sm.get_partinfo(bundle_qty=True)
            if part_info is None:
                return
            # check if the program is going to produce more than 99 sealed labels
            sealed_label_no = int(data["quantity"])//sm.part_info["raw_data"][0]  # Batch quantity / bundle quantity
            if sealed_label_no>99:
                ans=messagebox.askyesno("Warning",f"This entry has huge quantity and is going to create {sealed_label_no} sealed labels , do you want to continue?", icon='warning')
                if ans is False:
                    return
            sm.add_new_batch(data["quantity"],data["date_code"],data["remarks"],conditions)
            sm.new_batch_labels() # create sealed labels dictionary
            total_labels = "(" + sm.SL[0]["quantity"] + ") x "+ str(sm.total_SL) 
            if sm.total_SL >1 and sm.SL[0]["quantity"] != sm.SL[-1]["quantity"]:
                total_labels = "(" + sm.SL[0]["quantity"] +") x "+ str(sm.total_SL-1)+ " + (" + sm.SL[-1]["quantity"] +") x 1"
            ans=messagebox.askyesno("Info",f"Total Labels= {total_labels}\n\nDo you want to continue? This will not be included in the main inventory!", icon='info')
            if ans is False:
                return
            sm.to_csv()
            description =  "(" +  ', '.join(map(str, data.values())) + ')'
            update_log_table("Manufacturing","Create sealed label", new_description=description)
            logger.info("Created: sealed labels "+description)
            DB.cursor.execute("INSERT INTO extra_labels (part_no, quantity, date_code, remarks ,additional_info ,label_quantity ,label_type ,time_added, user_name) VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),%s);" ,
                                (data["part_no"],data["quantity"],data["date_code"],data["remarks"],conditions, sm.total_SL,"Sealed",LoginSystem.user_name))
            DB.conn.commit()
            messagebox.showinfo("Process info", f"{sm.total_SL} sealed labels created!")
            self.extra_labels_frame()
            return
        # ------------------------------Carton Labels------------------------#
        part_info = sm.get_partinfo(bundle_qty=True, stn_qty=True, stn_carton=True, uom_cavity=True)
        if part_info is None:
            return
        bundle_qty , stn_qty , uom , cavity = part_info["bundle_qty"] , part_info["stn_qty"] , part_info["uom"] , part_info["cavity"]
        customer =   sm.part_info["customer"]
        # if expiry date is exist then add it to remarks
        remarks = data["remarks"]
        if data["expiry_date"]:
            remarks += " ,"+data["expiry_date"] # add expiry date to carton remarks
        cm = CartonManager(data["part_no"],uom,cavity) # to deal with carton records
        # If single carton quantity
        if data["label_type"] == "Single Carton" :
            cm.add_carton_label(customer,data["part_no"],int(data["quantity"]),data["date_code"],remarks,1,sm.part_info["stn_carton"],0,1)
        else:
            # create carton labels before allocation
            batch_quantity = int(data["quantity"])
            if uom.upper() == "PCS" and cavity >1:
                batch_quantity = batch_quantity * cavity
            carton_label_no = batch_quantity//stn_qty  # Batch quantity / standard carton quantity
            loose_carton = batch_quantity%stn_qty 
            last_counter = carton_label_no+1 if loose_carton else carton_label_no
            cm.add_carton_label(customer,data["part_no"],stn_qty,data["date_code"],remarks,carton_label_no,sm.part_info["stn_carton"],0,last_counter)
            cm.add_carton_label(customer,data["part_no"],loose_carton,data["date_code"],remarks,1,sm.part_info["stn_carton"],carton_label_no,last_counter)
        ans=messagebox.askyesno("Info",f"Total Carton Labels= {cm.total_CL}\n\nDo you want to continue? This will not be included in the main inventory!", icon='info')
        if ans is False:
            return
        if cm.total_CL: 
            cm.to_csv()# create carton labels
            description =  "(" +  ', '.join(map(str, data.values())) + ')'
            update_log_table("Manufacturing","Create carton label", new_description=description)
            logger.info("Created: carton labels")
            DB.cursor.execute("INSERT INTO extra_labels (part_no, quantity, date_code, remarks ,additional_info ,label_quantity ,label_type ,time_added, user_name) VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),%s);" ,
                                (data["part_no"],data["quantity"],data["date_code"],data["remarks"],conditions , cm.total_CL,"Carton",LoginSystem.user_name))
            DB.conn.commit()
        messagebox.showinfo("Process info", f"{cm.total_CL} carton labels created!")
        self.extra_labels_frame()
    ##############################################################################################################
    def Reject_frame(self):
        body_frame = self.create_new_body()
        SectionTitle(body_frame,"Enter Rejection Parts:")
        part_no_entry = (
            ("part_no", "entry", (0, 0, 1), None),
        )
        self.part_no_entries = EntriesFrame(body_frame, part_no_entry); self.part_no_entries.pack()
        self.part_no_entries.disable_all()
        # add search btn for part no name
        frame = self.part_no_entries.frames["part_no"]
        self.search_part_no = SearchWindow(select_btn=self.select_part_no, layout="Search Part No")
        ctk.CTkButton(frame, image="search_icon", text="", command=self.search_part_no.new_window, width=20).pack(
            side="left")
        entries = (
            ("traveller_no", "entry", (1, 0, 1), None),
            ("quantity", "entry", (2, 0, 1), None),
            ("uom", "menu", (3, 0, 1), ("PCS", "PANEL")),
            ("reason", "menu", (4, 0, 1), ( 'BL INCOMPRINT - IN55'     , 'BL MISSING - M17'        , 'BL OVERLAP - OP04'       , 'BL PEELING - P38'    , 'BL REVERSE - R10'        ,
                                            'BL SHIFTED - S11'         , 'BL SMEARING - SM18'      , 'BL UNCLEAR - UC58'       , 'BROKEN - BR02'       , 'BURN - BN35'             ,
                                            'CARBON INCOMPRINT - CIN49', 'CARBON JAGGED - CJ33'    , 'CARBON SHIFTED - CS26'   , 'CARBON SKIP - CSP50' , 'CARBON SMEARING - CSM48' ,
                                            'DIRTY - DY25'             , 'FL INCOMPRINT - IN56'    , 'FL MISSING - M30'        , 'FL OVERLAP - OP36'   , 'FL PEELING - P39'        ,
                                            'FL REVERSE - R31'         , 'FL SHIFTED - S37'        , 'FL SMEARING - SM16'      , 'FL UNCLEAR - UC59'   , 'INK HOLE - IH60'         ,
                                            'LPSM INCOMPRINT - LP19'   , 'LPSM OVERLAP - LP45'     , 'LPSM OXIDISE - LP44'     , 'LPSM SHIFTED - LP06' , 'LPSM SMEARING - LP08'    ,
                                            'LPSM UNEVEN - LP27'       , 'NICK - NK28'             , 'OPEN - OP40'             , 'OVER - OE23'         , 'OVERLAP - EOP51'         ,
                                            'OXIDISE FLUX - OXF29'     , 'PIN MARK - PM53'         , 'POOR PLATING - PT24'     , 'PTH OPEN - OP61'     , 'PUNCH C-PAD - CP12'      ,
                                            'PUNCH CRACK - CK07'       , 'PUNCH DENTED - DT03'     , 'PUNCH EXTRA - EXN47'     , 'PUNCH REVERSE - PR13', 'PUNCH SHIFTED - PS41'    ,
                                            'SCRATCHES - SC01'         , 'SHORT - SR52'            , 'SM INCOMPRINT - IN22'    , 'SM OVERLAP - OP15'   , 'SM OXIDISE - OX05'       ,
                                            'SM PEELING - P32'         , 'SM SHIFTED - S20'        , 'SM SMEARING - SM21'      , 'SM UNEVEN - UN27'    , 'STAIN - ST34'            ,
                                            'UNDER - OE09'             , 'UNDERSIZE - US54'        , 'VCUT MISSING - VM43'     , 'VCUT SHIFTED - VS14' , 'VCUT SLANTING - VSL57'   ,
                                            'VCUT UNEVEN - VUN42')),
            ("date", "date", (5, 0, 1), None),
        )
        self.rejection_entries = EntriesFrame(body_frame, entries) ; self.rejection_entries.pack()
        # Display last Rejection
        SectionTitle(body_frame,"Last Rejection Parts:")
        self.last_rej_sheet = DisplayTable(body_frame,"Batch Rejection")
        columns = ("part_no", "traveller_no", "quantity", "uom", "reason", "date", "time_added")
        data = DB.select("batch_rejection", columns, "1=1 ORDER BY id DESC LIMIT 50" )
        self.last_rej_sheet.update(data)
        # confirm button
        self.create_footer(self.reject_btn)
    ###############        ###############        ###############        ###############
    def reject_btn(self):
        # Extract data from EntriesFrame instances
        data = {}
        for entries in (self.part_no_entries,self.rejection_entries):
            data.update(entries.get_data())
        # Checker 1: Validate entries
        failed_ls =validate_entry(data,popup_msg=True)
        if len(failed_ls) >0:
            return
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = (data["part_no"] , data["traveller_no"], data["quantity"], data["uom"], data["reason"], data["date"], current_datetime)
        col_name = ("part_no", "traveller_no", "quantity", "uom", "reason", "date", "time_added")
        successful = DB.insert("batch_rejection", col_name, data)
        if not successful:
            return
        messagebox.showinfo("Info", "The process was successful!")
        # Update last Rejection table
        columns = ("part_no", "traveller_no", "quantity", "uom", "reason", "date", "time_added")
        data = DB.select("batch_rejection", columns, "1=1 ORDER BY id DESC LIMIT 50" )
        self.last_rej_sheet.update(data)
        self.Reject_frame()
    ###############        ###############        ###############        ###############
    def view_frame(self):
        body_frame = self.create_new_body()
        ViewFrame(body_frame,["Batch Entry","Extra Labels" , "Reject Batch"])
##############################################################################################################
           
class SimilarBatchWindow(ctk.CTkToplevel):
    def __init__(self,data):
        self._continue = False
        # Checker : If there is similar batch..
        columns = ("Id", "part_no", "quantity" ,"date_code" ,"remarks" ,"additional_info" ,"user_name" ,"time")
        sealed_records = DB.select("entry_tracker",columns,"part_no = %s AND date_code=%s ORDER BY id DESC",(data["part_no"],data["date_code"]))
        if len(sealed_records) == 0:
            self._continue = True
            return
        super().__init__()
        self.title("Similar Batch")
        self.geometry("900x290")
        # Title
        ctk.CTkLabel(master=self,text="Warning: There is similar batch in database, do you want to enter this batch anyway?"
                               ).pack( pady=10, anchor="w", padx=10 )
        # table frame
        self.sheet = Sheet(self, height=200,
                           headers=["ID", "Part No", "quantity", "Date Code", "Remarks", "Additional Info","User Name" ,"Time" ],
                           data =sealed_records)
        self.sheet.enable_bindings("single_select","drag_select","select_all","column_select","row_select","column_width_resize","double_click_column_resize","arrowkeys","row_height_resize","double_click_row_resize")
        self.sheet.pack(padx=5,pady=2,expand=True,fill="x")
        col_size =100
        col_size= [col_size*0.5,col_size*2.5,col_size*0.5,col_size*0.65,col_size*1,col_size*1,col_size*1,col_size*1.2]
        self.sheet.set_column_widths(column_widths = col_size)
        frame = ctk.CTkFrame(self,fg_color="transparent")
        frame.pack(pady=2,)
        ctk.CTkButton(frame, text="Continue ?",command=self.continue_btn , width=50).pack(side="left" , padx=10 ,pady=2)
        ctk.CTkButton(frame, text="Go back",command=self.go_back_btn, width=50).pack(side="left" , padx=10)
        self.deiconify()
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)
    ###############        ###############        ###############        ###############
    def continue_btn(self):
        self._continue = True
        self.destroy()
    ###############        ###############        ###############        ###############
    def go_back_btn(self):
        self._continue = False
        self.destroy()
##############################################################################################################
        
class SealedManager():
    """Deal with sealed quantity: add new batch, get existing records,pack into cartons ...
    """
    def __init__(self,part_no=""):
        self.sealed_records = [] # list of sealed records
        self.SL = [] # sealed labels
        self.SL_additional_info = []
        self.total_SL = 0 # No. of sealed labels
        self.new_batch = {} # new batch details part_no,quantity,date_code,remarks    (after checking similar records)
        self.new_entry = {} # batch info without process (raw)
        self.part_no = part_no
        self.cartonsInfo = []  # list of carton info carton_no, quantity
        self.part_info = {} 
        self.allocated_cartons = {}
        self.init_allocated_cartons()
    ###############        ###############        ###############        ###############
    def get_sealed_records(self):
        """copy all sealed records from sealed_inventory for a single part number to self.sealed_records so it can be
           processed later.
        """
        part_no = self.part_no
        # get sealed record from sealed_inventory
        DB.cursor.execute("SELECT id ,part_no, quantity, date_code, remarks , additional_info from sealed_inventory WHERE part_no=%s ;" , (part_no,)  )
        sealed_records = DB.cursor.fetchall()
        if not sealed_records:
            logging.info("The part_no '{}' has No records in sealed inventory...".format(part_no))
            return 
        # create a list of dictionaries
        ls = []
        for record in sealed_records:
            if int(record[2])>0:
                record = list(record)
                record[4] = self.remove_none(record[4])
                record[4] = re.sub(r"(CAV)\s*=?:?\s*(\d+)", r"\1\2", record[4])# remove space between "CAV" and number
                record[4] = re.sub(r"NO\s*=?:?\s*(\d+)", r"CAV\1", record[4])# change "NO" to "CAV"
                sealed_dict = {
                    "id":record[0],
                    "part_no":record[1],
                    "quantity":int(record[2]),
                    "date_code":str(record[3]),
                    "remarks":record[4],
                    "additional_info":record[5],
                    "state":"stored batch", }
                ls.append(sealed_dict)
        # Overwrite self.sealed_records
        logger.info("sealed records: " + str(ls))
        self.sealed_records = ls
        self.sort_sealed_records()
        return True
    ###############        ###############        ###############        ###############
    def add_new_batch(self,quantity=0,date_code="",remarks="" , additional_info=""):
        """Add new batch manually to self.sealed_records
        Args:
            quantity (int): Number of part in the batch. Defaults to 0.
            date_code (str): Date code of the new batch Defaults to "".
            remarks (str, optional): Remarks of the batch Defaults to "".
        """
        self.new_entry = {
                "part_no":self.part_no,
                "quantity":int(quantity),
                "date_code":date_code,
                "remarks":remarks, 
                "additional_info":additional_info}
        # check if bundle_qty is available
        part_info = self.get_partinfo(bundle_qty=True,uom_cavity=True)
        if part_info["uom"].upper() == "PCS" and part_info["cavity"] > 1:
            quantity = int(quantity) * part_info["cavity"]
        self.new_entry["quantity"] = quantity # 
        remarks = re.sub(r"(CAV)\s*=?:?\s*(\d+)", r"\1\2", remarks)# remove space between "CAV" and number
        remarks = re.sub(r"NO\s*=?:?\s*(\d+)", r"CAV\1", remarks)# change "NO" to "CAV"
        match = re.search(r"EXP=(\d+-\d+-\d+)",additional_info) # add expiry date to remarks so it can be shown in carton labels
        if match is not None:
            remarks+= " , EXP="+ match.group(1)
        new_batch = {
                "id":None,
                "part_no":self.part_no,
                "quantity":int(quantity),
                "date_code":date_code,
                "remarks":remarks, 
                "additional_info":additional_info,  
                "state":"new batch", }
        logger.info("New batch: " + str(self.new_entry))
        # check if there is similar recrod in sealed inventory
        exist_record = False
        for record in self.sealed_records:
            if new_batch["date_code"] == record["date_code"] and new_batch["remarks"] == record["remarks"] and new_batch["additional_info"] == record["additional_info"]: # if there is similar record
                logger.info("An existing record in the Database with similar information has been found")
                record["quantity"] += new_batch["quantity"] #add quantity
                record["state"] = "mix"# mix stored with new batch
                record["new_batch"] = new_batch["quantity"] 
                self.new_batch = new_batch.copy()
                exist_record = True
                break
        if not exist_record:# if there is no record in sealed_inventory then add as new record.
            logger.info("No similar records were found in the sealed_inventory.")
            self.sealed_records.append(new_batch)
            self.new_batch = new_batch.copy()
        self.sort_sealed_records()
    ###############        ###############        ###############        ###############
    def sort_sealed_records(self):
        """sort sealed records by date_code 
        """
        sealed_records = self.sealed_records
        if sealed_records:
            # First: sort by quantity in descending order. (better to use greater quantity first if two records has
            # the same date_code but different remarks)
            sealed_records=sorted(sealed_records, key = lambda i: i['quantity'] , reverse=True)
            # convert data type from string to datetime object
            for record in sealed_records:
                if len(record['date_code'])==4:
                    yy= record['date_code'][-2:]
                    ww= record['date_code'][:2]
                    record['date_code_sort'] = datetime.strptime(f"{yy}-{ww}-1", r"%y-%W-%w").date()
                elif len(record['date_code'])==6:
                    yy= record['date_code'][-2:]
                    mm= record['date_code'][2:4]
                    dd = record['date_code'][:2]
                    record['date_code_sort']= datetime.strptime(f"{yy}-{mm}-{dd}", r"%y-%m-%d").date()
                else:
                    record['date_code_sort']= datetime.now().date()
            # sort by date 
            sealed_records = sorted(sealed_records, key=lambda x: x["date_code_sort"]) 
            for record in sealed_records:
                if 'date_code_sort' in record:
                    record.pop('date_code_sort')
            self.sealed_records = sealed_records
    ###############        ###############        ###############        ###############
    def total_carton_quantity(self,cartons):
        """Calculate how many carton in a carton list
        Args:
            cartons (list): list of carton dictionaries.
            {"part_no":,"carton_no":,"quantity":, "carton_quantity":, "earliest_date_code":"","date_codes":,"remarks":}
        Returns:
            [int]: number of carton in cartons list
        """
        total_carton = 0
        for carton in cartons:
            total_carton += carton["carton_quantity"]
        return int(total_carton)
    ###############        ###############        ###############        ###############
    def total_quantity(self,loose_quantity=True):
        """Calculate the total quantity of a part_no in sealed inventory regardless of date_code and remarks
        Args:
            loose_quantity (bool, optional): include loose quantity in each record. Defaults to True.
        Returns:
            [int]: total quantity of sealed record
        """
        if not loose_quantity:
            part_info = self.get_partinfo(bundle_qty=True)
            if part_info is None:
                return 0
            bundle_qty = part_info["bundle_qty"]
        total =0
        for record in self.sealed_records:
            if loose_quantity:
                total += record["quantity"]
            else:
                total += (record["quantity"]//bundle_qty)*bundle_qty
        return int(total)
    ###############        ###############        ###############        ###############
    def check_label_additional_info(self, additional_info=""):
        additional_info_dict = {}
        # condition: check if remarks has manufacturing date
        match = re.search(r"MFG=(\d+-\d+-\d+)",additional_info)
        if match is not None:
            additional_info_dict["MFG"] = match.group(1)
            if "MFG" not in self.SL_additional_info:
                self.SL_additional_info.append("MFG")
        # condition: check if remarks has expiry date
        match = re.search(r"EXP=(\d+-\d+-\d+)",additional_info)
        if match is not None:
            additional_info_dict["EXP"] = match.group(1)
            if "EXP" not in self.SL_additional_info: 
                self.SL_additional_info.append("EXP")
        # condition: check if remarks has packing date
        match = re.search(r"PKD=(\d+-\d+-\d+)",additional_info)
        if match is not None:
            additional_info_dict["PKD"] = match.group(1)
            if "PKD" not in self.SL_additional_info:
                self.SL_additional_info.append("PKD")
        return additional_info_dict
    ###############        ###############        ###############        ###############
    def add_label(self,part_no="",Qty=0,cavity=None,uom="",date_code="",remarks="" , additional_info=""):
        """add sealed label 
        Args:
            part_no (str): part number
            Qty (int): bundle quantity
            cavity (int): ...
            uom (str): unit of measurement
            date_code (str): printing date
        """
        if Qty == 0:
            logging.info("sealed label without quantity or date code.(LQD)")
            return
        date_code = "N/A" if date_code == "" or date_code == "0000" else date_code
        self.total_SL+=1
        sealedlabel = {}
        sealedlabel["part_no"] = part_no
        if cavity > 1 and uom.upper()=="PCS":
            Qty = int(Qty/cavity)
            sealedlabel["quantity"] = str(Qty)+" * "+str(cavity)+" "+str(uom)# standard quantity for each bundle
        else:
            sealedlabel["quantity"] = str(Qty)+" "+str(uom)
        sealedlabel["date_code"]= date_code
        sealedlabel["counter"] = self.total_SL
        additional_info = self.check_label_additional_info(additional_info)
        if "EXP" in additional_info:
            sealedlabel["EXP"] = additional_info["EXP"]
        if "MFG" in additional_info:
            sealedlabel["MFG"] = additional_info["MFG"]
        if "PKD" in additional_info:
            sealedlabel["PKD"] = additional_info["PKD"]
        self.SL.append(sealedlabel)
    ###############        ###############        ###############        ###############
    def new_batch_labels(self):
        part_info = self.get_partinfo(bundle_qty=True,uom_cavity=True) 
        bundle_qty, uom , cavity = part_info["bundle_qty"], part_info["uom"], part_info["cavity"]
        nb = self.new_batch
        bundle_no = int(nb["quantity"]//bundle_qty)
        loose_bundle = int(nb["quantity"]%bundle_qty)
        for i in range(bundle_no):
            self.add_label(self.part_no,bundle_qty,cavity,uom,nb["date_code"],nb["remarks"],nb["additional_info"])
        if loose_bundle:
            self.add_label(self.part_no,loose_bundle,cavity,uom,nb["date_code"],nb["remarks"],nb["additional_info"])
        total = self.total_SL
        for sealed_label in self.SL:
            sealed_label["counter"] = str(sealed_label["counter"])+"/"+str(total)
            
    ###############        ###############        ###############        ###############
    def to_csv(self):
        """create csv file for sealed_labels
        """
        if not self.SL: # sealed_labels
            return
        sealedlabel_path_ls = (sealedlabel_path_paper , sealedlabel_path_exp_paper ,sealedlabel_path_pkd_paper,
                            sealedlabel_path_sticker , sealedlabel_path_exp_sticker ,sealedlabel_path_pkd_sticker)
        for path in sealedlabel_path_ls:
            if not os.path.exists(path):
                os.makedirs(path)
        for condition in self.SL_additional_info:
            for sealedlabel in self.SL:
                if condition not in sealedlabel:
                    sealedlabel[condition] = "" # in case one of sealedlabel doesn't have a condition like other sealed labels
        now_date_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.part_info["paper_label"] == True:
            if ("EXP" in self.SL_additional_info) or ("MFG" in self.SL_additional_info):
                file_name = r'{}\{}_sealed_label_exp.csv'.format(sealedlabel_path_exp_paper,now_date_time)
            elif ("PKD" in self.SL_additional_info):
                file_name = r'{}\{}_sealed_label_pkd.csv'.format(sealedlabel_path_pkd_paper,now_date_time)
            else:
                file_name = r'{}\{}_sealed_label.csv'.format(sealedlabel_path_paper,now_date_time)
        else:
            if ("EXP" in self.SL_additional_info) or ("MFG" in self.SL_additional_info):
                file_name = r'{}\{}_sealed_label_exp.csv'.format(sealedlabel_path_exp_sticker,now_date_time)
            elif ("PKD" in self.SL_additional_info):
                file_name = r'{}\{}_sealed_label_pkd.csv'.format(sealedlabel_path_pkd_sticker,now_date_time)
            else:
                file_name = r'{}\{}_sealed_label.csv'.format(sealedlabel_path_sticker,now_date_time)
        fields = self.SL[0].keys()
        with open(file_name, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fields)
            dict_writer.writeheader()
            dict_writer.writerows(self.SL)
        print("'sealed_label.csv' has been created successfully.")
        logger.info("'sealed_label.csv' has been created successfully.")
        self.SL = []# reset sealed labels
    ###############        ###############        ###############        ###############
    def pack(self,amount=0 , weight_limit=0,loose_bundle=False):
        """Pack standard cartons or carton with weight limit.
        Args:
            amount (int, optional): number of cartons to pack. Defaults to 0=pack all.
            weight_limit (int, optional): if there is weight limit. Defaults to 0=no weight limit.
            loose_quantity (bool, optional): include loose bundle in carton. Defaults to True.
        Returns:
            [list]: list of dictionaries, each dictionary has info of a carton
                    {"part_no":,"carton_no":,"quantity":, "carton_quantity":, "earliest_date_code":,"date_codes":,"remarks":}
        """
        carton_ls = []
        part_no = self.part_no
        part_info = self.get_partinfo(bundle_qty=True, stn_qty=True, stn_carton=True,uom_cavity=True) 
        if part_info== None:
            print("The program won't be able to pack it into carton...")
            logger.error("The program won't be able to pack it into a carton...")
            return carton_ls # empty list
        bundle_qty, stn_qty, carton_no = part_info["bundle_qty"], part_info["stn_qty"], part_info["stn_carton"]
        if weight_limit>0: # if there is weight limit
            Qty = self.find_suitable_quantity(weight_limit)
            if not Qty:
                return carton_ls
            if stn_qty == Qty :
                weight_limit = 0
            stn_qty = Qty
        # initialize (for loop) variables
        remainder = total_carton =  0
        temp_date, temp_remarks, temp_id =[],[],[] # Initializing lists
        # loop through sealed_records to check if we can make a carton record
        for inx,record in enumerate(self.sealed_records):
            total_sealed_quantity = self.total_quantity(loose_bundle)
            if total_sealed_quantity < stn_qty and temp_id==[]:# if there is not enough quantity to make a standard carton
                break
            first_carton = True
            while remainder+record["quantity"] >= stn_qty:# while loop if there is enough quantity(parts) to make standard carton
                if temp_id:# multiple date codes
                    carton = {"part_no":part_no ,"carton_no":carton_no ,"quantity":stn_qty , "carton_quantity":1 , "loose_quantity":0 , "packing_date":datetime.now().date().isoformat()}
                    last_portion = stn_qty-remainder # last quantity to complete a carton
                    carton["date_codes"] = temp_date + [record["date_code"]+"="+str(last_portion)] # add date_code to date_codes list in carton
                    date_code0 = re.sub(r'=\d*',"",carton["date_codes"][0])# remove quantity from earliest_date_code
                    carton["earliest_date_code"] = int(date_code0)
                    carton["date_codes"] = " ".join(carton["date_codes"]) #convert date objects into string
                    carton["remarks"] = temp_remarks + ["("+record["remarks"]+")="+str(last_portion)] # add remarks to remarks list in carton
                    carton["remarks"] = " ".join(carton["remarks"]) #convert remarks into string
                    record["quantity"] -= (stn_qty - remainder)
                    self.allocated_cartons[carton_no][0]+=1
                elif first_carton and temp_id ==[]:# first carton of single date code
                    first_carton =False
                    carton = {"part_no":part_no ,"carton_no":carton_no ,"quantity":stn_qty , "carton_quantity":0, "earliest_date_code":record["date_code"],
                                "date_codes":record["date_code"], "remarks":record["remarks"] , "loose_quantity":0 , "packing_date":datetime.now().date().isoformat()}
                if not temp_id:
                    carton["carton_quantity"] += 1
                    record["quantity"] -= stn_qty
                    self.allocated_cartons[carton_no][0]+=1
                total_carton += 1
                if amount == total_carton:
                    if carton not in carton_ls:
                        carton_ls.append(carton)
                    return carton_ls
                if temp_id:
                    temp_date, temp_remarks, temp_id =[],[],[] # reset temporary lists
                    remainder =0
                    carton_ls.append(carton)
                # while loop end here
            if first_carton ==False:
                carton_ls.append(carton)
            # not enough quantity(parts) to make a carton%s then added to temporary variables and go to next sealed record
            total_sealed_quantity = self.total_quantity(loose_bundle)
            if total_sealed_quantity < stn_qty and temp_id==[]:
                break
            if (0 < remainder+record["quantity"] < stn_qty) and record["quantity"]>0 :
                if loose_bundle:
                    record_quantity = record["quantity"]
                else:
                    record_quantity = (record["quantity"]//bundle_qty)*bundle_qty
                remainder +=record_quantity
                if record_quantity>0:
                    temp_date.append(record["date_code"]+"="+str(record_quantity)) 
                    temp_remarks.append("("+record["remarks"]+")="+str(record_quantity))
                    temp_id.append(record["id"])
                    record["quantity"] -=record_quantity
        return carton_ls
    ###############        ###############        ###############        ###############
    def pack_subsequent(self,required_quantity=0,weight_limit=0):
        """pack one non-standard carton, it will pack whatever quantity is available but not more than required_quantity.
        Args:
            required_quantity (int, optional): number of needed quantity . Defaults to 0.
            weight_limit (int, optional): wight limit. Defaults to 0.
        Returns:
            [type]: single dictionary has info of subsequent carton , 'None' if could not be packed.
                    {"part_no":,"carton_no":,"quantity":, "carton_quantity":,"date_codes":,"remarks":}
        """
        if required_quantity <1:
            return
        part_no = self.part_no
        part_info = self.get_partinfo(stn_qty=True) 
        if part_info== None:
            print("The program won't be able to pack it into subsequent carton...")
            logger.error("The program won't be able to pack it into subsequent carton...")
            return
        stn_qty =  part_info["stn_qty"]
        logger.info("Creating subsequent_carton...")
        sub_carton = {"part_no":part_no ,"carton_no":"" ,"quantity":0 , "carton_quantity":0,"earliest_date_code":"","date_codes":[],"remarks":[]}
        if weight_limit>0:
            stn_qty = self.find_suitable_quantity(weight_limit)
        if required_quantity >stn_qty:
            required_quantity = stn_qty-1
        loose_quantity = 0
        delete_ls = [] # delete list for sealed_inventory records when its totally consumed
        Qty_ls = [] #for multiple date codes and remarks
        logger.info("Looking through sealed inventory...")
        for record in self.sealed_records:
            if record["quantity"] <1: # if sealed record has no quantity
                pass
            elif  sub_carton["quantity"] + record["quantity"] < required_quantity :# if record has quantity less than required quantity
                sub_carton["quantity"] += record["quantity"] 
                Qty_ls.append(record["quantity"])
                sub_carton["date_codes"].append(record["date_code"]) # add date_code to date_codes list in carton
                sub_carton["remarks"].append(record["remarks"])
                delete_ls.append(record["id"]) #adding delete record from sealed_records
            else:
                last_portion = required_quantity-sub_carton["quantity"]# last quantity to complete a carton
                loose_quantity = record["quantity"] - last_portion
                Qty_ls.append(required_quantity-sub_carton["quantity"]) 
                sub_carton["quantity"] = required_quantity
                sub_carton["date_codes"].append(record["date_code"]) # add date_code to date_codes list in carton
                sub_carton["remarks"].append(record["remarks"])
                delete_ls.append(record["id"])
                break
        if len(sub_carton["date_codes"])>1: # adding quantity for multiple date codes
            for i in range(len(sub_carton["date_codes"])):
                sub_carton["date_codes"][i] += "="+str(Qty_ls[i])
                sub_carton["remarks"][i] ="("+ sub_carton["remarks"][i]+")"+ "="+str(Qty_ls[i])
        logger.info("sub_carton quantity: {} ".format(sub_carton["quantity"]))
        logger.info("Now, The program is going to find suitable bin for the available quantity...") 
        sub_carton["earliest_date_code"] = sub_carton["date_codes"][0]
        sub_carton["date_codes"] = " ".join(sub_carton["date_codes"]) #convert date objects into string
        sub_carton["remarks"] = " ".join(sub_carton["remarks"]) #convert remarks into string
        sub_carton["carton_quantity"] = 1
        sub_carton["carton_no"] = "L"
        sub_carton["loose_quantity"] = sub_carton["quantity"]
        # updating sealed records
        for record in self.sealed_records: 
            if record["id"] in delete_ls: 
                record["quantity"] = 0 # set to zero
            if record["id"] == delete_ls[-1]:# last id in deleted list
                record["quantity"] = loose_quantity
                break
        self.allocated_cartons[sub_carton["carton_no"]][1]+=1
        sub_carton["packing_date"] = datetime.now().date().isoformat()
        return sub_carton
    ###############        ###############        ###############        ###############
    def init_allocated_cartons(self):
        #create carton dictionary
        DB.cursor.execute("SELECT carton_no FROM carton_info",)
        carton_nos = DB.cursor.fetchall()
        if not carton_nos:
            print("Couldn't find any carton information inside 'carton_info' table")
            messagebox.showerror("Error","Couldn't find any carton information inside 'carton_info' table")
            logger.error("Couldn't find any carton information inside 'carton_info' table")
            return
        allocated_cartons = {"carton number:":["Standard quantity","Non-Standard quantity"]}
        allocated_cartons = {"L":[0,0]}
        for carton_no in carton_nos:
            allocated_cartons[carton_no[0]]=[0,0]
        self.allocated_cartons = allocated_cartons
        
    ###############        ###############        ###############        ###############
    def find_suitable_quantity(self,weight_limit):
        """calculate the maximum quantity to fit in a carton with weight limit
        Args:
            weight_limit (float): ..
        Returns:
            [int]: quantity
        """
        part_info = self.get_partinfo(bundle_qty=True, stn_qty=True,part_weight=True) 
        if part_info== None:
            print("The program won't be able to calculate suitable quantity for part_no '{}' with weight limit '{}'".format(self.part_no,weight_limit))
            logger.error("The program won't be able to calculate suitable quantity for part_no '{}' with weight limit '{}'".format(self.part_no,weight_limit))
            return 
        bundle_qty, stn_qty, part_weight = part_info["bundle_qty"], part_info["stn_qty"], part_info["part_weight"]
        if weight_limit>0: 
            stnWeight = part_weight * stn_qty
            if stnWeight < weight_limit:
                return stn_qty
            else:
                bundle_no = int(stn_qty//bundle_qty)# the number of bundles in a carton
                for bundle_no in range(bundle_no,0,-1): # decrease number of bundles by 1 .
                    Qty = bundle_no*bundle_qty
                    carton_weight = part_weight * Qty
                    if carton_weight < weight_limit and Qty != 0:
                        return Qty
    ###############        ###############        ###############        ###############
    def remove_none(self,var , data_type="s"):
        if data_type.lower() == "s":#string
            return  str(var) if var != None else ""
        elif data_type.lower() == "i":#integer
            return int(var) if var != None else 0
        elif data_type.lower() == "f":#float
            return float(var) if var != None else 0
    ###############        ###############        ###############        ###############
    def get_partinfo(self,bundle_qty=False,stn_qty=False,stn_carton=False,uom_cavity=False,part_dimensions=False,part_weight=False,All=False):
        part_no = self.part_no
        if All==True:
            bundle_qty=stn_qty=stn_carton=uom_cavity=part_dimensions=part_weight=True
        if stn_qty==True or bundle_qty == True:
            uom_cavity=True
        not_available = []
        available = {}
        part_info = self.part_info.get("raw_data",None)
        if part_info is None:
            # availability for part info
            DB.cursor.execute("SELECT bundle_qty , stn_carton , stn_qty , weight , uom , cavity , customer ,part_X ,part_Y ,part_H ,paper_label FROM part_info WHERE part_no = %s" ,(part_no,))
            part_info = DB.cursor.fetchone()
            if not part_info:
                messagebox.showerror("Error","Oops,The part number '{}' doesn't exist at all, pls check 'part_info' table.".format(part_no))
                logger.error("Oops,The part number '{}' doesn't exist at all, pls check 'part_info' table.".format(part_no))
                return None
            i= 0
            part_info = list(part_info)
            for data_type in ("i","s","i","f","s","i","s","f","f","f"):
                part_info[i] = self.remove_none(part_info[i],data_type)
                i+=1
            self.part_info["raw_data"] = part_info
            self.part_info["paper_label"] = part_info[10]
        if uom_cavity:
            available["uom"]= self.part_info.get("uom",None)
            available["cavity"]= self.part_info.get("cavity",None)
            if available["uom"] is None or not available["cavity"]:
                if part_info[4] == ""  or (part_info[4].upper()  == "PANEL" and part_info[5] == 0)\
                    or (part_info[4].upper()=="PNL" and part_info[5] == 0):
                    not_available.append("uom_cavity")
                else:
                    available["uom"]=part_info[4]
                    available["cavity"]=part_info[5]
            uom = self.remove_none(available["uom"])
            cavity = self.remove_none(available["cavity"],"i")
        if bundle_qty: # check if bundle_qty is available
            available["bundle_qty"]= self.part_info.get("bundle_qty",None)
            if not available["bundle_qty"]:
                if part_info[0] == 0:
                    not_available.append("bundle_qty")
                elif uom.upper() == "PCS" and cavity>1 :
                    available["bundle_qty"]=part_info[0] * cavity
                else:
                    available["bundle_qty"]=part_info[0]
        if stn_qty:# check if stn_qty is available
            available["stn_qty"]= self.part_info.get("stn_qty",None)
            if  not available["stn_qty"]:
                if part_info[2] == 0:
                    not_available.append("stn_qty")
                elif uom.upper() == "PCS" and cavity>1 :
                    available["stn_qty"]=part_info[2] * cavity
                else:
                    available["stn_qty"]=part_info[2]
        if stn_carton:
            available["stn_carton"]= self.part_info.get("stn_carton",None)
            if not available["stn_carton"]:
                if part_info[1] == "":
                    not_available.append("stn_carton")
                else:
                    available["stn_carton"]=part_info[1]
        if part_dimensions:
            available["part_X"]= self.part_info.get("part_X",None)
            available["part_Y"]= self.part_info.get("part_Y",None)
            available["part_H"]= self.part_info.get("part_H",None)
            if not available["part_X"] or not available["part_Y"] or not available["part_H"]:
                if part_info[7] <= 0 or part_info[8] <= 0 or part_info[9] <= 0:
                    not_available.append("part_dimensions")
                else:
                    available["part_X"]=part_info[7]
                    available["part_Y"]=part_info[8]
                    available["part_H"]=part_info[9]
        if part_weight:
            available["part_weight"]= self.part_info.get("part_weight",None)
            if not available["part_weight"]:
                if part_info[3] <= 0:
                    not_available.append("part_weight")
                else:
                    available["part_weight"]=part_info[3]
        if not_available: # check if there are items in not_available list
            not_available = " , ".join(not_available)
            messagebox.showerror("Error","Oops,'{}' of the part number '{}' aren't valid or available, pls check 'part_info' table.".format(not_available,part_no))
            logger.error("Oops,'{}' of the part number '{}' aren't valid or available, pls check 'part_info' table.".format(not_available,part_no))
            return None
        self.part_info["customer"] = part_info[6]
        self.part_info.update(available)
        # return all available infos
        return available
    ###############        ###############        ###############        ###############
    def update_DB(self,log_id=0):
        """Update sealed_inventory and quantity in carton_info
        """
        for record in self.sealed_records:
            if record["quantity"]>0 and record["id"] is None: #if new patch
                DB.cursor.execute("INSERT INTO sealed_inventory (part_no, quantity, date_code, remarks ,additional_info ,log_id) VALUES (%s,%s,%s,%s,%s,%s);" ,
                               (record["part_no"],record["quantity"],record["date_code"],record["remarks"],record["additional_info"] , log_id))
            elif record["quantity"] <1 and record["id"] is not None:
                DB.cursor.execute("DELETE FROM sealed_inventory WHERE id=%s;" , (record["id"],))
            elif record["quantity"] >=1 and record["id"] is not None:
                DB.cursor.execute("UPDATE sealed_inventory SET quantity = %s ,log_id = %s WHERE id = %s;",(record["quantity"], log_id ,record["id"]))
        DB.conn.commit()
        if self.cartonsInfo : 
            for cartonInfo in self.cartonsInfo:
                DB.cursor.execute("UPDATE carton_info SET quantity = %s WHERE carton_no = %s;",(cartonInfo["quantity"],cartonInfo["carton_no"]) )
            DB.conn.commit()
        if self.new_entry:
            ne = self.new_entry # ne = new entry
            DB.cursor.execute("SELECT customer FROM part_info WHERE part_no = %s;", (ne["part_no"],))
            customer_input = DB.cursor.fetchone()
            customer = str(customer_input[0])
            DB.cursor.execute("INSERT INTO entry_tracker (part_no , quantity , date_code , remarks , additional_info, customer, time ,user_name,log_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
               (ne["part_no"],ne["quantity"],ne["date_code"],ne["remarks"],ne["additional_info"] , customer, datetime.now(), LoginSystem.user_name,log_id)                                               )
            DB.conn.commit()
##############################################################################################################

class CartonManager():
    def __init__(self,part_no="",uom="",cavity=0):
        self.part_no = part_no
        self.uom = uom
        self.cavity = cavity
        self.CL = []
        self.total_CL = 0
        self.cartons_list = []
        self.DO_records = []
        if not os.path.exists(cartonlabel_path):
            os.makedirs(cartonlabel_path)
        self.customer = ""
        DB.cursor.execute("SELECT customer FROM part_info WHERE part_no=%s", (part_no,))
        customer = DB.cursor.fetchone()
        if customer:
            self.customer = self.remove_none(customer[0])
    ###############        ###############        ###############        ###############
    def select_record(self,id):
        """search through delivery_order records and choose a record with required id
        Args:
            id (int): required id
        """
        if self.DO_records:
            temp=next((record for record in self.DO_records if record["id"] == id), None) # search for a single record has required id in delivery order records
            if temp is not None: # if there is a record
                self.selected_record = temp # copy the record to self.selected_record 
                return
        self.selected_record = None 
    ###############        ###############        ###############        ###############
    def sr_add_carton(self,carton={}, current_counter=0,last_counter=0):
        """add carton to selected_record and If selected record is None then it will be considered as temporary carton.
        Args:
            carton (dict): a dictionary that carry carton info = {"part_no":str ,"carton_no":str ,"quantity":int , 
                                    "carton_quantity":int, "earliest_date_code":str,"date_codes":str, "remarks":str}
            delivery_id (int, optional): attach carton record to delivery order. Defaults to 0 (temporary carton).
        """
        sr = self.selected_record # sr = selected delivery order
        if sr:# if Packed carton
            sr["fulfilled_quantity"] += (carton["carton_quantity"] * carton["quantity"])
            carton["delivery_id"] = sr['id']
            # self.add_carton_label(sr['customer'], carton['part_no'],carton["quantity"],carton["date_codes"],carton["remarks"],
            #                       carton["carton_quantity"],carton["carton_no"],current_counter,last_counter)
        else: # if Temporary carton
            carton["delivery_id"] = 0
            # self.add_carton_label(self.customer, carton['part_no'],carton["quantity"],carton["date_codes"],carton["remarks"],
            #                       carton["carton_quantity"],carton["carton_no"],current_counter,last_counter)
        # add the carton to carton_list either allocated or not.
        self.cartons_list.append(carton)
    ###############        ###############        ###############        ###############
    def get_by_part_no(self,fulfilled=False):
        """copy PGP records that has similar part_no
        Args:
            part_no ([str]): part number
            fulfilled (bool, optional): include records with complete fulfilled quantity. Defaults to False.
        """
        part_no = self.part_no
        if not fulfilled:
            DB.cursor.execute("SELECT id, customer ,part_no, quantity, uom ,delivery_order ,delivery_date ,fulfilled_quantity ,weight_limit ,cartons_id FROM delivery_orders WHERE part_no = %s AND quantity > fulfilled_quantity;" ,(part_no,))
            DO_records = DB.cursor.fetchall()
        else:
            DB.cursor.execute("SELECT id, customer ,part_no, quantity, uom ,delivery_order ,delivery_date ,fulfilled_quantity ,weight_limit ,cartons_id FROM delivery_orders WHERE part_no = %s;" ,(part_no,))
            DO_records = DB.cursor.fetchall()
        # loop through records and convert to dictionary
        for record in DO_records:
            record=self.convert_to_dict(record)
            #add record if id not exists in self.DO_records
            if not any(d['id'] == record["id"] for d in self.DO_records):
                self.DO_records.append(record)
    ###############        ###############        ###############        ###############
    def get_by_id(self,id):
        DB.cursor.execute("SELECT id, customer ,part_no, quantity, uom ,delivery_order ,delivery_date ,fulfilled_quantity ,weight_limit ,cartons_id FROM delivery_orders WHERE id = %s" ,(id,))
        record = DB.cursor.fetchone()
        if not record:
            messagebox.showerror("Error",f"The program couldn't Find the id of the delivery order:  id={id}")
            logger.error(f"The program couldn't Find the id of the delivery order:  id={id}")
            return
        record=self.convert_to_dict(record)
        #add record if id not exists in self.DO_records
        if not any(d['id'] == record["id"] for d in self.DO_records):
            self.DO_records.append(record)
        if not self.part_no:
            self.part_no = record["part_no"]
            self.uom = record["uom"]
        return True
    ###############        ###############        ###############        ###############
    def sort_DOs_records(self):
        if  self.DO_records:
            self.DO_records = sorted(self.DO_records, key=lambda d: d['delivery_date']) 
            return True
    ###############        ###############        ###############        ###############
    def sort_by_id(self,id):
        if  self.DO_records:
            self.sort_DOs_records()
            for inx,record in enumerate(self.DO_records): 
                if record['id'] == id:
                    if len(self.DO_records) >1:# swapping if there are more than one record
                        self.DO_records[0] , self.DO_records[inx] = self.DO_records[inx] , self.DO_records[0]
                    return True
            print(f"Delivery order id '{id}' that been selected is invalid")
            messagebox.showerror("Error",f"Delivery order id '{id}' that been selected is invalid")
            logger.error(f"Delivery order id '{id}' that been selected is invalid")              
    ###############        ###############        ###############        ###############
    def update_DB(self,log_id=0):
        # update the carton_table
        for carton in self.cartons_list:
            #check if there is similar carton info in carton_table
            DB.cursor.execute("SELECT id FROM carton_table WHERE part_no=%s AND date_codes=%s AND earliest_date_code=%s AND remarks= %s AND loose_quantity=%s AND carton_no=%s AND delivery_id=%s AND packing_date=%s;" ,
                            (carton["part_no"],carton["date_codes"],carton["earliest_date_code"],carton["remarks"],carton["loose_quantity"],carton["carton_no"],carton["delivery_id"],carton["packing_date"])  )
            exist_carton = DB.cursor.fetchone()
            if exist_carton:
                exist_carton_id = int(exist_carton[0])
                DB.cursor.execute("UPDATE carton_table SET carton_quantity =carton_quantity+%s WHERE id = %s;",(carton["carton_quantity"],exist_carton_id))
                DB.conn.commit()
            else:
                # insert new record into carton_table
                DB.cursor.execute("INSERT INTO carton_table (part_no, carton_quantity,carton_no, date_codes, earliest_date_code, remarks , loose_quantity , delivery_id , packing_date , log_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                            (carton["part_no"],carton["carton_quantity"],carton["carton_no"],carton["date_codes"],carton["earliest_date_code"],carton["remarks"],carton["loose_quantity"],carton["delivery_id"],carton["packing_date"],log_id)  )
                DB.conn.commit()
                if carton["delivery_id"] > 0: # if Packed carton
                    # get carton id
                    DB.cursor.execute("SELECT id FROM carton_table WHERE part_no=%s AND date_codes=%s ORDER BY id DESC LIMIT 1" , (carton["part_no"],carton["date_codes"]))
                    carton_id = DB.cursor.fetchone()
                    carton_id = carton_id[0]
                    self.select_record(carton["delivery_id"])
                    sr = self.selected_record
                    sr["cartons_id"] = carton_id if sr["cartons_id"]=="" else "{} | {}".format(sr["cartons_id"],carton_id)
        # update the delivery_order
        for record in self.DO_records:
            DB.cursor.execute("UPDATE Delivery_orders SET fulfilled_quantity = %s , cartons_id = %s WHERE id = %s;" , 
                            (record["fulfilled_quantity"] ,record["cartons_id"] , record["id"]) )
            DB.conn.commit()
    ###############        ###############        ###############        ###############
    def sr_archived(self):
        # archive delivery order
        sr = self.selected_record
        DB.cursor.execute("INSERT INTO archived_delivery_orders (id, customer ,part_no, quantity, uom ,delivery_order ,delivery_date ,fulfilled_quantity ,weight_limit ,cartons_id , time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);" ,
            (sr['id'],sr['customer'], sr['part_no'], sr['quantity'],sr['uom'], sr['delivery_order'], sr['delivery_date'],sr['fulfilled_quantity'], sr['weight_limit'], sr['cartons_id'] , datetime.now())  )
        DB.conn.commit()
        # archive the cartons of delivery order
        DB.cursor.execute("SELECT id, part_no, carton_quantity,carton_no, date_codes, earliest_date_code, remarks , loose_quantity , delivery_id FROM carton_table WHERE delivery_id = %s;" ,(sr['id'],))
        carton_records = DB.cursor.fetchall()
        for carton in carton_records:
            DB.cursor.execute("INSERT INTO archived_carton_table (id,part_no, carton_quantity,carton_no, date_codes, earliest_date_code, remarks , loose_quantity , delivery_id , time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                            (carton[0],carton[1],carton[2],carton[3],carton[4],carton[5],carton[6],carton[7],carton[8] , datetime.now())  )
            DB.conn.commit()
    ###############        ###############        ###############        ###############
    def delete(self,Delivery_order_id):
        DB.cursor.execute("DELETE FROM Delivery_orders WHERE id=%s;" , (Delivery_order_id,))
        DB.conn.commit()
        DB.cursor.execute("DELETE FROM carton_table WHERE delivery_id=%s;" , (Delivery_order_id,))
        DB.conn.commit()
    ###############        ###############        ###############        ###############
    def convert_to_dict(self,record):
        # id, customer ,part_no, quantity, uom ,delivery_order ,delivery_date ,fulfilled_quantity ,weight_limit ,cartons_id
        record = {"id":record[0],"customer":record[1],"part_no":record[2],"quantity":record[3],
                "uom":record[4] ,"delivery_order":record[5],"delivery_date":record[6],"fulfilled_quantity":record[7],
                "weight_limit":record[8] ,"cartons_id":record[9]}
        record["fulfilled_quantity"] = self.remove_none(record["fulfilled_quantity"] , "i")
        record["quantity"] = self.remove_none(record["quantity"] , "i")
        record["weight_limit"] = self.remove_none(record["weight_limit"] , "f")
        record["cartons_id"] = self.remove_none(record["cartons_id"])
        return record
    ###############        ###############        ###############        ###############
    def remove_none(self,var , data_type="s"):
        if data_type.lower() == "s":#string
            return  str(var) if var != None else ""
        elif data_type.lower() == "i":#integer
            return int(var) if var != None else 0
        elif data_type.lower() == "f":#float
            return float(var) if var != None else 0
    ###############        ###############        ###############        ###############
    def add_carton_label(self, customer="",part_no="",Qty=0,date_code="" ,remarks="",carton_quantity=0 ,carton_no ="",current_counter=0,last_counter=0):
        if carton_quantity <1 or Qty<1:
            return
        self.total_CL += carton_quantity
        pnl = self.uom.lower() == "pnl" or self.uom.lower() == "panel"
        Qty = str(Qty)+" "+str(self.uom)
        date_code = re.sub(r"(=\d+)", r"\1"+str(self.uom), date_code)
        remarks = re.sub(r"(\)=\d+)", r"\1"+str(self.uom), remarks)
        date_code = date_code.replace("0000","N/A")
        for i in range(carton_quantity):
            cartonlabel = {}
            cartonlabel["customer"] = customer
            cartonlabel["part_no"] = part_no
            cartonlabel["quantity"] = Qty
            cartonlabel["date_code"] = date_code
            cartonlabel["remarks"] = remarks
            cartonlabel["packing_date"] = datetime.now().date().isoformat()
            cartonlabel["carton_no"] = carton_no
            current_counter+=1
            counter = str(current_counter) + "/" + str(last_counter)
            cartonlabel["counter"] = counter
            self.CL.append(cartonlabel)
    ###############        ###############        ###############        ###############        
    def to_csv(self):
        if self.CL:
            now_date_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = r'{}\{}_carton_label.csv'.format(cartonlabel_path,now_date_time)
            fields = self.CL[0].keys()
            with open(file_name, 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, fields)
                dict_writer.writeheader()
                dict_writer.writerows(self.CL)
            print("'carton_label.csv' has been created successfully. ")
            logger.info("'carton_label.csv' has been created successfully. ")
##############################################################################################################

def inpro(qr_code="",id=""):
    qr_list = qr_code.split("|") # split QR code into part_no , quantity , date_code , remarks , additional_info 
    part_no = qr_list[0]
    new_batch_Qty = int(qr_list[1])
    sm = SealedManager(part_no) # for processing sealed records
    part_info = sm.get_partinfo(bundle_qty=True, stn_qty=True, stn_carton=True, uom_cavity=True)
    if part_info is None:
        return
    # check if standard quantity isn't dividable by bundle_qty
    bundle_qty , stn_qty , uom , cavity = part_info["bundle_qty"] , part_info["stn_qty"] , part_info["uom"] , part_info["cavity"]
    if stn_qty%bundle_qty>0:
        messagebox.showerror("Error",f"The standard quantity {stn_qty} can't be divided evenly by the bundle quantity {bundle_qty}..")
        return
    # check if the program is going to produce more than 99 sealed labels
    sealed_label_no = int(qr_list[1])//sm.part_info["raw_data"][0]  # Batch quantity / bundle quantity
    if sealed_label_no>99:
        ans=messagebox.askyesno("Warning",f"This entry has huge quantity and is going to create {sealed_label_no} sealed labels , do you want to continue?", icon='warning')
        if ans is False:
            return
    sm.get_sealed_records()
    sm.add_new_batch(qr_list[1],qr_list[2],qr_list[3],qr_list[4])
    sm.new_batch_labels() # sealed labels before allocation
    
    cm = CartonManager(part_no,uom,cavity) # to deal with carton records
    # create carton labels before allocation
    batch_quantity = int(qr_list[1])
    if uom.upper() == "PCS" and cavity >1:
        batch_quantity = batch_quantity * cavity
    carton_label_no = batch_quantity//stn_qty  # Batch quantity / standard carton quantity
    loose_carton = batch_quantity%stn_qty 
    last_counter = carton_label_no+1 if loose_carton else carton_label_no
    remarks = qr_list[3]
    match = re.search(r"EXP=\d+-\d+-\d+",qr_list[4]) # check for expiry date
    if match is not None:
        exp_date= match.group(0)
        remarks += " ,"+exp_date # add expiry date to carton remarks
    cm.add_carton_label(sm.part_info["customer"],part_no,stn_qty,qr_list[2],remarks,carton_label_no,sm.part_info["stn_carton"],0,last_counter)
    cm.add_carton_label(sm.part_info["customer"],part_no,loose_carton,qr_list[2],remarks,1,sm.part_info["stn_carton"],carton_label_no,last_counter)
    if id :# if user want to prioritize single delivery order id
        id = re.sub(r"[^\d]", "", str(id))
        id = int(id)
        ret =cm.get_by_id(id)
        if ret is None:
            print("Going back to the main menu..")
            return
    else:# if not , get all records that has same part number
        cm.get_by_part_no(part_no)
        cm.sort_DOs_records()
    if cm.DO_records: # if there is delivery orders found with same part number.
        logger.info("{} DO record\\s found:".format(len(cm.DO_records)))
        logger.info(str(cm.DO_records))
        for OnOff_loose_bundle in [False, True]:
            for record in cm.DO_records: 
                cm.select_record(record["id"])
                logger.info("Processing DO id: {}".format(record["id"]))
                _stn_qty = stn_qty 
                # if there is weight limit in this record
                if record["weight_limit"]>0: 
                    _stn_qty  =sm.find_suitable_quantity(record["weight_limit"])
                    if not _stn_qty:
                        print("id:",record["id"],"\tcustomer:",record["customer"],"\tDelivery Order:",record["delivery_order"],"\n")
                        continue
                #check if there is available quantity for standard carton
                unfulfilled_quantity = record["quantity"] - record["fulfilled_quantity"]
                available_quantity = sm.total_quantity(OnOff_loose_bundle)
                # determine counter current and last number
                current_counter = math.ceil(record["fulfilled_quantity"] / _stn_qty)
                last_counter =  math.ceil(record["quantity"] / _stn_qty)
                if unfulfilled_quantity >= _stn_qty and available_quantity >= _stn_qty:
                    #calculate how many carton needed to fulfill the delivery order
                    carton_need = unfulfilled_quantity//_stn_qty# convert to carton quantity
                    cartons =sm.pack(carton_need,record["weight_limit"],loose_bundle=OnOff_loose_bundle) #pack carton
                    for carton in cartons: # serve the cartons to delivery order
                        cm.sr_add_carton(carton,current_counter,last_counter)
                        current_counter += carton["carton_quantity"]
                #check if the record need subsequent carton
                unfulfilled_quantity = record["quantity"] - record["fulfilled_quantity"]
                available_quantity = sm.total_quantity()
                if unfulfilled_quantity < _stn_qty and available_quantity >= unfulfilled_quantity>0:#last carton
                    sub_carton =sm.pack_subsequent(unfulfilled_quantity,record["weight_limit"])
                    if sub_carton is not None:
                        cm.sr_add_carton(sub_carton,current_counter,last_counter)
                logger.info("cartons = {}".format(str(cm.cartons_list)))
    else:
        logger.info("No records were found. Going to update (carton_table & sealed_inventory) and then create temporary_label")
    
    cartons =sm.pack(loose_bundle=False)# pack whatever left into temporary carton
    cartons +=sm.pack(loose_bundle=True)
    if cartons: 
        logger.info("Temporary cartons = {}".format(str(cartons)))
        current_counter=0
        last_counter = sm.total_carton_quantity(cartons)
        cm.select_record(0) # 0 = temporary carton
        for carton in cartons:
            cm.sr_add_carton(carton)
    # create labels 
    sm.to_csv() # create sealed labels
    logger.info("Created: sealed labels")
    cm.to_csv()# create carton labels
    logger.info("Created: carton labels")
    # update log table
    log_id =update_log_table("Enter new batch" ,"", qr_list+[cavity,uom],"")
    logger.info("Updated: log_table")
    # update the database
    cm.update_DB(log_id) # update delivery_orders and carton_table
    logger.info("Updated: delivery_orders and carton_table")
    sm.update_DB(log_id) # update sealed_inventory
    logger.info("Updated: sealed_inventory")
    update_main_inventory(part_no)# update main inventory
    logger.info("Updated: main inventory")
    messagebox.showinfo("Info","'Batch Entry' process is completed successfully.")
    logger.info("'Batch Entry' process is completed")
    return True
##############################################################################################################