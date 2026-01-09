# MotionNode SDK - Python Tools

## set_location script

The MotionNode device will produce the most accurate heading output when you set the geographic location, which accounts for the Earth's variable magnetic field.  The software estimates the magnetic field vector based on the location: latitude, longitude, and elevation.

It's a good practice to set the location on your host MotionNode software service after installation.  

You can set a geographic location using the [set_location.py](./scripts/set_location.py) script, either by setting latitude/longitude/elevation manually, or using address lookup.

```
python set_location.py --latitude 47.6 --longitude 122 --elevation 20 
```

Note that elevation doesn't need to be very accurate for good results.

Alternatively, you can set an address, and get a geographic location automatically:

```
python set_location.py --address "Seattle, WA, USA" 
```

The previous examples set the location on the **localhost** (127.0.0.1), which is the MotionNode service running on your local computer.  You can also specify a *--host* option to set the location on another computer running the MotionNode service or a MotionNode POE, which also runs the MotionNode service.  Say the other host ip is 192.168.1.50:

```
python set_location.py --host 192.168.1.50 --location "Seattle, WA, USA" 
```

A network-connected MotionNode POE device can also be found by Zeroconf using the *--search* option:

```
python set_location.py --search --location "Seattle, WA, USA" 
```



## set_static_ip script

*This script only applies to network-connected MotionNode POE devices.*

You can set a static IP address on a MotionNode POE device using the [set_static_ip.sh](./scripts/set_static_ip.sh) bash script.  The script will ssh in to the MotionNode POE device using the *remote* user.  To do this, you will need to supply your unique *remote* user password.

**Warning - please be careful assigning static IP addresses, and be sure to avoid IP address conflicts on the network.  If your router supports DHCP, it may be a better choice to use DHCP reservation on your router.**

If the current device is configured without a static IP, please make sure that only one MotionNode POE device is connected to the local network before proceeding.

The following example command will search for the connected MotionNode POE device on the network using Zeroconf, and set a new static ip of **192.168.1.100**, and set the gateway and dns resolver ips as well.

```
python set_static_ip.py --host motionnode.local --ip 192.168.1.100 --gateway 192.168.1.1 --dns 8.8.8.8,8.8.4.4
```

Again, note that the gateway and dns ip addresses are not strictly necessary, if your network delivers this information via DHCP.

If the MotionNode POE device is already assigned a static ip address, use that for *--host* argument.  For example, if the current MotionNode IP address is currently 192.168.1.15:

```
python set_static_ip.py --host 192.168.1.15 --ip 192.168.1.100 --gateway 192.168.1.1 --dns 8.8.8.8,8.8.4.4
```

To set the static ip address and use no gateway or dns resolver ip:

```
python set_static_ip.py --host 192.168.1.15 --ip 192.168.1.100 --gateway "" --dns ""
```


After setting the static ip address, reboot the MotionNode POE device by unplug/plug power cycling.

### Removing a static IP

You can also remove a static ip address and revert to DHCP use the [set_dynamic_ip.sh](./scripts/set_dynamic_ip.sh) bash script.  The script will ssh in to the MotionNode POE device using the *remote* user.  To do this, you will need to supply your unique *remote* user password.

For example, if the current ip address is 192.168.1.15:

```
python set_dyamic_ip.py --host 192.168.1.15
```

Then reboot the MotionNode POE device by unplug/plug power cycling.  After giving it time to boot up, you can ping it to verify the new IP address is correctly configured (assigned by DHCP server on your network):

```
ping motionnode.local
```
