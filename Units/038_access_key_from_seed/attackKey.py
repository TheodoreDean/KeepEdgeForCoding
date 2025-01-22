from scapy.contrib.automotive.scanner.test_case import *
from scapy.contrib.automotive.uds_scan import *
from scapy.contrib.automotive.uds import *
from scapy.contrib.isotp import ISOTPNativeSocket
import random
import struct

#CAN FD
#socket = ISOTPNativeSocket('can0', tx_id=0x760, rx_id=0x770, padding=True, basecls=UDS,fd=True)

#CAN
socket = ISOTPNativeSocket('can1', tx_id=0x760, rx_id=0x770, padding=True, basecls=UDS)


'''
# no loop
uds_data=socket.sr1(UDS(service=0x11)/UDS_ER(b'\x01'),timeout=2)
print("reset")

time.sleep(4)
uds_data=socket.sr1(UDS(service=0x10)/UDS_DSC(diagnosticSessionType=0x03))
print('10 03 service response ',bytes(uds_data).hex())

uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\xD0\x03'))
print('31 D0 03 service response',bytes(uds_data).hex())	
uds_data=socket.sr1(UDS(service=0x85)/UDS_CDTCS(b'\x02'))
print('31 85 82 service response',bytes(uds_data).hex())
uds_data=socket.sr1(UDS(service=0x28)/UDS_CC(b'\x01\x03'))
print('28 81 03 service response',bytes(uds_data).hex())

uds_data=socket.sr1(UDS(service=0x10)/UDS_DSC(diagnosticSessionType=0x02),timeout=2)
#	print('10 02 service response ',bytes(uds_data).hex())
'''		

#tp = UDS_TesterPresentSender(sock=socket, interval=0.5, pkt=UDS(service=0x3E) / UDS_TP(subFunction=0x80))
#tp.start()

#uds_data=socket.sr1(UDS()/UDS_TP('\x80'))


def seedToKey(seedParam,keyParam):
	security_constant = b'\xed\xa7'
	uds_uintParam1 = int.from_bytes(seedParam,'big')
	uds_uintParam2 = int.from_bytes(security_constant,'big')
	uds_local_c = uds_uintParam1 ^ uds_uintParam2
	for j in range(32):
# in python convert int to unsigned int need to be done with someIntvalue & 0xFFFFFFFF 
		uds_local_c = (((uds_local_c << 7) & 0xFFFFFFFF) | ((uds_local_c >> 0x19) & 0xFFFFFFFF)) ^ uds_uintParam2
	keyParam = uds_local_c.to_bytes(4,"big")
	return keyParam	


for i in range(100):	


# no reset
	uds_data=socket.sr1(UDS(service=0x11)/UDS_ER(b'\x01'),timeout=2)
	print("reset")

	time.sleep(4)
	
	uds_data=socket.sr1(UDS(service=0x10)/UDS_DSC(diagnosticSessionType=0x03))
	print('10 03 service response ',bytes(uds_data).hex())

	uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\xD0\x03'))
	print('31 D0 03 service response',bytes(uds_data).hex())	
	uds_data=socket.sr1(UDS(service=0x85)/UDS_CDTCS(b'\x02'))
	print('31 85 82 service response',bytes(uds_data).hex())
	uds_data=socket.sr1(UDS(service=0x28)/UDS_CC(b'\x01\x03'))
	print('28 81 03 service response',bytes(uds_data).hex())

		print('67 07 service response',bytes(uds_data).hex())
		uds_param1 = bytes(uds_data)[2:6]
		print('67 07 seed response',bytes(uds_data)[2:6].hex())

		
#	file.write(bytes(uds_data).hex()+"\n") 

	uds_data=socket.sr1(UDS(service=0x3E)/UDS_TP(subFunction=0x80),timeout=0.5)	
	uds_data=socket.sr1(UDS(service=0x3E)/UDS_TP(subFunction=0x80),timeout=0.5)	
	uds_data=socket.sr1(UDS(service=0x3E)/UDS_TP(subFunction=0x80),timeout=0.5)	
	uds_data=socket.sr1(UDS(service=0x3E)/UDS_TP(subFunction=0x80),timeout=0.5)	
	uds_data=socket.sr1(UDS(service=0x3E)/UDS_TP(subFunction=0x80),timeout=0.5)	
	uds_data=socket.sr1(UDS(service=0x3E)/UDS_TP(subFunction=0x80),timeout=0.5)	
	uds_data=socket.sr1(UDS(service=0x3E)/UDS_TP(subFunction=0x80),timeout=0.5)	
	uds_data=socket.sr1(UDS(service=0x3E)/UDS_TP(subFunction=0x80),timeout=0.5)	
	uds_data=socket.sr1(UDS(service=0x3E)/UDS_TP(subFunction=0x80),timeout=0.5)	
	uds_data=socket.sr1(UDS(service=0x3E)/UDS_TP(subFunction=0x80),timeout=0.5)	
	uds_data=socket.sr1(UDS(service=0x3E)/UDS_TP(subFunction=0x80),timeout=0.5)	
	uds_data=socket.sr1(UDS(service=0x3E)/UDS_TP(subFunction=0x80),timeout=0.5)	

