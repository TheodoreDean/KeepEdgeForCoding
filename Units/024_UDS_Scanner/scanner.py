from scapy.all import *
from scapy.contrib.isotp import isotp_native_socket as ISOTPSocket
socket = ISOTPSocket('vcan0', sid=0x123, did=0x456, basecls=UDS)
uds_data = UDS() / UDS_DSC(diagnosticSessionType=0x03)
response = socket.sr1(uds_data)
