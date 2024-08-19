## Setup Scapy on Raspberry Pi  ###

#### Pre-condition
> Raspberry Pi 4B
> Extended board 2-CH-CAN-FD-HAT
> python3
> Scapy 2.5.0

#### Install 

```

apt-get install scapy

apt-get canutils
```

Set up extended board

refer to [https://www.waveshare.net/wiki/2-CH_CAN_FD_HAT]


#### Usage

```
sudo ip link set can0 up teype can bitrate 500000 dbitrate 2000000 restart-ms 1000 berr-reporting on fd on
sudo ifconfig can0 txqueuelen 65536



```
