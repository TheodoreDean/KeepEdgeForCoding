Hook local key by using Frida


### Environment and tools

> Netease MUMU x64
> Please be aware Frida-server should be consistent with the simulator architecture

> Frida 16.0.19

> Philips Smart home apk 2.0.6  or Tuya smart apk 5.0 


### Procedure

> 1 Get a rooted device or simulator

> 2 run Frida server in the device or simulator


```
adb shell
#or 
adb -s emulator-5444 shell
```
> if none works

```

adb kill-server
adb restart-server

```
> then


```
cd /data/local/tmp

./Frida-server x86 or ./Frida-server x64
```

> 3 start a new shell

```
# check all the processes and package name such as com.xxx.xxx
Frida-ps -U

# hook the getLocalKey function

frida -U -f com.philips.dachinaiot -l deviceRspBean.js
 
```

> 4 the result can be seen

![hooked localkey](https://github.com/TheodoreDean/KeepEdgeForCoding/blob/master/Units/027_hookLocalkey/philips%20app%20hook%20local%20key.png)





