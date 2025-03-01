#!/bin/bash

script_dir="$(dirname "$(readlink -f "$0")")"

function scan_wifi() {
	local bandwidth=$1
	local channel=$2
	local MAC_cli=$3

	local chanSpec=$(mcp -C 1 -N 1 -c "$channel/$bandwidth" -m $MAC_cli)

	pkill wpa_supplicant
	ifconfig wlan0 up

	nexutil -Iwlan0 -s500 -b -l34 "-v$chanSpec"

	# setting up monitor fails when it already exists. Can be happily ignored.
	iw phy `iw dev wlan0 info | gawk '/wiphy/ {printf "phy" $2}'` interface add mon0 type monitor 2> /dev/null
	ifconfig mon0 up
}

band=$1
channel=$2
mac=$3

num_coletas=1000
cont=1

while [ $cont -le $num_coletas ]
do
	scan_wifi $band $channel $mac
	tcpdump -i wlan0 dst port 5500 -c 500 -w "$script_dir/Scan/arq${cont}.pcap"

	cont=$((cont + 1)) 
done
