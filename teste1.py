import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import tkinter as tk
from tkinter import ttk
import pandas as pd
from tkinter import filedialog
import tkinter.messagebox
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
import timeit
from numba import jit
import numpy as np

global script_path
global isLiveOn
global selectedLive
script_path = os.getcwd()
isCapturingOn = False
isLiveOn = False
index_number_array = []
zscore_array = []

data_file = "1-SavedFiles/2019teste.bin"


def file_to_excel():
    if data_file == "":
        #tk.messagebox.showinfo('Atention', 'Select a file first')
        pass
    elif data_file[-3:] == "csv":
        ztest = pd.read_csv(data_file, sep=' ', names=["Time", "Ones"])
        ztest.dropna(inplace=True)
        ztest = ztest.reset_index()
        ztest['index'] = ztest['index'] + 1
        ztest['Sum'] = ztest['Ones'].cumsum()
        ztest['Average'] = ztest['Sum'] / (ztest['index'])
        ztest['Zscore'] = (ztest['Average'] - 1024) / (22.62741699796 / (ztest['index'] ** 0.5))
        data_file2 = os.path.basename(data_file)
        data_file2 = data_file2.replace(".csv", "")
        file_to_save = data_file.replace(".csv", ".xlsx")
        number_rows = len(ztest.index)
        writer = pd.ExcelWriter(file_to_save, engine='xlsxwriter')
        ztest.to_excel(writer, sheet_name='Z-Test', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Z-Test']
        chart = workbook.add_chart({'type': 'line'})
        chart.set_title({
            'name': 'Z-Score: ' + data_file2,
            'name_font': {
                'name': 'Calibri',
                'color': 'black',
            },
        })

        chart.set_x_axis({
            'name': 'Time',
            'name_font': {
                'name': 'Calibri',
                'color': 'black'
            },
            'num_font': {
                'name': 'Calibri',
                'color': 'black',
            },
        })

        chart.set_y_axis({
            'name': 'Z-Score',
            'name_font': {
                'name': 'Calibri',
                'color': 'black'
            },
            'num_font': {
                'color': 'black',
            },
        })

        chart.set_legend({'position': 'none'})
        chart.add_series({'values': ['Z-Test', 1, 5, number_rows, 5],
                          'categories': ['Z-Test', 1, 1, number_rows, 1]})
        worksheet.insert_chart('G2', chart)
        writer.save()
        #tk.messagebox.showinfo('File Saved', 'Saved as ' + file_to_save)
        return
    elif data_file[-3:] == "bin":
#         tk.messagebox.showinfo('Warning', """This couls take several seconds, please wait.
# Please do not close the Window.
# Press OK to start Analysis.""")
        #global num_ones_array
        num_ones_array = []
        num_ones_array = np.array(num_ones_array)
        with open(data_file, "rb") as file:  # open binary file
            bin_hex = BitArray(file)  # bin to hex
        bin_ascii = bin_hex.bin
        total_bits = len(bin_ascii)
        split_bin_ascii = wrap(bin_ascii, 2048)  # split in 2048 bits per line - 1 second
        # for i in split_bin_ascii:  # calculate number of 'ones' in each of the 2048 bits lines
        #     num_ones_array.append(i.count('1'))
        num_ones_array = bin_stuff(bin_ascii, num_ones_array, split_bin_ascii)
        # binSheet = pd.DataFrame()  # Array to Pandas Column
        # binSheet['Ones'] = num_ones_array
        # binSheet.dropna(inplace=True)
        # binSheet = binSheet.reset_index()
        # binSheet['index'] = binSheet['index'] + 1
        # binSheet = binSheet.rename(columns={'index': 'Time'})
        # binSheet['Sum'] = binSheet['Ones'].cumsum()
        # binSheet['Average'] = binSheet['Sum'] / (binSheet['Time'])
        # binSheet['Zscore'] = (binSheet['Average'] - 1024) / (22.62741699796 / (binSheet['Time'] ** 0.5))


        binSheet = binary_data(num_ones_array)
        data_file2 = os.path.basename(data_file)
        data_file2 = data_file2.replace(".bin", "")
        file_to_save = data_file.replace(".bin", ".xlsx")
        number_rows = len(binSheet.Time)
        writer = pd.ExcelWriter(file_to_save, engine='xlsxwriter')
        binSheet.to_excel(writer, sheet_name='Z-Test', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Z-Test']
        chart = workbook.add_chart({'type': 'line'})
        chart.set_title({
            'name': 'Z-Score: ' + data_file2,
            'name_font': {
                'name': 'Calibri',
                'color': 'black',
            },
        })

        chart.set_x_axis({
            'name': 'Time',
            'name_font': {
                'name': 'Calibri',
                'color': 'black'
            },
            'num_font': {
                'name': 'Calibri',
                'color': 'black',
            },
        })

        chart.set_y_axis({
            'name': 'Z-Score',
            'name_font': {
                'name': 'Calibri',
                'color': 'black'
            },
            'num_font': {
                'color': 'black',
            },
        })

        chart.set_legend({'position': 'none'})
        chart.add_series({'values': ['Z-Test', 1, 4, number_rows, 4],
                          'categories': ['Z-Test', 1, 0, number_rows, 0]})
        worksheet.insert_chart('G2', chart)
        writer.save()
        return
        #tk.messagebox.showinfo('File Saved', 'Saved as ' + file_to_save)
    else:
        #tk.messagebox.showinfo('Warning', 'Wrong File Type, Select a .bin or .csv file')
        pass


def binary_data(num_ones_array):
    binSheet = pd.DataFrame()  # Array to Pandas Column
    binSheet['Ones'] = num_ones_array
    binSheet.dropna(inplace=True)
    binSheet = binSheet.reset_index()
    binSheet['index'] = binSheet['index'] + 1
    binSheet = binSheet.rename(columns={'index': 'Time'})
    binSheet['Sum'] = binSheet['Ones'].cumsum()
    binSheet['Average'] = binSheet['Sum'] / (binSheet['Time'])
    binSheet['Zscore'] = (binSheet['Average'] - 1024) / (22.62741699796 / (binSheet['Time'] ** 0.5))
    return binSheet

@jit
def bin_stuff(bin_ascii, num_ones_array, split_bin_ascii):

    for i in split_bin_ascii:  # calculate number of 'ones' in each of the 2048 bits lines
        num_ones_array.append(i.count('1'))
    return num_ones_array

print(timeit.timeit(file_to_excel, number=1)/1)