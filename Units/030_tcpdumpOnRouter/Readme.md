#### capture the traffic on router


#### precondition

> ASUS AX86u-pro with SSH enabled

> install Wireshark

> Get tcpdump 

refer to [https://fw.koolcenter.com/binary/tcpdump/]


#### Steps
> refer to [https://www.jianshu.com/p/7fcf12ce4474]

> 1 install the PuTTY on Windows

> 2 scp ./tcpdump router@192.168.50.1:/tmp/home/root/

> 3 go to putty install path 
```
cd C:\ProgramData\Microsoft\Windows\Start Menu\Programs
``` 
> 4 execute the commands

```
plink.exe -batch -ssh -pw password router@192.168.50.1 "./tcpdump -n -i any -s 0 -w - not port 22" | "C:\Program Files\Wireshark\Wireshark.exe" -k -i -
```
