# Default imports
import time
import threading
import subprocess
import timeit
from time import localtime, strftime

# External imports
import pandas as pd
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from bitstring import BitArray
import serial
from serial.tools import list_ports

xor_value = 0

def sub_process():
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    proc = subprocess.Popen(f'datafiles/seedd.exe --limit-max-xfer --no-qa -f{xor_value} -b 256',
                                        stdout=subprocess.PIPE, startupinfo=startupinfo)
    chunk = proc.stdout.read()
    bin_hex = BitArray(chunk)  # bin to hex
    bin_ascii = bin_hex.bin  # hex to ASCII
    num_ones_array = bin_ascii.count('1')
    num_zeros_array = bin_ascii.count('0')
    print(num_ones_array, num_zeros_array, num_zeros_array + num_ones_array)

#sub_process()

print(timeit.timeit(sub_process, number=20)/20)