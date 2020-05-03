#!/usr/bin/python3
# coding: utf-8


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



print("Starting RngKitWin")
LARGE_FONT = ("Verdana", 12)
style.use("ggplot")

f = Figure(figsize=(7, 4), dpi=100)
a = f.add_subplot(111)
index_number_array = []
zscore_array = []
global script_path
global isLiveOn
global selectedLive
script_path = os.getcwd()
isCapturingOn = False
isLiveOn = False

def animate(i):
    xar = index_number_array
    yar = zscore_array
    a.clear()
    a.plot(xar, yar, color='orange')
    a.set_title("Live Plot")
    a.set_xlabel('Time(s)', fontsize=10)
    a.set_ylabel('Z-Score', fontsize='medium')


# Parametros tkinter
window = tk.Tk()
# window.geometry('880x180')  # window size
window.title("Welcome to RNG Project App")  # window title

# Adding Tabs tabs
tab_control = ttk.Notebook(window)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab_control.add(tab1, text='Data Analysis')
tab_control.add(tab2, text='Acquiring Data')
tab_control.add(tab3, text='Live Plot')

# ------------------------- TAB1---------------------------------------
# Frames
frameTab11 = tk.Frame(tab1, borderwidth="2", relief="ridge")
frameTab11.grid(column=0, row=0, sticky="ns")

frameTab12 = tk.Frame(tab1, borderwidth="2", relief="ridge")
frameTab12.grid(column=1, row=0, sticky="ns")

frameTab13 = tk.Frame(tab1, borderwidth="2", relief="ridge")
frameTab13.grid(column=2, row=0, sticky="ns")

frameTab14 = tk.Frame(tab1, borderwidth="2", relief="ridge")
frameTab14.grid(column=3, row=0, sticky="ns")

# Line 1 - Open collected file to work and transform to .xlsx
lbl1 = tk.Label(frameTab11, text="Click to open file ...",
                font=("Arial Bold", 11),
                padx=5, pady=5)  # Text inside window
lbl1.grid(column=0, row=0, sticky="ew")  # Label Position

# Image

bitB = Image.open("datafiles/BitB.png")
bitB = bitB.resize((200, 140), Image.ANTIALIAS)
bitBjov = ImageTk.PhotoImage(bitB)
labelimg = tk.Label(frameTab13, image=bitBjov)
labelimg.image = bitBjov
labelimg.grid(row=0, column=0, sticky="wens")

projIm = Image.open("datafiles/Proj.jpg")
projIm = projIm.resize((200, 140), Image.ANTIALIAS)
projImjov = ImageTk.PhotoImage(projIm)
labelimg2 = tk.Label(frameTab14, image=projImjov)
labelimg2.image = projImjov
labelimg2.grid(row=0, column=0, sticky="wens")


def open_file():
    global data_file
    data_file = filedialog.askopenfilename(initialdir=f"{script_path}/1-SavedFiles", title="Select file",
                                           filetypes=[("CSV and Binary", "*.csv *.bin"), ("All Files", "*.*")])
    lbl1.configure(text=data_file[-40::])
    btn1.configure(text="Select another file")


btn1 = tk.Button(frameTab12, text="Select File", bg="white", fg="blue",
                 command=open_file,
                 padx=5, pady=5)  # criar botão/ command=função do botão
btn1.grid(column=1, row=0, sticky="ew")  # posição do botão

# Linha 2 - Salvar arquivo para xlxs direto
lbl2 = tk.Label(frameTab11, text="Generate .xlsx File",
                font=("Arial Bold", 11),
                padx=5, pady=5)  # Text inside window
lbl2.grid(column=0, row=1, sticky="ew")  # posição do label


