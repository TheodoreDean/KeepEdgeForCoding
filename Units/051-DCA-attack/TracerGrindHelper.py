#!/usr/bin/env python
# for tracergrind trace format: exec message
global_execid = 0
global_ins_number = 0
global_codes_length = 0
global_addresses = b""
global_lengths = b""
global_codes = b""
global_mem_mesages = b""

def clear_global():
    global global_mem_mesages
    global global_ins_number
    global global_addresses
    global global_lengths
    global global_codes
    global global_codes_length
    global global_execid
    
    global_execid = 0
    global_ins_number = 0      
    global_codes_length = 0      
    global_addresses = b""      
    global_lengths = b""      
    global_codes = b""      
    global_mem_mesages = b""      
          


# callback for tracing basic blocks
def hook_block(trace):
    global global_mem_mesages
    global global_ins_number
    global global_addresses
    global global_lengths
    global global_codes
    global global_codes_length
    global global_execid

    if global_execid != 0:  # the first block
        # send memory message
        trace.write(global_mem_mesages)
        global_mem_mesages = b""

        # send the previous exec message
        trace.write((2).to_bytes(1, byteorder='big', signed=False))  # write message type 2=exec message   

        length = 41 + 9 * global_ins_number + global_codes_length
        trace.write(length.to_bytes(8, byteorder='little', signed=False))  # write message length

        trace.write(global_execid.to_bytes(8, byteorder='little', signed=True))  # write exec_id

        trace.write((1).to_bytes(8, byteorder='little', signed=False))  # write thread_id, always 1

        trace.write(global_ins_number.to_bytes(8, byteorder='little', signed=False))  # write number

        trace.write(global_codes_length.to_bytes(8, byteorder='little', signed=False))  # write code buffer length

        trace.write(global_addresses)  # write address buffer

        trace.write(global_lengths)  # write length buffer

        trace.write(global_codes)  # write code buffer
        #trace.flush()

    # clear the value
    global_mem_mesages = b""
    global_ins_number = 0
    global_codes_length = 0
    global_addresses = b""
    global_lengths = b""
    global_codes = b""
    global_execid += 1


# callback for tracing instructions
def hook_code(code, address, size):
    global global_ins_number
    global_ins_number += 1

    global global_addresses
    global_addresses = global_addresses + address
    global global_lengths
    global_lengths = global_lengths + size.to_bytes(1, byteorder='big', signed=False)
    global global_codes_length
    global_codes_length = global_codes_length + size
    global global_codes
    global_codes = global_codes + code


# callback for tracing memory access (READ or WRITE)
def hook_mem_access(insaddr, access, address, size, destreg1, destreg2):
    global global_mem_mesages
    data_len = len(destreg1) if destreg1 else int(size)
    if destreg2:
        data_len += len(destreg2) if isinstance(destreg2, (bytes, bytearray)) else int(size)
    # Total message size from type byte: 1 + 8 + 33 + data_len (must include destreg2 bytes).
    length = 42 + data_len
    global_mem_mesages = global_mem_mesages + (3).to_bytes(1, byteorder='big',
                                                           signed=False)  # write message type 3=memory message
    global_mem_mesages = global_mem_mesages + length.to_bytes(8, byteorder='little', signed=False)  # write length

    global_mem_mesages = global_mem_mesages + global_execid.to_bytes(8, byteorder='little',
                                                                     signed=True)  # write exec_id

    global_mem_mesages = global_mem_mesages + insaddr  # write instruction address

    if access == 1:
        global_mem_mesages = global_mem_mesages + (1).to_bytes(1, byteorder='big',
                                                               signed=False)  # write mode: 0=read 1=write
    else:  # READ
        global_mem_mesages = global_mem_mesages + (0).to_bytes(1, byteorder='big', signed=False)

    global_mem_mesages = global_mem_mesages + address.to_bytes(8, byteorder='little',
                                                               signed=False)  # write memory address
    global_mem_mesages = global_mem_mesages + data_len.to_bytes(8, byteorder='little',
                                                            signed=False)  # write data length
    global_mem_mesages = global_mem_mesages + destreg1  # write data
    if destreg2:
        global_mem_mesages = global_mem_mesages + destreg2  # write data (post-index / second operand)


def header(trace):
    # for TracerGrind, put the info msg at the begining of the trace
    trace.write((0).to_bytes(1, byteorder='big', signed=False))  # write message type 0=info message
    trace.write((9 + 24).to_bytes(1, byteorder='big', signed=False))  # write length
    trace.write(b"\x00\x00\x00\x00\x00\x00\x00")  # pad 7 00 for length field
    trace.write("TRACERGRIND_VERSION".encode())  # write STR_TRACERGRIND_VERSION , 19 bytes
    trace.write(b"\x00")  # write the end of a string
    trace.write("1.4".encode())  # write value
    trace.write(b"\x00")  # write the end of a string

    trace.write((0).to_bytes(1, byteorder='big', signed=False))  # write message type 0=info message
    trace.write((9 + 11).to_bytes(1, byteorder='big', signed=False))  # write length
    trace.write(b"\x00\x00\x00\x00\x00\x00\x00")  # pad 7 00 for length field
    trace.write("ARCH".encode())  # write ARCH , 4 bytes
    trace.write(b"\x00")  # write the end of a string
    trace.write("ARM64".encode())  # write value
    trace.write(b"\x00")  # write the end of a string
