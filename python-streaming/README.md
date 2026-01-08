# MotionNode Streaming: Motion SDK Python Example

Stream measurement and motion data from one or more connected MotionNode devices. Print out the data in CSV format in a terminal or stream to a CSV file.

Each sample in time is one row. Each column is one channel from one connected MotionNode device.

## Run the example

By default, the example application will read as many samples as possible and print them to the standard output. The samples are printed as they arrive, every ~10 milliseconds.

Edit the code to select which channels you want to read.  By default, this example streams the accelerometer (a), magnetometer (m), gyro (g), and Euler angles (r).

Configurable channels are documented in [configurable.xml](https://storage.googleapis.com/shadowmocap/configurable.xml)

This example script first stops, scans, and starts reading from any connected MotionNode devices.  It prints out the list of connected nodes, which are available to the user as a dictionary:

```
Reading from:
Node key: 2
  name: Node01
  uuid: 4166b70d-0825-434b-93f9-17a2ef537da9
  sampling rate: 100Hz
  accel_range: 2 g
Node key: 4
  name: Node2
  uuid: 4166b70d-0825-434b-93f9-17a2ef537da9
  sampling rate: 100Hz
  accel_range: 2 g
```

Each MotionNode device has a unique **uuid** string.  This string can be useful to apply the same node's data to a specific data related task, regardless of the order in which the devices are enumerated (which may change, based on the USB driver).

This example script also shows how to set the accelerometer sensitivity.  Each MotionNode device is calibrated at two sensitivities: ±2g and ±8g.  

The sampling rate can also be specified in Hz (fps).  Valid values are: [100, 200, 400, 500, 1000]

```
cd ../scripts
python example_stream.py  --help

usage: example_stream.py [-h] [--file FILE] [--frames FRAMES] [--header]
                  [--host HOST] [--port PORT]

optional arguments:
  -h, --help       show this help message and exit
  --file FILE      output file
  --frames FRAMES  read N frames
  --header         show channel names in the first row
  --host HOST      IP address of the Motion Service
  --port PORT      port number of the Motion Service
  --accel-range    accelerometer range (sensitivity)
  --sampling-rate  sampling rate in Hz
  --search         search for a MotionNode POE device using Zeroconf.  
```

## Examples

1. Output the stream to a csv file which you can open in spreadsheet editor (Openoffice, Libreoffice, Excel).  Include a header on the first line of the csv file.  The file is specified relative to the current working directory, or can be specified as a full path relative:

```console
python example_stream.py --header --file ./streamed_data.csv
```

2. Output the stream to the terminal, and include the header showing channel names

```console
python example_stream.py --header
```

3. Motion SDK uses TCP/IP sockets, so it is easy to stream over the network as shown in this example.  A MotionNode sensor is running on a different computer on your network.  Connect by specifying the hostname or ip address (here, 192.168.1.100).

```console
python example_stream.py --host 192.168.1.100
```

4. Specify the accelerometer sensitivity.  Select ±8g:

```console
python example_stream.py --accel-range 8
```

5. Specify the sampling rate.  Select 1000 Hz:

```console
python example_stream.py --sampling-rate 1000
```
