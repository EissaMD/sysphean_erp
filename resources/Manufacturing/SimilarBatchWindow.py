from ..Logics import DB
from config import *

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