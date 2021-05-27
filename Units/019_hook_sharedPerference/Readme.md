### Demo for Hook sharedPerference by Frida ###

#### requirements ####

> MacOS + Netease MUMU simulator + ADB + Frida 

> DIVA apk
[https://blog.csdn.net/Everywhere_wwx/article/details/82256421]

> Android studio


#### sharedPerference in Android ####

> public functions and internal functions

please refer to 
[https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/app/SharedPreferencesImpl.java]

#### how to write JS code to hook #####
>please refer to the 
[https://frida.re/docs/examples/android/]

#### steps ####
>1. run frida server in /data/local/tmp after connecting with simulator from MAC by 

```
adb connect 127.0.0.1:5555
#if 0 
//if necessary
adb -s emulator-5554 shell
#end if
```
>smoke-test 
```
frida-ps -U
```
>2. then craft the JS code to hook the putString() and getString() method

> 3. then run frida
```
frida -U -f jakhar.aseem.diva -l hookSharedPerference.js --no-pause
```
>4. try to access the notes. The log will reveal the notespin by reading the k-v value stored in sharedperference.

