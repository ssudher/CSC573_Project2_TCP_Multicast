# sq_binary = format(data,"b")
# #print(sq_binary)
# binary_data = ''.join(padding(format(ord(i),'b')) for i in data)
def padding(inp):
        rem = 16 - len(inp)
        final = ''
        for i in range(0,rem):
            final = '0' + final 
        final = final+inp
        return(final)

def checksum_calculator(val):
    split_bits = []
    #print("OMALEEEE",val)
    binary_data = val

    len_binary = len(binary_data)
    while len_binary < 16:
        binary_data = str(0) + str(binary_data) 
        # #print(binary_data)
        len_binary = len(binary_data)
        #print(len_binary)
    # #print(binary_data)
    # #print(len_binary)

    if len_binary > 16:

        if len_binary % 16 == 0:
            pass

        else:
            while len_binary % 16 != 0:
                # #print("More work")
                binary_data = str(0) + str(binary_data) 
                len_binary = len(binary_data)
            
            # #print(binary_data)
            #print(len_binary)

    test_list = []
    for pos,data in enumerate(binary_data):
        test_list.append(data)                                          
        if (pos+1) % 16 == 0:
            # #print(len(test_list))
            split_bits.append(test_list)
            test_list = []

    # #print(split_bits)
    final_dict = {}


    for no, each in enumerate(split_bits):
        final_dict[no] = ''.join(each)

    # #print(final_dict)


    
    final_addition = 0

    for key,value in final_dict.items():
        c = 0
        if key == 0:
            c = bin(int(value,2) + int('0',2))
            final_addition = padding(c.split('b')[1]) 
            # #print("first time")
            # #print(c)
        else:
            # #print("Here now")
            # #print(value,c)
            # #print(value,final_addition)
            c = bin(int(value,2) + int(final_addition,2))
            length_addition = len(str(c).split('b')[1])
            # #print("Length of the added vals:",length_addition)
            new_value = str(c).split('b')[1][1:]
            # #print(new_value)
            # #print(bin(int(new_value,2)))


            if 17 == int(length_addition):
                # #print("in here")
                final_addition = bin(int(new_value,2) + int('1',2))
            else:
                # #print("down here")
                final_addition = c

    #print("!!!!!!!!!!!!!!!!!!!!!!!!!!",final_addition)
    final_add = padding(final_addition.split('b')[1])

    inverse = []
    for i in final_add:
        if i == '0':
            inverse.append('1')
        elif i == '1':
            inverse.append('0')

    sq_inv_binary = ''.join(inverse)


    # #print("sum:",final_add)
    # #print(type(final_add))
    # #print("checksum_Gen:",sq_inv_binary)


    # #print("Checksum check....\n")

    sum2 = bin(int(final_add,2) + int(sq_inv_binary,2))
    # #print(final_add)
    #print("KOOOTHII",sq_inv_binary)
    return sq_inv_binary


# op = checksum_calculator('0010000001110100011010000110100101110011')
# #print(op)
