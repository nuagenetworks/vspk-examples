# -*- coding: utf-8 -*-
"""
vm_add_interface is a tool to add one or more new interface to a VM inside a Nuage VSP environment.

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

--- Version history ---
2017-10-12 - 0.1 - Initial development version
2020-07-06 - 1.0 - Migrate to v6 API

--- Usage ---
run 'python vm_add_interface.py -h' for an overview
"""
from builtins import str
import argparse
import getpass
import logging
from vspk import v6 as vsdk


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="vm_add_interface is a tool to add a new interface to a VM inside a Nuage VSP environment.")
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect (deprecated)', dest='nosslcheck', action='store_true')
    parser.add_argument('-i', '--ip', required=False, help="IP address of a nic which has to be attached to a Nuage subnet or L2 domain", dest='ips', type=str, action='append')
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-m', '--mac', required=True, help="MAC address of a nic which has to be attached to a Nuage subnet or L2 domain", dest='macs', type=str, action='append')
    parser.add_argument('-E', '--nuage-enterprise', required=True, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('-H', '--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('-p', '--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('-P', '--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('-U', '--nuage-user', required=True, help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('-s', '--subnet', required=True, help='Subnet or L2 domain UUID to attach the mac address to', dest='subnets', type=str, action='append')
    parser.add_argument('-u', '--uuid', required=True, help='UUID of the VM in VSD to which the interfaces need to be added', dest='uuid', type=str)
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', action='store_true')
    args = parser.parse_args()
    return args


def main():
    """
    Main function to handle statistics
    """

    # Handling arguments
    args = get_args()
    debug = args.debug
    log_file = None
    if args.logfile:
        log_file = args.logfile
    nuage_enterprise = args.nuage_enterprise
    nuage_host = args.nuage_host
    nuage_port = args.nuage_port
    nuage_password = None
    if args.nuage_password:
        nuage_password = args.nuage_password
    nuage_username = args.nuage_username
#    nosslcheck = args.nosslcheck
    verbose = args.verbose
    ips = []
    if args.ips:
        ips = args.ips
    macs = args.macs
    subnets = args.subnets
    uuid = args.uuid

    # Logging settings
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(filename=log_file, format='%(asctime)s %(levelname)s %(message)s', level=log_level)
    logger = logging.getLogger(__name__)

    # Sanity checks
    if len(macs) > 0 and len(macs) != len(subnets):
        logger.critical('The amount of macs is not equal to the amount of subnets, which is an invalid configuration.')
        return 1

    if len(ips) > 0 and len(macs) != len(ips):
        logger.critical('Some IPs are specified, but not the same amount as macs and subnets, which is an invalid configuration.')
        return 1

    # Getting user password for Nuage connection
    if nuage_password is None:
        logger.debug('No command line Nuage password received, requesting Nuage password from user')
        nuage_password = getpass.getpass(prompt='Enter password for Nuage host {0:s} for user {1:s}: '.format(nuage_host, nuage_username))

    try:
        # Connecting to Nuage
        logger.info('Connecting to Nuage server {0:s}:{1:d} with username {2:s}'.format(nuage_host, nuage_port, nuage_username))
        nc = vsdk.NUVSDSession(username=nuage_username, password=nuage_password, enterprise=nuage_enterprise, api_url="https://{0:s}:{1:d}".format(nuage_host, nuage_port))
        nc.start()

    except Exception as e:
        logger.error('Could not connect to Nuage host {0:s} with user {1:s} and specified password'.format(nuage_host, nuage_username))
        logger.critical('Caught exception: {0:s}'.format(str(e)))
        return 1

    logger.debug('Trying to fetch VM with ID {0:s}'.format(uuid))
    vm = vsdk.NUVM(id=uuid)
    vm.fetch()

    for mac in macs:
        index = macs.index(mac)
        subnet_id = subnets[index]
        subnet_type = None
        logger.info('Handling mac address {0:s} connection to subnet or L2 domain {1:s}'.format(mac, subnet_id))

        logger.debug('Trying to fetch subnet for ID {0:s}'.format(subnet_id))
        try:
            subnet = vsdk.NUSubnet(id=subnet_id)
            subnet.fetch()
            subnet_type = 'SUBNET'
        except:
            logger.debug('Subnet with ID {0:s} does not exist, looking for a L2 domain'.format(subnet_id))
            try:
                subnet = vsdk.NUL2Domain(id=subnet_id)
                subnet.fetch()
                subnet_type = 'L2DOMAIN'
            except:
                logger.error('Subnet with ID {0:s} can not be found as an subnet in an L3 domain or as an L2 domain, skipping mac {1:s} and subnet {2:s} and continuing to the next pair'.format(subnet_id, mac, subnet_id))
                continue

        vm_interface = vsdk.NUVMInterface()
        if len(ips) > 0:
            vm_interface.ip_address = ips[index]
        vm_interface.mac = mac
        vm_interface.name = 'if-{0:s}'.format(mac).replace(':','-')
        vm_interface.attached_network_id = subnet_id
        vm_interface.attached_network_type = subnet_type

        logger.debug('Creating interface {0:s} on VM {1:s}'.format(vm_interface.name, vm.name))
        try:
            vm.create_child(vm_interface)
        except Exception as e:
            logger.error('Failed to create interface {0:s} on VM {1:s}: {2:s}'.format(vm_interface.name, vm.name, str(e)))

    logger.info('Successfully added interfaces to VM {0:s}'.format(vm.name))
    return 0

# Start program
if __name__ == "__main__":
    main()
