import customtkinter as ctk
from tkinter import messagebox , filedialog , Toplevel , StringVar
from tksheet import Sheet
from tkcalendar import Calendar, DateEntry
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image , ImageTk

import csv
import os
import threading
from datetime import datetime , date , timedelta
import math 
import re
from cryptography.fernet import Fernet
from dateutil.relativedelta import relativedelta

from configparser import ConfigParser
config = ConfigParser()
config.read("CONFIG.ini")

import logging
logging.basicConfig(filename=".\sysphean_erp.log", format='%(asctime)s %(levelname)s: %(message)s   func:%(funcName)s')
logger=logging.getLogger()
logger.setLevel(logging.INFO)

import pandas as pd
import numpy as np
import xlrd

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

################################  Path variables      ###########################################################
#database_path = config["Path Variables" ]["db_path" ]
sealedlabel_path_paper = config["Path Variables" ]["sealedlabel_paper_path"]
sealedlabel_path_exp_paper = config["Path Variables" ]["sealedlabel_exp_paper_path"]
sealedlabel_path_pkd_paper = config["Path Variables" ]["sealedlabel_pkd_paper_path"]

sealedlabel_path_sticker = config["Path Variables" ]["sealedlabel_sticker_path"]
sealedlabel_path_exp_sticker = config["Path Variables" ]["sealedlabel_exp_sticker_path"]
sealedlabel_path_pkd_sticker = config["Path Variables" ]["sealedlabel_pkd_sticker_path"]

cartonlabel_path = config["Path Variables" ]["cartonlabel_path"]
log_path = config["Path Variables" ]["log_path"]
##############################################################################################################