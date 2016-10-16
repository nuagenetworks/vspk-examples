# -*- coding: utf-8 -*-
"""
vcenter_vm_os_to_nuage_policygroups is a script that will translate vCenter VM operating system settings to Policy
groups on that VM in Nuage for VMs in a certain set of Clusters.

This script has the following features:
    * Assings Policy Groups depending on regular expressions matching the VM Operating system in vCenter
    * Supports multiple Policy Groups per VM/vPort (will match multiple regular expressions on the same VM and
      assign all Policy Groups)
    * Run only for VMs on a certain set of clusters
    * Remove policy groups that are not valid according to the regex's (if option is enabled)
    * Validates if the VM is attached to a valid Nuage L2 or L3 domain (checks Nuage metadata on the VM)
    * Validates if the Policy Group is valid in the domain to which the VM/vPort is attached

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

--- Version history ---
2016-10-16 - 1.0

--- CSV ---
It requires a mapping file which is a CSV, configured with the following fields (fields with <> surrounding
 them are mandatory):
"<vCenter VM OS regex>","<Policy Group>"

Example CSV content:
".*Windows.*","Windows"
".*Centos.*","Centos"
".*Ubuntu.*","Ubuntu"

All the VMware VMs which are attached to a Nuage domain (L2 or L3) in the provided list of clusters and which operating
 system contains 'Windows', will get the Windows Policy group (if that policy group exists for that domain)

--- Limitations ---
- Only supports VMs with one interface

--- Usage ---
Run 'python vcenter_vm_os_to_nuage_policygroups.py -h' for an overview

--- Documentation ---
http://github.com/nuagenetworks/vspk-examples/blob/master/docs/vcenter_vm_os_to_nuage_policygroups.md

--- Example ---
---- All VMs in two clusters, with debug output to a log file ----
python vcenter_vm_os_to_nuage_policygroups.py -c DC1-Compute -c DC2-Compute -d -l /tmp/PG-set.log -m vm-os_policy-groups.csv --nuage-enterprise csp --nuage-host 192.168.1.10 --nuage-port 443 --nuage-password csproot --nuage-user csproot -r -S --vcenter-host 192.168.1.20 --vcenter-port 443 --vcenter-password vmware --vcenter-user root

"""

