#!/usr/bin/python3
# coding: utf-8


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
import xlsxwriter
import subprocess
from PIL import Image, ImageTk
import threading
from bitstring import BitArray, BitStream
from textwrap import wrap
import random



# define o local da onde o script esta sendo rodado
global script_path
global isCapturingOn
global selectedColeta
global selectedCombo
global selectedComboM1
global selectedComboM2
global selectedEntryId1
global selectedEntryId2
global selectedLive
global selectedComboLive
global bLiveName
global isLiveOn
script_path = os.getcwd()
isCapturingOn = False
isLiveOn = False

# Parametros tkinter
window = tk.Tk()
window.geometry('880x180')  # window size
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

bitB = Image.open("BitB.png")
bitB = bitB.resize((200, 140), Image.ANTIALIAS)
bitBjov = ImageTk.PhotoImage(bitB)
labelimg = tk.Label(frameTab13, image=bitBjov)
labelimg.image = bitBjov
labelimg.grid(row = 0, column = 0, sticky="wens")

projIm = Image.open("Proj.jpg")
projIm = projIm.resize((200, 140), Image.ANTIALIAS)
projImjov = ImageTk.PhotoImage(projIm)
labelimg2 = tk.Label(frameTab14, image=projImjov)
labelimg2.image = projImjov
labelimg2.grid(row = 0, column = 0, sticky="wens")


def open_file():
    global data_file
    data_file = filedialog.askopenfilename(initialdir=script_path, title="Select file",
                                filetypes=(("all files", "*.*"), ("Binary Files", '*.bin'), ("CSV Files", '*.csv')))
    lbl1.configure(text=data_file[-40::])
    btn1.configure(text="Select another file")



btn1 = tk.Button(frameTab12, text="Select File", bg="white", fg="blue",
                     command=open_file,
                     padx=5, pady=5)  # criar botão/ command=função do botão
btn1.grid(column=1, row=0, sticky="ew")  # posição do botão

# Linha 2 - Salvar arquivo para xlxs direto
lbl2 = tk.Label(frameTab11, text="Create .xlsx File",
                    font=("Arial Bold", 11),
                     padx=5, pady=5)  # Text inside window
lbl2.grid(column=0, row=1, sticky="ew")  # posição do label

