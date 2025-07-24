#### Get token from Xiaomi Cloud

##### Steps

##### 
>1. download the python scripts from https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor


>2. run the scripts and input the password 


>3. Get the 2FA link in the shell.

>4. Open the link in browser and F12 to get the detail meata data.

>  
```
self._ssecurity = "######"
self.userId = "66666666"
self._cUserId = "######"
self._passToken = None
self._location = None
self._code = None
self._serviceToken = "******"
```
> refer to the screenshot in the root folder


> The general steps to modify the scripts

```
github\Xiaomi-cloud-tokens-extractor> python .\token_extractor.py
Username (email or user ID):
33366699933
Password:
Server (one of: cn, de, us, ru, tw, sg, in, i2) Leave empty to check all available:
cn
Logging in...
Two factor authentication required, please use following url and restart extractor:
https://account.xiaomi.com/identity/authStart?sid=xiaomiio&context=***

Step 2 : Click the provided 2FA link, complete the authentication, and retrieve the following four parameters from your browser. For details, refer to steps 5 and 6 of the 10-step guide.
Step 3 : Populate the following fields in the init method of the XiaomiCloudConnector class in token_extractor.py:
self._ssecurity = "######"
self.userId = "66666666"
self._cUserId = "######"
self._passToken = None
self._location = None
self._code = None
self._serviceToken = "******"

Step 4 : Modify the login logic in the main function:
logged = connector.login() => logged = True

Step 5 : Restart the extractor. No username or password is required.
github\Xiaomi-cloud-tokens-extractor> python .\token_extractor.py
Username (email or user ID):
Password:
Server (one of: cn, de, us, ru, tw, sg, in, i2) Leave empty to check all available:
cn
Logging in...
Logged in.
Devices found for server "cn" @ home "725001278743":
NAME: Xiaomi Smart Home Hub 2



```
