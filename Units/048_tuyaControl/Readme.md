## TinyTuya 

### Precondition

> 1. python -m pip install tinytuya

> 2. get the localkey


### Steps


> 1. get familiar with protocol of the device. dps information of the device

> 2. Discover the device
```
python3 -m tinytuya scan

# get the IP and device ID.

# Excample as below
Unknown v3.4 Device   Product ID = svds85e3tkimokda  [Valid Broadcast]:
    Address = 192.168.8.88   Device ID = 6ca20a88c7d302606d2nld (len:22)  Local Key =   Version = 3.4  Type = default, MAC = 


```


> 3. monitor the message send from device via  monitor.py

> 4. control the device via the relevant scripts



