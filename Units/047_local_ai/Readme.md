##Python call local AI

### Pre
>1. ollama install a local AI 
>2. create knowledge database
>3. in the same LAN

### Step

>1. configure on the server side

```
sudo vim /etc/systemd/system/ollama.service



#right after [Environment] insert
Environment="OLLAMA_HOST=0.0.0.0"

sudo systemctl daemon-reload
sudo systemctl restart ollama

```

>2. write the relevant code
```
refer to the python scripts in the root folder

```





