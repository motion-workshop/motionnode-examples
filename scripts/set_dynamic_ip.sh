#!/bin/bash

# MotionNode POE: Set dynamic ip script
# This script will ssh in to a network connected MotionNode POE device
# and set a new network configuration enabling DHCP, removing any 
# static ip address assignment.

# parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --host)
      HOST="$2"
      shift # Past argument
      shift # Past value
      ;;
    --help)
      echo "Usage: $0 --host <device_hostname_or_ip>"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [ "${HOST}" == "" ] ; then
    echo "Usage: $0 --host <device_hostname_or_ip>"
    exit 1
fi

echo "Setting networking config for host ${HOST}"
echo "Dynamic IP using DHCP."

CMD1="sudo rm /etc/netplan/*.yaml &> /dev/null" 
CMD2="sudo netplan apply"
CMD3="sudo nmcli connection modify \"Wired connection 1\" ipv4.method auto"

SSH_CMD="ssh -t remote@${HOST} ${CMD1}; ${CMD2}; ${CMD3}"
${SSH_CMD}
if [ $? -eq 0 ]; then
  echo "New networking config set.  Please power cycle the MotionNode POE device now."
else
  echo "Error setting networking config."
fi


