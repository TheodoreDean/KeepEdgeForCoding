### Android root on Android 13 Jailbreak on iOS 15

#### Android root

##### Device and tool version

> Redmi Note 11 5G 
> Android MIUI 14.0.2
> Android 13
> Magisk 26.1

##### Steps

> 1. Unlock the device

> 2. Following the [https://www.bilibili.com/read/cv23129584/] 

> 3. Install Magisk and ADB tools(e.g., adb,fastboot and etc.) 

> 4.  Download the relevant images from [ https://xiaomirom.com/]

> And transfer the images to the device's path

> Click "安装" -> "选择并修补一个文件" 选择下载的镜像

> 修补后，/download 路径会出现 magisk_patched-XXXXX_XXXXX.img

> 导出后，使用fastboot指令进行刷机

```
fastboot devices
// the device will appear if anything is correct
fastboot flash boot_a  magisk_patched-XXXXX_XXXXX.img
fastboot flash boot_b  magisk_patched-XXXXX_XXXXX.img

``` 
> 5. Open the magisk APP and the magisk version (v26.1) shoule be appeared if rooted.



#### iOS 15 jailbreak

##### Device jailbreak

> iPhone SE 3
> iOS 15.4 
>  

##### steps

> generally refer to [https://baijiahao.baidu.com/s?id=1771528355850111229&wfr=spider&for=pc]

> 1. Install TrollStore following [https://github.com/opa334/TrollStore]
> 2. Install Dopamine following [https://ellekit.space/dopamine/]
> 3. Select Sileo
> 4. Note: Open the sileo and Reload the software resource page
> 5. Install Ellekit (The ellekit won't appear if you didn't reload/fresh in the software resource page)
> 6. Then install the Filza or other apps if necessary.









