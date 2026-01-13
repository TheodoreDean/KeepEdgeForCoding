
import tinytuya

# Connect to Device
d = tinytuya.Device(
    dev_id='6ca20a88c7d302606d2nld',
    address='192.168.8.88',
    local_key='2_KT517Exzo$JFvV',
    version=3.4)

# Check the status
data = d.status()
print('set_status() result %r' % data)

# Craft the payload to start cooking
payload=d.generate_payload(tinytuya.CONTROL_NEW, {'1':True, '123':'False'})

data=d._send_receive(payload)


# Air volume switch to 3

payload=d.generate_payload(tinytuya.CONTROL_NEW, {'3':'S3', '4':'FS3'})
data=d._send_receive(payload)


