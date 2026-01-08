#!/usr/bin/env python

"""
example_stream.py:  Connect to the MotionNode service on the specified 
host, and stream data to the terminal or a CSV file.

If no --host is specified, then the script will set the location on 
the localhost (127.0.0.1), unless the --search option is set.  

If --search option is set, the script will search for any connected 
MotionNode POE device using Zeroconf, and stream from that
device.


Example usage:

# stream from any MotionNode devices connected on the localhost MotionNode service
python example_stream.py 

# stream from a MotionNode POE device on the network. Find using Zeroconf
python example_stream.py --search 

# stream from any MotionNode devices connected on the MotionNode service at 
# ip address 192.168.1.50
python example_stream.py --host 192.168.1.50


Copyright (c) 2026, Motion Workshop
All rights reserved.
"""

import argparse
import sys
from xml.etree.ElementTree import XML
import json
import MotionSDK
from MotionNodePOEBrowser import *

PortConsole = 32075


"""
Parse the name map and get each connected node's key/id pairs.

Args: 
    xml_node_list: node list in xml format

Returns:
    name_map dictionary from key (name) to id (index)
"""
def parse_name_map(xml_node_list):
    name_map = {}

    tree = XML(xml_node_list)

    # <node key="N" id="Name"> ... </node>
    list = tree.findall(".//node")
    for itr in list:
        name_map[int(itr.get("key"))] = itr.get("id")

    return name_map


"""
Scan and start reading from the specified host running 
MotionNode service.  This could be a computer, or 
MotionNode POE device, residing at the specified ip address.

Args:
    args: command line ArgumentParser arguments
    node_ip_addr: ip address string of target host running the M

Returns:
    tuple of success boolean and list of node dictionaries 
    describing each connected/reading node.
"""
def scan_and_start_reading(args, node_ip_addr):

    node_list = []

    # Use the Lua scripting interface to remove current node list, and rescan
    lua_client = MotionSDK.Client(node_ip_addr, PortConsole)
    lua_chunk = " node.close()" " node.erase()" " node.scan()"
    MotionSDK.LuaConsole.SendChunk(lua_client, lua_chunk, 5)

    # Set the accelerometer max range (sensitivity)
    # The MotionNode supports calibrated values of 2 or 8.
    accel_range_valid_values = [2, 8]
    if args.accel_range not in accel_range_valid_values:
        print(
            "Error, --accel-range possible values: {}".format(accel_range_valid_values)
        )
        return False, node_list

    lua_chunk = " result = node.set_gselect({})" " print(result)".format(
        args.accel_range
    )
    console_result = MotionSDK.LuaConsole.SendChunk(lua_client, lua_chunk, 5)
    if "false" in console_result:
        print("Error setting accel_range={}".format(args.accel_range))
        return False, node_list

    # Set the sampling rate based on input args.
    # valid values are 100, 200, 400, 500, 1000.
    sampling_rate_valid_values = [100, 200, 400, 500, 1000]
    if args.sampling_rate not in sampling_rate_valid_values:
        print(
            "Error, --sampling-rate possible values: {}".format(
                sampling_rate_valid_values
            )
        )
        return False, node_list

    # setting is specified as time-step.  Convert from sampling rate.
    args_time_step = 1.0 / args.sampling_rate
    lua_chunk = " result = node.set_time_step({})" " print(result)".format(
        args_time_step
    )
    console_result = MotionSDK.LuaConsole.SendChunk(lua_client, lua_chunk, 5)
    if "false" in console_result:
        print("Error setting sampling_rate={}".format(args_time_step))
        return False, node_list

    # relist nodes and verify that all settings are correct.
    lua_chunk = " list = node.configuration()" " print(list)"
    current_config = json.loads(
        MotionSDK.LuaConsole.SendChunk(lua_client, lua_chunk, 5)
    )

    # add the node as dictionary to return list
    for node in current_config["items"]:
        if "Bus" not in node["name"]:

            if args_time_step != node["time_step"]:
                print(
                    "Error: configured time_step {} != args time_step {}".format(
                        node["time_step"], args_time_step
                    )
                )
                return False, node_list

            if args.accel_range != node["gselect"]:
                print(
                    "Error: configured accel_range {} != args accel_range {}".format(
                        node["gselect"], args.accel_range
                    )
                )
                return False, node_list

            node_dict = {}
            node_dict["key"] = node["key"]
            node_dict["name"] = node["name"]
            node_dict["uuid"] = node["uuid"]
            node_dict["sampling_rate"] = int(1.0 / node["time_step"])
            node_dict["accel_range"] = node["gselect"]
            node_list.append(node_dict)

    if not len(node_list):
        print("Error: scanned node configuration is empty.")
        return False, node_list

    # finally, start reading from the configured nodes.
    lua_chunk = (
        " node.start()"
        " if node.is_reading() then"
        "   print('Reading from ' .. node.num_reading() .. ' device(s)')"
        " else"
        "   print('Failed to start reading')"
        " end"
    )
    console_result = MotionSDK.LuaConsole.SendChunk(lua_client, lua_chunk, 5)
    lua_client.close()
    if "Failed" in console_result:
        print("Error in start reading.")
        return False, node_list
    else:
        return True, node_list


