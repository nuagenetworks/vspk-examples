# -*- coding: utf-8 -*-
"""

Check the examples for several combinations of arguments.

--- CSV Strucure ---
A CSV file for each vCenter will be created as a backup of the information in VCIN. This file will have the following
 structure. This structure is compatible with the vcin_vdt_configure_from_vsphere.py script in the VSPK-Examples Github
 repository (https://github.com/nuagenetworks/vspk-examples)
    "<IP>/<FQDN>",
    "[name]",
    "[hypervisor user]",
    "[hypervisor password]",
    "[management network portgroup]",
    "[data network portgroup]",
    "[vm network portgroup]",
    "[multicast sourece portgroup]",
    "[use management DHCP (True|False)]",
    "[management IP]",
    "[management netmask (octet structure)]",
    "[management gateway]",
    "[management DNS 1]",
    "[management DNS 2]",
    "[separate data network (True|False)]",
    "[use data DHCP (True|False)]",
    "[data IP]",
    "[data netmask (octet structure)]",
    "[data gateway]",
    "[data DNS 1]",
    "[data DNS 2]",
    "[MTU]",
    "[require metadata (True|False)]",
    "[generic split activation (True|False)]",
    "[multi VM support (True|False)]",
    "[DHCP relay server (IP)]",
    "[flow eviction threshold]",
    "[datapath sync timeout]",
    "[network uplink interface]",
    "[network uplink IP]",
    "[network uplink netmask (octet structure)]",
    "[network uplink gateway]",
    "[script URL]",
    "[personality]",
    "[site ID]",
    "[NFS server address (IP)]",
    "[NFS mount path]",
    "[primay Nuage controller (IP)]",
    "[secondary Nuage controller (IP)]",
    "[primary NTP server (IP)]",
    "[secondary NTP server (IP)]",
    "[static route target IP]",
    "[static route netmask (octet structure)]",
    "[static route next-hop gateway]",
    "[multicast send interface]",
    "[multicast send IP]",
    "[multicast send netmask (octet structure)]",
    "[multicast receive IP]",
    "[multicast receive netmask (octet structure)]",
    "[Host Agent VM Port Group]",
    "[Host Agent VM Datastore]"

--- Version history ---
2016-10-12 - 1.0 - Initial release
2016-10-13 - 1.1 - Updated to support Generic split activation.

--- Usage ---
Run 'python vcin_hypervisors_backup.py -h' for an overview

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

"""

import argparse
import csv
import getpass
import logging
import os.path
import requests

from vspk import v5_0 as vsdk


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="A tool to backup your configuration in VCIN to a CSV file which can be used with the vcin_vdt_configure_from_vsphere.py script.")
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-E', '--nuage-enterprise', required=True, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('-H', '--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('-P', '--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('-p', '--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('-u', '--nuage-user', required=True, help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('-o', '--output-folder', required=True, help='The folder to where to write the output to, a file per vCenter will be created', dest='output_folder', type=str)
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect', dest='nosslcheck', action='store_true')
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', action='store_true')
    args = parser.parse_args()
    return args

def main():
    """
    Backup the vCenter Integration Node configuration
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
    output_folder = args.output_folder
    nosslcheck = args.nosslcheck
    verbose = args.verbose
    # Logging settings
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING


    logging.basicConfig(filename=log_file, format='%(asctime)s %(levelname)s %(message)s', level=log_level)
    logger = logging.getLogger(__name__)

    # Checking if folder is writeable
    if not os.access(output_folder, os.W_OK):
        logger.critical('Folder {0:s} is not writable, exiting.'.format(output_folder))
        return 1

    # Disabling SSL verification if set
    ssl_context = None
    if nosslcheck:
        logger.debug('Disabling SSL certificate verification.')
        requests.packages.urllib3.disable_warnings()

    # Getting user password for Nuage connection
    if nuage_password is None:
        logger.debug('No command line Nuage password received, requesting Nuage password from user')
        nuage_password = getpass.getpass(
            prompt='Enter password for Nuage host {0:s} for user {1:s}: '.format(nuage_host, nuage_username))

    nc = None

    # Connecting to Nuage
    try:
        logger.info('Connecting to Nuage server {0:s}:{1:d} with username {2:s}'.format(nuage_host, nuage_port, nuage_username))
        nc = vsdk.NUVSDSession(username=nuage_username, password=nuage_password, enterprise=nuage_enterprise,
                               api_url="https://{0:s}:{1:d}".format(nuage_host, nuage_port))
        nc.start()
    except IOError, e:
        pass

    if not nc or not nc.is_current_session():
        logger.error(
            'Could not connect to Nuage host {0:s} with user {1:s} and specified password'.format(nuage_host, nuage_username))
        return 1

    logger.info('Connected to Nuage')

    # Run through each vCenter
    for nvc in nc.user.vcenters.get():
        logger.debug('Running for vCenter {0:s}'.format(nvc.name))
        hosts = []
        for ndc in nvc.vcenter_data_centers.get():
            logger.debug('Running for DC {0:s}'.format(ndc.name))
            for ncl in ndc.vcenter_clusters.get():
                logger.debug('Running for cluster {0:s}'.format(ncl.name))
                for host in ncl.vcenter_hypervisors.get():
                    logger.debug('Handling host {0:s}'.format(host.name))
                    host = [
                        host.hypervisor_ip,
                        host.name,
                        host.hypervisor_user,
                        host.hypervisor_password,
                        host.mgmt_network_portgroup,
                        host.data_network_portgroup,
                        host.vm_network_portgroup,
                        host.multicast_source_portgroup,
                        host.allow_mgmt_dhcp,
                        host.mgmt_ip_address,
                        host.mgmt_netmask,
                        host.mgmt_gateway,
                        host.mgmt_dns1,
                        host.mgmt_dns2,
                        host.separate_data_network,
                        host.allow_data_dhcp,
                        host.data_ip_address,
                        host.data_netmask,
                        host.data_gateway,
                        host.data_dns1,
                        host.data_dns2,
                        host.mtu,
                        host.v_require_nuage_metadata,
                        host.generic_split_activation,
                        host.multi_vmssupport,
                        host.dhcp_relay_server,
                        host.flow_eviction_threshold,
                        host.datapath_sync_timeout,
                        host.network_uplink_interface,
                        host.network_uplink_interface_ip,
                        host.network_uplink_interface_netmask,
                        host.network_uplink_interface_gateway,
                        host.customized_script_url,
                        host.personality,
                        host.site_id,
                        host.nfs_log_server,
                        host.nfs_mount_path,
                        host.primary_nuage_controller,
                        host.secondary_nuage_controller,
                        host.ntp_server1,
                        host.ntp_server2,
                        host.static_route,
                        host.static_route_netmask,
                        host.static_route_gateway,
                        host.multicast_send_interface,
                        host.multicast_send_interface_ip,
                        host.multicast_send_interface_netmask,
                        host.multicast_receive_interface_ip,
                        host.multicast_receive_interface_netmask,
                        '',
                        ''
                    ]
                    hosts.append(host)

                logger.debug('Writing CSV for vCenter {0:s}'.format(nvc.name))
                with open('{0:s}/{1:s}.csv'.format(output_folder, nvc.name), 'w') as hostlist:
                    writer = csv.writer(hostlist, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                    writer.writerows(hosts)

            logger.info('Completed all tasks.')
            return 0

# Start program
if __name__ == "__main__":
    main()
