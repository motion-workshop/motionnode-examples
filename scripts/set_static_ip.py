#!/usr/bin/env python

"""
motionnode-poe/set_static_ip.py:  Sets a new static ip address for a
MotionNode POE device on the local area network.

If no --host is specified, then the script will search for any connected 
MotionNode POE device using Zeroconf, and set the static ip on that device.

Example usage: 

python set_static_ip.py --ip 192.168.1.100 --gateway 192.168.1.1 --dns 8.8.8.8,8.8.4.4

If you know the device's IP address is 192.168.1.15:

python set_static_ip.py --host 192.168.1.15 --ip 192.168.1.100 --gateway 192.168.1.1 --dns 8.8.8.8,8.8.4.4

Copyright (c) 2026, Motion Workshop
All rights reserved.
"""

import argparse
import sys
from xml.etree.ElementTree import XML
import MotionSDK
from MotionNodePOEBrowser import *

PortConsole = 32075

"""
Sets a new static ip address for the MotionNode POE device
at the specified ip address.

Args:
    node_ip_addr: current target device IP address
    new_static_ip: new static IP address to set
    new_gateway_ip: new gateway IP address to set (optional)
    new_dns_ip:  new dns resolution IP address to set (optional)
    
Returns:
    True if successful
"""
def set_static_ip_address(
    node_ip_addr, new_static_ip, new_gateway_ip="", new_dns_ip=""
):

    lua_client = MotionSDK.Client(node_ip_addr, PortConsole)

    # set the static ip address
    lua_chunk = (
        ' result = node.system.set_default("static_ip", "{}")'
        " print(result)".format(new_static_ip)
    )
    console_result = MotionSDK.LuaConsole.SendChunk(lua_client, lua_chunk, 5)
    if "false" in console_result:
        print("Error setting static ip address='{}'".format(new_static_ip))
        return False
    else:
        print("Success - set static ip address='{}'".format(new_static_ip))

    # set the gateway address
    lua_chunk = (
        ' result = node.system.set_default("static_gateway", "{}")'
        " print(result)".format(new_gateway_ip)
    )
    console_result = MotionSDK.LuaConsole.SendChunk(lua_client, lua_chunk, 5)
    if "false" in console_result:
        print("Error setting static gateway ip address='{}'".format(new_gateway_ip))
        return False
    else:
        print("Success - set static gateway ip address='{}'".format(new_gateway_ip))

    # set the dns resolution address
    lua_chunk = (
        ' result = node.system.set_default("static_dns", "{}")'
        " print(result)".format(new_dns_ip)
    )
    console_result = MotionSDK.LuaConsole.SendChunk(lua_client, lua_chunk, 5)
    if "false" in console_result:
        print("Error setting dns resolution ip address='{}'".format(new_dns_ip))
        return False
    else:
        print("Success - set dns resolution ip address='{}'".format(new_dns_ip))

    print("\nPlease reboot (power cycle) the MotionNode POE device now.")
    
    return True


"""
Connect to a given host running the MotionNode service
and set its static IP address.

Args:
    args: command line ArgumentParser arguments

Returns:
    True if successful
"""
def connect_and_set_static_ip(args):

    node_ip_addr = ""

    # if no host ip address is specified on the command line, then scan.
    if not args.host:
        # Find any MotionNode POE devices on the network using
        # zeroconf, waiting up to 2 seconds for scanning.
        wait_duration = 2
        node_browser = MotionNodePOEBrowser(wait_duration)
        print("MotionNode PoE Devices:")
        node_ip_addr_list = node_browser.get_node_list()
        for node in node_ip_addr_list:
            print(node)
        print("")
        # In this example, we'll directly connect to the first scanned node,
        # ipv4 address.
        node_ip_addr = node_ip_addr_list[0][0]
    else:
        node_ip_addr = args.host

    # set the new static ip address for the target MotionNode POE device
    set_ip_success = set_static_ip_address(node_ip_addr, args.ip, args.gateway, args.dns)
    if not set_ip_success:
        return False

    return True


def main(argv):
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("--ip", help="new static ip address to set")
    parser.add_argument("--gateway", help="new static gateway ip address to set", default="")
    parser.add_argument("--dns", help="new static dns resolution ip address to set", default="")

    parser.add_argument(
        "--host", help="IP address of the MotionNode POE device", default=""
    )

    args = parser.parse_args()

    connect_and_set_static_ip(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
