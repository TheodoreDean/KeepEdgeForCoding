import socket
from datetime import datetime, timedelta
import json

from protocol import Message
from miioprotocol import MiIOProtocol
from construct import (
    Adapter,
    Bytes,
    Checksum,
    Const,
    Default,
    GreedyBytes,
    Hex,
    IfThenElse,
    Int16ub,
    Int32ub,
    Pointer,
    RawCopy,
    Rebuild,
    Struct,
)

helobytes = bytes.fromhex(
    "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.settimeout(5)

s.sendto(helobytes, ('192.168.31.73', 54321))
data, recv_addr = s.recvfrom(1024)
print('receive data is ',data.hex())
m: Message = Message.parse(data)
print('first m is ', m)
header = m.header.value
 
miioplug = MiIOProtocol()
miioplug._device_id = bytes.fromhex('2246b494')
miioplug._device_ts = header.ts
miioplug.ip = "192.168.31.73"
miioplug.token = bytes.fromhex('ed0ec8e98fd21edd701ee653713a293b')

# method 1
#miioplug.send("set_properties",[{'did': '575059092', 'siid':2,'piid':1 ,'value':True}])
#miioplug.send("set_properties",[{'did': '575059092', 'siid':2,'piid':1 ,'value':True}])


# method 2
request = miioplug._create_request("set_properties",[{'did': '575059092', 'siid':2,'value':True,'piid':1 }])

print('@@@@@@request is ',request)
send_ts = miioplug._device_ts + timedelta(seconds=1)
header = {
    "length": 0,
    "unknown": 0x00000000,
    "device_id": miioplug._device_id,
    "ts": send_ts,
}

msg = {"data": {"value": request}, "header": {"value": header}, "checksum": 0}



print('\n')
print('$$$$$message before build',msg)
print('\n')




m1 = Message.build(msg, token=miioplug.token)
print('\n')

print('&&&&&message after build',m1)
print('&&&&&message hex after build',m1.hex())

s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s1.settimeout(3)
s1.sendto(m1,(miioplug.ip,54321))

data, addr = s1.recvfrom(4096)
m2 = Message.parse(data, token=bytes.fromhex('ed0ec8e98fd21edd701ee653713a293b'))
print('######## hex',data.hex())
print('######## value',m2)



#21310080000000002246b4940011b837 cf84579b7e48bf2beac38dd52ad9ec69 #d11c9c7f2eb387525cc66320569e0704bff3625384f2ada02b2c6df1e0f423fbaa4b123dc0a06bdd2bf2894074f41802a7260d1f043df1c897da391a0d808d9ad318c2df6c81d54dfcde8f4cba326fb0be593176e70d930b107c912bd69134c6

#21310080000000002246b4940012e27a e0eb579c213df02e3d2a179313788f56
#d11c9c7f2eb387525cc66320569e0704bff3625384f2ada02b2c6df1e0f423fbaa4b123dc0a06bdd2bf2894074f41802a7260d1f043df1c897da391a0d808d9a0eb98ce51195a7c4a564746b085c1fb96a718cea9837ca5922666f6cd22fe07c










