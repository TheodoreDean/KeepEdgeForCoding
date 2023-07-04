### Control Tuya IoT device in a LAN network environment

#### Testing environment

> 1. AirFryer 
> 2. Ubuntu 20.04 
> 3. tinytuya
[https://github.com/jasonacox/tinytuya]
> 4. tuyaapi
[https://github.com/codetheweb/tuyapi]

#### precondition

> 1. Must have Tuya account to retrieve the device ID and local key

> 2. The IoT should be paired with any offical APP, such Philips smart. Tuya smart.

#### Procedure

##### Get the local key


> 1. Register a developer account and retrieve the local key for specific device
[https://post.smzdm.com/p/a8x7de87/]

>> 1.1 login the website [https://auth.tuya.com/?from=http%3A%2F%2Fmyaccount.tuya.com%2Faccount]

>> 1.2 Get the device id whithin the same LAN. It requires to wake up the device.

```
python3 -m tinytuya scan

```
```
# the reply could be

TinyTuya (Tuya device scanner) [1.12.8]

Scanning on UDP ports 6666 and 6667 and 7000 for devices for 18 seconds...

Unknown v3.4 Device   Product ID = fcjlxz1c8v2rvqiu  [Valid Broadcast]:
    Address = 192.168.8.7   Device ID = 6c874057b686eb014bw7ry (len:22)  Local Key =   Version = 3.4  Type = default, MAC = 
    No Stats for 192.168.8.7: DEVICE KEY required to poll for status
Scan completed in 18.0926 seconds                  
                    
Scan Complete!  Found 1 devices.
Broadcasted: 1
Versions: 3.4: 1
Unknown Devices: 1

>> Saving device snapshot data to snapshot.json

```

>> 1.3 Create a new project and in the website [https://iot.tuya.com/cloud/basic?id=p16879212852435c8tae&toptab=project] get the access ID and Access key.

```
xjxcctyxw7kyjqvpk5kd
c7820007047c4c65880aabac3013d490

```

>> 1.4 then login the website [https://iot.tuya.com/cloud/explorer?id=p16879212852435c8tae&groupId=group-1633641687672688668&interfaceId=1633017151335964700] and get the local key with the device id above



```
tuya-cli wizard

#output
? Do you want to use these saved API credentials? xjxcctyxw7kyjqvpk5kd c7820007047c4c6
5880aabac3013d490 cn Yes
? Provide a 'virtual ID' of a device currently registered in the app: 6c874057b686eb01
4bw7ry
[
  {
    name: 'HD9880TOE1',
    id: '6c874057b686eb014bw7ry',
    key: 'Cn2mN8njH5j8KXas'
  }
]

```
Or refer to [https://github.com/codetheweb/tuyapi/blob/master/docs/SETUP.md] to get local key

Alternatively, reverse engineering on the APP and hack the local key




> 2. Create the python scripts

> First of all, sniff and monitor the traffic (what data points are used to implement different functionality)

> Secondly, modify the control traffic
 
critical part of the code

```
import tinytuya

# Connect to Device
d = tinytuya.CoverDevice(
    dev_id='6c874057b686eb014bw7ry',
    address='192.168.8.7',      
    local_key='Cn2mN8njH5j8KXas',
    version=3.4)

# Check the status
data = d.status()
print('set_status() result %r' % data)

# Craft the payload to start cooking
payload=d.generate_payload(tinytuya.CONTROL_NEW, {'6': 40, '9': 60, '10': 357, '101': 'cooking', '102': 'precook', '103': False, '104': 'ManualWoTProbe1'})
d._send_receive(payload)

```
> 3. The example can be seen in the scripts named startcook.py and pause.py

