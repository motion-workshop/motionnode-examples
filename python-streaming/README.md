# MotionNode Streaming: Motion SDK Python Example

Stream measurement and motion data from the MotionNode device. Print out the data in
CSV format in a terminal or stream to a CSV file.

Each sample in time is one row. Each column is one channel from one connected 
MotionNode device.

## Run the example

By default, the example application will read as many samples as possible and
print them to the standard output. The samples are printed as they arrive,
every ~10 milliseconds.

Edit the code to select which channels you want to read.  By default, this 
example streams the accelerometer (a), magnetometer (m), gyro (g), and Euler 
angles (r).

Configurable channels are documented in [configurable.xml](https://storage.googleapis.com/shadowmocap/configurable.xml)

```
python example.py  --help

usage: example.py [-h] [--file FILE] [--frames FRAMES] [--header]
                  [--host HOST] [--port PORT]

optional arguments:
  -h, --help       show this help message and exit
  --file FILE      output file
  --frames FRAMES  read N frames
  --header         show channel names in the first row
  --host HOST      IP address of the Motion Service
  --port PORT      port number of the Motion Service
```

## Examples

1. Output the stream to a csv file which you can open in spreadsheet editor (Openoffice, Libreoffice, Excel).  Include a header on the first line of the csv file:

```console
python example.py --header --file ./streamed_data.csv
```

2. Output the stream to the terminal.

```console
python example.py --header
```

3. Motion SDK uses TCP/IP sockets, so it is easy to stream over the network as shown in thsi example.  A MotionNode sensor is running on a different computer on your network.  Connect by specifying the hostname or ip address (here, 192.168.1.100).

```console
python example.py --header --host 192.168.1.100
```

