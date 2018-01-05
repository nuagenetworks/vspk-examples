# -*- coding: utf-8 -*-
"""
vm_split_activation is a tool to do split activation of a VM inside a Nuage VSP
environment.

For each interface on the VM, connected to a Nuage subnet or L2 domain, a mac
address and subnet needs to be specified. At least one mac address and subnet
needs to be defined.

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

--- Version history ---
2016-08-06 - 0.1 - Initial development version
2016-08-08 - 0.2 - Bugfixes
2016-08-08 - 1.0 - Initial release

--- Usage ---
run 'python vm_split_activation.py -h' for an overview
"""
import argparse
import getpass
import logging
import requests
from vspk import v5_0 as vsdk


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="vm_split_activation is a tool to do split activation of a VM inside a Nuage VSP environment.")
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect', dest='nosslcheck', action='store_true')
    parser.add_argument('-e', '--external', required=False, help='When specified, the entities will be created with the indication that they are managed by an external system.', dest='external', action='store_true')
    parser.add_argument('-i', '--ip', required=False, help="IP address of a nic which has to be attached to a Nuage subnet or L2 domain", dest='ips', type=str, action='append')
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-m', '--mac', required=True, help="MAC address of a nic which has to be attached to a Nuage subnet or L2 domain", dest='macs', type=str, action='append')
    parser.add_argument('-n', '--name', required=True, help='Name of the VM that needs to be activated', dest='name', type=str)
    parser.add_argument('-E', '--nuage-enterprise', required=True, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('-H', '--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('-p', '--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('-P', '--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('-U', '--nuage-user', required=True, help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('-s', '--subnet', required=True, help='Subnet or L2 domain to attach the mac address to', dest='subnets', type=str, action='append')
    parser.add_argument('-u', '--uuid', required=True, help='UUID of the VM that needs to be activated', dest='uuid', type=str)
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
    nosslcheck = args.nosslcheck
    verbose = args.verbose
    external = args.external
    ips = []
    if args.ips:
        ips = args.ips
    macs = args.macs
    name = args.name
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

    except Exception as e:
        logger.error('Could not connect to Nuage host %s with user %s and specified password' % (nuage_host, nuage_username))
        logger.critical('Caught exception: %s' % str(e))
        return 1

    # Handling each mac/subnet combination and creating the necessary vPorts and VM Interfaces
    vports = []
    vm_interfaces = []
    for mac in macs:
        index = macs.index(mac)
        subnet_id = subnets[index]
        logger.info('Handling mac address %s connection to subnet or L2 domain %s' % (mac, subnet_id))

        logger.debug('Trying to fetch subnet for ID %s' % subnet_id)
        try:
            subnet = vsdk.NUSubnet(id=subnet_id)
            subnet.fetch()
        except:
            logger.debug('Subnet with ID %s does not exist, looking for a L2 domain' % subnet_id)
            try:
                subnet = vsdk.NUL2Domain(id=subnet_id)
                subnet.fetch()
            except:
                logger.error('Subnet with ID %s can not be found as an subnet in an L3 domain or as an L2 domain, skipping mac %s and subnet %s and continuing to the next pair' % (subnet_id, mac, subnet_id))
                continue

        # Creating vPort in subnet
        logger.debug('Creating vPort %s-vPort-%s in subnet %s (%s)' % (name, index, subnet.name, subnet_id))
        vport = vsdk.NUVPort(name='%s-vPort-%s' % (name, index), address_spoofing='INHERITED', type='VM', description='Automatically created, do not edit.')
        if external:
            vport.external_id = '%s-vPort-%s' % (name, index)
        subnet.create_child(vport)
        vports.append(vport)

        # Creating VMInterface
        logger.debug('Creating VMInterface object %s-vm-interface-%s for mac %s with vPort ID %s' % (name, index, mac, vport.id))
        vm_interface = vsdk.NUVMInterface(name='%s-vm-interface-%s' % (name, index), vport_id=vport.id, mac=mac)
        if external:
            vm_interface.external_id = '%s-vm-interface-%s' % (name, index)
        if len(ips) > 0:
            vm_interface.ip_address = ips[index]
        vm_interfaces.append(vm_interface)

    # Creating VM
    logger.info('Creating VM %s with UUID %s' % (name, uuid))
    vm = vsdk.NUVM(name=name, uuid=uuid, interfaces=vm_interfaces)
    if external:
        vm.external_id = uuid
    try:
        logger.debug('Trying to save VM %s.' % name)
        nc.user.create_child(vm)
    except Exception as e:
        logger.critical('VM %s can not be created because of error %s' % (name, str(e)))
        logger.debug('Cleaning up the vPorts')
        for vport in vports:
            logger.debug('Deleting vPort %s' % vport.name)
            vport.delete()
        return 1

    logger.info('Created all necessary entities in the appropriate subnets or L2 domains for VM %s' % name)
    return 0

# Start program
if __name__ == "__main__":
    main()
