from config import *
from ..UI import Page , EntriesFrame  , RadioButtons , ChartWin
from ..Logics import DB


class SaleReport(Page):
        def __init__(self):
                self.create_new_page("Sale Report")
                self.sale_report()
        ###############        ###############        ###############        ###############
        def sale_report(self):
                self.create_new_body()
                body_frame = self.create_new_body()
                frame = ctk.CTkFrame(body_frame,fg_color="transparent") ; frame.pack(fill="x" ,pady=8)
                ctk.CTkLabel(frame,text="Select a range and one of the options below to generate sale report:",font=("Arial", 14, "bold")).pack(padx=10,pady=15 ,side ="left")
                # Date form
                entries = ( 
                        ("start_date"   , "date"       ,(0,0,1),None),
                        ("end_date"     , "date"       ,(0,1,1),None),
                        )
                self.date_range = EntriesFrame(body_frame,entries) ; self.date_range.pack()
                self.radio_btns = RadioButtons()
                # Time period form
                frame = ctk.CTkFrame(body_frame,fg_color="transparent") ; frame.pack(fill="x",pady=8)
                entries = ( 
                        ("time_period"  , "seg_btn"    ,(0,0,1),["Yearly", "Monthly", "Weekly", "Daily"]),
                        )
                self.time_period = EntriesFrame(frame,entries,False)
                self.radio_btns.add_button(frame,"time_period","Sales over time period: ",tuple(self.time_period.entry_dict.values()))
                self.time_period.pack(side="left",fill="x",expand=True)
                # sellers_rank form
                frame = ctk.CTkFrame(body_frame,fg_color="transparent") ; frame.pack(fill="x" ,pady=8)
                entries = ( 
                        ("top"  , "seg_btn"    ,(0,0,1),["3", "5", "10", "15", "20", "25","30"]),
                        )
                self.top_seller = EntriesFrame(frame,entries,False)
                self.radio_btns.add_button(frame,"sellers_rank","Sales Rep: Best seller (Ranks on graph).",tuple(self.top_seller.entry_dict.values()))
                self.top_seller.pack(side="left",fill="x",expand=True)
                # sale_revenue form
                frame = ctk.CTkFrame(body_frame,fg_color="transparent") ; frame.pack(fill="x" ,pady=8)
                entries = ( 
                        ("top"  , "seg_btn"    ,(0,0,1),["3", "5", "10", "15", "20", "25","30"]),
                        )
                self.sale_revenue = EntriesFrame(frame,entries,False)
                self.radio_btns.add_button(frame,"sale_revenue","Sales Revenue: The total amount of revenue generated from each sale.",tuple(self.sale_revenue.entry_dict.values()))
                self.sale_revenue.pack(side="left",fill="x",expand=True)
                # sellers_rank form
                frame = ctk.CTkFrame(body_frame,fg_color="transparent") ; frame.pack(fill="x" ,pady=8)
                self.radio_btns.add_button(frame,"quantity_rank","Sales Quantity Sold: The number of units sold for each product.")
                # sellers_rank form
                frame = ctk.CTkFrame(body_frame,fg_color="transparent") ; frame.pack(fill="x" ,pady=8)
                self.radio_btns.add_button(frame,"products","Sales by Product: Best selling items, Categories Product,")
                ####
                self.radio_btns.disable_all_elements()
                self.create_footer(self.generate_btn,"Generate")
        ###############        ###############        ###############        ###############
        def generate_btn(self):
                report_name = self.radio_btns.selected
                if not report_name:
                        messagebox.showerror("ERROR",f"Please select one of the options to generate sale report.")
                        return
                date = self.date_range.get_data()
                date_range = (datetime.strptime(date["start_date"], "%Y-%m-%d").date() , datetime.strptime(date["end_date"], "%Y-%m-%d").date())
                if date_range[0]>= date_range[1]:
                        messagebox.showerror("ERROR",f"The End Date should be greater than the Start Date")
                        return
                if report_name == "time_period":
                        self.time_period_btn(date_range)
                elif report_name == "sellers_rank":
                        self.sellers_rank_btn(date_range)
        ###############        ###############        ###############        ###############
        def time_period_btn(self,date_range=(datetime.today(),datetime.today())):
                start_date , end_date = date_range
                start_year , end_year = start_date.year , end_date.year
                years_diffs = end_year - start_year
                time_period = self.time_period.get_data()["time_period"]
                total_price_ls = []
                if time_period == "Yearly" :
                        years_ls = [] 
                        for i in range(years_diffs+1):
                                year = start_year+i
                                years_ls.append(year)
                                DB.cursor.execute(f"SELECT sum(total_price) FROM sale_order WHERE delivery_date BETWEEN '{year}-01-01' AND '{year}-12-31'")
                                total_price_ls.append(DB.cursor.fetchone()[0] or 0)
                        ChartWin().create_plt("Time Period (Yearly)",("Year","MYR"),(years_ls,total_price_ls))
                elif time_period == "Monthly" :
                        months_diff = (years_diffs*12) + (end_date.month - start_date.month)
                        months_ls = []
                        current_date = start_date
                        for i in range(months_diff+1):
                                if i: current_date = current_date + relativedelta(months=1)
                                year , month=current_date.year , str(current_date.month).zfill(2)
                                months_ls.append(f"{year}-{month}")
                                DB.cursor.execute(f"SELECT sum(total_price) FROM sale_order WHERE delivery_date BETWEEN '{year}-{month}-01' AND '{year}-{month}-31'")
                                total_price_ls.append(DB.cursor.fetchone()[0] or 0)
                        ChartWin().create_plt("Time Period (Monthly)",("Month","MYR"),(months_ls,total_price_ls))
                elif time_period == "Weekly" :
                        start_week = start_date - relativedelta(days=start_date.isocalendar()[2]-1)
                        end_week = end_date + relativedelta(days=7-start_date.isocalendar()[2])
                        weeks_diff = end_week.isocalendar()[1] - start_week.isocalendar()[1]
                        current_date = start_week
                        weeks_ls = []
                        for i in range(weeks_diff+1):
                                if i: current_date = current_date + relativedelta(weeks=1)
                                year ,month , day , last_day = current_date.year , str(current_date.month).zfill(2), str(current_date.day).zfill(2), str(current_date.day+6).zfill(2)
                                week = current_date.isocalendar()[1]
                                weeks_ls.append(f"{year}-{week}")
                                DB.cursor.execute(f"SELECT sum(total_price) FROM sale_order WHERE delivery_date BETWEEN '{year}-{month}-{day}' AND '{year}-{month}-{last_day}'")
                                total_price_ls.append(DB.cursor.fetchone()[0] or 0)
                        ChartWin().create_plt("Time Period (Weekly)",("Week","MYR"),(weeks_ls,total_price_ls),True)
                elif time_period == "Daily" :
                        days_diff = (end_date-start_date).days
                        if days_diff >  30:
                                messagebox.showerror("ERROR",f"Daily report: The number of days should not exceed 30 days.")
                                return
                        day_ls = []
                        current_date = start_date
                        for i in range(days_diff+1):
                                if i: current_date = current_date + relativedelta(days=1)
                                current_date_str = "{}-{}-{}".format(current_date.year , str(current_date.month).zfill(2), str(current_date.day).zfill(2))
                                day_ls.append(current_date_str)
                                DB.cursor.execute(f"SELECT sum(total_price) FROM sale_order WHERE delivery_date = %s",(current_date_str,))
                                total_price_ls.append(DB.cursor.fetchone()[0] or 0)
                        ChartWin().create_plt("Time Period (Daily)",("Day","MYR"),(day_ls,total_price_ls),True)
        ###############        ###############        ###############        ###############
        def sellers_rank_btn(self,date_range=(datetime.today(),datetime.today())):
                start_date , end_date = date_range
                start_date = "{}-{}-{}".format(start_date.year , str(start_date.month).zfill(2), str(start_date.day).zfill(2))
                end_date = "{}-{}-{}".format(end_date.year , str(end_date.month).zfill(2), str(end_date.day).zfill(2))
                DB.cursor.execute(f"SELECT DISTINCT sales_representative FROM sale_order WHERE delivery_date BETWEEN %s AND %s",(start_date,end_date))
                seller_ls = [i[0] for i in DB.cursor.fetchall()]
                ls = []
                for seller in seller_ls:
                        DB.cursor.execute(f"SELECT sum(total_price) FROM sale_order WHERE sales_representative = %s AND delivery_date BETWEEN %s AND %s",(seller,start_date,end_date))
                        ls.append((seller,DB.cursor.fetchone()[0] or 0))
                ls =sorted(ls, key = lambda x: x[1], reverse = True)
                top = self.top_seller.get_data()
                top = int(top["top"])
                seller_ls , total_price_ls = [] , []
                i = 1
                for seller,total_price in ls:
                        seller_ls.append(seller)
                        total_price_ls.append(total_price)
                        if i == top:
                                break
                        i+=1
                ChartWin().create_bar("Top sellers",("Seller","MYR"),(seller_ls,total_price_ls))