def Ztesta():
    if data_file == "":
        tk.messagebox.showinfo('Atention', 'Select a file first')
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
        tk.messagebox.showinfo('File Saved', 'Saved as ' + file_to_save)
    elif data_file[-3:] == "bin":
        tk.messagebox.showinfo('Warning', """This couls take several seconds, please wait.
Please do not close the Window.
Press OK to start Analysis.""")
        global num_ones_array
        num_ones_array = []
        with open(data_file, "rb") as file:  # open binary file
            bin_hex = BitArray(file)  # bin to hex
        bin_ascii = bin_hex.bin
        total_bits = len(bin_ascii)
        split_bin_ascii = wrap(bin_ascii, 2048)  # split in 2048 bits per line - 1 second
        for i in split_bin_ascii:  # calculate number of 'ones' in each of the 2048 bits lines
            num_ones_array.append(i.count('1'))
        binSheet = pd.DataFrame()  # Array to Pandas Column
        binSheet['Ones'] = num_ones_array
        binSheet.dropna(inplace=True)
        binSheet = binSheet.reset_index()
        binSheet['index'] = binSheet['index'] + 1
        binSheet = binSheet.rename(columns={'index': 'Time'})
        binSheet['Sum'] = binSheet['Ones'].cumsum()
        binSheet['Average'] = binSheet['Sum'] / (binSheet['Time'])
        binSheet['Zscore'] = (binSheet['Average'] - 1024) / (22.62741699796 / (binSheet['Time'] ** 0.5))

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
        tk.messagebox.showinfo('File Saved', 'Saved as ' + file_to_save)
    else:
        tk.messagebox.showinfo('Warning', 'Wrong File Type, Select a .bin or .csv file')


btn2 = tk.Button(frameTab12, text="Generate", bg="white", fg="blue",
                 command=Ztesta,
                 padx=5, pady=5)  # criar botão/ command=função do botão
btn2.grid(column=1, row=1, sticky="ew")  # posição do botão

# Linha 3 - Salvar as arquivo para xlxs
lbl3 = tk.Label(frameTab11, text="Generate and Save as...",
                font=("Arial Bold", 11),
                padx=5, pady=5)  # Text inside window
lbl3.grid(column=0, row=2, sticky="ew")  # posição do label


def Ztest():
    if data_file == "":
        tk.messagebox.showinfo('Atention', 'Select a file first')
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
        file_to_save = filedialog.asksaveasfilename(initialdir=f"{script_path}/1-SavedFiles",
                                                    initialfile=data_file2,
                                                    title="Select file",
                                                    filetypes=(("XLSX Files", '*.xlsx'), ("all files", "*.*")))
        if len(file_to_save) < 1:
            return
        data_file2 = os.path.basename(data_file)
        data_file2 = data_file2.replace(".csv", "")
        number_rows = len(ztest.index)
        writer = pd.ExcelWriter((file_to_save + ".xlsx"), engine='xlsxwriter')
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
        tk.messagebox.showinfo('File Saved', 'Saved as ' + (file_to_save + ".xlsx"))
    elif data_file[-3:] == "bin":
        data_file2 = os.path.basename(data_file)
        data_file2 = data_file2.replace(".bin", "")
        file_to_save = filedialog.asksaveasfilename(initialdir=f"{script_path}/1-SavedFiles",
                                                    initialfile=data_file2,
                                                    title="Select file",
                                                    filetypes=(("XLSX Files", '*.xlsx'), ("all files", "*.*")))
        if len(file_to_save) < 1:
            return
        tk.messagebox.showinfo('Warning', """This couls take several seconds, please wait.
Please do not close the Window.
Press OK to start Analysis.""")
        global num_ones_array
        num_ones_array = []
        with open(data_file, "rb") as file:  # open binary file
            bin_hex = BitArray(file)  # bin to hex
        bin_ascii = bin_hex.bin
        total_bits = len(bin_ascii)
        split_bin_ascii = wrap(bin_ascii, 2048)  # split in 2048 bits per line - 1 second
        for i in split_bin_ascii:  # calculate number of 'ones' in each of the 2048 bits lines
            num_ones_array.append(i.count('1'))
        binSheet = pd.DataFrame()  # Array to Pandas Column
        binSheet['Ones'] = num_ones_array
        binSheet.dropna(inplace=True)
        binSheet = binSheet.reset_index()
        binSheet['index'] = binSheet['index'] + 1
        binSheet = binSheet.rename(columns={'index': 'Time'})
        binSheet['Sum'] = binSheet['Ones'].cumsum()
        binSheet['Average'] = binSheet['Sum'] / (binSheet['Time'])
        binSheet['Zscore'] = (binSheet['Average'] - 1024) / (22.62741699796 / (binSheet['Time'] ** 0.5))

        file_to_save = file_to_save.replace(".bin", ".xlsx")
        data_file2 = os.path.basename(data_file)
        data_file2 = data_file2.replace(".csv", "")
        number_rows = len(binSheet.Time)
        writer = pd.ExcelWriter((file_to_save + ".xlsx"), engine='xlsxwriter')
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
        tk.messagebox.showinfo('File Saved', 'Saved as ' + (file_to_save + ".xlsx"))
    else:
        tk.messagebox.showinfo('Warning', 'Wrong File Type, Select a .bin or .csv file')


