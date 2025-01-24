from scapy.contrib.automotive.scanner.test_case import *
from scapy.contrib.automotive.uds_scan import *
from scapy.contrib.automotive.uds import *
from scapy.contrib.isotp import ISOTPNativeSocket
import random
import struct


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


	uds_param2 = b'\xed\xa7'

	uds_uintParam1 = int.from_bytes(uds_param1,'big')
	uds_uintParam2 = int.from_bytes(uds_param2,'big')



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
 


	

