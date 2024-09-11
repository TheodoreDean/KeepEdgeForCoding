### Capture BLE with wireshark and nRF52840

#### precondition

> Wireshark

> python3

> nRF 52840


#### Steps

> refer to [https://blog.csdn.net/zl374216459/article/details/105102770]

> step 1 Set up Wireshark with nRF sniff tools
[https://www.nordicsemi.com/Products/Development-tools/nrf-sniffer-for-bluetooth-le/download]

> step 2 Change the path in Wireshark

> step 3 execut the following scripts in the C>\Program Files\Wireshark\extcap
```
nrf_sniffer_ble.bat --extcap-interfaces
```

> step 4 reopen the wireshark the nRF sniffer for Bluetooth LE COMX will appear.

> 
