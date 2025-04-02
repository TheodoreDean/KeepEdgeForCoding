import pyvisa
import time
import matplotlib.pyplot as plt
from datetime import datetime
	

# Power supply configuration
VISA_ADDR = "TCPIP::192.168.40.80::5025:SOCKET"
SELECTED_CHANNEL = 2  # é€‰æ‹©1-3é€šé“
SAMPLING_TIME = 100    # æ€»é‡‡æ ·æ—¶é—´(ç§’)
INTERVAL = 0.1        # é‡‡æ ·é—´éš”(ç§’)


rm = pyvisa.ResourceManager()
print(rm.list_resources())
time.sleep(0.5)


myPower = rm.open_resource(VISA_ADDR)
#para= myPower.query('*IDN?')
#print(para)


#set up channel
#para= myPower.write('INSTrument:NSELect CHANnel 3')
#print(para)

#set up voltage
para= myPower.write('SOUR:VOLT 12,(@2)')
print(para)

#set up current
para= myPower.write('SOUR:CURR 1,(@2)')
print(para)

#set the channel
#myPower.write(f"INST:NSEL 2")

#turn on
para= myPower.write('OUTP ON,(@2)')
print(para)

# Measure Current and Voltage
timestamps, voltages, currents = [],[],[]
start_time=datetime.now()


plt.ion()
fig, ax = plt.subplots(2, 1, figsize=(10, 6))
plt.suptitle(f"Channel Monitoring - Keysight Power Supply")

while (datetime.now() - start_time).total_seconds() < SAMPLING_TIME:
	# èŽ·å–æµ‹é‡æ•°æ®
	current_time = (datetime.now() - start_time).total_seconds()
	voltage = float(myPower.query("MEAS:VOLT?").strip())
	current = float(myPower.query("MEAS:CURR?").strip())

	# å­˜å‚¨æ•°æ®
	timestamps.append(datetime.now())
	voltages.append(voltage)
	currents.append(current)

	# æ›´æ–°ç”µåŽ‹å›¾è¡¨
	ax[0].clear()
	ax[0].plot(timestamps, voltages, 'b-', label='Voltage')
	ax[0].set_ylabel('Voltage (V)')
	ax[0].grid(True)
	ax[0].legend()

	# æ›´æ–°ç”µæµå›¾è¡¨
	ax[1].clear()
	ax[1].plot(timestamps, currents, 'r-', label='Current')
	ax[1].set_ylabel('Current (A)')
	ax[1].set_xlabel('Time (s)')
	ax[1].grid(True)
	ax[1].legend()

	plt.tight_layout()
	plt.pause(0.01)
	time.sleep(INTERVAL)




print("wait 2 seconds")

#Query the volt
para= myPower.query('MEAS:VOLT?')
print(float(para.strip()))

#Query the current
para= myPower.query('MEAS:CURR?')
print(float(para.strip()))


#turn off
para= myPower.write('OUTP OFF,(@2)')
print(para)


# close the connection
para= myPower.close()
print(para)

#print(reply)
plt.ioff()
plt.show()
