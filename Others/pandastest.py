import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import tkinter.messagebox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import time
from time import localtime, strftime
import subprocess
from PIL import Image, ImageTk
import threading
from bitstring import BitArray
from textwrap import wrap
import serial
from serial.tools import list_ports
import csv


def bblaWin():
    global is_bblaWin_on
    global file_name
    is_bblaWin_on = True
    startupinfo = None
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    file_name = time.strftime("%Y%m%d-%H%M%S")
    is_bblaWin_on = 10
    index_number = 0
    while is_bblaWin_on != 0:
        index_number += 1
        is_bblaWin_on -= 1
        with open(file_name + '.bin', "ab") as bin_file: # save binary file
            proc = subprocess.Popen('seedd.exe --limit-max-xfer --no-qa -f2 -b 256', stdout=subprocess.PIPE, startupinfo=startupinfo)
            chunk = proc.stdout.read()
            bin_file.write(chunk)
        bin_hex = BitArray(chunk) # bin to hex
        bin_ascii = bin_hex.bin #hex to ASCII
        num_ones_array = int(bin_ascii.count('1')) # count numbers of ones in the 2048 string
        with open(file_name + '.csv', "a+") as write_file:  # open file and append time and number of ones
            write_file.write('{} {} {}\n'.format(index_number, strftime("%H:%M:%S", localtime()), num_ones_array))
        with open(file_name + '.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=' ')
            csv_indexs = []
            csv_ones = []
            for row in readCSV:
                csv_index = row[0]
                csv_one = int(row[2])
                csv_indexs.append(csv_index)
                csv_ones.append(csv_one)
            print(csv_ones)
            sums_csv = sum(csv_ones)
            print(sums_csv)
            avrg_csv = sums_csv / index_number
            print(avrg_csv)
            zscore_csv = (avrg_csv - 1024) / (22.62741699796 / (index_number ** 0.5))
            print(zscore_csv)




bblaWin()