import argparse
import atexit
import csv
import getpass
import logging
import os.path
import re
import requests

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
from vspk import v4_0 as vsdk


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="Script which will apply policy groups on VMs depending on the VM OS in vCenter for a certain set of Clusters")
    parser.add_argument('-c', '--cluster', required=True, help='Cluster that has to be scanned for VMs (can be specified multiple times)', dest='clusters', type=str, action='append')
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-m', '--mapping-file', required=True, help='CSV file which contains the mapping of vCenter OS to policy groups', dest='mapping_file', type=str)
    parser.add_argument('--nuage-enterprise', required=True, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('--nuage-user', required=True, help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('-r', '--remove-policygroups', required=False, help='Remove policygroups from all VMs before adding the correct matching ones.', dest='remove_policygroups', action='store_true')
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect', dest='nosslcheck', action='store_true')
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', action='store_true')
    parser.add_argument('--vcenter-host', required=True, help='The vCenter server to connect to, use the IP', dest='vcenter_host', type=str)
    parser.add_argument('--vcenter-port', required=False, help='The vCenter server HTTPS port to connect to (default = 443)', dest='vcenter_https_port', type=int, default=443)
    parser.add_argument('--vcenter-password', required=False, help='The password with which to connect to the vCenter host. If not specified, the user is prompted at runtime for a password', dest='vcenter_password', type=str)
    parser.add_argument('--vcenter-user', required=True, help='The username with which to connect to the vCenter host', dest='vcenter_username', type=str)
    args = parser.parse_args()
    return args


def update_nuage_policy_group(logger, nc, nc_vm_properties, nc_vm_pgs, remove_policygroups):
    # Finding domain
    nc_domain = None
    nc_domain_name = ''
    if nc_vm_properties['nuage.domain'] is not None:
        nc_domain = nc.user.domains.get_first(filter="name == '{0:s}'".format(nc_vm_properties['nuage.domain']))
        nc_domain_name = nc_vm_properties['nuage.domain']
    elif nc_vm_properties['nuage.l2domain'] is not None:
        nc_domain = nc.user.l2_domains.get_first(filter="name == '{0:s}'".format(nc_vm_properties['nuage.l2domain']))
        nc_domain_name = nc_vm_properties['nuage.l2domain']

    if nc_domain is None:
        # If still none, the domain does not exist, skip it
        logger.error('Domain {0:s} can not be found in Nuage for VM {1:s}, skipping it' .format(nc_domain_name, nc_vm_properties['name']))
        return False

    if remove_policygroups:
        logger.info('Clearing all policy tags from VM {0:s} in Nuage'.format(nc_vm_properties['name']))
        nc_vport_pgs = []
    else:
        logger.info('Starting from the existing set of Policy Groups for VM {0:s}'.format(nc_vm_properties['name']))
        nc_vport_pgs = nc_vm_properties['vport'].policy_groups.get()

    pg_change = False
    for nc_pg_name in nc_vm_pgs:
        # Getting the policy group which matches the required one
        logger.debug('Looking for Policy Group {0:s} in domain {0:s} for VM {0:s}'.format(nc_pg_name, nc_vm_properties['nuage.domain'], nc_vm_properties['name']))
        nc_vm_pg = nc_domain.policy_groups.get_first(filter="name == '{0:s}'".format(nc_pg_name))
        if nc_vm_pg is None:
            logger.error('Policy Group {0:s} can not be found in domain {0:s} for VM {0:s}, skipping it'.format(nc_pg_name, nc_vm_properties['nuage.domain'], nc_vm_properties['name']))
            continue

        if not any(x.id == nc_vm_pg.id for x in nc_vport_pgs):
            # Adding Policy Group to vPort
            logger.debug('Adding Policy Group {0:s} to VM {0:s}'.format(nc_pg_name, nc_vm_properties['name']))
            nc_vport_pgs.append(nc_vm_pg)
            pg_change = True

    if pg_change:
        nc_vm_properties['vport'].assign(nc_vport_pgs, vsdk.NUPolicyGroup)
        logger.info('Saved {0:d} Policy Groups to VM {0:s}'.format(len(nc_vport_pgs), nc_vm_properties['name']))
    else:
        logger.info('No changes found in the Policy Group settings for VM {0:s}, skipping'.format(nc_vm_properties['name']))

    return True


def main():
    """
    Main function to handle vcenter vm os and the mapping to a policy group
    """

    # Handling arguments
    args = get_args()
    clusters = []
    if args.clusters:
        clusters = args.clusters
    debug = args.debug
    log_file = None
    if args.logfile:
        log_file = args.logfile
    mapping_file = args.mapping_file
    nuage_enterprise = args.nuage_enterprise
    nuage_host = args.nuage_host
    nuage_port = args.nuage_port
    nuage_password = None
    if args.nuage_password:
        nuage_password = args.nuage_password
    nuage_username = args.nuage_username
    remove_policygroups = args.remove_policygroups
    nosslcheck = args.nosslcheck
    verbose = args.verbose
    vcenter_host = args.vcenter_host
    vcenter_https_port = args.vcenter_https_port
    vcenter_password = None
    if args.vcenter_password:
        vcenter_password = args.vcenter_password
    vcenter_username = args.vcenter_username

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
    ssl_context = None
    if nosslcheck:
        logger.debug('Disabling SSL certificate verification.')
        requests.packages.urllib3.disable_warnings()
        import ssl
        if hasattr(ssl, 'SSLContext'):
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            ssl_context.verify_mode = ssl.CERT_NONE

    # Getting user password for Nuage connection
    if nuage_password is None:
        logger.debug('No command line Nuage password received, requesting Nuage password from user')
        nuage_password = getpass.getpass(prompt='Enter password for Nuage host {0:s} for user {1:s}: '.format(nuage_host, nuage_username))

    # Getting user password for vCenter connection
    if vcenter_password is None:
        logger.debug('No command line vCenter password received, requesting vCenter password from user')
        vcenter_password = getpass.getpass(prompt='Enter password for vCenter host {0:s} for user {1:s}: '.format(vcenter_host, vcenter_username))

    try:
        vc = None
        nc = None

        # Connecting to Nuage
        try:
            logger.info('Connecting to Nuage server %s:%s with username %s' % (nuage_host, nuage_port, nuage_username))
            nc = vsdk.NUVSDSession(username=nuage_username, password=nuage_password, enterprise=nuage_enterprise, api_url="https://{0:s}:{1:s}".format(nuage_host, nuage_port))
            nc.start()
        except IOError:
            pass

        if not nc or not nc.is_current_session():
            logger.error('Could not connect to Nuage host {0:s} with user {1:s} and specified password'.format(nuage_host, nuage_username))
            return 1

        # Connecting to vCenter
        try:
            logger.info('Connecting to vCenter server {0:s}:{1:s} with username {2:s}'.format(vcenter_host, vcenter_https_port, vcenter_username))
            if ssl_context:
                vc = SmartConnect(host=vcenter_host, user=vcenter_username, pwd=vcenter_password, port=int(vcenter_https_port), sslContext=ssl_context)
            else:
                vc = SmartConnect(host=vcenter_host, user=vcenter_username, pwd=vcenter_password, port=int(vcenter_https_port))

        except IOError:
            pass

        if not vc:
            logger.error('Could not connect to vCenter host {0:s} with user {1:s} and specified password'.format(vcenter_host, vcenter_username))
            return 1

        logger.debug('Registering vCenter disconnect at exit')
        atexit.register(Disconnect, vc)

        logger.info('Connected to both Nuage & vCenter servers')

    except vmodl.MethodFault, e:
        logger.critical('Caught vmodl fault: {0:s}'.format(e.msg))
        return 1
    except Exception, e:
        logger.critical('Caught exception: {0:s}'.format(str(e)))
        return 1

    # CSV Handling
    if not os.path.isfile(mapping_file):
        logger.critical('Mapping file {0:s} does not exist, exiting'.format(mapping_file))
        return 1

    mapping_list = {}
    # CSV fields:
    # vCenter VM name regex, Policy group
    logger.debug('Parsing mapping file {0:s}'.format(mapping_file))

    with open(mapping_file, 'rb') as maplist:
        mapping_list_raw = csv.reader(maplist, delimiter=',', quotechar='"')
        for row in mapping_list_raw:
            logger.debug('Found CSV row: {0:s}'.format(','.join(row)))
            mapping_list[row[0]] = row[1]

    # Getting clusters in the current vCenter
    logger.debug('Gathering all Clusters from the vCenter {0:s}'.format(vcenter_host))
    content = vc.content
    obj_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.ClusterComputeResource], True)
    vc_cl_list = obj_view.view
    obj_view.Destroy()

    for vc_cl in vc_cl_list:
        if vc_cl.name not in clusters:
            continue

        # Getting VMs in the current vCenter Cluster
        logger.debug('Gathering all VMs from the vCenter Cluster {0:s}'.format(vc_cl.name))
        obj_view = content.viewManager.CreateContainerView(vc_cl, [vim.VirtualMachine], True)
        vc_vm_list = obj_view.view
        obj_view.Destroy()

        for vc_vm in vc_vm_list:
            # Verifying if VM matches a regex in the list
            logger.debug('Found VM {0:s}, checking'.format(vc_vm.name))

            # If the VM is a template skip it
            if vc_vm.config.template:
                logger.debug('VM {0:s} is a template, skipping'.format(vc_vm.name))
                continue

            # Getting VM info
            nc_vm_properties = {}
            vc_vm_nuage_enterprise = next((x for x in vc_vm.config.extraConfig if x.key == 'nuage.enterprise'), None)
            vc_vm_nuage_domain = next((x for x in vc_vm.config.extraConfig if x.key == 'nuage.nic0.domain'), None)
            vc_vm_nuage_l2domain = next((x for x in vc_vm.config.extraConfig if x.key == 'nuage.nic0.l2domain'), None)
            vc_vm_nuage_zone = next((x for x in vc_vm.config.extraConfig if x.key == 'nuage.nic0.zone'), None)
            vc_vm_nuage_network = next((x for x in vc_vm.config.extraConfig if x.key == 'nuage.nic0.network'), None)

            # Check if all the settings for an L3 domain are present
            if vc_vm_nuage_enterprise is None or vc_vm_nuage_domain is None or vc_vm_nuage_zone is None or vc_vm_nuage_network is None:
                # Check if it is an L2 domain
                if vc_vm_nuage_enterprise is None or vc_vm_nuage_l2domain is None:
                    logger.info('VM {0:s} has no correct Nuage metadata set, assuming it is not a VM connected through Nuage and skipping it.'.format(vc_vm.name))
                    continue

            nc_vm_properties['name'] = vc_vm.name
            nc_vm_properties['os'] = vc_vm.config.guestFullName
            nc_vm_properties['nuage.enterprise'] = vc_vm_nuage_enterprise.value
            # If domain is not set, it is an l2 domain
            if vc_vm_nuage_domain is not None:
                nc_vm_properties['nuage.domain'] = vc_vm_nuage_domain.value
                nc_vm_properties['nuage.l2domain'] = None
                nc_vm_domain_name = vc_vm_nuage_domain.value
            else:
                nc_vm_properties['nuage.domain'] = None
                nc_vm_properties['nuage.l2domain'] = vc_vm_nuage_l2domain.value
                nc_vm_domain_name = vc_vm_nuage_l2domain.value
            if vc_vm_nuage_zone is not None:
                nc_vm_properties['nuage.zone'] = vc_vm_nuage_zone.value
            else:
                nc_vm_properties['nuage.zone'] = None
            if vc_vm_nuage_network is not None:
                nc_vm_properties['nuage.network'] = vc_vm_nuage_network.value
            else:
                nc_vm_properties['nuage.network'] = None

            logger.debug('VM {0:s} with OS {1:s} has following Nuage settings: Enterprise {2:s}, Domain {3:s}, Zone {4:s}, Subnet {5:s}'.format(nc_vm_properties['name'], nc_vm_properties['os'], nc_vm_properties['nuage.enterprise'], nc_vm_domain_name, nc_vm_properties['nuage.zone'], nc_vm_properties['nuage.network']))

            # Getting VM MAC
            vc_vm_nic = next((x for x in vc_vm.config.hardware.device if isinstance(x, vim.vm.device.VirtualEthernetCard)), None)
            if vc_vm_nic is None:
                logger.error('VM {0:s} has no valid network interfaces, skipping it'.format(nc_vm_properties['name']))
                continue

            nc_vm_properties['mac'] = vc_vm_nic.macAddress
            logger.debug('VM {0:s} has MAC {1:s}'.format(nc_vm_properties['name'], nc_vm_properties['mac']))

            # Getting Nuage vport for this VM
            nc_vm_properties['vm_interface'] = nc.user.vm_interfaces.get_first(filter="MAC == '{0:s}'".format(nc_vm_properties['mac']))
            if nc_vm_properties['vm_interface'] is None:
                logger.error('VM {0:s} with MAC address {1:s} is not known in Nuage, skipping it'.format(nc_vm_properties['name'], nc_vm_properties['mac']))
                continue

            # Getting Nuage vport for this VM
            nc_vm_properties['vport'] = vsdk.NUVPort(id=nc_vm_properties['vm_interface'].vport_id)
            try:
                nc_vm_properties['vport'].fetch()
            except Exception:
                logger.error('VM {0:s} with MAC address {1:s} has a vm_interface but no vport in Nuage, this should not be possible... Skipping it'.format(nc_vm_properties['name'], nc_vm_properties['mac']))
                continue

            logger.debug('Found vm_interface and vport for VM {0:s} with MAC address {1:s}'.format(nc_vm_properties['name'], nc_vm_properties['mac']))

            # Checking regex's on VMs
            nc_vm_pgs = []
            for regex in mapping_list.keys():
                logger.debug('Checking regex "{0:s}" on VM {1:s} with OS {2:s}'.format(regex, nc_vm_properties['name'], nc_vm_properties['os']))
                pattern = re.compile(regex)
                if pattern.match(nc_vm_properties['os']):
                    logger.debug('Found match: regex "{0:s}" and VM OS "{1:s}", adding to the task list to hand over to Nuage.'.format(regex, nc_vm_properties['os']))
                    nc_vm_pgs.append(mapping_list[regex])

            if len(nc_vm_pgs) > 0:
                logger.debug('Handing task over to Nuage part to set {0:d} Policy Groups on VM {0:s}'.format(len(nc_vm_pgs), nc_vm_properties['name']))
                update_nuage_policy_group(logger=logger, nc=nc, nc_vm_properties=nc_vm_properties, nc_vm_pgs=nc_vm_pgs, remove_policygroups=remove_policygroups)

    logger.info('All done!')
    return 0

# Start program
if __name__ == "__main__":
    main()