btn3 = tk.Button(frameTab12, text="Save as...", bg="white", fg="blue",
                 command=Ztest,
                 padx=5, pady=5)  # criar botão/ command=função do botão
btn3.grid(column=1, row=2, sticky="ew")  # posição do botão

# ------------------------------TAB2 -----------------------------------

# Frames
frameTab21 = tk.Frame(tab2, borderwidth="2", relief="ridge")
frameTab21.grid(column=0, row=0, sticky="ns")

frameTab22 = tk.Frame(tab2, borderwidth="2", relief="ridge")
frameTab22.grid(column=1, row=0, sticky="ns")

frameTab23 = tk.Frame(tab2, borderwidth="2", relief="ridge")
frameTab23.grid(column=2, row=0, sticky="ns")

frameTab24 = tk.Frame(tab2, borderwidth="2", relief="ridge")
frameTab24.grid(column=3, row=0, sticky="ns")

frameTab25 = tk.Frame(tab2, borderwidth="2", relief="ridge")
frameTab25.grid(column=4, row=0, sticky="ns")

# Radiobuttons
selectedColeta = tk.IntVar()
selectedColeta.set(1)
radBbla = tk.ttk.Radiobutton(frameTab21, text='Bitbabbler', value=1, variable=selectedColeta)
radTrng = tk.ttk.Radiobutton(frameTab21, text='TrueRng', value=2, variable=selectedColeta)
radMbbla = tk.ttk.Radiobutton(frameTab21, text='Two Bitbabbler', value=3, variable=selectedColeta)
radMrng = tk.ttk.Radiobutton(frameTab21, text='Bitbabbler + TrueRng', value=4, variable=selectedColeta)
radBbla.grid(column=0, row=1, sticky="ew")
radTrng.grid(column=0, row=2, sticky="ew")
radMbbla.grid(column=0, row=3, sticky="ew")
radMrng.grid(column=0, row=4, sticky="ew")

# Combobox - bbla
selectedCombo = tk.StringVar()
comboBbla = tk.ttk.Combobox(frameTab22, width=3)
comboBbla['values'] = (0, 1, 2, 3, 4)
comboBbla.current(0)
comboBbla.grid(column=0, row=1)

# Combobox - mbbla - Raw/XOR
selectedComboM1 = tk.StringVar()
comboMbla1 = tk.ttk.Combobox(frameTab22, width=3)
comboMbla1['values'] = (0, 1, 2, 3, 4)
comboMbla1.current(0)
comboMbla1.grid(column=0, row=3)
selectedComboM2 = tk.StringVar()
comboMbla2 = tk.ttk.Combobox(frameTab22, width=3)
comboMbla2['values'] = (0, 1, 2, 3, 4)
comboMbla2.current(0)
comboMbla2.grid(column=1, row=3)