#	fuzzdata = random.randbytes(4)
#	byte_sequence = {random.randbytes(4) for _ in range(0x10)}
#	print(byte_sequence)
# level =1 
#	uds_data=socket.sr1(UDS(service=0x27)/UDS_SA(b'\x08\xb4\xb5\xd3\xca'),timeout=2)

# level =5
#	uds_data=socket.sr1(UDS(service=0x27)/UDS_SA(b'\x08\x11\x81\x86\xc0'),timeout=2)

# level =3
#	uds_data=socket.sr1(UDS(service=0x27)/UDS_SA(b'\x08\x03\xbe\xb4\x0e'),timeout=2)	

	uds_param2 = b'\xed\xa7'

	uds_uintParam1 = int.from_bytes(uds_param1,'big')
	uds_uintParam2 = int.from_bytes(uds_param2,'big')


#	uds_uintParam1 = struct.unpack("I",uds_param1)[0]
#	uds_uintParam2 = struct.unpack("<H",uds_param2)[0]

	uds_local_c = uds_uintParam1 ^ uds_uintParam2
	

	print('pre uds local_c value ',uds_local_c)
	

	for j in range(32):
		uds_local_c = (((uds_local_c << 7) & 0xFFFFFFFF) | ((uds_local_c >> 0x19) & 0xFFFFFFFF)) ^ uds_uintParam2
#		uds_local_c = (uds_local_c << 7 | uds_local_c >> 0x19) ^ uds_uintParam2
	
#	uds_local_c = uds_local_c & 0xFFFFFFFF	
		
	print('post uds local_c value ',uds_local_c)
#	packed_local_c = struct.pack('>I',uds_local_c)
	packed_local_c = uds_local_c.to_bytes(4,"big")

	print('packed local c is',packed_local_c)
	keyValue=b'\x00\x00\x00\x00'
	keyValue = seedToKey(uds_param1,keyValue)
	print('key value',keyValue.hex())
# level =7
	uds_data=socket.sr1(UDS(service=0x27)/UDS_SA(b'\x08'+keyValue),timeout=2)	
	
	if (uds_data != None):
		print('67 08 service response',bytes(uds_data).hex())
	time.sleep(5)


	#print('27 07 service response',bytes(uds_data).hex())
 

'''

for i in range(1000000):	
	print('start loop No.', i)
#	tp = UDS_TesterPresentSender(sock=socket, interval=0.5, pkt=UDS() / UDS_TP(b'\x80'))
#	tp.start()
#	time.sleep(2)
#	tp.stop()

	uds_data=socket.sr1(UDS(service=0x10)/UDS_DSC(diagnosticSessionType=0x02),timeout=2)
	#	print('10 02 service response ',bytes(uds_data).hex())
			

	tp = UDS_TesterPresentSender(sock=socket, interval=0.5,pkt=UDS() / UDS_TP(b'\x80'))
	tp.start()


	uds_data=socket.sr1(UDS(service=0x27)/UDS_SA(b'\x07'))
	print('27 07 service response',bytes(uds_data).hex())
	tp.stop()

	
	new_uds_data=bytes(uds_data)[2:18]
	print(new_uds_data.hex())
	print(i)
	file.write(new_uds_data.hex()+"\n") 

'''


#	uds_data=socket.sr1(UDS(service=0x27)/UDS_SA(b'\x62\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'))
#	print('27 62 service response',bytes(uds_data).hex())

#	uds_data=socket.sr1(UDS(service=0x11)/UDS_DSC(diagnosticSessionType=0x01))
#	print('11 01 service response ',bytes(uds_data).hex())	

#	uds_data=socket.sr1(UDS(service=0x27)/UDS_SA(b'\x03',securityAccessType=0x03))
#	print(bytes(uds_data).hex())

#	uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\x0f\x28\x02',routineControlType=0x01))
#00 reply   71010f28 00 000 9 000000 0003 000001 0003 000100 0003 000101 0003 000102 0003 010001 0003 00e5dc 0003 001d1a 0003 001d1b0003
#01 reply	71010f28 00 000 8 000000 0003 000001 0003 000100 0003 000101 0003 000102 0003 00e5dc 0003 001d1a 0003 001d1b 0003
#02 reply   71010f28 00 000 1 010001 0003