"""
Connect to a given host running the MotionNode service
and stream data to the terminal or csv file, with 
settings applied according to the commandline args.

Args:
    args: command line ArgumentParser arguments
    out:  TextIO object for output of streaming data
    
Returns:
    True if successful
"""
def stream_data_to_csv(args, out):

    node_ip_addr = ""

    # if no host ip address is specified on the command line, then scan.
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
    # scan and attempt to start reading from any connected
    # MotionNode device(s)
    is_node_reading, node_list = scan_and_start_reading(args, node_ip_addr)
    if not is_node_reading:
        return False

    print("Reading from:")

    for node in node_list:
        print(
            "Node key: {}\n  name: {}\n  uuid: {}\n  sampling-rate: {} Hz\n  accel-range: {} g\n".format(
                node["key"],
                node["name"],
                node["uuid"],
                node["sampling_rate"],
                node["accel_range"],
            )
        )

    # Request the channels that we want from every connected device. The full
    # list is available here:
    #
    #   https://www.motionshadow.com/download/media/configurable.xml
    #
    # Select the local accelerometer (a), magnetometer (m), gyro (g),
    # and Euler angles (r). This yields 12 numeric values per device
    # per frame.
    #
    xml_string = (
        '<?xml version="1.0"?>'
        '<configurable inactive="1">'
        "<a/>"
        "<m/>"
        "<g/>"
        "<r/>"
        "</configurable>"
    )

    client = MotionSDK.Client(node_ip_addr, args.port)

    if not client.writeData(xml_string):
        raise RuntimeError(
            "failed to send channel list request to Configurable service"
        )

    num_frames = 0
    xml_node_list = None

    # keep a list of actual node key:name pairs
    # removing any parent Bus nodes (which are empty data)
    node_list_imus = {}

    while True:
        # Block, waiting for the next sample.
        data = client.readData(time_out_second=5)
        if data is None:
            raise RuntimeError("data stream interrupted or timed out")
            break

        if data.startswith(b"<?xml"):
            xml_node_list = data
            continue

        container = MotionSDK.Format.Configurable(data)

        # Consume the XML node name list. If the print header option is active
        # add that now.
        if xml_node_list:

            # populate a node_list_imus with the names of each IMU ("node_xx")
            # removing any empty "Bus" container nodes.
            name_map = parse_name_map(xml_node_list)
            for key, val in name_map.items():
                if "Bus" not in val:
                    node_list_imus[key] = val

            if args.header:
                # generate the csv header.  change this to match the selected
                # configurable channels.
                ChannelName = [
                    "ax",
                    "ay",
                    "az",
                    "mx",
                    "my",
                    "mz",
                    "gz",
                    "gy",
                    "gz",
                    "rx",
                    "ry",
                    "rz",
                ]

                flat_list = []
                for key in container:
                    if key not in node_list_imus:
                        continue

                    if key not in name_map:
                        raise RuntimeError(
                            "device missing from name map, unable to print " "header"
                        )

                    item = container[key]
                    if len(ChannelName) != item.size():
                        raise RuntimeError(
                            "expected {} channels but found {}, unable to "
                            "print header".format(len(ChannelName), item.size())
                        )

                    name = name_map[key]
                    for channel in ChannelName:
                        flat_list.append("{}.{}".format(name, channel))

                if not len(flat_list):
                    raise RuntimeError("unknown data format, unabled to print header")

                out.write(",".join(["{}".format(v) for v in flat_list]) + "\n")

            xml_node_list = None

        #
        # Make an array of all of the values, in order, that are part of one
        # sample. This is a single row in the output.
        #
        flat_list = []
        for key in container:
            if key not in node_list_imus:
                continue
            item = container[key]
            for i in range(item.size()):
                flat_list.append(item.value(i))

        if not len(flat_list):
            raise RuntimeError("unknown data format in stream")

        out.write(",".join(["{}".format(round(v, 8)) for v in flat_list]) + "\n")

        if args.frames > 0:
            num_frames += 1
            if num_frames >= args.frames:
                break
    
    return True


def main(argv):
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("--file", help="output file", default="")
    parser.add_argument("--frames", help="read N frames", type=int, default=0)
    parser.add_argument(
        "--header", help="show channel names in the first row", action="store_true"
    )
    parser.add_argument(
        "--host", help="IP address of the Motion Service", default="127.0.0.1"
    )
    parser.add_argument("--search", help="search for a MotionNode POE device using Zeroconf.", action="store_true")
    parser.add_argument(
        "--port",
        help="port number address of the Motion Service",
        type=int,
        default=32076,
    )
    parser.add_argument(
        "--accel-range", help="accelerometer sensitivity (range)", type=int, default=2
    )
    parser.add_argument(
        "--sampling-rate", help="sampling rate in Hz", type=int, default=100
    )

    args = parser.parse_args()

    if args.file:
        with open(args.file, "w") as f:
            stream_data_to_csv(args, f)
    else:
        stream_data_to_csv(args, sys.stdout)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
