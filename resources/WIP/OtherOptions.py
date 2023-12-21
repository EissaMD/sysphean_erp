from config import *
from ..UI import Page
from ..Logics import DB , update_main_inventory
from ..LoginSystem import LoginSystem

class OtherOptions(DB,Page):
    def __init__(self):
        menu_ls = {
            "Auto Update Inventory": self.Auto_Update_frame,
        }
        self.starting = False
        self.create_new_page("Other Options", menu_ls)
    ###############        ###############        ###############        ###############
    def Auto_Update_frame(self):
        body_frame = self.create_new_body()
        textbox = tk.Text(master=body_frame, bg="gray90")
        textbox.grid(row=1, column=0, columnspan=len([i for i in range(4)]), sticky="nwe", pady=10, padx=20)
        ctk.CTkButton(master=body_frame, text="Start Update Inventory",
                                command=lambda: self.auto_update_btn(textbox), height=35
                                ).grid(row=2, column=1, pady=10)

        def stop_btn():
            self.starting = False

        ctk.CTkButton(master=body_frame, text="Stop", command=stop_btn, height=35).grid(row=2, column=2,pady=10)
    ###############        ###############        ###############        ###############
    def auto_update_btn(self, textbox):
        if self.starting == True:
            return
        self.starting = True
        def updating():
            part_no_ls = DB.select("part_info", ("part_no",))
            no_of_part_no = DB.select("part_info", ("COUNT(part_no)",))
            no_of_part_no = no_of_part_no[0][0]
            textbox.delete(1.0, tk.END)
            i = 1
            for part_no in part_no_ls:
                if not self.starting:  # stop the loop
                    return
                update_main_inventory(part_no[0])
                line = f"\n{i}/{no_of_part_no}. part_no: {part_no[0]} successfully updated!"
                textbox.insert(tk.END, line)
                textbox.see(tk.END)
                i += 1
            messagebox.showinfo("Process info", "The main inventory is successfully updated!")
            self.starting = False
        threading.Thread(target=updating).start()
    ###############        ###############        ###############        ###############
