import socket
import os
import threading
import subprocess
import random
import sys
import pickle
import time
import csv
from checksum_udp import *

# use this command to run!
# python3 p2mpclient.py receiver1 receiver2 receiver3 7735 ./data/actual.txt 500
# GLOBALS
rand_seq_number = 0
global_ack = {}
total_time = {}
data_collector = {}
timeout_value = 0
timer_interrupt_flag = 0
timer_interrupt_reset = 0

lock = threading.Lock()

def timer_interrupt():
    global timer_interrupt_reset
    global timeout_value
    global timer_interrupt_flag

    while(True):
        while True:
            # print('.spin')
            time.sleep(0.8)
            if(timer_interrupt_reset):
                break

        while(timeout_value>0):
            print("reducing timer: ",timeout_value)
            timeout_value -= 50
            time.sleep(0.2)

        print("TIMEOUT OCCURRED!")
        timer_interrupt_flag = 1
        # while(True):
        #     print(".")
        #     time.sleep(0.8)
        #     if(timer_interrupt_reset == 1):
        #         print('break!')
        #         break

timer = threading.Thread(name = "timer interrupt",target=timer_interrupt, args=())
timer.setDaemon(True)
timer.start()

# input("here")
# lock.acquire()
# print('resetting the timer')
# timer_interrupt_reset = 1
# timeout_value = 5000
# lock.release()
# while True:
#     print("waiting for global ack")
#     break_1 = input()
#     if(break_1):
#         break
#     pass

class Essentials:
    def __init__(self):
        self.MSS = 500
        self.file_name = ""
        self.destination_ip = []
        self.file_data = ""
        self.binary_rep = ""
        self.segment = {} # the dictionary that will have the segment information. {seq_no, checksum, pattern, data}

    # to convert any integer into a binary equivalent
    # (returns a String)
    def toBinary(self, n):
        return ''.join(str(1 & int(n) >> i) for i in range(32)[::-1])

    # based on the loop iterator, we can call this function which gives the corresponding chunk of data
    # (returns a String which is the binary equivalence of the data chunk)
    def create_data_segment(self, seq):
        # MSS*8 -> gives us MSS bytes of data, seq will give us the data according to the sequence in the loop
        # print("this is the binary from: ", (self.MSS*8*seq)," to: ", ((self.MSS*8*seq)+self.MSS*8))
        return self.binary_rep[(self.MSS*8*seq):((self.MSS*8*seq)+self.MSS*8)]

    def padding(self, inp):
        rem = 8 - len(inp)
        final = ''
        for i in range(0,rem):
            final = '0'+ final
        final = final+inp
        return(final)

    # reads the file given in the console and stores the required data
    def read_input_file(self):
        with open(self.file_name,"r",encoding='utf-8') as file:
            self.file_data = file.read()
        self.binary_rep = (''.join(self.padding(format(ord(x), 'b')) for x in self.file_data))
        # for elem in self.file_data:
        #     self.binary_rep = self.binary_rep + self.padding((format(ord(elem), 'b')))

    # this is the function to generate a random number for the first time to be used as the sequence_number
    # (returns a Interger value that can be used as a random number)
    def random_sequence_gen(self):
        rand_seq_number = (random.randint(1, 101))
        return(rand_seq_number)

    # just a initial function to extract the input args from the console.
    # (doesn't return anything)
    def extract_destinations(self):
        global global_ack

        self.MSS = int(sys.argv[-1])
        self.file_name = sys.argv[-2]
        for elem in sys.argv:
            if elem == 'p2mpclient.py':
                continue
            if elem == '7735':
                break
            self.destination_ip.append(elem)
        # print(self.MSS, self.file_name, self.destination_ip)
        # initialization the global acknowledgements to 0.
        # to keep track of all the acknowledgements
        for dest in self.destination_ip:
            global_ack[dest] = 0
            total_time[dest] = -1
            data_collector[dest] = []

ess = Essentials()
# to read the data from the console
ess.extract_destinations()
# to read the input file and convert it into its binary format
ess.read_input_file()

