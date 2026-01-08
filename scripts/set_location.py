#!/usr/bin/env python

"""
motionnode-poe/set_location.py:  Sets a location
(latitude and longitude, elevation) for a
MotionNode POE device on the local area network.

If no --host is specified, then the script will set the location on 
the localhost (127.0.0.1), unless the --search option is set.  

If --search option is set, the script will search for any connected 
MotionNode POE device using Zeroconf, and set the location on that
device.

Example usage:

# set location on the localhost MotionNode service
python set_location.py --latitude 47.6 --longitude 122 --elevation 20 

# set location on the localhost MotionNode service using an address
python set_location.py --address "Seattle, WA, USA"

# set location on a MotionNode POE device using Zeroconf
python set_location.py --search --latitude 47.6 --longitude 122 --elevation 20 

# set location on the MotionNode POE device's MotionNode service at 
# ip address 192.168.1.50
python set_location.py --host 192.168.1.50 --latitude 47.6 --longitude 122 --elevation 20 


Copyright (c) 2026, Motion Workshop
All rights reserved.
"""

import argparse
import sys
from xml.etree.ElementTree import XML
import MotionSDK
from MotionNodePOEBrowser import *
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

PortConsole = 32075


"""
Sets the geographic location for MotionNode POE device
at specified ip address.

Args:
    node_ip_addr: current target device IP address
    latitude: new location latitude to set
    longitude: new location longitude to set
    elevation:  new location elevation to set
    
Returns:
    True if successful
"""
def set_location(
    node_ip_addr, latitude, longitude, elevation
):

    lua_client = MotionSDK.Client(node_ip_addr, PortConsole)

    # set the static ip address
    lua_chunk = (
        ' result = node.system.location({}, {}, {})'
        " print(result)".format(latitude, longitude, elevation)
    )
  
    console_result = MotionSDK.LuaConsole.SendChunk(lua_client, lua_chunk, 5)
    if "false" in console_result:
        print("Error setting location = {}, {}, {}".format(latitude, longitude, elevation))
        return False
    else:
        print("Success - set location = {}, {}, {}".format(latitude, longitude, elevation))

    return True


"""
Run geocode call to estimate lat/long.  Try up to max_attempts 
times, as sometimes this api times out.

Args:
    address: address string, for example "Seattle, WA, USA"
"""
def get_geocode_location(address):
    attempt=1
    max_attempts=5
    try:
        geolocator = Nominatim(user_agent="geo_app")
        return geolocator.geocode(address)
        #return geopy.geocode(address)
    except GeocoderTimedOut:
        if attempt <= max_attempts:
            return do_geocode(address, attempt=attempt+1)
        raise


"""
Get the elevation at a location on Earth

Args:
    latitude: location latitude in degrees
    longitude: location longitude in degrees

Returns:
    elevation in meters at given location
"""
def get_elevation(latitude, longitude):
    try:
      url = f"https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longitude}"
      response = requests.get(url).json()
      return response['results'][0]['elevation']
    except:
      print("Error - elevation api call failed.")
      raise


"""
Connect to a given host running the MotionNode service
and set the geographic location.

Args:
    args: command line ArgumentParser arguments

Returns:
    True if successful
"""
def connect_and_set_location(args):

    node_ip_addr = ""

    # if no host ip address is specified on the command line,
    # then scan.
    if args.search:
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
      if not args.host:
        print("Error, --host must be specified if --search option not set.")
        return False
      else:
        node_ip_addr = args.host

    # if address was specified, attempt to get the lat/long via geopy.
    if args.address:
        location = get_geocode_location(args.address)
        if not location:
            print(f"Error - location service failed to find {args.address}")
            return False
        
        elevation = get_elevation(location.latitude, location.longitude)
        # set the new static ip address for the target MotionNode POE device
        set_location_success = set_location(node_ip_addr, location.latitude, location.longitude, elevation)
        if not set_location_success:
            return False
    else:
        # set the new static ip address for the target MotionNode POE device
        set_location_success = set_location(node_ip_addr, args.latitude, args.longitude, args.elevation)
        if not set_location_success:
            return False

    return True


def main(argv):
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("--latitude", help="new location latitude in degrees")
    parser.add_argument("--longitude", help="new location longitude in degrees")
    parser.add_argument("--elevation", help="new location elevation in meters")
    parser.add_argument("--address", help="new location address.  attempt to look up geolocation automatically.")
    parser.add_argument("--search", help="search for a MotionNode POE device using Zeroconf.", action="store_true")
    
    parser.add_argument(
        "--host", help="IP address of the MotionNode POE device", default="127.0.0.1"
    )

    args = parser.parse_args()

    connect_and_set_location(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
