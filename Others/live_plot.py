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
        num_ones_array = bin_ascii.count('1') # count numbers of ones in the 2048 string
        with open(file_name + '.csv', "a+") as write_file: # open file and append time and number of ones
            write_file.write('{} {} {}\n'.format(index_number, strftime("%H:%M:%S", localtime()), num_ones_array))
        ztest = pd.read_csv((file_name + '.csv'), sep=' ', names=["Number", "Time", "Ones"])
        ztest.dropna(inplace=True)
        ztest['Sum'] = ztest['Ones'].cumsum()
        ztest['Average'] = ztest['Sum'] / (ztest['Number'])
        ztest['Zscore'] = (ztest['Average'] - 1024) / (22.62741699796 / (ztest['Number'] ** 0.5))
        print(ztest)
        #time.sleep(1)

bblaWin()

#thread_run_bbla = threading.Thread(target=bblaWin).start()

#time.sleep(10)
#is_bblaWin_on = False

#elapsed_time = timeit.timeit(bblaWin, number=1)/10 # time function 100 times
#print(elapsed_time)


def livePlotConf():
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