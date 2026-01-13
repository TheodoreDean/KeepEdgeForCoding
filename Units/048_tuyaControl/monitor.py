import tinytuya
import pyfiglet

text_slant = pyfiglet.figlet_format("Brightsight", font="slant")
print(text_slant)


# Connect to Device
d = tinytuya.Device(
    dev_id='6ca20a88c7d302606d2nld',
    address='192.168.8.88',
    local_key='2_KT517Exzo$JFvV',
    version=3.4)

# Check the status
data = d.status()
print('set_status() result %r' % data)


print(" > Begin Monitor Loop <")
while(True):
    # See if any data is available
    data = d.receive()
    print('Received Payload: %r' % data)






