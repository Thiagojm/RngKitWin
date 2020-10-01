import binascii
from textwrap import wrap

from bitstring import BitArray
import time


lista = ["111000", "101010", "000111"]

num_ones_array = list(map(lambda x: x.count("1"), lista))



# for i in lista:  # calculate number of 'ones' in each of the 2048 bits lines
#     num_ones_array.append(i.count('1'))

print(num_ones_array)

