'''
UDP RECEIVER
Python version: 3.7.4
Authors: Shrikanth Sudhersan, Dhanraj Vedanth Raghunathan 

USAGE:
python3 p2mpserver.py output.out 0.05 7735
python3 p2mpserver.py 7735 output.out 0.05


'''

import random
import sys
import os      
import socket
import threading
from datetime import datetime
import pickle
import time
import random
from main_logic import *


#Global vars
UDP_IP_ADDRESS = ""
UDP_PORT_NO = int(sys.argv[1])
global_sq_num = 0
global_sq_num_exp = 0
sequence_flag = 0

'''
initial() function runs a while true loop; Everytime the the function receives data from the sender
it calls the function checksum_gen() [main_logic.py]and also uses the function in 'checksum_receiver.py'.
The output is fed to a logic that handles the possible sequencing and checksum errors that could occur.
'''

def decode_binary_string(s, encoding='UTF-8'):
    byte_string = ''.join(chr(int(s[i*8:i*8+8],2)) for i in range(len(s)//8))
    return byte_string

def initial():
    # print(os.path.join(os.getcwd(),'output.out'))
    if os.path.exists(str((os.path.join(os.getcwd(),'output.out')))):
        os.remove(os.path.join(os.getcwd(),'output.out'))
    global global_sq_num, global_sq_num_exp, sequence_flag
    msg = "ACK anupren"
    to_send = pickle.dumps(msg)
    print("Listening on port:", str(UDP_PORT_NO))
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

    while True:
        ###########################
        addrpair = serverSock
        addrpair = serverSock.recvfrom(9000)
        random_gen = random.uniform(0,1)
        random_gen = random_gen

        data = pickle.loads(addrpair[0])
        addr = addrpair[1]
        # print ("Message: ", data)
        # print("Sender Details:", addr)
        each = data
        if each[2] == '1111111111111111':
            return 0
        summed, current_sqn, datapat = checksum_gen(each)

        # print(summed)
        # print(each[1])
        checksum_result = bin(int(each[1],2) + int(summed,2))
        # print(checksum_result, current_sqn, datapat)
        # print("Checksum")
        # print(checksum_result)


        if datapat == '0101010101010101':
            if checksum_result == '0b1111111111111111':
                if sequence_flag == 0:
                    if str(random_gen) <= str(sys.argv[3]):
                        print("Dropping it due to threshold." + ', Current Sq no: ' + str(current_sqn))
                        print("Threshold:",str(sys.argv[3]))
                        print("Generated Probability",str(random_gen))
                    else: 
                        #print('first time')
                        global_sq_num = current_sqn
                        datt = []
                        to_send = str(global_sq_num)
                        datt.append(to_send)
                        datt.append('0000000000000000')
                        datt.append('1010101010101010')
                        serverSock.sendto(pickle.dumps(datt), addr)
                        global_sq_num_exp = global_sq_num + 1
                        # print(sequence_flag,global_sq_num,global_sq_num_exp)
                        sequence_flag = 1
                        with open(os.path.join(os.getcwd(),str(sys.argv[2])),'a+') as w:
                                to_write = decode_binary_string(each[3])
                                w.write(str(to_write))
                    
                    
                else: 
                    # print("inner if")
                    # print("Current, expected")
                    # print(global_sq_num,global_sq_num_exp)
                    if current_sqn != global_sq_num_exp:
                        print("Out of order, sending ACK for sq num last recv", str(global_sq_num))
                        datt = []
                        to_send = str(global_sq_num)
                        datt.append(to_send)
                        datt.append('0000000000000000')
                        datt.append('1010101010101010')
                        serverSock.sendto(pickle.dumps(datt), addr)
                        print(current_sqn)
                        # print(sequence_flag,global_sq_num,global_sq_num_exp)
                        # input()
                    if current_sqn == global_sq_num_exp:
                        if str(random_gen) <= str(sys.argv[3]):
                            print("Dropping it due to threshold." + ', Current Sq no: ' + str(current_sqn))
                            print("Threshold:",str(sys.argv[3]))
                            print("Generated Probability",str(random_gen))
                        else: 
                            print("In Order, Sending ACK")
                            ##Update sq num
                            print(current_sqn)
                            # print(sequence_flag,global_sq_num,global_sq_num_exp)
                            global_sq_num = global_sq_num_exp
                            global_sq_num_exp += 1
                            datt = []
                            to_send = str(global_sq_num)
                            datt.append(to_send)
                            datt.append('0000000000000000')
                            datt.append('1010101010101010')
                            serverSock.sendto(pickle.dumps(datt), addr)
                            #Write to a file
                            with open(os.path.join(os.getcwd(),str(sys.argv[2])),'a+') as w:
                                to_write = decode_binary_string(each[3])
                                w.write(str(to_write))

                        
                
            if checksum_result != '0b1111111111111111':
                print("Invalid Checksum, wont respond.")

                




initial()