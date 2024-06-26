###Socket manipulation ###

####precondition ####


> Wireshark

> Python3 

> PacketSender

#### Methodology ####

> refer to [https://github.com/OpenMiHome/mihome-binary-protocol/blob/master/doc/PROTOCOL.md]

> refer to [https://github.com/rytilahti/python-miio]



> The communication between IoT device and gateway is encrypted.

> The encryption key can be recovered by reverse engineering. 

#### Example ####

> MiIO protocol is UDP based socket protocol, which is using AES CBC mode for encryption.  

> For each device, the unique Token will be generated after registration on the Mi home app.

> AES key = md5(token)

> IV= md5(AES key + token)

> padding PKCS7 128
#### Step ####

1. By using Python script open the switch
```
miiocli device  --ip 192.168.31.7x --token xxxx5fa4853959f64f1e22ee6ccdxxxx raw_command set_properties "[{'did': '575059092', 'siid':2,'piid':1 ,'value':True}]"
```
2. Capture the network traffic by Wireshark

```
data format



0                   1                   2                   3   
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Magic number = 0x2131         | Packet Length (incl. header)  |
|-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-|
| Unknown1 0x0000                                               |
|-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-|
| Device ID ("did")  e.g., 0x 22 46 b4 94                       |
|-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-|
| TimeStamp          e.g., 0x 00 3a 25 39                       |
|-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-|
| MD5 checksum                                                  |
|-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-|
| optional variable-sized data (encrypted)                      |
|...............................................................|
```

> step1  send client hello packet 21 31 00 20 FF FF FF FF
![step1](https://github.com/TheodoreDean/KeepEdgeForCoding/blob/master/Units/032_iOS_python_Socket/step1%20client%20hello.png)

> step2 send handshake message and update the timestamp(time in hello packet+1)

![step2](https://github.com/TheodoreDean/KeepEdgeForCoding/blob/master/Units/032_iOS_python_Socket/step2%20handshake.png)

> step3 Send an actual control command
![step3](https://github.com/TheodoreDean/KeepEdgeForCoding/blob/master/Units/032_iOS_python_Socket/step3%20controll%20command.png)


```
e.g.,  plaintext as below
{"id": 1, "method":"set_properties","params":{"did": "575059092","siid":2,"piid":1,"value":true}};

```

[]



3. Craft the control script by using python-miio
```

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

```









 
