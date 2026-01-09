#!/bin/bash

# MotionNode POE: Set static ip script
# This script will ssh in to a network connected MotionNode POE device
# and set a new network configuration with a static ip address,
# optionally also setting a gateway and dns resolver ip address.

# parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --host)
      HOST="$2"
      shift # Past argument
      shift # Past value
      ;;
    --ip)
      IP_ADDRESS="$2"
      shift # Past argument
      shift # Past value
      ;;
    --gateway)
      GATEWAY="$2"
      shift
      shift
      ;;
    --dns)
      DNS_RESOLVER="$2"
      shift
      shift
      ;;
    --help)
      echo "Usage: $0 --host <device_hostname_or_ip> --ip <static_ip_> --gateway <gateway_ip> --dns <dns_resolver_ip>"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [ "${HOST}" == "" ] || [ "${IP_ADDRESS}" == "" ]; then
    echo "Usage: $0 --host <device_hostname_or_ip> --ip <static_ip_> --gateway <gateway_ip> --dns <dns_resolver_ip>"
    echo "--dns, --gateway are optional."
    exit 1
fi

echo "Setting networking config for host ${HOST}"
echo "Static IP = ${IP_ADDRESS}"
echo "Gateway IP = ${GATEWAY}"
echo "DNS Resolver = ${DNS_RESOLVER}"

CMD1="sudo rm /etc/netplan/*.yaml &> /dev/null" 
CMD2="sudo nmcli connection modify \"Wired connection 1\" ipv4.addresses \"${IP_ADDRESS}/24\" ipv4.gateway \"${GATEWAY}\" ipv4.dns \"${DNS_RESOLVER}\" ipv4.method manual"
#CMD3="sudo nmcli connection down \"Wired connection 1\" &> /dev/null < /dev/null; sudo nmcli connection up \"Wired connection 1\" &> /dev/null < /dev/null"

SSH_CMD="ssh -t remote@${HOST} ${CMD1}; ${CMD2}"
$SSH_CMD
#echo "${SSH_CMD}"
if [ $? -eq 0 ]; then
  echo "New networking config set.  Please power cycle the MotionNode POE device now."
else
  echo "Error setting networking config."
fi