# para fuzzing
#	uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\x0f\x28'+ random.randbytes(1),routineControlType=0x01))

#	print('31 01 0f 28 xx service ',bytes(uds_data).hex())
	
#	uds_data=socket.sr1(UDS(service=0x10)/UDS_DSC(diagnosticSessionType=0x3))
#	print('1003 service ',bytes(uds_data).hex())	

#	uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\x0f\x29\x00\x01\x01\x01',routineControlType=0x01))
#	print('31 01 0f 29 00 01 00 01 service ',bytes(uds_data).hex())
		
#	uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\x0f\x29\x00\xe5\xdc\x00',routineControlType=0x01))
#	print('31 01 0f 29 00 xx xx 00 service ',bytes(uds_data).hex())

#00 00 00 00 00 reply  71010f29 00 000000
#00 00 00 00 01 reply  71010f29 00 000000 0300000000000000000000000000000000000000000000000000000000
#00 00 00 01 01 reply  71010f29 00 000100 0300000000000000000000000000000000000000000000000000000000
#00 00 00 01 00 reply  71010f29 00 000100

#00 00 01 00 00 reply  71010f29 00 010000
#00 00 01 00 01 reply  71010f29 00 010000 0300000000000000000000000000000000000000000000000000000000
#00 00 01 01 00 reply  71010f29 00 010100
#00 00 01 01 01 reply  71010f29 00 010100 0300000000000000000000000000000000000000000000000000000000



# 62 f190 57 4d 57 31 31 47 43 30 33 30 48 59 30 36 31 35 38
#31 
#	uds_data=socket.sr1(UDS(service=0x2E)/UDS_WDBI(b'\xF1\x90\x56\x4d\x57\x31\x31\x47\x43\x30\x33\x30\x48\x59\x30\x36\x31\x35\x38'))
#	print('2E  service ',bytes(uds_data).hex())
	
'''	
	uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\x0f\x2A\x00\x1d\x1a\x00\x11\x22\x33\x44\x55',routineControlType=0x01))
	print('31 01 0f 2A 00 00 00 01 service ',bytes(uds_data).hex())
	fuzzdata= random.randbytes(1)
	print(fuzzdata)
	uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\x0f\x2B\x00\x1d\x1a'+fuzzdata,routineControlType=0x01))
	print('31 01 0f 2B 00 00 00 01 service ',bytes(uds_data).hex())	
	if bytes(uds_data) != b'\x7f\x31\x22':
		print("bingo")
		file= open('discoverNewParameters.txt','a')
		file.write(fuzzdata)
		file.write('\n')

'''
	
#  	time.sleep(6)

#	uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\x0f\x2c',routineControlType=0x01))
#	print('31 01 0f 01 service ',bytes(uds_data).hex())
#	uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\x0f\x0c\x04',routineControlType=0x01))
#	print('31 01 0f 02 service ',bytes(uds_data).hex())
		
#	uds_data=socket.sr1(UDS(service=0x10)/UDS_DSC(diagnosticSessionType=0x03),verbose=False)
#	uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\x0f\x0c\x03',routineControlType=0x01))
#	uds_data=socket.sr1(UDS(service=0x85)/UDS_CDTCS(b'\x02'))
#	uds_data=socket.sr1(UDS(service=0x28)/UDS_CC(b'\x01\x01'))
#	uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\x10\x03\x01',routineControlType=0x01))
#	uds_data=socket.sr1(UDS(service=0x10)/UDS_DSC(diagnosticSessionType=0x02),verbose=False)

#	uds_data=socket.sr1(UDS(service=0x11)/UDS_DSC(diagnosticSessionType=0x01),verbose=False)
#	print('11 01 service ',bytes(uds_data).hex())

#	file.write(bytes(uds_data).hex())
#	file.write('\n')
'''
bytes(UDS(service=0x27)/UDS_SA(b'\x11\xFF\xFF\xFF\xFF',secu  tyAccessType=0x11)).hex()

#reset 

uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\x0f\x0c\x00',routineControlType=0x01))

'''
''' # fuzz 0f 0c 00
for i in range(10000000):
	print('start loop No.', i)
	uds_data=socket.sr1(UDS(service=0x10)/UDS_DSC(diagnosticSessionType=0x3))
	uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\x0f\x0c\x00',routineControlType=0x01))
	print('31 01 0f 00 service ',bytes(uds_data).hex())
	time.sleep(6)

	uds_data=socket.sr1(UDS(service=0x31)/UDS_RC(b'\x01\x0f\x0c\x01',routineControlType=0x01))
	print('31 01 0f 01 service ',bytes(uds_data).hex())
'''
