from bitstring import BitArray, BitStream
import time
from time import localtime, strftime
import subprocess


def bblaWin():
    startupinfo = None
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    file_name = time.strftime("%Y%m%d-%H%M%S")
    is_true = 10
    while is_true != 0:
        is_true -= 1
        with open(file_name + '.bin', "ab") as bin_file: # save binary file
            proc = subprocess.Popen('seedd.exe --limit-max-xfer --no-qa -f1 -b 256', stdout=subprocess.PIPE, startupinfo=startupinfo)
            chunk = proc.stdout.read()
            bin_file.write(chunk)
        bin_hex = BitArray(chunk) # bin to hex
        bin_ascii = bin_hex.bin #hex to ASCII
        num_ones_array = bin_ascii.count('1') # count numbers of ones in the 2048 string
        with open(file_name + '.csv', "a+") as write_file: # open file and append time and number of ones
            write_file.write('{} {}\n'.format(strftime("%H:%M:%S", localtime()), num_ones_array))
        #time.sleep(1)


bblaWin()
