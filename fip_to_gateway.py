# -*- coding: utf-8 -*-
"""
fip_to_gateway creates an uplink subnet on VRS/VRS-G gateway to access FIP subnet inside Shared Resource Domain

--- Author ---
Michael Kashin <michael.kashin@nokia.com>

--- Version history ---
2016-10-06 - 1.0 - First version

--- Usage ---
run 'python fip_to_gateway.py -h' for an overview

--- Documentation ---
http://github.com/nuagenetworks/vspk-examples/blob/master/docs/fip_to_gateway.md

--- Example ---
python fip_to_gateway.py -E csp -H 10.6.132.43 -p csproot -u csproot -S \
       --address 10.6.132.160 --mask 255.255.255.224 --gw 10.6.132.190 \
       --ip 10.6.132.161 --mac f4:cc:55:e0:14:00 --fip 10.6.132.192 \
       --vrs 10.6.132.47 --port eth0 --vlan 205
"""

import argparse
import getpass
import logging
import requests

from vspk import v4_0 as vsdk

UPLINK_TYPE = 'UPLINK_SUBNET'

def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="Tool to create an uplink subnet for FIP access via VSR gateway.")
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-E', '--nuage-enterprise', required=True, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('-H', '--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('-P', '--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('-p', '--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('-u', '--nuage-user', required=True, help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect', dest='nosslcheck', action='store_true')
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', action='store_true')
    parser.add_argument('--fip', required=True, help='FIP subnet CIDR', dest='fip_net')
    parser.add_argument('--address', required=True, help='Uplink network address', dest='uplink_addr')
    parser.add_argument('--mask', required=True, help='Uplink network netmask', dest='uplink_mask')
    parser.add_argument('--gw', required=True, help='Uplink network gateway', dest='uplink_gw')
    parser.add_argument('--ip', required=True, help='Uplink interface IP', dest='uplink_ip')
    parser.add_argument('--mac', required=True, help='Uplink interface MAC', dest='uplink_mac')
    parser.add_argument('--vrs', required=True, help='VRS Gateway IP address', dest='vrs_ip')
    parser.add_argument('--port', required=True, help='VRS Gateway Network Interface Name', dest='vrs_port')
    parser.add_argument('--vlan', required=True, help='VRS Gateway Network Interface Vlan ID', dest='vrs_vlan')
    args = parser.parse_args()
    return args


def main():
    """
    Main function to create Uplink subnet via REST API
    """

    # Handling arguments
    args                = get_args()
    debug               = args.debug
    log_file            = None
    if args.logfile:
        log_file        = args.logfile
    nuage_enterprise    = args.nuage_enterprise
    nuage_host          = args.nuage_host
    nuage_port          = args.nuage_port
    nuage_password      = None
    if args.nuage_password:
        nuage_password  = args.nuage_password
    nuage_username      = args.nuage_username
    nosslcheck          = args.nosslcheck
    verbose             = args.verbose
    fip_net             = args.fip_net
    uplink_addr         = args.uplink_addr
    uplink_mask         = args.uplink_mask
    uplink_gw           = args.uplink_gw
    uplink_ip           = args.uplink_ip
    uplink_mac          = args.uplink_mac
    vrs_ip              = args.vrs_ip
    vrs_port            = args.vrs_port
    vrs_vlan            = args.vrs_vlan

    # Logging settings
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(filename=log_file, format='%(asctime)s %(levelname)s %(message)s', level=log_level)
    logger = logging.getLogger(__name__)

    # Disabling SSL verification if set
    if nosslcheck:
        logger.debug('Disabling SSL certificate verification.')
        requests.packages.urllib3.disable_warnings()

    # Getting user password for Nuage connection
    if nuage_password is None:
        logger.debug('No command line Nuage password received, requesting Nuage password from user')
        nuage_password = getpass.getpass(prompt='Enter password for Nuage host %s for user %s: ' % (nuage_host, nuage_username))

    try:
        # Connecting to Nuage
        logger.info('Connecting to Nuage server %s:%s with username %s' % (nuage_host, nuage_port, nuage_username))
        nc = vsdk.NUVSDSession(username=nuage_username, password=nuage_password, enterprise=nuage_enterprise, api_url="https://%s:%s" % (nuage_host, nuage_port))
        nc.start()

    except Exception, e:
        logger.error('Could not connect to Nuage host %s with user %s and specified password' % (nuage_host, nuage_username))
        logger.critical('Caught exception: %s' % str(e))
        return 1

    nuage_user = nc.user

    logger.debug('Getting FIP subnet parent ID')
    fip_obj = nuage_user.subnets.get_first(filter="address == '{0}'".format(fip_net))
    shared_resource_id = fip_obj.parent_id
    logger.debug('FIP parent ID is: {0}'.format(shared_resource_id))

    logger.debug('Creating a new VLAN on Gateway port')
    new_vlan = vsdk.NUVLAN(value=vrs_vlan)
    gw = nuage_user.gateways.get_first(filter="name == '{0}'".format(vrs_ip))
    port = gw.ports.get_first(filter="name == '{0}'".format(vrs_port))
    port.create_child(new_vlan)
    vlan_id = new_vlan.id
    logger.debug('New VLAN ID is: {0}'.format(vlan_id))

    logger.debug('Creating an Uplink Subnet')

    shared_subnet = vsdk.NUSharedNetworkResource(name='uplink subnet {0}'.format(uplink_addr.replace('.','-')), \
        description='Uplink subnet to Gateway {0}'.format(vrs_ip.replace('.','-')), \
        address=uplink_addr, \
        netmask=uplink_mask, \
        gateway=uplink_gw, \
        type=UPLINK_TYPE, \
        uplink_interface_ip=uplink_ip, \
        uplink_interface_mac=uplink_mac, \
        uplink_gw_vlan_attachment_id=vlan_id, \
        shared_resource_parent_id=shared_resource_id, \
        uplink_vport_name = 'uplink vport {0} Vlan{1}'.format(vrs_port, vrs_vlan))

    nuage_user.create_child(shared_subnet)
    logger.warning('Uplink Subnet is created')
    return 0

# Start program
if __name__ == "__main__":
    main()