def Ztesta():
    if data_file == "":
        tk.messagebox.showinfo('Atention','Select a file first')
    elif data_file[-3:] == "csv":
        ztest = pd.read_csv(data_file, sep=' ', names=["Time", "Ones"])
        ztest.dropna(inplace = True)
        ztest = ztest.reset_index()
        ztest['index'] = ztest['index'] + 1
        ztest['Sum'] = ztest['Ones'].cumsum()
        ztest['Average'] = ztest['Sum']/(ztest['index'])
        ztest['Zscore'] = (ztest['Average']-1024)/(22.62741699796/(ztest['index']**0.5))
        file_to_save =  data_file.replace(".csv", ".xlsx")
        data_file2 = os.path.basename(data_file)
        data_file2 = data_file2.replace(".csv", "")
        number_rows = len(ztest.index)
        writer = pd.ExcelWriter(file_to_save, engine='xlsxwriter')
        ztest.to_excel(writer,sheet_name='Z-Test',index=False)
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
        tk.messagebox.showinfo('File Saved','Saved as ' + file_to_save)
    elif data_file[-3:] == "bin":
        tk.messagebox.showinfo('Warning',"""This couls take several seconds, please wait.
Please do not close the Window.
Press OK to start Analysis.""")
        global num_ones_array
        num_ones_array = []
        with open(data_file, "rb") as file: # open binary file
            bin_hex = BitArray(file) # bin to hex
        bin_ascii = bin_hex.bin
        total_bits = len(bin_ascii)
        split_bin_ascii = wrap(bin_ascii, 2048) # split in 2048 bits per line - 1 second
        for i in split_bin_ascii: # calculate number of 'ones' in each of the 2048 bits lines
            num_ones_array.append(i.count('1'))
        binSheet = pd.DataFrame()                       # Array to Pandas Column
        binSheet['Ones'] = num_ones_array
        binSheet.dropna(inplace = True)
        binSheet = binSheet.reset_index()
        binSheet['index'] = binSheet['index'] + 1
        binSheet = binSheet.rename(columns = {'index': 'Time'})
        binSheet['Sum'] = binSheet['Ones'].cumsum()
        binSheet['Average'] = binSheet['Sum']/(binSheet['Time'])
        binSheet['Zscore'] = (binSheet['Average']-1024)/(22.62741699796/(binSheet['Time']**0.5))

        file_to_save = data_file.replace(".bin", ".xlsx")
        #data_file2 = os.path.basename(data_file)
        #data_file2 = data_file2.replace(".csv", "")
        number_rows = len(binSheet.Time)
        writer = pd.ExcelWriter(file_to_save, engine='xlsxwriter')
        binSheet.to_excel(writer,sheet_name='Z-Test',index=False)
        workbook = writer.book
        worksheet = writer.sheets['Z-Test']
        chart = workbook.add_chart({'type': 'line'})
        chart.set_title({
        'name': 'Z-Score: ',
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
        tk.messagebox.showinfo('File Saved','Saved as ' + (file_to_save + ".xlsx"))
    else:
        tk.messagebox.showinfo('Warning', 'Wrong File Type, Select a .bin or .csv file')

btn2 = tk.Button(frameTab12, text="Generate", bg="white", fg="blue",
                     command=Ztesta,
                     padx=5, pady=5)  # criar botão/ command=função do botão
btn2.grid(column=1, row=1, sticky="ew")  # posição do botão

# Linha 3 - Salvar as arquivo para xlxs
lbl3 = tk.Label(frameTab11, text="Create and Save as...",
                    font=("Arial Bold", 11),
                     padx=5, pady=5)  # Text inside window
lbl3.grid(column=0, row=2, sticky="ew")  # posição do label

def Ztest():
    if data_file == "":
        tk.messagebox.showinfo('Atention','Select a file first')
    elif data_file[-3:] == "csv":
        ztest = pd.read_csv(data_file, sep=' ', names=["Time", "Ones"])
        ztest.dropna(inplace = True)
        ztest = ztest.reset_index()
        ztest['index'] = ztest['index'] + 1
        ztest['Sum'] = ztest['Ones'].cumsum()
        ztest['Average'] = ztest['Sum']/(ztest['index'])
        ztest['Zscore'] = (ztest['Average']-1024)/(22.62741699796/(ztest['index']**0.5))
        data_file2 = os.path.basename(data_file)
        data_file2 = data_file2.replace(".csv", "")
        file_to_save =  filedialog.asksaveasfilename(initialdir=script_path,
                                                     initialfile=data_file2,
                                                     title="Select file", 
                                                     filetypes=(("XLSX Files", '*.xlsx'),("all files","*.*")))
        number_rows = len(ztest.index)
        writer = pd.ExcelWriter((file_to_save + ".xlsx"), engine='xlsxwriter')
        ztest.to_excel(writer,sheet_name='Z-Test',index=False)
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
        tk.messagebox.showinfo('File Saved','Saved as ' + file_to_save)
    elif data_file[-3:] == "bin":
        data_file2 = os.path.basename(data_file)
        data_file2 = data_file2.replace(".bin", "")
        file_to_save =  filedialog.asksaveasfilename(initialdir=script_path,
                                                     initialfile=data_file2,
                                                     title="Select file", 
                                                     filetypes=(("XLSX Files", '*.xlsx'),("all files","*.*")))
        tk.messagebox.showinfo('Warning',"""This couls take several seconds, please wait.
Please do not close the Window.
Press OK to start Analysis.""")
        global num_ones_array
        num_ones_array = []
        with open(data_file, "rb") as file: # open binary file
            bin_hex = BitArray(file) # bin to hex
        bin_ascii = bin_hex.bin
        total_bits = len(bin_ascii)
        split_bin_ascii = wrap(bin_ascii, 2048) # split in 2048 bits per line - 1 second
        for i in split_bin_ascii: # calculate number of 'ones' in each of the 2048 bits lines
            num_ones_array.append(i.count('1'))
        binSheet = pd.DataFrame()                       # Array to Pandas Column
        binSheet['Ones'] = num_ones_array
        binSheet.dropna(inplace = True)
        binSheet = binSheet.reset_index()
        binSheet['index'] = binSheet['index'] + 1
        binSheet = binSheet.rename(columns = {'index': 'Time'})
        binSheet['Sum'] = binSheet['Ones'].cumsum()
        binSheet['Average'] = binSheet['Sum']/(binSheet['Time'])
        binSheet['Zscore'] = (binSheet['Average']-1024)/(22.62741699796/(binSheet['Time']**0.5))

        file_to_save = file_to_save.replace(".bin", ".xlsx")
        #data_file2 = os.path.basename(data_file)
        #data_file2 = data_file2.replace(".csv", "")
        number_rows = len(binSheet.Time)
        writer = pd.ExcelWriter((file_to_save + ".xlsx"), engine='xlsxwriter')
        binSheet.to_excel(writer,sheet_name='Z-Test',index=False)
        workbook = writer.book
        worksheet = writer.sheets['Z-Test']
        chart = workbook.add_chart({'type': 'line'})
        chart.set_title({
        'name': 'Z-Score: ',
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
        tk.messagebox.showinfo('File Saved','Saved as ' + (file_to_save + ".xlsx"))        
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
radBbla = tk.ttk.Radiobutton(frameTab21,text='Bitbabbler', value=1, variable=selectedColeta)
radTrng = tk.ttk.Radiobutton(frameTab21,text='TrueRng', value=2, variable=selectedColeta)
radMbbla = tk.ttk.Radiobutton(frameTab21,text='Two Bitbabbler', value=3, variable=selectedColeta)
radMrng = tk.ttk.Radiobutton(frameTab21,text='Bitbabbler + TrueRng', value=4, variable=selectedColeta)
radBbla.grid(column=0, row=1, sticky="ew")
radTrng.grid(column=0, row=2, sticky="ew")
radMbbla.grid(column=0, row=3, sticky="ew")
radMrng.grid(column=0, row=4, sticky="ew")

# Combobox - bbla
selectedCombo = tk.StringVar()
comboBbla = tk.ttk.Combobox(frameTab22, width=3)
comboBbla['values']= (0, 1, 2, 3, 4)
comboBbla.current(0)
comboBbla.grid(column=0, row=1)

# Combobox - mbbla - Raw/XOR
selectedComboM1 = tk.StringVar()
comboMbla1 = tk.ttk.Combobox(frameTab22, width=3)
comboMbla1['values']= (0, 1, 2, 3, 4)
comboMbla1.current(0)
comboMbla1.grid(column=0, row=3)
selectedComboM2 = tk.StringVar()
comboMbla2 = tk.ttk.Combobox(frameTab22, width=3)
comboMbla2['values']= (0, 1, 2, 3, 4)
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

matrix = Image.open("matrix.jpg")
matrix = matrix.resize((200, 140), Image.ANTIALIAS)
matrixjov = ImageTk.PhotoImage(matrix)
labelmatrix = tk.Label(frameTab25, image=matrixjov)
labelmatrix.image = matrixjov
labelmatrix.grid(row = 0, column = 0, sticky="wens")


def bbla():  # criar função para quando o botão for clicado
    selectedCombo = comboBbla.get()
    subprocess.run(["./bbla f{}".format(selectedCombo)], shell=True)


def rng():  # criar função para quando o botão for clicado
    #subprocess.call('.\RNG Capture.bat')
    file_name = time.strftime("%Y%m%d-%H%M%S")
    is_true = 20
    while is_true != 0:
        is_true -= 1
        #with open('/dev/random', "rb") as file:  # open binary file
            #chunk = file.read(256)  # define number of bytes to read
        list = []
        for x in range(2048):
            list.append(random.randint(0, 1))
        chunk = ''.join((str(e) for e in list))
        num_ones_array = chunk.count('1')  # count numbers of ones in the 2048 string
        with open(file_name + '.csv', "a+") as write_file:  # open file and append time and number of ones
            write_file.write('{} {}\n'.format(strftime("%H:%M:%S", localtime()), num_ones_array))
        time.sleep(1)


def mbbla():
    selectedComboM1 = comboMbla1.get()
    selectedComboM2 = comboMbla2.get()
    selectedEntryId1 = entryMblaId1.get()
    selectedEntryId2 = entryMblaId2.get()
    subprocess.run(["./mbbla f{} f{} {} {}".format(selectedComboM1, selectedComboM2, selectedEntryId1, selectedEntryId2)], shell=True)
    

def mrng():
    tk.messagebox.showinfo('Alert','Still under development')


def startCollecting():  # criar função para quando o botão for clicado
    global isCapturingOn
    global selectedColeta
    if isCapturingOn == False:
        isCapturingOn = True
        if selectedColeta.get() == 1:
            bbla()
        elif selectedColeta.get() == 2:
            rng()
        elif selectedColeta.get() == 3:
            mbbla()
        elif selectedColeta.get() == 4:
            mrng()
        tk.messagebox.showinfo('Alert','Capture Started, click "Stop" to finish.')      
    else:
        tk.messagebox.showinfo('Alert','Already Capturing Data...')


def stopCollecting():
    global isCapturingOn
    global selectedColeta
    if isCapturingOn == True:
        isCapturingOn = False
        if selectedColeta.get() == 1:
            subprocess.run(["ps -ef | awk '/bbla/{print$2}' | sudo xargs kill 2>/dev/null"], shell=True)   
        elif selectedColeta.get() == 2:
            subprocess.run(["ps -ef | awk '/rng/{print$2}' | sudo xargs kill 2>/dev/null"], shell=True)
        elif selectedColeta.get() == 3:
            subprocess.run(["ps -ef | awk '/mbbla/{print$2}' | sudo xargs kill 2>/dev/null"], shell=True)
        elif selectedColeta.get() == 4:
            subprocess.run(["ps -ef | awk '/mrng/{print$2}' | sudo xargs kill 2>/dev/null"], shell=True)
        tk.messagebox.showinfo('File Saved','Salvo em ' + script_path + '/coletas')
    else:
        tk.messagebox.showinfo('Alert','Capture not started')



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
frameTab31.grid(column=0, row=0, sticky="ns")

frameTab32 = tk.Frame(tab3, borderwidth="2", relief="ridge")
frameTab32.grid(column=1, row=0, sticky="ns")

frameTab33 = tk.Frame(tab3, borderwidth="2", relief="ridge")
frameTab33.grid(column=2, row=0, sticky="ns")

frameTab34 = tk.Frame(tab3, borderwidth="2", relief="ridge")
frameTab34.grid(column=3, row=0, sticky="ns")

frameTab35 = tk.Frame(tab3, borderwidth="2", relief="ridge")
frameTab35.grid(column=4, row=0, sticky="ns")

# Radiobuttons
selectedLive = tk.IntVar()
selectedLive.set(1)
radBlive = tk.ttk.Radiobutton(frameTab31,text='Bitbabbler', value=1, variable=selectedLive)
radTrngLive = tk.ttk.Radiobutton(frameTab31,text='TrueRng', value=2, variable=selectedLive)
radBlive.grid(column=0, row=1, sticky="ewns")
radTrngLive.grid(column=0, row=2, sticky="ewns")

# Combobox - bbla
selectedComboLive = tk.StringVar()
comboBLive = tk.ttk.Combobox(frameTab32, width=3)
comboBLive['values']= (0, 1, 2, 3, 4)
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
lbl31.grid(column=0, row=0, sticky="ew", columnspan=2)  # posição do label

lbl31i = tk.Label(frameTab32, text=" ",
                     font=("Arial Bold", 9))  # Text inside window
lbl31i.grid(column=0, row=2, sticky="ew")  # posição do label

# Funções

def livePlotConf():
    subprocess.run(["ps -ef | awk '/blive/{print$2}' | sudo xargs kill 2>/dev/null"], shell=True)
    subprocess.run(["ps -ef | awk '/rnglive/{print$2}' | sudo xargs kill 2>/dev/null"], shell=True)
    plt.rcParams["figure.figsize"] = (12, 6)
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    global bLiveName
    global script_path
    global selectedLive
    bLiveName = time.strftime("%Y%m%d-%H%M%S")
    selectedComboLive = comboBLive.get()
    if selectedLive.get() == 1:
        subprocess.run(["./blive {} f{}".format(bLiveName, selectedComboLive)], shell=True)
    elif selectedLive.get() == 2:
        subprocess.run(["./rnglive {}".format(bLiveName)], shell=True)
    def animate(i):
        pullData = open((script_path + "/coletas/" + bLiveName + "zscore.txt"), "r").read()
        dataArray = pullData.split('\n')
        xar = []
        yar = []
        for eachLine in dataArray:
            if len(eachLine) > 1:
                x, y = eachLine.split(' ')
                xar.append(x)
                yar.append(float(y))
        ax1.clear()
        ax1.grid()
        ax1.plot(xar, yar, marker='o', color='orange')
        ax1.tick_params(axis='x', rotation=45)
        ax1.set_title("Live Plot")
        ax1.set_xticks(ax1.get_xticks()[::5])
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()


def livePlot():
    threading.Thread(target=livePlotConf).start()
    global isLiveOn
    isLiveOn = True


def stopLive():
    global isLiveOn
    global selectedComboLive
    if isLiveOn == True:
        isLiveOn = False
        if selectedLive.get() == 1:
            subprocess.run(["ps -ef | awk '/blive/{print$2}' | sudo xargs kill 2>/dev/null"], shell=True)   
        elif selectedLive.get() == 2:
            subprocess.run(["ps -ef | awk '/rnglive/{print$2}' | sudo xargs kill 2>/dev/null"], shell=True)
        tk.messagebox.showinfo('WARNING !!! ',' Close the Graph window before acquiring new Data!!')
    else:
        tk.messagebox.showinfo('Alert','Capure not started')

# Buttons
btn31 = tk.Button(frameTab34, text="Live Plot", bg="white", fg="blue",
                     command=livePlot,
                     padx=5, pady=5)  # criar botão/ command=função do botão
btn31.grid(column=3, row=0, sticky="ew")  # posição do botão

btn32 = tk.Button(frameTab34, text="Stop", bg="white", fg="blue",
                     command=stopLive,
                     padx=5, pady=5)  # criar botão/ command=função do botão
btn32.grid(column=3, row=1, sticky="ew")  # posição do botão

# Image

graph = Image.open("graph.png")
graph = graph.resize((200, 140), Image.ANTIALIAS)
graphjov = ImageTk.PhotoImage(graph)
labelGraph = tk.Label(frameTab35, image=graphjov)
labelGraph.image = graphjov
labelGraph.grid(row = 0, column = 0, sticky="wens")


# Confirma saída do programa e fecha de vez
def confirmExit():
    if tk.messagebox.askokcancel('Quit', 'Are you sure you want to exit?'):
        window.destroy()


window.protocol('WM_DELETE_WINDOW', confirmExit)


# need loop to maintain it open - Abre o tkinter e mantem em loop
tab_control.pack(expand=1, fill='both')
window.mainloop()  


