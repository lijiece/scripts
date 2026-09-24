#!/bin/bash
## This script scans the hosts in a subnet.

NETWORK="172.16.0.0/24"
echo "Scanning network $NETWORK"
sudo nmap -sP $NETWORK --disable-arp-ping | tee nmap_scan.txt
sudo arp-scan --interface=eth0 $NETWORK | tee arp_scan.txt
