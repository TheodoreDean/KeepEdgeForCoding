

from miio.device import Device


dev = Device("192.168.31.73","ed0ec8e98fd21edd701ee653713a293b")

# close
#dev.send("set_properties",[{'did': '575059092', 'siid':2,'piid':1 ,'value':False}])

# open
dev.send("set_properties",[{'did': '575059092', 'siid':2,'piid':1 ,'value':True}])


#miiocli device  --ip 192.168.31.73 --token ed0ec8e98fd21edd701ee653713a293b raw_command set_properties "[{'did': '575059092', 'siid':2,'piid':1 ,'value':True}]"
