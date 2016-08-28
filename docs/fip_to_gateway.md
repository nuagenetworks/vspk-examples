fip_to_gateway.py
===============
fip_to_gateway creates an uplink subnet on VSG/VRS-G gateway to access FIP subnet inside Shared Resource Domain

### Author ###
Michael Kashin <michael.kashin@nokia.com>

### Version history ###
2016-10-06 - 1.0 - First version

### Usage ###
usage: fip_to_gateway.py [-h] [-d] [-l LOGFILE] -E NUAGE_ENTERPRISE -H
                         NUAGE_HOST [-P NUAGE_PORT] [-p NUAGE_PASSWORD] -u
                         NUAGE_USERNAME [-S] [-v] --fip FIP_NET --address
                         UPLINK_ADDR --mask UPLINK_MASK --gw UPLINK_GW --ip
                         UPLINK_IP --mac UPLINK_MAC --vrs VRS_IP --port
                         VRS_PORT --vlan VRS_VLAN

Tool to create an uplink subnet for FIP access via VSR gateway.

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Enable debug output
  -l LOGFILE, --log-file LOGFILE
                        File to log to (default = stdout)
  -E NUAGE_ENTERPRISE, --nuage-enterprise NUAGE_ENTERPRISE
                        The enterprise with which to connect to the Nuage
                        VSD/SDK host
  -H NUAGE_HOST, --nuage-host NUAGE_HOST
                        The Nuage VSD/SDK endpoint to connect to
  -P NUAGE_PORT, --nuage-port NUAGE_PORT
                        The Nuage VSD/SDK server port to connect to (default =
                        8443)
  -p NUAGE_PASSWORD, --nuage-password NUAGE_PASSWORD
                        The password with which to connect to the Nuage
                        VSD/SDK host. If not specified, the user is prompted
                        at runtime for a password
  -u NUAGE_USERNAME, --nuage-user NUAGE_USERNAME
                        The username with which to connect to the Nuage
                        VSD/SDK host
  -S, --disable-SSL-certificate-verification
                        Disable SSL certificate verification on connect
  -v, --verbose         Enable verbose output
  --fip FIP_NET         FIP subnet CIDR
  --address UPLINK_ADDR
                        Uplink network address
  --mask UPLINK_MASK    Uplink network netmask
  --gw UPLINK_GW        Uplink network gateway
  --ip UPLINK_IP        Uplink interface IP
  --mac UPLINK_MAC      Uplink interface MAC
  --vrs VRS_IP          VRS Gateway IP address
  --port VRS_PORT       VRS Gateway Network Interface Name
  --vlan VRS_VLAN       VRS Gateway Network Interface Vlan ID

### Example ###
python fip_to_gateway.py -E csp -H 10.6.132.43 -p csproot -u csproot -S \
       --address 10.6.132.160 --mask 255.255.255.224 --gw 10.6.132.190 \
       --ip 10.6.132.161 --mac f4:cc:55:e0:14:00 --fip 10.6.132.192 \
       --vrs 10.6.132.47 --port eth0 --vlan 205

### Requirements ###
* Nuage VSPK/VSDK (3.2+)

### Nuage Requirements ###
* VSG/VRS-G gateway should exist and the vlan MUST NOT be configured
* Floating IP subnet should be configured

