from config import *
from .Logics import DB

class LoginSystem():
    F=Fernet(b'Cgfow1pOUko9As6UAox4FfJSX63kcKXnLJBICAFCnyE=')
    def __init__(self,create_empty_frame,create_main_frame):
        LoginSystem.create_empty_frame = create_empty_frame
        LoginSystem.create_main_frame = create_main_frame
        LoginSystem.user_name = ""
    ###############        ###############        ###############        ###############
    def start():
        main_frame = LoginSystem.create_empty_frame()
        main_frame.configure( fg_color="transparent")
        ctk.CTkLabel(main_frame, text="" ,image='background').pack()
        frame = ctk.CTkFrame(main_frame , fg_color="#FFFFFF") ; frame.place(relx=0.28, rely=0.85, anchor="center")
        ctk.CTkLabel(frame , image='user_icon' , text="", fg_color="#FFFFFF" ).pack( pady=10,side="left")
        # input frame
        input_frame = ctk.CTkFrame(master=frame , fg_color="#FFFFFF")
        input_frame.pack(side="left")
        # user name
        ctk.CTkLabel(master=input_frame, text="User Name: " , width = 100, fg_color="#FFFFFF").grid(row=0, column=0 )
        LoginSystem.user = ctk.CTkEntry(master=input_frame , width = 200 , fg_color="#FFFFFF")
        LoginSystem.user.grid(row=0, column=1)
        # password
        ctk.CTkLabel(master=input_frame, text="Password: " , width = 100, fg_color="#FFFFFF").grid(row=1, column=0 , pady=(10,0) )
        LoginSystem.password = ctk.CTkEntry(master=input_frame , show="*" ,  width = 200 , fg_color="#FFFFFF")
        LoginSystem.password.grid(row=1, column=1 , pady=(10,0))
        ctk.CTkButton(input_frame,text="Enter" , width=50 , command=LoginSystem.login_btn).grid(row=0, column=2,rowspan=2 ,sticky="ns" , padx=5)
    ###############        ###############        ###############        ###############
    def login_btn():
        user        = LoginSystem.user.get()
        password    = LoginSystem.password.get()
        DB.cursor.execute("SELECT user_name, password, admin, sales, inventory, manufacturing, Procurement, time_created FROM user WHERE user_name=%s;",(user,))
        user_info = DB.cursor.fetchone()
        if not user_info:
            messagebox.showinfo("Info", "Wrong username, please try again!")
            return
        stored_pass =LoginSystem.F.decrypt(user_info[1].encode()).decode()
        if stored_pass != password:
            messagebox.showinfo("Info",  "Wrong password, please try again!")
            return
        LoginSystem.user_info = {
                                    "user_name"     : user_info[0],
                                    "password"      : user_info[1],
                                    "admin"         : int(user_info[2]),
                                    "Sales"         : int(user_info[3]) or int(user_info[2]),
                                    "Inventory"     : int(user_info[4]) or int(user_info[2]),
                                    "Manufacturing" : int(user_info[5]) or int(user_info[2]),
                                    "Procurement"   : int(user_info[6]) or int(user_info[2]),
                                    "WIP"           : int(user_info[2]),
                                    "About"         : 1,
                                }
        LoginSystem.user_name = user
        LoginSystem.create_main_frame()
##############################################################################################################