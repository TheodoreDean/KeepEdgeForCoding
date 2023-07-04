# Author SGS Brightsight
# 2023.Jun29
import tinytuya



# Print Logo
print("""
 _____  _____  _____  ______        _         _      _         _         _      _   
/  ___||  __ \/  ___| | ___ \      (_)       | |    | |       (_)       | |    | |  
\ `--. | |  \/\ `--.  | |_/ / _ __  _   __ _ | |__  | |_  ___  _   __ _ | |__  | |_ 
 `--. \| | __  `--. \ | ___ \| '__|| | / _` || '_ \ | __|/ __|| | / _` || '_ \ | __|
/\__/ /| |_\ \/\__/ / | |_/ /| |   | || (_| || | | || |_ \__ \| || (_| || | | || |_ 
\____/  \____/\____/  \____/ |_|   |_| \__, ||_| |_| \__||___/|_| \__, ||_| |_| \__|
                                        __/ |                      __/ |            
                                       |___/                      |___/             
                                                                                                                                                                    
                                                                             
""")


print("""



  _____                                       _    _             
 |  __ \                                     | |  (_)            
 | |__) |_ _ _   _ ___  ___    ___ ___   ___ | | ___ _ __   __ _ 
 |  ___/ _` | | | / __|/ _ \  / __/ _ \ / _ \| |/ / | '_ \ / _` |
 | |  | (_| | |_| \__ \  __/ | (_| (_) | (_) |   <| | | | | (_| |
 |_|   \__,_|\__,_|___/\___|  \___\___/ \___/|_|\_\_|_| |_|\__, |
                                                            __/ |
                                                           |___/ 

                            
                             
                                      

""")


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

# pause
payload=d.generate_payload(tinytuya.CONTROL_NEW, {'6': 40, '9': 60, '10': 357, '101': 'pause', '102': 'cooking', '103': False, '104': 'ManualWoTProbe1'})
d._send_receive(payload)


data = d.status()
print('set_status() result %r' % data)
#print("Value of DPS 102 is ", data['dps']['102'])


# Start monitoring
d.set_socketPersistent(True)

print(" > Send Request for Status < ")
payload = d.generate_payload(tinytuya.DP_QUERY)
d.send(payload)

print(" > Begin Monitor Loop <")
while(True):
    # See if any data is available
    data = d.receive()
    print('Received Payload: %r' % data)

    # Send keyalive heartbeat
    print(" > Send Heartbeat Ping < ")
    payload = d.generate_payload(tinytuya.HEART_BEAT)
    d.send(payload)
    
