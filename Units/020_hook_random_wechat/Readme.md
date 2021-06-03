### how to hook dice random function in wechat ###

#### requirements  ####
> MacOS with MUMU simulator

> adb frida

> wechat apk file

#### analysis steps ####
> decomplie the apk file by jadx-gui

> address the position where the random() are used(that's hardest part)

> basically, the idea to enumerate every place call  new emojiInfo(or any other key word for dice) and determin which is the one for dice.  
refer to [https://blog.sari3l.com/posts/5da99ec5/]
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

#### execution steps ####
> open the MUMU simulator 

> connect it by using adb
```
adb connect 127.0.0.1:5555
adb shell
```

> execute the frida server
```
cd /data/local/tmp
./frida-server
```
> execute the frida with script
```
 frida -U -f com.tencent.mm -l hookwechat.js --no-pause

```

