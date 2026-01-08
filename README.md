# MotionNode SDK Examples

This repository provides examples and tutorials how to stream data using the Motion SDK for MotionNode USB and MotionNode POE devices.  

- **[Prerequisites](#prerequisites)**
- **[MotionNode Software](#motionnode-software)**
- **[MotionNode streaming example](#motionnode-streaming-example)**
- **[MotionNode POE tutorial](#motionnode-poe-tutorial)**
- **[Setting location](#setting-location)**

## Prerequisites

First set up your python virtual environment and get the required dependencies:

```bash
python -m venv .
source ./bin/activate
pip install -r requirements.txt
```

## MotionNode Software

To connect and stream data from a MotionNode USB device, or more than one MotionNode POE devices, you need to first install the [MotionNode software](https://www.motionnode.com/software) on the host.  The host can be a PC, Raspberry Pi or other Linux based single board computer (SBC).   

Once installed, you can open the MotionNode app, or use the equivalent web browser interface at:

[http://127.0.0.1:32080](http://motionnode.local:32080)

You can scan, start reading, preview 3d rotation, view charts, and record takes in the MotionNode app.


## MotionNode streaming example

If you have a MotionNode USB device (2025 and newer), please follow the example in [python-streaming](./python-streaming/README.md).

## MotionNode POE tutorial

For MotionNode POE users, please follow the [MotionNode POE README](./motionnode-poe/README.md).  It provides a tutorial showing how to connect to one or more devices via the MotionNode service running on the host, or [directly connect](./motionnode-poe/README_direct_connect.md) to a single MotionNode POE device using only python (no other software required).

## Setting location

The MotionNode device will produce the most accurate heading output when you set the geographic location, which accounts for the Earth's variable magnetic field.  The MotionNode software estimates the magnetic field vector based on the location: latitude, longitude, and elevation.

It's a good practice to set the location on your host MotionNode software service after installation.  There are three ways to set the location:

### Option 1. Use the web browser interface location tab

If your host has an internet connection, you can set the location manually at any time from the **location** tab in the web browser ui.  This is convenient, as you can set a general city/state name rather than latitude/longitude.  In the location tab, click the "+" icon on the lower right to add a new location:

[http://127.0.0.1:32080/#/location](http://motionnode.local:32080/#/location)


### Option 2. Use the web browser interface console

[http://127.0.0.1:32080/#/console](http://motionnode.local:32080/#/console)

In this example let's say that we would like to set the location to Seattle's coordinates of latitude=47.6, longitude=122, elevation=20m. In the console command entry box, run the following command:

```
=node.system.location(47.6, 122, 20)
```

### Option 3. Use the Python set_location script

You can set a geographic location using the included [set_location](./scripts/set_location.py) script.   

```
cd scripts
python set_location.py --latitude 47.6 --longitude 122 --elevation 20 
```

Note that elevation doesn't need to be very accurate for good results.

Alternatively, you can set an address, and get a geographic location automatically (requires internet connection):

```
cd scripts
python set_location.py --location "Seattle, WA, USA" 
```

Please see the [set_location README](README_tools.md#set_location-script) for more details