# Entry - mbbla - Bitbabbler ID
selectedEntryId1 = tk.StringVar()
entryMblaId1 = tk.Entry(frameTab23, width=8, textvariable=selectedEntryId1)
selectedEntryId1.set("JA1ANI")
entryMblaId1.grid(column=0, row=3)
selectedEntryId2 = tk.StringVar()
entryMblaId2 = tk.Entry(frameTab23, width=8, textvariable=selectedEntryId2)
selectedEntryId2.set("OSYJHX")
entryMblaId2.grid(column=1, row=3)

lbl20 = tk.Label(frameTab21, text="Choose RNG",
                 font=("Arial Bold", 11),
                 padx=5, pady=5)  # Text inside window
lbl20.grid(column=0, row=0, sticky="ew")  # posição do label

lbl21 = tk.Label(frameTab22, text="RAW/XOR",
                 font=("Arial Bold", 11),
                 padx=5, pady=5)  # Text inside window
lbl21.grid(column=0, row=0, sticky="ew", columnspan=2)  # posição do label

lbl21i = tk.Label(frameTab22, text=" ",
                  font=("Arial Bold", 9))  # Text inside window
lbl21i.grid(column=0, row=2, sticky="ew")  # posição do label

lbl22 = tk.Label(frameTab23, text="BitBabblers IDs",
                 font=("Arial Bold", 11),
                 padx=5, pady=5)  # Text inside window
lbl22.grid(column=0, row=0, sticky="ew", columnspan=2)  # posição do label

lbl22i = tk.Label(frameTab23, text=" ",
                  font=("Arial Bold", 9))  # Text inside window
lbl22i.grid(column=0, row=1, sticky="ew")  # posição do label

lbl22ii = tk.Label(frameTab23, text=" ",
                   font=("Arial Bold", 9))  # Text inside window
lbl22ii.grid(column=0, row=2, sticky="ew")  # posição do label

# Imagem

matrix = Image.open("datafiles/matrix.jpg")
matrix = matrix.resize((200, 140), Image.ANTIALIAS)
matrixjov = ImageTk.PhotoImage(matrix)
labelmatrix = tk.Label(frameTab25, image=matrixjov)
labelmatrix.image = matrixjov
labelmatrix.grid(row=0, column=0, sticky="wens")


def bbla():  # criar função para quando o botão for clicado
    selectedCombo = comboBbla.get()
    global isCapturingOn
    isCapturingOn = True
    startupinfo = None
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    file_name = time.strftime("%Y%m%d-%H%M%S_bitb_f{}".format(selectedCombo))
    file_name = f"1-SavedFiles/{file_name}"
    while isCapturingOn:
        start_cap = int(time.time() * 1000)
        with open(file_name + '.bin', "ab") as bin_file:  # save binary file
            proc = subprocess.Popen("datafiles/seedd.exe --limit-max-xfer --no-qa -f{} -b 256".format(selectedCombo),
                                    stdout=subprocess.PIPE, startupinfo=startupinfo, stderr=subprocess.DEVNULL)
            chunk = proc.stdout.read()
            bin_file.write(chunk)
        bin_hex = BitArray(chunk)  # bin to hex
        bin_ascii = bin_hex.bin  # hex to ASCII
        num_ones_array = bin_ascii.count('1')  # count numbers of ones in the 2048 string
        with open(file_name + '.csv', "a+") as write_file:  # open file and append time and number of ones
            write_file.write('{} {}\n'.format(strftime("%H:%M:%S", localtime()), num_ones_array))
        end_cap = int(time.time() * 1000)
        # print(1 - (end_cap - start_cap)/1000)
        try:
            time.sleep(1 - (end_cap - start_cap) / 1000)
        except Exception:
            pass


