import binascii
from textwrap import wrap

from bitstring import BitArray
import re
import time

data_file = "1-SavedFiles/20200224T121659-t.bin"



with open(data_file, "rb") as file:  # open binary file
    bin_hex = BitArray(file)  # bin to hex

bin_ascii = bin_hex.bin

start = time.time()
#split_bin_ascii = list(map(''.join, zip(*[iter(bin_ascii)] * 2048)))  # Waaaaay faster then wrap
split_bin_ascii = re.findall("." * 2048, bin_ascii)
end = time.time()

#num_ones_array = list(map(lambda x: x.count("1"), split_bin_ascii))

print(end - start)




# for i in lista:  # calculate number of 'ones' in each of the 2048 bits lines
#     num_ones_array.append(i.count('1'))



