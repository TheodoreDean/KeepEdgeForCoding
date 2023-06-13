### Dump and decrypt iOS application on App store ###

#### General methodology 
>1. Jailbreak the iphone 
>2. Download the app from App Store
>3. By using Frida decrypt the application dynamically from flash and export the IPA file accordingly.

#### Environment
> Jailbreak iphone 
>> Iphone 5s on iOS 12.5.7

> Macbook 
>> MacOS 13.1

>> Frida-ios-dump

#### Steps
>1. Jailbreak the iPhone5s with checkra1n
[https://checkra.in/]

> Please be aware the DFU mode only can be entered by standard USB cable.(Type-C is not working!!!) 

>2. Install Cydia provided in Checkra1n then install the necessary plug-in such as AFC2 for 64bits and AppSync
[https://www.i4.cn/news_detail_1623.html]

>3. Download the app form App Store or install it with IPA file.

>4. Install Frida 
>>install frida-ios-dump on Mac
[https://github.com/AloneMonkey/frida-ios-dump]
```
sudo mkdir /opt/dump && cd /opt/dump && sudo git clone https://github.com/AloneMonkey/frida-ios-dump

#install required library
sudo pip install -r /opt/dump/frida-ios-dump/requirements.txt --upgrade

# change the parameters(account or pwd if necessary)
vim /opt/dump/frida-ios-dump/dump.py

# parameters by default
#User = 'root'
#Password = 'alpine'
#Host = 'localhost'
#Port = 2222
```


>>install frida on iPhone in Cydia

>>add source [https://build.frida.re] and install Frida on iPhone.

>>login iPhone via ssh and killall SpringBoard.

>5. Install USB proxy on Mac

refer to [https://www.jianshu.com/p/80c1311530c3]

```
brew install usbmuxd  
```

> open termial 1 and execute (or simply open the terminal on i4tools) 
```
iproxy 2222 22 (port mapping)
```

> open termial 2 and execute
```
ssh -p 2222 root@127.0.0.1
```
> the pwd is as above

> open terminal 3 and execute

> Please be aware that the app must running on the iPhone in the meantime.
```
cd /opt/dump/frida-ios-dump/

python3 dump.py -l 

sudo python3 dump.py com.xx.xx.xx

```


