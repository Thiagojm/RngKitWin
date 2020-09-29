import binascii
from textwrap import wrap

from bitstring import BitArray
import time


data_file = "1-SavedFiles/teste 1mb.bin"


def bit_array():
    start_func = time.time()
    with open(data_file, "rb") as file:  # open binary file
        bin_hex = BitArray(file)  # bin to hex
    bin_ascii = bin_hex.bin
    split_bin_ascii = wrap(bin_ascii, 2048) # 12 seg
    #split_bin_ascii = list(map(''.join, zip(*[iter(bin_ascii)] * 2048))) # 0.63 s
    print(split_bin_ascii)
    end_func = time.time()
    total_time = end_func - start_func
    print(total_time)

bit_array()




def apendando(): # 10seg
    o = []
    while bin_ascii:
        o.append(bin_ascii[:2048])
        bin_ascii = bin_ascii[2048:]