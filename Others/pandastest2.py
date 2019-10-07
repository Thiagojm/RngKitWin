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


def livebblaWin():
    global is_bblaWin_on
    global file_name
    global zscore_array
    global index_number_array
    is_bblaWin_on = True
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    file_name = time.strftime("%Y%m%d-%H%M%S")
    index_number = 0
    csv_ones = []
    zscore_array = []
    index_number_array = []
    #selectedComboLive = comboBLive.get()
    while is_bblaWin_on:
        start_cap = int(time.time() * 1000)
        index_number += 1
        with open(file_name + '.bin', "ab") as bin_file: # save binary file
            proc = subprocess.Popen('seedd.exe --limit-max-xfer --no-qa -f{} -b 256'.format(1), stdout=subprocess.PIPE, startupinfo=startupinfo)
            chunk = proc.stdout.read()
            bin_file.write(chunk)
        bin_hex = BitArray(chunk) # bin to hex
        bin_ascii = bin_hex.bin #hex to ASCII
        num_ones_array = int(bin_ascii.count('1')) # count numbers of ones in the 2048 string
        csv_ones.append(num_ones_array)
        #print(csv_ones)
        sums_csv = sum(csv_ones)
        #print(sums_csv)
        avrg_csv = sums_csv / index_number
        #print(avrg_csv)
        zscore_csv = (avrg_csv - 1024) / (22.62741699796 / (index_number ** 0.5))
        #print(zscore_csv)
        zscore_array.append(zscore_csv)
        index_number_array.append(index_number)
        #with open(file_name + '.csv', "a+") as write_file:  # open file and append time and number of ones
        #    write_file.write('{} {}\n'.format(strftime("%H:%M:%S", localtime()), num_ones_array))
        end_cap = int(time.time() * 1000)
        print(1 - (end_cap - start_cap)/1000)
        try:
            time.sleep(1 - (end_cap - start_cap) / 1000)
        except Exception:
            pass

threading.Thread(target=livebblaWin).start()
time.sleep(4)

def livePlotConf():
    plt.rcParams["figure.figsize"] = (6, 3)
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)

    def animate(i):
        xar = index_number_array
        yar = zscore_array
        ax1.clear()
        ax1.grid()
        ax1.plot(xar, yar, marker='o', color='orange')
        #ax1.tick_params(axis='x', rotation=45)
        ax1.set_title("Live Plot")
        #ax1.set_xticks(ax1.get_xticks()[::5])
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()

threading.Thread(target=livePlotConf).start()
