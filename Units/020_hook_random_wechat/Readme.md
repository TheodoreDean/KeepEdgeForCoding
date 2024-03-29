### how to hook dice random function in wechat ###

#### requirements  ####
> MacOS with MUMU simulator

> adb frida

> wechat apk file (testing version)
> 链接: [https://pan.baidu.com/s/1t6tfuktEVVFygKWoxkVA-Q] 
> 密码: hw6c

> wechat 7.0.22 apk file
> 链接: [https://pan.baidu.com/s/1j1cK2ulFHLLq-Cujifs71Q] 
> 密码: pbw2

> jadx-gui 1.2.0
> Path: /usr/local/bin/jadx-gui

#### analysis steps ####
> decomplie the testing apk file by jadx-gui

> address the position where the random() are used(that's hardest part)

> basically, the idea to enumerate every place call  new emojiInfo(or any other key word for dice) and determin which is the one for dice.  
refer to [https://blog.sari3l.com/posts/5da99ec5/]
![search for the random function1](https://raw.githubusercontent.com/TheodoreDean/KeepEdgeForCoding/master/Units/020_hook_random_wechat/Screen%20Shot%202021-06-03%20at%201.59.59%20PM.png)
![search for the random function2](https://github.com/TheodoreDean/KeepEdgeForCoding/blob/master/Units/020_hook_random_wechat/Screen%20Shot%202021-06-03%20at%202.00.14%20PM.png)
![search for the random function3](https://github.com/TheodoreDean/KeepEdgeForCoding/blob/master/Units/020_hook_random_wechat/Screen%20Shot%202021-06-03%20at%202.00.52%20PM.png)

> the by.jV was found for the key operation for dice
> at com.tencent.mm.sdk.platformtools.by ,jV() call random(), which means by.jV need to hook

> craft the script and change the return value
```
Java.perform(function () {
var be= Java.use("com.tencent.mm.sdk.platformtools.by");
send(typeof(be));
send(typeof(be.jV));
send("start")
be.jV.implementation = function(){
    var type = arguments[0];
    send("start")
    send("type="+type);
    return 5;
};
send("end")
});

``` 
> samilarly, wechat 7.0.22(to 8.0.6) has the same random generation function just like by.jY(Util.getIntRandom).

#### execution steps ####
> open the MUMU simulator 

> connect it by using adb
```
adb connect 127.0.0.1:5555
adb shell
adb -s emulator-5554 shell //if necessary 
```

> execute the frida server

> Please be careful about the frida-server version (x86 or x64 depending on architecture of the device or emulator)

```
cd /data/local/tmp
./frida-server
```
> execute the frida with script
```
 frida -U -f com.tencent.mm -l hookwechat.js --no-pause

```

