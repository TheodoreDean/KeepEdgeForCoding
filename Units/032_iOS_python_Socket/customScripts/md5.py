import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import json
import datetime


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


def md5(data: bytes) -> bytes:
        """Calculates a md5 hashsum for the given bytes object."""
        checksum = hashlib.md5()  # nosec
        checksum.update(data)
        return checksum.digest()
        
testdata= bytes.fromhex('21310050000000002246b4940019831ced0ec8e98fd21edd701ee653713a293bc5af67375b4b32d5785c36373de1c562733589127721373b3fad8da6fb59d1f0a2f09fa4e7d181067e15325b408d2a3f')
testdata1=bytes.fromhex('21310080000000002246b4940011b837ed0ec8e98fd21edd701ee653713a293bd11c9c7f2eb387525cc66320569e0704bff3625384f2ada02b2c6df1e0f423fbaa4b123dc0a06bdd2bf2894074f41802a7260d1f043df1c897da391a0d808d9ad318c2df6c81d54dfcde8f4cba326fb0be593176e70d930b107c912bd69134c6')
testdata2=bytes.fromhex('21310080000000002246b4940011b837')
print('md5 i s',md5(testdata2))

 
print('md5 i s',md5(testdata).hex())

token = bytes.fromhex('ed0ec8e98fd21edd701ee653713a293b')
key = md5(token)
print("key is ",key.hex())

print("key + token is ",(key+token).hex())
IV =  md5(key+token)
print("IV is ",IV.hex())

# encryption 

'''
padder = padding.PKCS7(128).padder()
plaintext = bytes.fromhex("ed0ec8e98fd21edd701ee653713a293b")

padded_plaintext = padder.update(plaintext) + padder.finalize()
cipher = Cipher(algorithms.AES(key), modes.CBC(IV), backend=default_backend())
encryptor = cipher.encryptor()
ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

print("decryptedData is ",ciphertext.hex())

'''
#decrytion
ciphertext=bytes.fromhex("21310210000000002246b494003e8b55ef4bf0d07dac8b4976b9a8e6644a1b8dd11c9c7f2eb387525cc66320569e07047bc3c3eb37d14659af863b9c36253a182f8b1fb2e9b7950a412dfd328535caac1a81f3b184dff170366681b8c149027d0d4230c68ec3db49170100771630871092fa6e1a1e7585a35d97c1a7592774577f1bfdc700b58e4feee908dd21591a2cc4a48ceb2d20e1f0aa9c5d78028327268e9c519f9e6e7d74c1714bf5770e0a3f260409e5c191c4df071324a9653e98bc5b48d979850a300de7a94ef8c33b147a28497c1f8acb6a0237eb93a61a6d2870394bf9145568c252f21cd5f7138404665504e049a682ea29d9e91c56a807657dae9d256fdcdd1f20d32cd251429ac870a6afbe94cf82cbbe913b53aeb28d8010d8e2e5c3428af21730ed609a5f222d13f83adddb763573ee1ae8f99ddb75ce36ad32fccb49022790964836fe240aada4c049d96cc048a2019c0e898f6ea78a1dab1c1de148f7372aae2102c53b15dc5562aa24963545ca123c1c042688774e987d9e452fd280930737a4b8c90dba463b6afe4c0d0151a766d38af5962a06e75cd687678679d3954981ceb4322faa16eee20648fd84e1c4395a90f896139baad0897e33f47be04190047f3cf8805f096659760e515a3c4227a145818ce079885944896913c4562b71d242e459e40b47aaf6ad4b0345eaea94d3bcae84141b732d841a883413006beac4b4e91ed1309f77")
#plaintext is b'\xdb|\xc4\x89\x85\x81CB\xca\x00wz)\x0b\xc2\xd1\x98\xac\xec\x11u\xd0g\x92\x1b\xb7\x01\xfd\xa6y\xad\xe6\xae\xc6\xeec\xb9\x8a\xb2\x1cC\xae{H\xf2n3\xfa:{"life":4098901,"model":"cuco.plug.v3","token":"ed0ec8e98fd21edd701ee653713a293b","ipflag":1,"fw_ver":"1.0.7","mcu_fw_ver":"0018","miio_ver":"0.1.0","hw_ver":"ESP32C3","mmfree":42336,"workmode":2,"mac":"68:AB:BC:E6:21:5E","wifi_fw_ver":"WifiVer.N\\/A","ap":{"ssid":"Migao_Home","bssid":"C8:BF:4C:3A:62:3B","rssi":-53,"primary":1},"netif":{"localIp":"192.168.31.73","mask":"255.255.255.0","gw":"192.168.31.1"},"uid":1244457931,"config_type":"miwifi"},"exe_time":10}'

