#
# @file    sdk/python/MotionSDK.py
# @version 2.6
#
# Copyright (c) 2025, Motion Workshop
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
import argparse
import sys
from xml.etree.ElementTree import XML
import json
import MotionSDK

PortConsole = 32075

def parse_name_map(xml_node_list):
    name_map = {}

    tree = XML(xml_node_list)

    # <node key="N" id="Name"> ... </node>
    list = tree.findall(".//node")
    for itr in list:
        name_map[int(itr.get("key"))] = itr.get("id")

    return name_map

'''
Scan and start reading from any connected MotionNode devices.
Returns a list of node dictionaries describing each 
connected/reading node.
'''
def scan_and_start_reading(args):
  
    node_list = []
    
    # Use the Lua scripting interface to make scan and start reading 
    # from any connected MotionNode devices on the specified host.
    #
    lua_client = MotionSDK.Client(args.host, PortConsole)  
    lua_chunk = \
        " node.close()" \
        " node.scan()" \
        " list = node.configuration()" \
        " print(list)"
    current_config = json.loads(MotionSDK.LuaConsole.SendChunk(lua_client, lua_chunk, 5))
    for node in current_config['items']:
      if "Bus" not in node['name']:
        node_dict = {}
        node_dict['key'] = node['key']
        node_dict['name'] = node['name']
        node_dict['uuid'] = node['uuid']
        node_dict['accel_range'] = node['gselect']
        node_list.append(node_dict)
    
    if not len(node_list):
      print("Error: scanned node configuration is empty.")
      return False, node_list

    # In this example, set the accelerometer max range (sensitivity)
    # to 2g.  The MotionNode supports calibrated values of 2 or 8.
    accel_range = 2
    lua_chunk = \
        " result = node.set_gselect({})" \
        " print(result)".format(accel_range)
    console_result = MotionSDK.LuaConsole.SendChunk(lua_client, lua_chunk, 5)
    if "false" in console_result:
      print("Error setting accel_range={}".format(accel_range))
      return False, node_list
    
    lua_chunk = \
        " node.start()" \
        " if node.is_reading() then" \
        "   print('Reading from ' .. node.num_reading() .. ' device(s)')" \
        " else" \
        "   print('Failed to start reading')" \
        " end"   
    console_result = MotionSDK.LuaConsole.SendChunk(lua_client, lua_chunk, 5)
    lua_client.close()
    if "Failed" in console_result:
      print("Error in start reading.")
      return False, node_list
    else:
      return True, node_list

    
def stream_data_to_csv(args, out):
  
    # scan and attempt to start reading from any connected 
    # MotionNode device(s)
    is_node_reading, node_list = scan_and_start_reading(args)
    if not is_node_reading:
      return 1
    
    print("Reading from:")
    
    for node in node_list:
      print("Node key: {}\n  name: {}\n  uuid: {}\n  accel_range: {}\n".format(node['key'], 
            node['name'], node['uuid'], node['accel_range']))    


    # Request the channels that we want from every connected device. The full
    # list is available here:
    #
    #   https://www.motionshadow.com/download/media/configurable.xml
    #
    # Select the local accelerometer (a), magnetometer (m), gyro (g), 
    # and Euler angles (r). This yields 12 numeric values per device 
    # per frame. 
    #
    xml_string = \
        "<?xml version=\"1.0\"?>" \
        "<configurable inactive=\"1\">" \
        "<a/>" \
        "<m/>" \
        "<g/>" \
        "<r/>" \
        "</configurable>"

    client = MotionSDK.Client(args.host, args.port)

    if not client.writeData(xml_string):
        raise RuntimeError(
            "failed to send channel list request to Configurable service")

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
                    'ax', 'ay', 'az', 'mx', 'my', 'mz', 
                    'gz', 'gy', 'gz', 'rx', 'ry', 'rz'
                ]

                flat_list = []
                for key in container:
                    if key not in node_list_imus:
                        continue
                      
                    if key not in name_map:
                        raise RuntimeError(
                            "device missing from name map, unable to print "
                            "header")

                    item = container[key]
                    if len(ChannelName) != item.size():
                        raise RuntimeError(
                            "expected {} channels but found {}, unable to "
                            "print header".format(
                                len(ChannelName), item.size()))

                    name = name_map[key]
                    for channel in ChannelName:
                        flat_list.append("{}.{}".format(name, channel))

                if not len(flat_list):
                    raise RuntimeError(
                        "unknown data format, unabled to print header")

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


def main(argv):
    parser = argparse.ArgumentParser(
        description="")

    parser.add_argument(
        "--file",
        help="output file",
        default="")
    parser.add_argument(
        "--frames",
        help="read N frames",
        type=int, default=0)
    parser.add_argument(
        "--header",
        help="show channel names in the first row",
        action="store_true")
    parser.add_argument(
        "--host",
        help="IP address of the Motion Service",
        default="127.0.0.1")
    parser.add_argument(
        "--port",
        help="port number address of the Motion Service",
        type=int, default=32076)

    args = parser.parse_args()

    if args.file:
        with open(args.file, 'w') as f:
            stream_data_to_csv(args, f)
    else:
        stream_data_to_csv(args, sys.stdout)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
