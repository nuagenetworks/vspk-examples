# -*- coding: utf-8 -*-
"""
Used to update the UUID of a VM in case it has changed in the hypervisor.

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

--- Version history ---
2018-05-13 1.0 Initial version

--- Usage ---
run 'python vm_update_uuid.py -h' for an overview
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

    parser = argparse.ArgumentParser(description="vm_update_uuid is a tool to update UUID of a VM that was created with split activation.")
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect', dest='nosslcheck', action='store_true')
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-E', '--nuage-enterprise', required=True, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('-H', '--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('-p', '--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('-P', '--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('-U', '--nuage-user', required=True, help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('-i', '--id', required=True, help='ID of the VM in VSD that needs to be updated', dest='vmid', type=str)
    parser.add_argument('-u', '--uuid', required=True, help='The new UUID that needs to be configured for the VM', dest='uuid', type=str)
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
    vmid = args.vmid
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

    # Updating VM UUID
    logger.info('Updating VM %s UUID to %s' % (vmid, uuid))
    vm = vsdk.NUVM(id=vmid)
    try:
        vm.fetch()
        logger.debug('VM ID %s - OLD UUID %s - NEW UUID %s' % (vmid, vm.uuid, uuid))
        vm.uuid = uuid
        vm.resync_info = None
        vm.save()
    except Exception as e:
        logger.critical('VM %s can not be updated because of error %s' % (vmid, str(e)))
        return 1

    logger.info('Updated VM %s' % vmid)
    return 0

# Start program
if __name__ == "__main__":
    main()