class Sender:
    def __init__(self):
        self.total_datagram_num = 0
        self.first_time = 0
        self.sequence_number = 0
        self.data_pattern = "0101010101010101" # this pattern indicates that segment is a data-segment.
        self.datagram = []
        self.tester = 100

    def global_ack_check(self):
        global global_ack
        final_ack = 1
        for dest in global_ack.keys():
            final_ack *= global_ack[dest]
        return final_ack

    def sender_listner(self, dest_ip, tid):
        global global_ack
        global timer_interrupt_flag
        global timer_interrupt_reset
        global timeout_value
        while True:
            Message = self.datagram
            success = 0
            bufferSize = 1024
            UDP_IP_ADDRESS = dest_ip
            UDP_PORT_NO = 7735
            acknowledgement_pattern = 0
            acknowledged_sequence = 0

            # to_send = str.encode(Message)
            clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            clientSock.settimeout(4)

            print("tid: ", tid, "-------Sending datagram seq: -------", self.datagram[0])
            to_send = pickle.dumps(Message)
            clientSock.sendto(to_send, (UDP_IP_ADDRESS, UDP_PORT_NO))
            sent_time = time.time()
            # start the timer here
            lock.acquire()
            timeout_value = 500
            timer_interrupt_flag = 0
            timer_interrupt_reset = 1
            lock.release()

            try:
                acknowledgement = clientSock.recvfrom(bufferSize)
                received_time = time.time()
                acknowledgement = pickle.loads(acknowledgement[0])
                print("tid: ", tid, "-------Receiving datagram seq: -------", acknowledgement[0])
            except Exception as e:
                acknowledgement = None
                received_time = time.time()
                acknowledgement_pattern = 0
                acknowledged_sequence = 0

            if(acknowledgement!=None):
                if(len(acknowledgement)==3):
                    acknowledged_sequence = acknowledgement[0]
                    acknowledgement_pattern = acknowledgement[2]

            # check if the sequence number is the one we expect.
            if (str(acknowledgement_pattern) == "1010101010101010"):
                if (str(acknowledged_sequence) == str(self.sequence_number)):
                    data_collector[dest_ip].append([self.sequence_number,(received_time-sent_time)])
                    print("tid: ",tid, "--------Acknowledgement accepted!!! seq: ", self.datagram[0], "\n\n\n")
                    global_ack[dest_ip] = 1
                    return 1
            else:
                data_collector[dest_ip].append([self.sequence_number, 0])
                # if the acknowledgement is not correct, spin here till timeout occurs
                while True:
                    # print("..",tid)
                    if (timer_interrupt_flag == 1):
                        print("tid: ",tid, "Timeout occurred for sequence number: ",self.sequence_number)
                        break

    def sending_function(self, destination, tid):
        global timer_interrupt_flag
        global timeout_value
        global timer_interrupt_reset
        global global_ack
        # print("total length of the file: ",len(ess.binary_rep),"This is the size of one datagram: ",ess.MSS)
        self.total_datagram_num = int((int(len(ess.binary_rep)/ess.MSS))/8)
        if(self.total_datagram_num==0):
            self.total_datagram_num = 1
        # print("total loops: ",self.total_datagram_num)
        for seq in range(0,self.total_datagram_num):
            # print("seq: ",seq,"-> tid: ",tid)
            # just resetting the acknowledgement for this thread!
            global_ack[destination] = 0
            if(self.first_time == 0):
                self.sequence_number = ess.random_sequence_gen()
                self.first_time = 1

            data = ess.create_data_segment(seq)
            # print("*****************************",data)
            checksum = checksum_calculator(str(data))
            # print("EPDI!!!!!!",checksum)
            self.datagram.clear()
            self.datagram.append(self.sequence_number)
            self.datagram.append(checksum)
            self.datagram.append(self.data_pattern)
            self.datagram.append(data)

            self.sender_listner(destination, tid)

            # print("seq: ",seq,"---tid:---",tid,"global ack: ",global_ack[destination],"----returned from sender!---%completed:", (seq/self.total_datagram_num)*100,"\n\n\n")
            # this is the place all the threads are going to spin till all the receivers have sent a positive ack.
            while(not(self.global_ack_check())):
                pass

            # this sleep is for solving the dead-lock situation and thread synchronization issues amongst threads.
            time.sleep(0.1)

            # stop the time here
            # making the timer_interrupt 0, makes the timer_thread to go into spin wait
            lock.acquire()
            timer_interrupt_reset = 0
            lock.release()
            self.sequence_number += 1

    def print_the_thread(self, IP):
        print("This is self.tester start", self.tester)
        self.tester = IP
        print("this is the self.tester end:", self.tester)


def final_ack(dest_ip):
    Message = ['','','1111111111111111','']
    bufferSize = 1024
    UDP_IP_ADDRESS = dest_ip
    UDP_PORT_NO = 7735

    # to_send = str.encode(Message)
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSock.settimeout(10)

    # print("Sending this: ", Message)
    to_send = pickle.dumps(Message)
    clientSock.sendto(to_send, (UDP_IP_ADDRESS, UDP_PORT_NO))
    return 1


def thread_handler(IP, t_num):
    print("*************************Thread ",t_num," started!!*********************")
    send = Sender()
    str_time = time.time()
    send.sending_function(IP, t_num)
    total_time[IP] = time.time() - str_time
    final_ack(IP)
    print("*************************Thread ",t_num," ended!!*********************")

threads = []
for index, IP in enumerate(ess.destination_ip):
    print('creating a thread for : ', IP)
    t = threading.Thread(name = "Worker func",target=thread_handler, args=(IP,index,))
    threads.append(t)
    t.start()

# wait for all the threads to complete

for t in threads:
    t.join()

# df = pd.DataFrame(data_collector)
output_name = 'output_recv_'+str(len(ess.destination_ip))+'_MSS_'+str(ess.MSS)+'.csv'
# print(output_name)
# df.to_excel("./data/"+output_name, index=False)

with open(output_name, "w+") as f:
    for key,val in data_collector.items():
        f.write(str(key) + ','+ str(total_time[key]) + '\n')
        for each in val:
            f.write(str(each[0]) + ',' + str(each[1]) + '\n')

print('_______________________________________________________________________________')
for d in data_collector.keys():
    print("DESTINATION: ",d, "time_taken: ",total_time[d])
    for item in data_collector[d]:
        print(item)
    print("\n-X-X-X--X-X-X--X-X-X-\n")
print('_______________________________________________________________________________')