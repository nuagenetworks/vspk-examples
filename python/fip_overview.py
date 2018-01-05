# -*- coding: utf-8 -*-
"""
fip_overview produces a table with information on all VMs with a FIP attached. Output can also be given in JSON format.

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

--- Version history ---
2016-01-24 - 1.0
2016-01-26 - 1.1 - JSON output supported

--- Usage ---
run 'python fip_overview.py -h' for an overview

--- Documentation ---
http://github.com/nuagenetworks/vspk-examples/blob/master/docs/fip_overview.md

--- Example ---
python fip_overview.py -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S

"""

import argparse
import getpass
import json
import logging
import requests

from prettytable import PrettyTable
from vspk import v5_0 as vsdk


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="Tool to list all FIPs attached to the VMs to which the user has access to.")
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-j', '--json', required=False, help='Print as JSON, not as a table', dest='json_output', action='store_true')
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-E', '--nuage-enterprise', required=True, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('-H', '--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('-P', '--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('-p', '--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('-u', '--nuage-user', required=True, help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect', dest='nosslcheck', action='store_true')
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', action='store_true')
    args = parser.parse_args()
    return args


def main():
    """
    Main function to handle vcenter vm names and the mapping to a policy group
    """

    # Handling arguments
    args                = get_args()
    debug               = args.debug
    json_output         = args.json_output
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

    if json_output:
        logger.debug('Setting up json output')
        json_object = []
    else:
        logger.debug('Setting up basic output table')
        pt = PrettyTable(['Enterprise', 'Domain', 'VM Name', 'VM IP', 'VM MAC', 'FIP'])

    logger.debug('Getting FIPs for the logged in user.')
    for nc_fip in nc.user.floating_ips.get():
        logger.debug('Found FIP with IP %s' % nc_fip.address)
        nc_vport = nc_fip.vports.get()[0]
        nc_interface = nc_vport.vm_interfaces.get()[0]
        nc_vm = nc_vport.vms.get()[0]

        if json_output:
            json_dict = {
                'Enterprise': nc_vm.enterprise_name,
                'Domain': nc_interface.domain_name,
                'VM Name': nc_vm.name,
                'VM IP': nc_interface.ip_address,
                'VM MAC': nc_interface.mac,
                'FIP': nc_fip.address
            }
            json_object.append(json_dict)
        else:
            logger.debug('Add row: %s, %s, %s, %s, %s, %s' % (nc_vm.enterprise_name, nc_interface.domain_name, nc_vm.name, nc_interface.ip_address, nc_interface.mac, nc_fip.address))
            pt.add_row([nc_vm.enterprise_name, nc_interface.domain_name, nc_vm.name, nc_interface.ip_address, nc_interface.mac, nc_fip.address])

    if json_output:
        print json.dumps(json_object, sort_keys=True, indent=4)
    else:
        print pt

    return 0

# Start program
if __name__ == "__main__":
    main()
