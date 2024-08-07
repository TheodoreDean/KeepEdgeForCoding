### IoT controller by home assistant with homekit on iOS


#### pre-condition

> 1. install Docker on ubuntu 22.04

> 2. install Home assistant

> 3. install HACS（3rd party store） 

> 4. get Xiaomi miot plug-in

> 5. get homekit plug-in



#### Steps

#####

> 1. install docker on Ubuntu

> refer to [!https://blog.csdn.net/lml1781978327/article/details/133608062]

> 2. install home assistant (docker images)

```
docker pull homeassistant/home-assistant

docker run -d --name="home-assistants" -v /root/home:/config -p 8123:8123 homeassistant/home-assistant:latest

docker ps -a

docker container update --restart=always 容器ID

```

> 3. install HACS inside the home assistant

> first of all, enter the terminal of the home assistant
```
docker images


docker start CONTAINER ID
// Please be aware that the ID of one instance is unique. This command will start/restart the specific image.

docker ps 
//check the running container and get the ID of the container

docker exec -it ID /bin/bash 
// enter the inside of the container

```



> then install the HACS refer to [https://github.com/hacs-china]

```
wget -O - https://hacs.vip/get | bash -

//offical website
wget -O - https://install.hacs.xyz | bash -


```

> 4. Get the token and configure it in the Xiaomi Miot and Homekit bridge.
```
Use one homekit bridge via home assistant
one bridge maps to multiple IoT devices
in iOS home app, set up all IoT devices's name and control it.
```

> 5. Use iOS device to scan the QR code in homekit bridge

> refer to [https://zhuanlan.zhihu.com/p/614043807]

> please be aware that the home assistant and IoT device should be in the same LAN. So the docker network mode should be sent.

```
docker start --net host ID
```

> 6. Use the Siri to control the IoT device.



> refer to [https://www.bilibili.com/video/BV1AT411Y7qM/]
 

> 7. If the Server is down or restarted accidentally, the following steps are needed.

```
docker ps -a

the below error may occur
Cannot connect to the Docker daemon at unix:/var/run/docker.sock. Is the docker daemon running?

```

> If the docker images cannot be executed, normally it is because the docker exits but the configuration file is not deleted
> refer to [https://stackoverflow.com/questions/40524602/error-creating-default-bridge-network-cannot-create-network-docker0-confli]
> refer to [https://stackoverflow.com/questions/44678725/cannot-connect-to-the-docker-daemon-at-unix-var-run-docker-sock-is-the-docker]




> The solution could be 
```
sudo rm -rf /var/lib/docker/network
sudo systemctl start docker

docker ps -a 
// get the containner ID


docker start container ID
// start the container

```




