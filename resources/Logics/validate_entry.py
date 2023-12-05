from config import *

def validate_entry(entry_dict={},popup_msg=True):
    failed_ls = []
    for key, value in entry_dict.items():
        key = key.lower()
        # check part_no
        if key == "part_no":
            if value == "":
                failed_ls.append(key)
        # check float
        if key == "weight":
            try:
                test=float(value)
            except:
                failed_ls.append(key)
        # check integer
        if key in ("cavity"):
            try:
                test=int(value)
            except:
                failed_ls.append(key)
        # check uom
        if key == "uom":
            if value != "PCS" or value != "PANEL":
                failed_ls.append(key)
        # check quantity
        if key in ("quantity" , "bundle_qty" , "stn_qty"):
            try:
                if int(value) <1:
                    raise Exception
            except:
                failed_ls.append(key)
        # check date_code
        if key == "date_code":
            if len(value)==4:
                yy= value[-2:]
                ww= value[:2]
                try:
                    test = datetime.strptime(f"{yy}-{ww}-1", r"%y-%W-%w")
                except:
                    failed_ls.append(key)
            elif len(value)==6:
                yy= value[-2:]
                mm= value[2:4]
                dd = value[:2]
                try:
                    test = datetime.strptime(f"{yy}-{mm}-{dd}", r"%y-%m-%d")
                except:
                    failed_ls.append(key)
            else:
                failed_ls.append(key)
        # check date entry
        if key in ("expiry_date" , "manufacturing_date" , "packing_date"):
            try:
                if value != "":
                    test = datetime.strptime(value, r"%Y-%m-%d")
            except:
                failed_ls.append(key)
    if popup_msg is True and len(failed_ls)>0:
        error_text = f"Invalid entry, Please check your entries and try again. \nCheck the following entries={str(failed_ls)}"
        messagebox.showerror("Error",error_text)
    return failed_ls