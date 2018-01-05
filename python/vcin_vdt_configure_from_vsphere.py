# -*- coding: utf-8 -*-
"""
vcin_vdt_configure_from_vsphere is a script which will configure the full vCenter tree of Datacenters, Clusters and Hosts into the Nuage vCenter Integration Node and the Nuage vCenter Deployment Tool. It is also capable of configuring the ESXi hosts with the correct Agent VM settings.

This script has the following features:
    * Configure a vCenter structure inside the Nuage vCenter Deployment Tool
    * Configure the full tree of Datacenters, Clusters and Hosts, or
    * Configure a subset of the tree by specifying which:
        * Datacenters to add
        * Clusters to add
        * Hosts to add
    * Host and VRS configuration values can be set per host using a CSV file.
    * ESXi Host Agent VM settings can be configured per host, either by using the CSV file or automatically, in which case it will use the management network (hv-management-network) and the first available local VMFS datastore on the host.
    * Data on fields that require a specific type of data (IP's, True/False fields and limited selection fields)
    * It will only create those entities that are specified and do not exist yet.
    * It will update existing host and VRS configurations: only the fields for which data has been provided, empty fields are not overwritten.
    * Passwords that are not specified as arguments, will be prompted for (security measure)
    * Provide verbose & debug logging

Check the examples for several combinations of arguments.

--- Limitations ---
    * You can only add hosts to a cluster, not to a datacenter. vCenter supports this, but the Nuage vCenter Deployment Tool does not.
    * Only adding Hosts which all have the same username, password, management network, data network, VM network and Multicast Source network are supported
    * If --all-hosts is specified, it will use the first VMkernel IP address it encounters for the Host

--- CSV Strucure ---
A CSV file can be used to import individual settings for each host. The structure of this CSV looks like this (fields in <> are mandatory, fields with [] can be left blank)
 (for overview purpose, each field is on it's own line. In the file itself, this should all be one line)
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

--- Usage ---
Run 'python vcin_vdt_configure_from_vsphere.py -h' for an overview

--- Documentation ---
http://github.com/nuagenetworks/vspk-examples/blob/master/docs/vcin_vdt_configure_from_vsphere.md

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

--- Examples ---
---- Create all datacenters, clusters & hosts ----
python vcin_vdt_configure_from_vsphere.py -d --nuage-enterprise csp --nuage-host 10.167.43.52 --nuage-user csproot --nuage-vrs-ovf http://10.167.43.14/VMware-VRS/VRS_3.2.2-74.ovf -S --vcenter-host 10.167.43.24 --vcenter-user root --vcenter-name "Main vCenter" -l /tmp/populate.log --all-datacenters  --all-clusters --all-hosts --hv-user root --hv-management-network Management --hv-data-network "Data Control" --hv-vm-network 1-Compute-OVSPG --hv-mc-network 1-Compute-PG1

---- Create 1 datacenter, 2 clusters & all hosts - Only the hosts in the selected clusters are added in this case ----
python vcin_vdt_configure_from_vsphere.py -d --nuage-enterprise csp --nuage-host 10.167.43.52 --nuage-user csproot --nuage-vrs-ovf http://10.167.43.14/VMware-VRS/VRS_3.2.2-74.ovf -S --vcenter-host 10.167.43.24 --vcenter-user root --vcenter-name "Main vCenter" -l /tmp/populate.log --datacenter "Main DC" --cluster DC1-Compute --cluster DC2-Compute --all-hosts --hv-user root --hv-management-network Management --hv-data-network "Data Control" --hv-vm-network 1-Compute-OVSPG --hv-mc-network 1-Compute-PG1

---- Create 1 datacenter, 2 clusters & 2 hosts - Only if the host exists in one of the selected clusters, it is added to that cluster ----
python vcin_vdt_configure_from_vsphere.py -d --nuage-enterprise csp --nuage-host 10.167.43.52 --nuage-user csproot --nuage-vrs-ovf http://10.167.43.14/VMware-VRS/VRS_3.2.2-74.ovf -S --vcenter-host 10.167.43.24 --vcenter-user root --vcenter-name "Main vCenter" -l /tmp/populate.log --datacenter "Main DC" --cluster DC1-Compute --cluster DC2-Compute --host 10.167.43.9 --host 10.167.43.12 --hv-user root --hv-management-network Management --hv-data-network "Data Control" --hv-vm-network 1-Compute-OVSPG --hv-mc-network 1-Compute-PG1

---- Create 1 datacenter, 2 clusters & the hosts with their specific configuration from the hosts-file.csv in the samples folder - Only the hosts in the selected clusters are added in this case ----
python vcin_vdt_configure_from_vsphere.py -d --nuage-enterprise csp --nuage-host 10.167.43.52 --nuage-user csproot --nuage-vrs-ovf http://10.167.43.14/VMware-VRS/VRS_3.2.2-74.ovf -S --vcenter-host 10.167.43.24 --vcenter-user root --vcenter-name "Main vCenter" -l /tmp/populate.log --datacenter "Main DC" --cluster DC1-Compute --cluster DC2-Compute --hosts-file samples/hosts-file.csv --hv-user root --hv-management-network Management --hv-data-network "Data Control" --hv-vm-network 1-Compute-OVSPG --hv-mc-network 1-Compute-PG1

---- Create 1 datacenter, 2 clusters & the hosts with their specific configuration from the hosts-file.csv in the samples folder and configure the hosts Agent VM settings - Only the hosts in the selected clusters are added in this case ----
python vcin_vdt_configure_from_vsphere.py -d --nuage-enterprise csp --nuage-host 10.167.43.52 --nuage-user csproot --nuage-vrs-ovf http://10.167.43.14/VMware-VRS/VRS_3.2.2-74.ovf -S --vcenter-host 10.167.43.24 --vcenter-user root --vcenter-name "Main vCenter" -l /tmp/populate.log --datacenter "Main DC" --cluster DC1-Compute --cluster DC2-Compute --hosts-file samples/hosts-file.csv --hv-user root --hv-management-network Management --hv-data-network "Data Control" --hv-vm-network 1-Compute-OVSPG --hv-mc-network 1-Compute-PG1 --host-configure-agent
"""