#ciphertext=bytes.fromhex("b3be8c917f0eaf0de885393e7b01792bb83848d13b46669562f5e7e4c7a07902e0bc3e92ffa21f204dbd080b8b03fd644aa18018bd0ae327ec26f8ea28330c30271dab538aa4b6a6592bf65abe1f83665d148abb0ed66db1a7fb42d21f6b3702f1a58b96bc25a33ac645c548d9d3db46")
#plaintext is  b'{"id": 1, "method": "miIO.info", "params": []}\x00'

#ciphertext=bytes.fromhex("b3be8c917f0eaf0de885393e7b01792bb83848d13b46669562f5e7e4c7a07902e0bc3e92ffa21f204dbd080b8b03fd644aa18018bd0ae327ec26f8ea28330c30271dab538aa4b6a6592bf65abe1f83665d148abb0ed66db1a7fb42d21f6b3702f1a58b96bc25a33ac645c548d9d3db46")
#plaintext is b'{"id": 2, "method": "set_properties", "params": [{"did": "575059092", "siid": 2, "piid": 1, "value": true}]}\x00'

#ciphertext=bytes.fromhex("6a5f94ddfd57d948fc5f778679c2b573a6871521c668b30d0752d1ee07bc91695ee6e7330e7e36a3862b779ea2f8e22d619e298df97d3f2d922f65290429730c7cc40d47176048fa32711c216a983f13c7d8190174dbb7d19ea220e7f5ac603ccf42240664871f8277829f6077a8839b")

cipher = Cipher(algorithms.AES(key), modes.CBC(IV), backend=default_backend())

decryptor = cipher.decryptor()
padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

unpadder = padding.PKCS7(128).unpadder()
unpadded_plaintext = unpadder.update(padded_plaintext)
unpadded_plaintext += unpadder.finalize()
print("plaintext is ",unpadded_plaintext)
print("plaintext is ",unpadded_plaintext.hex())

print("\n")


obj = {'did': '575059092', 'siid': 2,'piid': 1 ,'value': False}
jsondata = json.dumps(obj).encode("utf-8")
print("Jason data is",jsondata)
print("Jason type is data is", type(jsondata),jsondata.hex())


print("time is ",datetime.datetime.utcnow())

'''
15e1f96d5df88358
7dd8202cc05a2b86
29b5a81c622835de
3244edb45b578ef8

7b22646964223a20
2235373530353930
3932222c20227369
6964223a20322c20
2270696964223a20
312c202276616c75
65223a2066616c73
657d

#plaintext is  b'{"id": 1, "method": "miIO.info", "params": []}\x00'
7b226964223a2031
2c20226d6574686f
64223a20226d6949
4f2e696e666f222c
2022706172616d73
223a205b5d7d00



# 49b7681bba486a987022709b438479b7 
c5af67375b4b32d5
785c36373de1c562
65206bbdfb7496f8
9d9bbb09d24a1333
67dca34863c8ae4b
e9994fb3c7c7741b
30ea8191c345aa18
4efbae579cffdb0f
f2d297e9d2a52220
d29c1e4c2db1c493
48c385bb83d2b174
5c1a5950cd24ed39
ec4bf8724fb114dd
590e88139b855066

'''
'''
c5af67375b4b32d5785c36373de1c562733589127721373b3fad8da6fb59d1f0a2f09fa4e7d181067e15325b408d2a3f
'''





