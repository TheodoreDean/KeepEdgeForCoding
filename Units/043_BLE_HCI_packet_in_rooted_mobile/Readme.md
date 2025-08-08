### Capture BLE data in a rooted cellphone ###

#### Device

> 1. Xiaomi rooted device.
> 2. ADB


#### Step
refer to [!https://blog.csdn.net/weixin_41477306/article/details/127042849]


> 1. open the BLE capture function in developer option

> 2. *#*#5959#*#* to capture the BLE

> 3. Pair the device and control the device via the BLE

> 4. repeat *#*#5959#*#* to store the HCI log.

> 5. Get the data via ADB

```

adb pull /sdcard/MIUI/debug_log/bugreport-xxxx-xx-xx-xxxxx.zip

```

> 6. unzip the file and get the btsnoop_hci.log in /bugreport-2025-07-24-173806/common/com.android.bluetooth

> 7. Open the file via Wireshark