def trng3():
    global isCapturingOn
    isCapturingOn = True
    blocksize = 256
    ports = dict()
    ports_avaiable = list(list_ports.comports())
    rng_com_port = None
    for temp in ports_avaiable:
        if temp[1].startswith("TrueRNG"):
            if rng_com_port == None:  # always chooses the 1st TrueRNG found
                rng_com_port = str(temp[0])
    file_name = time.strftime("%Y%m%d-%H%M%S_trng")
    file_name = f"1-SavedFiles/{file_name}"
    while isCapturingOn:
        start_cap = int(time.time() * 1000)
        with open(file_name + '.bin', "ab") as bin_file:  # save binary file
            try:
                ser = serial.Serial(port=rng_com_port, timeout=10)  # timeout set at 10 seconds in case the read fails
            except:
                print('Port Not Usable!')
                print('Do you have permissions set to read ' + rng_com_port + ' ?')
            if (ser.isOpen() == False):
                ser.open()
            ser.setDTR(True)
            ser.flushInput()
            try:
                x = ser.read(blocksize)  # read bytes from serial port
            except:
                print('Read Failed!!!')
            if bin_file != 0:
                bin_file.write(x)
            ser.close()
            if bin_file != 0:
                bin_file.close()
        bin_hex = BitArray(x)  # bin to hex
        bin_ascii = bin_hex.bin  # hex to ASCII
        num_ones_array = bin_ascii.count('1')  # count numbers of ones in the 2048 string
        with open(file_name + '.csv', "a+") as write_file:  # open file and append time and number of ones
            write_file.write('{} {}\n'.format(strftime("%H:%M:%S", localtime()), num_ones_array))
        end_cap = int(time.time() * 1000)
        # print(1 - (end_cap - start_cap) / 1000)
        try:
            time.sleep(1 - (end_cap - start_cap) / 1000)
        except Exception:
            pass


def mbbla():
    tk.messagebox.showinfo('Alert', 'Stil under development')


def startCollecting():  # criar função para quando o botão for clicado
    global isCapturingOn
    global selectedColeta
    if isCapturingOn == False:
        isCapturingOn = True
        if selectedColeta.get() == 1:
            threading.Thread(target=bbla).start()
        elif selectedColeta.get() == 2:
            threading.Thread(target=trng3).start()
        elif selectedColeta.get() == 3:
            mbbla()
            isCapturingOn = False
            return
        elif selectedColeta.get() == 4:
            threading.Thread(target=bbla).start()
            threading.Thread(target=trng3).start()
        tk.messagebox.showinfo('Alert', 'Capture Started, click "Stop" to finish.')
    else:
        tk.messagebox.showinfo('Alert', 'Already Capturing Data...')


def stopCollecting():
    global isCapturingOn
    global selectedColeta
    if isCapturingOn == True:
        isCapturingOn = False
        tk.messagebox.showinfo('File Saved', 'Salvo em ' + f"{script_path}/1-SavedFiles")
    else:
        tk.messagebox.showinfo('Alert', 'Capture not started')


btn21 = tk.Button(frameTab24, text="Start Capturing", bg="white", fg="blue",
                  command=startCollecting,
                  padx=5, pady=5)  # criar botão/ command=função do botão
btn21.grid(column=3, row=0, sticky="ew")  # posição do botão

btn22 = tk.Button(frameTab24, text="Stop", bg="white", fg="blue",
                  command=stopCollecting,
                  padx=5, pady=5)  # criar botão/ command=função do botão
btn22.grid(column=3, row=1, sticky="ew")  # posição do botão

# ------------------------------TAB3 -----------------------------------

# Frames
frameTab31 = tk.Frame(tab3, borderwidth="2", relief="ridge")
frameTab31.grid(column=0, row=0, sticky="ewns")

frameTab32 = tk.Frame(tab3, borderwidth="2", relief="ridge")
frameTab32.grid(column=1, row=0, sticky="ewns")

frameTab34 = tk.Frame(tab3, borderwidth="2", relief="ridge")
frameTab34.grid(column=2, row=0, sticky="ewns")

frameTab36 = tk.Frame(tab3, borderwidth="2", relief="ridge")
frameTab36.grid(column=0, row=1, sticky="ewns", columnspan=3)

frameTab37 = tk.Frame(tab3, borderwidth="2", relief="ridge")
frameTab37.grid(column=0, row=2, sticky="ewns", columnspan=3)

