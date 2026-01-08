"""
MotionNodePOEBrowser class: Browse and find any MotionNode PoE device on 
the network using zeroconf (avahi / bonjour protocol).

Copyright (c) 2026, Motion Workshop
All rights reserved.
"""

from time import sleep
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange, ZeroconfServiceTypes
from typing import cast


class MotionNodePOEBrowser:
  
  class MotionNodeListener:
      node_list = []

      def add_service(self, zc, type_, name):
          info = zc.get_service_info(type_, name)
          #print(f"Service {name} added, service info: {info}")
          info = zc.get_service_info(type_, name)
          if info:
              # Use parsed_addresses() for a list of string IPs (e.g., ["192.168.1.10"])
              addresses = info.parsed_addresses()
              if len(addresses) and addresses not in self.node_list:
                  self.node_list.append(addresses)
                  
      def update_service(self, zc, type_, name):
        pass

  node_list = []

  def __init__(self, wait_duration=2):    
    zeroconf = Zeroconf()
    listener = self.MotionNodeListener()

    services = ["_motionnode._tcp.local."]

    browser = ServiceBrowser(
        zeroconf, services, listener
    )

    sleep(wait_duration)
    
    self.node_list = listener.node_list
    zeroconf.close()

  def get_node_list(self):
    return self.node_list
  