import argparse
import atexit
import csv
import getpass
import logging
import os.path
import requests
import socket

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
from vspk import v5_0 as vsdk


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="Add a (sub)tree from a vCenter's structure to the Nuage vCenter Deployment Tool. This can be done by specifying the datacenters, clusters and hosts you want to add. You can also specify to include all datacenters and/or clusters and/or hosts, depending on your requirements. It is also possible to provide a CSV file containing the hosts to add and each hosts specific configuration. Creation will only happen if the entity doesn't exist yet in the vCenter Deployment Tool. Hosts will be updated with the new configuration if you run the script with already existsing hosts. This script is also capable of updating the ESXi Hosts Agent VM settings.")
    parser.add_argument('--all-clusters', required=False, help='Configure all Clusters from the selected vCenter Datacenters', dest='all_clusters', action='store_true')
    parser.add_argument('--all-datacenters', required=False, help='Configure all vCenter Datacenters from the vCenter', dest='all_datacenters', action='store_true')
    parser.add_argument('--all-hosts', required=False, help='Configure all Hosts from the selected Clusters', dest='all_hosts', action='store_true')
    parser.add_argument('--cluster', required=False, help='Cluster that has to be present in the Nuage vCenter Deployment Tool (can be specified multiple times)', dest='clusters', type=str, action='append')
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-f', '--allow-fqdn', required=False, help='Allow the use of FQDN in the CSV hosts file instead of IP', dest='allow_fqdn', action='store_true')
    parser.add_argument('--datacenter', required=False, help='Datacenter that has to be present in the Nuage vCenter Deployment Tool (can be specified multiple times)', dest='datacenters', type=str, action='append')
    parser.add_argument('--host', required=False, help='Host IPs that has to be present in the Nuage vCenter Deployment Tool (can be specified multiple times)', dest='hosts', type=str, action='append')
    parser.add_argument('--host-configure-agent', required=False, help='Configure the VM Agent settings of the vCenter Hosts. It will configure the Management network you specify as an argument with --hv-management-network, or the one in the CSV file if specified. For datastore it will use the first available local datastore, or the one specified in the CSV file if provided.', dest='host_configure_agent', action='store_true')
    parser.add_argument('--hosts-file', required=False, help='CSV file which contains the configuration for each hypervisor', dest='hosts_file', type=str)
    parser.add_argument('--hv-user', required=True, help='The ESXi (default) hosts username', dest='hv_username', type=str)
    parser.add_argument('--hv-password', required=False, help='The ESXi hosts password. If not specified, the user is prompted at runtime for a password', dest='hv_password', type=str)
    parser.add_argument('--hv-management-network', required=True, help='The ESXi hosts management network', dest='hv_management_network', type=str)
    parser.add_argument('--hv-data-network', required=True, help='The ESXi hosts data network', dest='hv_data_network', type=str)
    parser.add_argument('--hv-vm-network', required=True, help='The ESXi hosts VM network', dest='hv_vm_network', type=str)
    parser.add_argument('--hv-mc-network', required=True, help='The ESXi hosts Multicast Source network', dest='hv_mc_network', type=str)
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('--nuage-enterprise', required=True, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('--nuage-user', required=True, help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('--nuage-vrs-ovf', required=False, help='The URL of the VRS OVF file', dest='nuage_vrs_ovf', type=str)
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect', dest='nosslcheck', action='store_true')
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', action='store_true')
    parser.add_argument('--vcenter-host', required=True, help='The vCenter server to connect to, use the IP', dest='vcenter_host', type=str)
    parser.add_argument('--vcenter-name', required=False, help='The name of the vCenter you want in the vCenter Deployment Tool', dest='vcenter_name', type=str)
    parser.add_argument('--vcenter-http-port', required=False, help='The vCenter server HTTP port to connect to (default = 80)', dest='vcenter_http_port', type=int, default=80)
    parser.add_argument('--vcenter-https-port', required=False, help='The vCenter server HTTPS port to connect to (default = 443)', dest='vcenter_https_port', type=int, default=443)
    parser.add_argument('--vcenter-password', required=False, help='The password with which to connect to the vCenter host. If not specified, the user is prompted at runtime for a password', dest='vcenter_password', type=str)
    parser.add_argument('--vcenter-user', required=True, help='The username with which to connect to the vCenter host', dest='vcenter_username', type=str)
    args = parser.parse_args()
    return args


def handle_vdt_datacenter(logger, nc, vc, nuage_vcenter, vc_dc, nc_dc_list, vcenter_name, all_clusters, all_hosts, clusters, hosts, hosts_list, hv_username, hv_password, hv_management_network, hv_data_network, hv_vm_network, hv_mc_network, host_configure_agent, allow_fqdn):
    # Checking if the Datacenter exists in the Nuage vCenter Deployment Tool
    logger.debug('Checking vCenter Datacenter %s in Nuage vCenter Deployment Tool' % vc_dc.name)
    active_nc_dc = None
    for nc_dc in nc_dc_list:
        if vc_dc.name == nc_dc.name:
            active_nc_dc = nc_dc
            logger.debug('Found Datacenter %s in Nuage vCenter Deployment Tool' % vc_dc.name)
            break

    # If the Datacenter does not exist in Nuage vCenter Deployment Tool, create it
    if not active_nc_dc:
        logger.debug('Datacenter %s not found in the vCenter %s in the Nuage vCenter Deployment Tool, creating' % (vc_dc.name, vcenter_name))
        active_nc_dc = vsdk.NUVCenterDataCenter(name=vc_dc.name)
        nuage_vcenter.create_child(active_nc_dc)
        logger.info('Created Datacenter %s from the vCenter %s in the Nuage vCenter Deployment Tool' % (vc_dc.name, vcenter_name))

    # Getting clusters in the current vCenter Datacenter
    logger.debug('Gathering all Clusters from the vCenter Datacenter %s' % vc_dc.name)
    content = vc.content
    obj_view = content.viewManager.CreateContainerView(vc_dc, [vim.ClusterComputeResource], True)
    vc_cl_list = obj_view.view
    obj_view.Destroy()

    # Getting clusters in current Nuage Datacenter
    logger.debug('Gathering all Clusters from the Nuage Datacenter %s' % vc_dc.name)
    nc_cl_list = active_nc_dc.vcenter_clusters.get()

    for vc_cl in vc_cl_list:
        if all_clusters or vc_cl.name in clusters:
            logger.debug('vCenter Cluster %s is in list that has to be present in the Nuage vCenter Deployment Tool, checking if it already exists.' % vc_cl.name)
            handle_vdt_cluster(logger=logger, nc=nc, vc=vc, vc_dc=vc_dc, vc_cl=vc_cl, nuage_dc=active_nc_dc, nc_cl_list=nc_cl_list, all_hosts=all_hosts, hosts=hosts, hosts_list=hosts_list, hv_username=hv_username, hv_password=hv_password, hv_management_network=hv_management_network, hv_data_network=hv_data_network, hv_vm_network=hv_vm_network, hv_mc_network=hv_mc_network, host_configure_agent=host_configure_agent, allow_fqdn=allow_fqdn)


def handle_vdt_cluster(logger, nc, vc, vc_dc, vc_cl, nuage_dc, nc_cl_list, all_hosts, hosts, hosts_list, hv_username, hv_password, hv_management_network, hv_data_network, hv_vm_network, hv_mc_network, host_configure_agent, allow_fqdn):
    # Checking if the Cluster exists in the Nuage vCenter Deployment Tool
    logger.debug('Checking vCenter Cluster %s in Nuage vCenter Deployment Tool' % vc_cl.name)
    active_nc_cl = None
    for nc_cl in nc_cl_list:
        if vc_cl.name == nc_cl.name:
            active_nc_cl = nc_cl
            logger.debug('Found Cluster %s in Nuage vCenter Deployment Tool' % vc_cl.name)
            break

    if not active_nc_cl:
        logger.debug('Cluster %s not found in the vCenter Datacenter %s in the Nuage vCenter Deployment Tool, creating' % (vc_cl.name, vc_dc.name))
        active_nc_cl = vsdk.NUVCenterCluster(name=vc_cl.name)
        nuage_dc.create_child(active_nc_cl)
        logger.info('Created Cluster %s from the vCenter Datacenter %s in the Nuage vCenter Deployment Tool' % (vc_cl.name, vc_dc.name))

    # Getting hosts in the current vCenter Cluster
    logger.debug('Gathering all Hosts from the vCenter Cluster %s' % vc_cl.name)
    content = vc.content
    obj_view = content.viewManager.CreateContainerView(vc_cl, [vim.HostSystem], True)
    vc_host_list = obj_view.view
    obj_view.Destroy()

    # Getting hosts in current Nuage Cluster
    logger.debug('Gathering all Hosts from the Nuage Cluster %s' % vc_cl.name)
    nc_host_list = active_nc_cl.vcenter_hypervisors.get()

    for vc_host in vc_host_list:
        if all_hosts:
            # Determining Host management IP
            vc_host_ip = None

            if allow_fqdn:
                vc_host_ip = vc_host.name
            else:
                # Determine management IP based on 'management' property
                vnic_mgmtIP_list = []
                for vc_host_NicManager in vc_host.config.virtualNicManagerInfo.netConfig:
                    if vc_host_NicManager.nicType == 'management':
                        if(len(vc_host_NicManager.selectedVnic) > 0):
                            for vnic in vc_host_NicManager.candidateVnic:
                                if vnic.key in vc_host_NicManager.selectedVnic:
                                    if ip_address_is_valid(vnic.spec.ip.ipAddress):
                                        vnic_mgmtIP_list.append(vnic.spec.ip.ipAddress)
                        break

                if len(vnic_mgmtIP_list) > 0:
                    for vnic_ip in vnic_mgmtIP_list:
                        if ip_address_is_valid(vnic_ip):
                            logger.debug('Found managenent IP %s for vCenter Host %s' % (vnic_ip, vc_host.name))
                            vc_host_ip = vnic_ip
                            break
                else:
                    # Did not find any Management IP, use first IP
                    for vnic in vc_host.config.network.vnic:
                        logger.debug('Checking vnic for Host %s in vCenter Cluster %s' % (vc_host.name, vc_cl.name))
                        if ip_address_is_valid(vnic.spec.ip.ipAddress):
                            logger.debug('Found management IP %s for vCenter Host %s' % (vnic.spec.ip.ipAddress, vc_host.name))
                            vc_host_ip = vnic.spec.ip.ipAddress
                            break

            handle_vdt_host(logger=logger, nc=nc, vc=vc, vc_cl=vc_cl, vc_host=vc_host, vc_host_ip=vc_host_ip, nuage_cl=active_nc_cl, nc_host_list=nc_host_list, hosts_list=hosts_list, hv_username=hv_username, hv_password=hv_password, hv_management_network=hv_management_network, hv_data_network=hv_data_network, hv_vm_network=hv_vm_network, hv_mc_network=hv_mc_network, host_configure_agent=host_configure_agent, allow_fqdn=allow_fqdn)
        elif allow_fqdn and vc_host.name in hosts:
            logger.debug('vCenter Host %s is in list that has to be present in the Nuage vCenter Deployment Tool, checking if it already exists.' % vc_host.name)
            handle_vdt_host(logger=logger, nc=nc, vc=vc, vc_cl=vc_cl, vc_host=vc_host, vc_host_ip=vc_host.name, nuage_cl=active_nc_cl, nc_host_list=nc_host_list, hosts_list=hosts_list, hv_username=hv_username, hv_password=hv_password, hv_management_network=hv_management_network, hv_data_network=hv_data_network, hv_vm_network=hv_vm_network, hv_mc_network=hv_mc_network, host_configure_agent=host_configure_agent, allow_fqdn=allow_fqdn)
        else:
            # Get all IPs in a list for this host to check if the IP is present in the hosts to add
            for vnic in vc_host.config.network.vnic:
                logger.debug('Found IP %s for vCenter Host %s' % (vnic.spec.ip.ipAddress, vc_host.name))
                if vnic.spec.ip.ipAddress in hosts:
                    logger.debug('vCenter Host %s with IP %s is in list that has to be present in the Nuage vCenter Deployment Tool, checking if it already exists.' % (vc_host.name, vnic.spec.ip.ipAddress))
                    handle_vdt_host(logger=logger, nc=nc, vc=vc, vc_cl=vc_cl, vc_host=vc_host, vc_host_ip=vnic.spec.ip.ipAddress, nuage_cl=active_nc_cl, nc_host_list=nc_host_list, hosts_list=hosts_list, hv_username=hv_username, hv_password=hv_password, hv_management_network=hv_management_network, hv_data_network=hv_data_network, hv_vm_network=hv_vm_network, hv_mc_network=hv_mc_network, host_configure_agent=host_configure_agent, allow_fqdn=allow_fqdn)
                    break


def handle_vdt_host(logger, nc, vc, vc_cl, vc_host, vc_host_ip, nuage_cl, nc_host_list, hosts_list, hv_username, hv_password, hv_management_network, hv_data_network, hv_vm_network, hv_mc_network, host_configure_agent, allow_fqdn):
    logger.debug('Checking vCenter Host %s in the Nuage vCenter Deployment Tool' % vc_host.name)
    active_nc_host = None
    for nc_host in nc_host_list:
        if vc_host_ip == nc_host.hypervisor_ip:
            logger.debug('Found Host with IP %s in the Nuage vCenter Deployment Tool' % vc_host_ip)
            active_nc_host = nc_host
            break

    if not active_nc_host:
        logger.debug('Host %s with IP %s not found in the vCenter Cluster %s in the Nuage vCenter Deployment Tool, creating' % (vc_host.name, vc_host_ip, vc_cl.name))
        active_nc_host = vsdk.NUVCenterHypervisor(name=vc_host.name, hypervisor_ip=vc_host_ip, hypervisor_user=hv_username, hypervisor_password=hv_password, mgmt_network_portgroup=hv_management_network, data_network_portgroup=hv_data_network, vm_network_portgroup=hv_vm_network, multicast_source_portgroup=hv_mc_network)
        nuage_cl.create_child(active_nc_host)
        logger.info('Created Host %s with IP %s from the vCenter Cluster %s in the Nuage vCenter Deployment Tool' % (vc_host.name, vc_host_ip, vc_cl.name))

    # Once we come here, we can update the host (circumventing a known issue with the creation of a host not setting its networks)
    active_nc_host.mgmt_network_portgroup = hv_management_network
    active_nc_host.data_network_portgroup = hv_data_network
    active_nc_host.vm_network_portgroup = hv_vm_network
    active_nc_host.multicast_source_portgroup = hv_mc_network

    # Setting base values for vCenter Host VM Agent configuration in case they are needed
    agent_portgroup_name = hv_management_network
    agent_datastore_name = None

    # if hosts_list is not empty, use those values if they are set, if it is, use the general ones
    if hosts_list:
        if vc_host_ip in hosts_list:
            logger.debug('Host %s with IP %s from the vCenter Cluster %s found in the hosts file. Updating its information from the file' % (vc_host.name, vc_host_ip, vc_cl.name))
            row = hosts_list[vc_host_ip]
            # 0 - "<IP>" - hypervisor_ip
            # 1 - "[name]" - name
            if row[1]:
                active_nc_host.name = row[1]
            # 2 - "[hypervisor user]" - hypervisor_user
            if row[2]:
                active_nc_host.hypervisor_user = row[2]
            # 3 - "[hypervisor password]" - hypervisor_password
            if row[3]:
                active_nc_host.hypervisor_password = row[3]
            # 4 - "[management network portgroup]" - mgmt_network_portgroup
            if row[4]:
                active_nc_host.mgmt_network_portgroup = row[4]
            # 5 - "[data network portgroup]" - data_network_portgroup
            if row[5]:
                active_nc_host.data_network_portgroup = row[5]
            # 6 - "[vm network portgroup]" - vm_network_portgroup
            if row[6]:
                active_nc_host.vm_network_portgroup = row[6]
            # 7 - "[multicast sourece portgroup]" - multicast_source_portgroup
            if row[7]:
                active_nc_host.multicast_source_portgroup = row[7]
            # 8 - "[use management DHCP (True|False)]" - allow_mgmt_dhcp
            if row[8].lower() == 'true':
                active_nc_host.allow_mgmt_dhcp = True
            else:
                active_nc_host.allow_mgmt_dhcp = False
            # 9 - "[management IP]" - mgmt_ip_address
            if row[9] and ip_address_is_valid(row[9]):
                active_nc_host.mgmt_ip_address = row[9]
            # 10 - "[management netmask (octet structure)]" - mgmt_netmask
            if row[10]:
                active_nc_host.mgmt_netmask = row[10]
            # 11 - "[management gateway]" - mgmt_gateway
            if row[11] and ip_address_is_valid(row[11]):
                active_nc_host.mgmt_gateway = row[11]
            # 12 - "[management DNS 1]" - mgmt_dns1
            if row[12] and ip_address_is_valid(row[12]):
                active_nc_host.mgmt_dns1 = row[12]
            # 13 - "[management DNS 2]" - mgmt_dns2
            if row[13] and ip_address_is_valid(row[13]):
                active_nc_host.mgmt_dns2 = row[13]
            # 14 - "[separate data network (True|False)]" - separate_data_network
            if row[14].lower() == 'true':
                active_nc_host.separate_data_network = True
            else:
                active_nc_host.separate_data_network = False
            # 15 - "[use data DHCP (True|False)]" - allow_data_dhcp
            if row[15].lower() == 'true':
                active_nc_host.allow_data_dhcp = True
            else:
                active_nc_host.allow_data_dhcp = False
            # 16 - "[data IP]" - data_ip_address
            if row[16] and ip_address_is_valid(row[16]):
                active_nc_host.data_ip_address = row[16]
            # 17 - "[data netmask (octet structure)]" - data_netmask
            if row[17]:
                active_nc_host.data_netmask = row[17]
            # 18 - "[data gateway]" - data_gateway
            if row[18] and ip_address_is_valid(row[18]):
                active_nc_host.data_gateway = row[18]
            # 19 - "[data DNS 1]" - data_dns1
            if row[19] and ip_address_is_valid(row[19]):
                active_nc_host.data_dns1 = row[19]
            # 20 - "[data DNS 2]" - data_dns2
            if row[20] and ip_address_is_valid(row[20]):
                active_nc_host.data_dns2 = row[20]
            # 21 - "[MTU]" - mtu
            if row[21]:
                active_nc_host.mtu = row[21]
            # 22 - "[require metadata (True|False)]" - v_require_nuage_metadata
            if row[22].lower() == 'true':
                active_nc_host.v_require_nuage_metadata = True
            else:
                active_nc_host.v_require_nuage_metadata = False
            # 23 - "[generic split activation (True|False)]" - generic_split_activation
            if row[23].lower() == 'true':
                active_nc_host.generic_split_activation = True
            else:
                active_nc_host.generic_split_activation = False
            # 24 - "[multi VM support (True|False)]" - multi_vmssupport
            if row[24].lower() == 'true':
                active_nc_host.multi_vmssupport = True
            else:
                active_nc_host.multi_vmssupport = False
            # 25 - "[DHCP relay server (IP)]" - dhcp_relay_server
            if row[25] and ip_address_is_valid(row[25]):
                active_nc_host.dhcp_relay_server = row[25]
            # 26 - "[flow eviction threshold]" - flow_eviction_threshold
            if row[26]:
                active_nc_host.flow_eviction_threshold = row[26]
            # 27 - "[datapath sync timeout]" - datapath_sync_timeout
            if row[27]:
                active_nc_host.datapath_sync_timeout = row[27]
            # 28 - "[network uplink interface]" - network_uplink_interface
            if row[28]:
                active_nc_host.network_uplink_interface = row[28]
            # 29 - "[network uplink IP]" - network_uplink_interface_ip
            if row[29] and ip_address_is_valid(row[29]):
                active_nc_host.network_uplink_interface_ip = row[29]
            # 30 - "[network uplink netmask (octet structure)]" - network_uplink_interface_netmask
            if row[30]:
                active_nc_host.network_uplink_interface_netmask = row[30]
            # 31 - "[network uplink gateway]" - network_uplink_interface_gateway
            if row[31] and ip_address_is_valid(row[31]):
                active_nc_host.network_uplink_interface_gateway = row[31]
            # 32 - "[script URL]" - customized_script_url
            if row[32]:
                active_nc_host.customized_script_url = row[32]
            # 33 - "[personality]" - personality
            if row[33].lower() == 'vrs' or row[33].lower() == 'vrs-g':
                active_nc_host.personality = row[33]
            # 34 - "[site ID]" - site_id
            if row[34]:
                active_nc_host.site_id = row[34]
            # 35 - "[NFS server address (IP)]" - nfs_log_server
            if row[35] and ip_address_is_valid(row[35]):
                active_nc_host.nfs_log_server = row[35]
            # 36 - "[NFS mount path]" - nfs_mount_path
            if row[36]:
                active_nc_host.nfs_mount_path = row[36]
            # 37 - "[primary Nuage controller (IP)]" - primary_nuage_controller
            if row[37] and ip_address_is_valid(row[37]):
                active_nc_host.primary_nuage_controller = row[37]
            # 38 - "[secondary Nuage controller (IP)]" - secondary_nuage_controller
            if row[38] and ip_address_is_valid(row[38]):
                active_nc_host.secondary_nuage_controller = row[38]
            # 39 - "[primary NTP server (IP)]" - ntp_server1
            if row[39] and ip_address_is_valid(row[39]):
                active_nc_host.ntp_server1 = row[39]
            # 40 - "[secondary NTP server (IP)]" - ntp_server2
            if row[40] and ip_address_is_valid(row[40]):
                active_nc_host.ntp_server2 = row[40]
            # 41 - "[static route target IP]" - static_route
            if row[41] and ip_address_is_valid(row[41]):
                active_nc_host.static_route = row[41]
            # 42 - "[static route target IP]" - static_route_netmask
            if row[42]:
                active_nc_host.static_route_netmask = row[42]
            # 43 - "[static route next-hop gateway]" - static_route_gateway
            if row[43] and ip_address_is_valid(row[43]):
                active_nc_host.static_route_gateway = row[43]
            # 44 - "[multicast send interface]" - multicast_send_interface
            if row[44]:
                active_nc_host.multicast_send_interface = row[44]
            # 45 - "[multicast send IP]" - multicast_send_interface_ip
            if row[45] and ip_address_is_valid(row[45]):
                active_nc_host.multicast_send_interface_ip = row[45]
            # 46 - "[multicast send netmask (octet structure)]" - multicast_send_interface_netmask
            if row[46]:
                active_nc_host.multicast_send_interface_netmask = row[46]
            # 47 - "[multicast receive IP]" - multicast_receive_interface_ip
            if row[47] and ip_address_is_valid(row[47]):
                active_nc_host.multicast_receive_interface_ip = row[47]
            # 48 - "[multicast receive netmask (octet structure)]" - multicast_receive_interface_netmask
            if row[48]:
                active_nc_host.multicast_receive_interface_netmask = row[48]
            # 49 - "[Host Agent VM Port Group]"
            if row[49]:
                agent_portgroup_name = row[49]
            # 50 - "[Host Agent VM Datastore]"
            if row[50]:
                agent_datastore_name = row[50]
        else:
            logger.warning('Host %s with IP %s from the vCenter Cluster %s is not in the hosts file, it will not be updated.' % (vc_host.name, vc_host_ip, vc_cl.name))
    else:
        logger.debug('No hosts file specified, only updating host %s with IP %s from the vCenter Cluster %s with the latest network information.' % (vc_host.name, vc_host_ip, vc_cl.name))

    # Saving active host
    active_nc_host.save()
    logger.info('Updated Host %s with IP %s from the vCenter Cluster %s in the Nuage vCenter Deployment Tool' % (vc_host.name, vc_host_ip, vc_cl.name))

    # Updating the vCenter host if the flag is set.
    if host_configure_agent:
        update_host_vm_agent_configuration(logger=logger, vc_cl=vc_cl, vc_host=vc_host, vc_host_ip=vc_host_ip, agent_portgroup_name=agent_portgroup_name, agent_datastore_name=agent_datastore_name)


def update_host_vm_agent_configuration(logger, vc_cl, vc_host, vc_host_ip, agent_portgroup_name, agent_datastore_name):
    logger.debug('Configuring the Agent VM settings for Host %s with IP %s from the vCenter Cluster %s' % (vc_host.name, vc_host_ip, vc_cl.name))
    # Setting base variables
    agent_portgroup = None
    agent_datastore = None

    # Find the correct Port group
    logger.debug('Searching fo Port group %s for Host %s with IP %s from the vCenter Cluster %s' % (agent_portgroup_name, vc_host.name, vc_host_ip, vc_cl.name))
    for network in vc_host.network:
        logger.debug('Checking Port group %s on Host %s with IP %s from the vCenter Cluster %s' % (network.name, vc_host.name, vc_host_ip, vc_cl.name))
        if network.name == agent_portgroup_name:
            logger.debug('Found Port group %s for Host %s with IP %s from the vCenter Cluster %s' % (network.name, vc_host.name, vc_host_ip, vc_cl.name))
            agent_portgroup = network
            break

    # If no port group found, stop and do not configure the Agent VM settings of the host
    if not agent_portgroup:
        logger.error('No Port group named %s found for Host %s with IP %s from the vCenter Cluster %s. Skipping Host Agent VM Settings configuration' % (agent_portgroup_name, vc_host.name, vc_host_ip, vc_cl.name))
        return -1

    # Finding the first local datastore name if there hasn't been one specified
    if not agent_datastore_name:
        logger.debug('Searching for first local VMFS datastore on Host %s with IP %s from the vCenter Cluster %s' % (vc_host.name, vc_host_ip, vc_cl.name))
        for fs in vc_host.configManager.storageSystem.fileSystemVolumeInfo.mountInfo:
            logger.debug('Checking Datastore %s for Host %s with IP %s from the vCenter Cluster %s' % (fs.volume.name, vc_host.name, vc_host_ip, vc_cl.name))
            if fs.volume.type == "VMFS" and fs.volume.local:
                logger.debug('Found local Datastore %s for Host %s with IP %s from the vCenter Cluster %s' % (fs.volume.name, vc_host.name, vc_host_ip, vc_cl.name))
                agent_datastore_name = fs.volume.name
                break

    # Find the correct Datastore
    logger.debug('Searching for Datastore %s for Host %s with IP %s from the vCenter Cluster %s' % (agent_datastore_name, vc_host.name, vc_host_ip, vc_cl.name))
    for datastore in vc_host.datastore:
        logger.debug('Checking Datastore %s on Host %s with IP %s from the vCenter Cluster %s' % (datastore.name, vc_host.name, vc_host_ip, vc_cl.name))
        if datastore.name == agent_datastore_name:
            logger.debug('Found Datastore %s for Host %s with IP %s from the vCenter Cluster %s' % (datastore.name, vc_host.name, vc_host_ip, vc_cl.name))
            agent_datastore = datastore
            break

    # If no datastore found, stop and do not configure the Agent VM settings of the host
    if not agent_datastore:
        logger.error('No datastore named %s found for Host %s with IP %s from the vCenter Cluster %s. Skipping Host Agent VM Settings configuration' % (agent_datastore_name, vc_host.name, vc_host_ip, vc_cl.name))
        return -1

    # Setting actual Agent VM settings
    logger.debug('Setting the Agent VM settings for Host %s with IP %s from the vCenter Cluster %s to: datastore %s and port group %s' % (vc_host.name, vc_host_ip, vc_cl.name, agent_datastore.name, agent_portgroup.name))
    try:
        agent_config = vim.host.EsxAgentHostManager.ConfigInfo(agentVmDatastore=agent_datastore, agentVmNetwork=agent_portgroup)
        vc_host.configManager.esxAgentHostManager.EsxAgentHostManagerUpdateConfig(configInfo=agent_config)
    except vim.fault.HostConfigFault, e:
        logger.error('FAILED to configure the Agent VM settings for Host %s with IP %s from the vCenter Cluster %s to: datastore %s and port group %s. Exception: %s' % (vc_host.name, vc_host_ip, vc_cl.name, agent_datastore.name, agent_portgroup.name, e.msg))
        return -1

    logger.debug('Successful configured the Agent VM settings for Host %s with IP %s from the vCenter Cluster %s to: datastore %s and port group %s' % (vc_host.name, vc_host_ip, vc_cl.name, agent_datastore.name, agent_portgroup.name))
    return 0


def ip_address_is_valid(address):
    try:
        socket.inet_aton(address)
    except socket.error:
        return False
    else:
        return True


def main():
    """
    Manage the vCenter Integration Node configuration
    """

    # Handling arguments
    args = get_args()
    all_clusters = args.all_clusters
    all_datacenters = args.all_datacenters
    all_hosts = args.all_hosts
    clusters = []
    if args.clusters:
        clusters = args.clusters
    debug = args.debug
    allow_fqdn = args.allow_fqdn
    datacenters = []
    if args.datacenters:
        datacenters = args.datacenters
    hosts = []
    if args.hosts:
        hosts = args.hosts
    host_configure_agent = args.host_configure_agent
    hosts_file = None
    if args.hosts_file:
        hosts_file = args.hosts_file
    hv_username = None
    if args.hv_username:
        hv_username = args.hv_username
    hv_password = None
    if args.hv_password:
        hv_password = args.hv_password
    hv_management_network = None
    if args.hv_management_network:
        hv_management_network = args.hv_management_network
    hv_data_network = None
    if args.hv_data_network:
        hv_data_network = args.hv_data_network
    hv_vm_network = None
    if args.hv_vm_network:
        hv_vm_network = args.hv_vm_network
    hv_mc_network = None
    if args.hv_mc_network:
        hv_mc_network = args.hv_mc_network
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
    nuage_vrs_ovf = None
    if args.nuage_vrs_ovf:
        nuage_vrs_ovf = args.nuage_vrs_ovf
    nosslcheck = args.nosslcheck
    verbose = args.verbose
    vcenter_host = args.vcenter_host
    vcenter_name = vcenter_host
    if args.vcenter_name:
        vcenter_name = args.vcenter_name
    vcenter_https_port = args.vcenter_https_port
    vcenter_http_port = args.vcenter_http_port
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

    # Input checking
    if not all_datacenters and len(datacenters) < 1:
        logger.critical('Not all datacenters have to be present in the Nuage Deployment tool (--all-datacenters option NOT enabled), but also no datacenters specified (at least one --datacenter)')
        return 1
    if not all_clusters and len(clusters) < 1:
        logger.critical('Not all clusters have to be present in the Nuage Deployment tool (--all-clusters option NOT enabled), but also no clusters specified (at least one --cluster)')
        return 1
    if not all_hosts and len(hosts) < 1 and not hosts_file:
        logger.critical('Not all hosts have to be present in the Nuage Deployment tool (--all-hosts option NOT enabled), but also no hosts specified (at least one --host or specify a file with the host information via --hosts-file)')
        return 1
    if all_datacenters and len(datacenters) > 0:
        logger.warning('You enabled all datacenters and added individual datacenter options, --all-datacenters takes precendence and overwrites the specified datacenters.')
        datacenters = []
    if all_clusters and len(clusters) > 0:
        logger.warning('You enabled all clusters and added individual cluster options, --all-clusters takes precendence and overwrites the specified clusters.')
        clusters = []
    if all_hosts and len(hosts) > 0 and not hosts_file:
        logger.warning('You enabled all hosts and added individual hosts options, --all-hosts takes precendence and overwrites the specified hosts.')
        hosts = []
    elif all_hosts and len(hosts) < 1 and hosts_file:
        logger.warning('You enabled all hosts and provided a hosts file, the hosts file takes precendence over the --all-hosts flag and this flag will be ignored.')
        all_hosts = False
    elif not all_hosts and len(hosts) > 0 and hosts_file:
        logger.warning('You specified host with the --host argument and provided a hosts file, the hosts file takes precendence over the --host paramerters and these will be ignored.')
        hosts = []

    # CSV Handling
    hosts_list = None
    if hosts_file:
        hosts_list = {}
        # CSV fields:
        # VM Name, Resource Pool, Folder, MAC Address, Post Script
        logger.debug('Parsing csv %s' % hosts_file)

        if not os.path.isfile(hosts_file):
            logger.critical('CSV file %s does not exist, exiting' % hosts_file)
            return 1

        with open(hosts_file, 'rb') as hostlist:
            hosts_list_raw = csv.reader(hostlist, delimiter=',', quotechar='"')
            for row in hosts_list_raw:
                logger.debug('Found CSV row: %s' % ','.join(row))
                # Adding IP to the hosts variable so it can also be used in further handling if it's a valid IP
                if allow_fqdn or ip_address_is_valid(row[0]):
                    hosts_list[row[0]] = row
                    hosts.append(row[0])
                else:
                    logger.warning('Found an invalid IP %s in the hosts file and FQDNs are not allowed, skipping line' % row[0])

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
        nuage_password = getpass.getpass(prompt='Enter password for Nuage host %s for user %s: ' % (nuage_host, nuage_username))

    # Getting user password for vCenter connection
    if vcenter_password is None:
        logger.debug('No command line vCenter password received, requesting vCenter password from user')
        vcenter_password = getpass.getpass(prompt='Enter password for vCenter host %s for user %s: ' % (vcenter_host, vcenter_username))

    # Getting user password for hosts
    if hv_password is None:
        logger.debug('No command line Host password received, requesting Host password from user')
        hv_password = getpass.getpass(prompt='Enter password for the hosts inside vCenter %s for user %s: ' % (vcenter_host, hv_username))

    try:
        vc = None
        nc = None

        # Connecting to Nuage
        try:
            logger.info('Connecting to Nuage server %s:%s with username %s' % (nuage_host, nuage_port, nuage_username))
            nc = vsdk.NUVSDSession(username=nuage_username, password=nuage_password, enterprise=nuage_enterprise, api_url="https://%s:%s" % (nuage_host, nuage_port))
            nc.start()
        except IOError, e:
            pass

        if not nc or not nc.is_current_session():
            logger.error('Could not connect to Nuage host %s with user %s and specified password' % (nuage_host, nuage_username))
            return 1

        # Connecting to vCenter
        try:
            logger.info('Connecting to vCenter server %s:%s with username %s' % (vcenter_host, vcenter_https_port, vcenter_username))
            if ssl_context:
                vc = SmartConnect(host=vcenter_host, user=vcenter_username, pwd=vcenter_password, port=int(vcenter_https_port), sslContext=ssl_context)
            else:
                vc = SmartConnect(host=vcenter_host, user=vcenter_username, pwd=vcenter_password, port=int(vcenter_https_port))

        except IOError, e:
            pass

        if not vc:
            logger.error('Could not connect to vCenter host %s with user %s and specified password' % (vcenter_host, vcenter_username))
            return 1

        logger.debug('Registering vCenter disconnect at exit')
        atexit.register(Disconnect, vc)

        logger.info('Connected to both Nuage & vCenter servers')

        # Check if the vCenter exists in Nuage vCenter Deployment Tool
        nuage_vcenter = None
        logger.debug('Checking if vCenter %s is already present in Nuage vCenter Deployment Tool' % vcenter_name)
        for nvc in nc.user.vcenters.get():
            if nvc.ip_address == vcenter_host:
                logger.debug('Found vCenter %s, not recreating' % vcenter_name)
                nuage_vcenter = nvc
                break

        # If th vCenter does not exist in Nuage vCenter Deployment Tool, create it
        if not nuage_vcenter:
            logger.debug('vCenter %s with IP %s not found in the Nuage vCenter Deployment Tool, creating' % (vcenter_name, vcenter_host))
            nuage_vcenter = vsdk.NUVCenter(name=vcenter_name, ip_address=vcenter_host, user_name=vcenter_username, password=vcenter_password, http_port=vcenter_http_port, https_port=vcenter_https_port, ovf_url=nuage_vrs_ovf)
            nc.user.create_child(nuage_vcenter)
            logger.info('Created vCenter %s in the Nuage vCenter Deployment Tool' % vcenter_name)

        # Datacenter Handling
        # Gathering all Datacenters inside the vCenter
        logger.debug('Gathering all Datacenters from vCenter')
        content = vc.content
        obj_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datacenter], True)
        vc_dc_list = obj_view.view
        obj_view.Destroy()

        # Gathering all Datacenters inside the Nuage vCenter
        logger.debug('Gathering all Datacenter from the Nuage vCenter entry')
        nc_dc_list = nuage_vcenter.vcenter_data_centers.get()

        # Parsing all datacenters
        for vc_dc in vc_dc_list:
            if all_datacenters or vc_dc.name in datacenters:
                logger.debug('vCenter Datacenter %s is in list that has to be present in the Nuage vCenter Deployment Tool, checking if it already exists.' % vc_dc.name)
                handle_vdt_datacenter(logger=logger, nc=nc, vc=vc, nuage_vcenter=nuage_vcenter, vc_dc=vc_dc, nc_dc_list=nc_dc_list, vcenter_name=vcenter_name, all_clusters=all_clusters, all_hosts=all_hosts, clusters=clusters, hosts=hosts, hosts_list=hosts_list, hv_username=hv_username, hv_password=hv_password, hv_management_network=hv_management_network, hv_data_network=hv_data_network, hv_vm_network=hv_vm_network, hv_mc_network=hv_mc_network, host_configure_agent=host_configure_agent, allow_fqdn=allow_fqdn)

        logger.info('Completed all tasks.')
        return 0

    except vmodl.MethodFault, e:
        logger.critical('Caught vmodl fault: %s' % e.msg)
        return 1
    except Exception, e:
        logger.critical('Caught exception: %s' % str(e))
        return 1

# Start program
if __name__ == "__main__":
    main()
