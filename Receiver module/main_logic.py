'''
UDP RECEIVER- Subfunction
Python version: 3.7.4
Authors: Shrikanth Sudhersan, Dhanraj Vedanth Raghunathan 
'''

import os
import re 
from checksum_receiver import *


'''
This script is used as a part of the main UDP receiver logic. The function checksum_gen() uses functions 
from the file 'checksum_receiver' by invoking the 'checksum_calculator()' funtion.
This logic returns back the calculated sum for the data part of the message.
'''
def checksum_checker(final_add):
    inverse = []
    for i in final_add:
        if i == '0':
            inverse.append('1')
        elif i == '1':
            inverse.append('0')

    sq_inv_binary = ''.join(inverse)
    # print("Checksum check....\n")

    sum2 = bin(int(final_add,2) + int(sq_inv_binary,2))
    # print(sum2)
    return sq_inv_binary, sum2

def checksum_gen(data_rcv):
    seq_num, checksum, datapattern, data = data_rcv

    # print(seq_num, checksum, datapattern, data)

    final_data = checksum_calculator(data)
    # print("Final data")
    # print(final_data)

    # inverse_data, checksum_result = checksum_checker(final_data)

    # print("Inverse and checksum")
    # print(inverse_data, checksum_result)

    return final_data, seq_num, datapattern