# Radiobuttons
selectedLive = tk.IntVar()
selectedLive.set(1)
radBlive = tk.ttk.Radiobutton(frameTab31, text='Bitbabbler', value=1, variable=selectedLive)
radTrngLive = tk.ttk.Radiobutton(frameTab31, text='TrueRng', value=2, variable=selectedLive)
radBlive.grid(column=0, row=1, sticky="ewns")
radTrngLive.grid(column=0, row=2, sticky="ewns")

# Combobox - bbla
selectedComboLive = tk.StringVar()
comboBLive = tk.ttk.Combobox(frameTab32, width=3)
comboBLive['values'] = (0, 1)
comboBLive.current(0)
comboBLive.grid(column=0, row=1)

# Labels
lbl30 = tk.Label(frameTab31, text="Choose RNG",
                 font=("Arial Bold", 11),
                 padx=5, pady=5)  # Text inside window
lbl30.grid(column=0, row=0, sticky="ew")  # posição do label

lbl31 = tk.Label(frameTab32, text="RAW/XOR",
                 font=("Arial Bold", 11),
                 padx=5, pady=5)  # Text inside window
lbl31.grid(column=0, row=0, sticky="ew")  # posição do label


# Funções
def livebblaWin():  # Function to take live data from bitbabbler
    global isLiveOn
    global zscore_array
    global index_number_array
    isLiveOn = True
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    selectedComboLive = comboBLive.get()
    file_name = time.strftime("%Y%m%d-%H%M%S_bitb_f{}".format(selectedComboLive))
    file_name = f"1-SavedFiles/{file_name}"
    index_number = 0
    csv_ones = []
    zscore_array = []
    index_number_array = []
    while isLiveOn:
        start_cap = int(time.time() * 1000)
        index_number += 1
        with open(file_name + '.bin', "ab+") as bin_file:  # save binary file
            proc = subprocess.Popen('datafiles/seedd.exe --limit-max-xfer --no-qa -f{} -b 256'.format(selectedComboLive),
                                    stdout=subprocess.PIPE, startupinfo=startupinfo)
            chunk = proc.stdout.read()
            bin_file.write(chunk)
        bin_hex = BitArray(chunk)  # bin to hex
        bin_ascii = bin_hex.bin  # hex to ASCII
        if not bin_ascii:
            isLiveOn = False
            tk.messagebox.showinfo('WARNING !!! ',
                                   'Something went wrong, is the device attached? Attach it and restart the program!!!')
            break
        num_ones_array = int(bin_ascii.count('1'))  # count numbers of ones in the 2048 string
        csv_ones.append(num_ones_array)
        sums_csv = sum(csv_ones)
        avrg_csv = sums_csv / index_number
        zscore_csv = (avrg_csv - 1024) / (22.62741699796 / (index_number ** 0.5))
        zscore_array.append(zscore_csv)
        index_number_array.append(index_number)
        with open(file_name + '.csv', "a+") as write_file:  # open file and append time and number of ones
            write_file.write('{} {}\n'.format(strftime("%H:%M:%S", localtime()), num_ones_array))
        end_cap = int(time.time() * 1000)
        # print(1 - (end_cap - start_cap) / 1000)
        try:
            time.sleep(1 - (end_cap - start_cap) / 1000)
        except Exception:
            pass


def trng3live():
    global isLiveOn
    global zscore_array
    global index_number_array
    isLiveOn = True
    file_name = time.strftime("%Y%m%d-%H%M%S_trng")
    file_name = f"1-SavedFiles/{file_name}"
    index_number = 0
    csv_ones = []
    zscore_array = []
    index_number_array = []
    blocksize = 256
    ports_avaiable = list(list_ports.comports())
    rng_com_port = None
    # Loop on all available ports to find TrueRNG
    for temp in ports_avaiable:
        if temp[1].startswith("TrueRNG"):
            if rng_com_port == None:  # always chooses the 1st TrueRNG found
                rng_com_port = str(temp[0])
    while isLiveOn:
        start_cap = int(time.time() * 1000)
        index_number += 1
        with open(file_name + '.bin', "ab+") as bin_file:  # save binary file
            try:
                ser = serial.Serial(port=rng_com_port,
                                    timeout=10)  # timeout set at 10 seconds in case the read fails
            except:
                print('Port Not Usable!')
                print('Do you have permissions set to read ' + rng_com_port + ' ?')
            # Open the serial port if it isn't open
            if (ser.isOpen() == False):
                try:
                    ser.open()
                except:
                    isLiveOn = False
                    tk.messagebox.showinfo('WARNING !!! ',
                                           'Something went wrong, is the device attached? Attach it and restart the program!!!')
                    return
            # Set Data Terminal Ready to start flow
            ser.setDTR(True)
            # This clears the receive buffer so we aren't using buffered data
            ser.flushInput()
            try:
                chunk = ser.read(blocksize)  # read bytes from serial port
            except:
                print('Read Failed!!!')
                # If we were able to open the file, write to disk
            if bin_file != 0:
                bin_file.write(chunk)
            # Close the serial port
            ser.close()
        bin_hex = BitArray(chunk)  # bin to hex
        bin_ascii = bin_hex.bin  # hex to ASCII
        num_ones_array = int(bin_ascii.count('1'))  # count numbers of ones in the 2048 string
        csv_ones.append(num_ones_array)
        sums_csv = sum(csv_ones)
        avrg_csv = sums_csv / index_number
        zscore_csv = (avrg_csv - 1024) / (22.62741699796 / (index_number ** 0.5))
        zscore_array.append(zscore_csv)
        index_number_array.append(index_number)
        with open(file_name + '.csv', "a+") as write_file:  # open file and append time and number of ones
            write_file.write('{} {}\n'.format(strftime("%H:%M:%S", localtime()), num_ones_array))
        end_cap = int(time.time() * 1000)
        # print(1 - (end_cap - start_cap) / 1000)
        try:
            time.sleep(1 - (end_cap - start_cap) / 1000)
        except Exception:
            pass


def livePlot():
    global selectedLive
    global isLiveOn
    if isLiveOn == True:
        tk.messagebox.showinfo('WARNING !!! ', ' Press Stop before starting new Plot')
        return
    else:
        if selectedLive.get() == 1:  # start Bitbabbler live
            threading.Thread(target=livebblaWin).start()
        elif selectedLive.get() == 2:  # start TrueRNG live
            threading.Thread(target=trng3live).start()


def stopLive():
    global isLiveOn
    if isLiveOn == True:
        isLiveOn = False
        # ani.event_source.stop()
        tk.messagebox.showinfo('File Saved', 'Saved in 1-SavedFiles')
    else:
        tk.messagebox.showinfo('Alert', 'Capure not started')


# Buttons
btn31 = tk.Button(frameTab34, text="Live Plot", bg="white", fg="blue",
                  command=livePlot,
                  padx=6, pady=6)  # criar botão/ command=função do botão
btn31.grid(column=2, row=0, sticky="ew")  # posição do botão

btn32 = tk.Button(frameTab34, text="Stop", bg="white", fg="blue",
                  command=stopLive,
                  padx=6, pady=6)  # criar botão/ command=função do botão
btn32.grid(column=2, row=1, sticky="ew")  # posição do botão



# Confirma saída do programa e fecha de vez
def confirmExit():
    if tk.messagebox.askokcancel('Quit', 'Are you sure you want to exit?'):
        global isLiveOn
        global isCapturingOn
        isLiveOn = False
        isCapturingOn = False
        time.sleep(0.5)
        window.destroy()


canvas = FigureCanvasTkAgg(f, frameTab36)
canvas.draw()
canvas.get_tk_widget().grid(row=1,column=0)
toolbar = NavigationToolbar2Tk(canvas, frameTab37)
ani = animation.FuncAnimation(f, animate, interval=1000)


window.protocol('WM_DELETE_WINDOW', confirmExit)

# need loop to maintain it open - Abre o tkinter e mantem em loop
tab_control.pack(expand=1, fill='both')
window.mainloop()


