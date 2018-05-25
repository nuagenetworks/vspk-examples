# -*- coding: utf-8 -*-
"""
migrate_vmware_vm_to_nuage.py migrate a VMware VM, with VMware tools or open-vm-tools, to a Nuage VSP environment.

In default mode it will gather the VMs IP and check if it is part of the specified subnet. If it is, it will populate the VM with the correct metadata and reconnect the interface to the OVS-PG.

In split activation mode, it will gather the MAC, UUID and IP from the VM and create a vPort and VM before reconnecting the nic to the OVS-PG.

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

--- Version history ---
2016-03-20 - 1.0
2018-05-14 - 1.1 - Added support for flushing the NIC connection so the OS reinitiates its network stack (useful for clearing arp tables)

--- Usage ---
run 'python migrate_vmware_vm_to_nuage.py -h' for an overview

--- Best practice ---
For L3 domain make sure to specify the full stack of information (enterprise, domain, zone, subnet)

--- Documentation ---
http://github.com/nuagenetworks/vspk-examples/blob/master/docs/migrate_vmware_vm_to_nuage.md

--- Examples ---
---- Migrate VM to layer 3 subnet in Nuage with metadata ----
python migrate_vmware_vm_to_nuage.py --nuage-enterprise csp --nuage-host 10.189.2.254 --nuage-user csproot --nuage-vm-user hradmin --nuage-vm-enterprise HR --nuage-vm-domain HR-Main-Domain --nuage-vm-zone Front --nuage-vm-subnet Web-Net --vcenter-host vc01.hr.company.tld --vcenter-user administrator@vsphere.local --vcenter-port-group Nuage-VM-PG1 --vcenter-vm LEGACY-VM -S -m metadata

---- Migrate VM to layer 3 subnet in Nuage with split-activation ----
python migrate_vmware_vm_to_nuage.py --nuage-enterprise csp --nuage-host 10.189.2.254 --nuage-user csproot --nuage-vm-user hradmin --nuage-vm-enterprise Finance --nuage-vm-domain Finance-Main-Domain --nuage-vm-zone Front --nuage-vm-subnet Web-Net --vcenter-host vc01.fi.company.tld --vcenter-user administrator@vsphere.local --vcenter-port-group Nuage-VM-PG1 --vcenter-vm LEGACY-VM -S -m split-activation

---- Migrate VM to layer 2 subnet in Nuage with metadata ----
python migrate_vmware_vm_to_nuage.py --nuage-enterprise csp --nuage-host 10.189.2.254 --nuage-user csproot --nuage-vm-user hradmin --nuage-vm-enterprise HR --nuage-vm-subnet L2-Domain --vcenter-host vc01.hr.company.tld --vcenter-user administrator@vsphere.local --vcenter-port-group Nuage-VM-PG1 --vcenter-vm LEGACY-VM -S -m metadata

---- Migrate VM to layer 2 subnet in Nuage with split-activation ----
python migrate_vmware_vm_to_nuage.py --nuage-enterprise csp --nuage-host 10.189.2.254 --nuage-user csproot --nuage-vm-user hradmin --nuage-vm-enterprise Finance --nuage-vm-subnet L2-Domain --vcenter-host vc01.fi.company.tld --vcenter-user administrator@vsphere.local --vcenter-port-group Nuage-VM-PG1 --vcenter-vm LEGACY-VM -S -m split-activation
"""
import argparse
import atexit
import getpass
import ipaddress
import logging
import re
from time import sleep
import requests
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
from vspk import v5_0 as vsdk


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="Tool to migrate a VMware VM, with VMware tools or open-vm-tools, to a Nuage VSP environment. In default mode it will gather the VMs IP and check if it is part of the specified subnet. If it is, it will populate the VM with the correct metadata and reconnect the interface to the OVS-PG. In split activation mode, it will gather the MAC, UUID and IP from the VM and create a vPort and VM before reconnecting the nic to the OVS-PG.")
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-f', '--flush', required=False, help='Flush the VM nic connection, this disconnects the VM interface and reconnects it.', dest='flush', action='store_true')
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-m', '--mode', required=False, help='Select between metadata and split-activation', dest='mode', type=str, choices=['metadata', 'split-activation'], default='medatada')
    parser.add_argument('--nuage-enterprise', required=True, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('--nuage-user', required=True, help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('--nuage-vm-enterprise', required=True, help='The Nuage enterprise to which the VM should be connected', dest='nuage_vm_enterprise', type=str)
    parser.add_argument('--nuage-vm-domain', required=False, help='The Nuage domain to which the VM should be connected', dest='nuage_vm_domain', type=str)
    parser.add_argument('--nuage-vm-zone', required=False, help='The Nuage zone to which the VM should be connected', dest='nuage_vm_zone', type=str)
    parser.add_argument('--nuage-vm-subnet', required=True, help='The Nuage subnet to which the VM should be connected', dest='nuage_vm_subnet', type=str)
    parser.add_argument('--nuage-vm-user', required=True, help='The Nuage User owning the VM', dest='nuage_vm_user', type=str)
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect', dest='nosslcheck', action='store_true')
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', action='store_true')
    parser.add_argument('--vcenter-host', required=True, help='The vCenter or ESXi host to connect to', dest='vcenter_host', type=str)
    parser.add_argument('--vcenter-port', required=False, help='vCenter Server port to connect to (default = 443)', dest='vcenter_port', type=int, default=443)
    parser.add_argument('--vcenter-password', required=False, help='The password with which to connect to the vCenter host. If not specified, the user is prompted at runtime for a password', dest='vcenter_password', type=str)
    parser.add_argument('--vcenter-user', required=True, help='The username with which to connect to the vCenter host', dest='vcenter_username', type=str)
    parser.add_argument('--vcenter-port-group', required=True, help='The name of the distributed Portgroup to which the interface needs to be attached.', dest='vcenter_portgroup', type=str)
    parser.add_argument('--vcenter-vm', required=True, help='The name of the VM to migrate', dest='vcenter_vm', type=str)
    args = parser.parse_args()
    return args


def get_vcenter_object(logger, vc, vimtype, name):
    """
    Get the vsphere object associated with a given text name
    """
    content = vc.RetrieveContent()
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for view in container.view:
        logger.debug('Checking object: %s' % view.name)
        if view.name == name:
            logger.debug('Found object: %s' % view.name)
            obj = view
            break
    return obj


def get_nuage_object(logger, parent, nuagetype, search_query, single_entity=False):
    """
    Get a Nuage opbject matching a search query
    """
    logger.debug('Finding Nuage entities for object matching search query "%s"' % search_query)
    if single_entity:
        entities = parent.fetcher_for_rest_name(nuagetype.lower()).get_first(filter=search_query)
    else:
        entities = parent.fetcher_for_rest_name(nuagetype.lower()).get(filter=search_query)
    return entities


def main():
    """
    Main function to handle statistics
    """

    # Handling arguments
    args = get_args()
    debug = args.debug
    flush = args.flush
    log_file = None
    if args.logfile:
        log_file = args.logfile
    mode = args.mode
    nuage_enterprise = args.nuage_enterprise
    nuage_host = args.nuage_host
    nuage_port = args.nuage_port
    nuage_password = None
    if args.nuage_password:
        nuage_password = args.nuage_password
    nuage_username = args.nuage_username
    nosslcheck = args.nosslcheck
    verbose = args.verbose
    nuage_vm_enterprise = args.nuage_vm_enterprise
    nuage_vm_domain = None
    if args.nuage_vm_domain:
        nuage_vm_domain = args.nuage_vm_domain
    nuage_vm_zone = None
    if args.nuage_vm_zone:
        nuage_vm_zone = args.nuage_vm_zone
    nuage_vm_subnet = args.nuage_vm_subnet
    nuage_vm_user = None
    if args.nuage_vm_user:
        nuage_vm_user = args.nuage_vm_user
    vcenter_host = args.vcenter_host
    vcenter_port = args.vcenter_port
    vcenter_password = None
    if args.vcenter_password:
        vcenter_password = args.vcenter_password
    vcenter_username = args.vcenter_username
    vcenter_portgroup = args.vcenter_portgroup
    vcenter_vm = args.vcenter_vm

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
        nuage_password = getpass.getpass(prompt='Enter password for Nuage host %s for user %s: ' % (nuage_host, nuage_username))

    # Getting user password for vCenter connection
    if vcenter_password is None:
        logger.debug('No command line vCenter password received, requesting vCenter password from user')
        vcenter_password = getpass.getpass(prompt='Enter password for vCenter host %s for user %s: ' % (vcenter_host, vcenter_username))

    try:
        vc = None
        nc = None

        # Connecting to Nuage
        logger.info('Connecting to Nuage server %s:%s with username %s' % (nuage_host, nuage_port, nuage_username))
        nc = vsdk.NUVSDSession(username=nuage_username, password=nuage_password, enterprise=nuage_enterprise, api_url="https://%s:%s" % (nuage_host, nuage_port))
        nc.start()

        if not nc or not nc.is_current_session():
            logger.error('Could not connect to Nuage host %s with user %s, enterprise %s and specified password' % (nuage_host, nuage_username, nuage_enterprise))
            return 1

        # Connecting to vCenter
        try:
            logger.info('Connecting to vCenter server %s:%s with username %s' % (vcenter_host, vcenter_port, vcenter_username))
            if ssl_context:
                vc = SmartConnect(host=vcenter_host, user=vcenter_username, pwd=vcenter_password, port=int(vcenter_port), sslContext=ssl_context)
            else:
                vc = SmartConnect(host=vcenter_host, user=vcenter_username, pwd=vcenter_password, port=int(vcenter_port))
        except IOError, e:
            pass

        if not vc:
            logger.error('Could not connect to vCenter host %s with user %s and specified password' % (vcenter_host, vcenter_username))
            return 1

        logger.info('Connected to both Nuage & vCenter servers')

        logger.debug('Registering vCenter disconnect at exit')
        atexit.register(Disconnect, vc)

        # Finding the Virtual Machine
        logger.debug('Searching for Virtual Machine: %s' % vcenter_vm)
        vc_vm = get_vcenter_object(logger, vc, [vim.VirtualMachine], vcenter_vm)
        if vc_vm is None:
            logger.critical('VM %s not found, ending run' % vcenter_vm)
            return 1

        # Finding the Portgroup
        logger.debug('Searching for Distributed Portgroup %s' % vcenter_portgroup)
        vc_dvs_pg = get_vcenter_object(logger, vc, [vim.dvs.DistributedVirtualPortgroup], vcenter_portgroup)
        if vc_dvs_pg is None:
            logger.critical('Unknown distributed portgroup %s, exiting' % vcenter_portgroup)
            return 1

        # Finding enterprise
        logger.debug('Searching for enterprise %s' % nuage_vm_enterprise)
        nc_enterprise = get_nuage_object(logger, nc.user, 'ENTERPRISE', 'name == "%s"' % nuage_vm_enterprise, True)
        if nc_enterprise is None:
            logger.critical('Unknown enterprise %s, exiting' % nuage_vm_enterprise)
            return 1

        # Finding subnet
        logger.debug('Searching for the subnet, first by looking at the subnet itself.')
        nc_subnet = None
        nc_subnets = get_nuage_object(logger, nc.user, 'SUBNET', 'name == "%s"' % nuage_vm_subnet, False)

        if len(nc_subnets) == 1:
            logger.debug('Found the L3 subnet %s in Nuage' % nuage_vm_subnet)
            nc_subnet = nc_subnets[0]
        elif len(nc_subnets) == 0:
            logger.debug('Found no L3 subnet with name %s, checking L2 domains' % nuage_vm_subnet)
            nc_subnet = get_nuage_object(logger, nc_enterprise, 'L2DOMAIN', 'name == "%s"' % nuage_vm_subnet, True)
        elif len(nc_subnets) > 1 and nuage_vm_domain is not None and nuage_vm_zone is not None:
            logger.debug('Found more than one L3 subnet with name %s, using Domain %s and Zone %s to find the right subnet' % (nuage_vm_subnet, nuage_vm_domain, nuage_vm_zone))
            nc_domain = get_nuage_object(logger, nc_enterprise, 'DOMAIN', 'name == "%s"' % nuage_vm_domain, True)
            if nc_domain is None:
                logger.critical('Domain %s does not exist in Enterprise %s, exiting' % (nuage_vm_domain, nuage_vm_zone))
                return 1
            nc_zone = get_nuage_object(logger, nc_domain, 'ZONE', 'name == "%s"' % nuage_vm_zone, True)
            if nc_zone is None:
                logger.critical('Zone %s does not exist in Domain %s in Enterprise %s, exiting' % (nuage_vm_zone, nuage_vm_domain, nuage_vm_enterprise))
                return 1
            nc_subnet = get_nuage_object(logger, nc_zone, 'SUBNET', 'name == "%s"' % nuage_vm_subnet, False)

        if nc_subnet is None:
            logger.critical('Subnet with name %s does not exist as an L3 subnet or an L2 domain, exiting')
            return 1

        # Getting VM UUID
        logger.debug('Getting VM UUID, MAC & IP')
        vc_vm_uuid = vc_vm.config.uuid
        logger.debug('Found UUID %s for VM %s' % (vc_vm_uuid, vcenter_vm))
        vc_vm_net_info = vc_vm.guest.net
        vc_vm_mac = None
        vc_vm_ip = None

        for cur_net in vc_vm_net_info:
            if cur_net.macAddress:
                logger.debug('Mac address %s found for VM %s' % (cur_net.macAddress, vcenter_vm))
                vc_vm_mac = cur_net.macAddress
            if vc_vm_mac and cur_net.ipConfig:
                if cur_net.ipConfig.ipAddress:
                    for cur_ip in cur_net.ipConfig.ipAddress:
                        logger.debug('Checking ip address %s for VM %s' % (cur_ip.ipAddress, vcenter_vm))
                        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', cur_ip.ipAddress) and cur_ip.ipAddress != '127.0.0.1':
                            vc_vm_ip = cur_ip.ipAddress
                            break
            if vc_vm_mac and vc_vm_ip:
                logger.debug('Found MAC %s and IP %s for VM %s' % (vc_vm_mac, vc_vm_ip, vcenter_vm))
                break

        # Check if IP is in subnet
        logger.debug('Verifying that IP %s of VM %s is part of subnet %s' % (vc_vm_ip, vcenter_vm, nuage_vm_subnet))
        if not ipaddress.ip_address(unicode(vc_vm_ip, 'utf-8')) in ipaddress.ip_network('%s/%s' % (nc_subnet.address, nc_subnet.netmask)):
            logger.critical('IP %s is not part of subnet %s with netmask %s' % (vc_vm_ip, nc_subnet.address, nc_subnet.netmask))
            return 1

        logger.info('Found UUID %s, MAC %s and IP %s for VM %s' % (vc_vm_uuid, vc_vm_mac, vc_vm_ip, vcenter_vm))

        # if metadata mode, create metadata on the VM
        if mode.lower() == 'metadata':
            logger.debug('Setting the metadata on VM %s' % vcenter_vm)
            vm_option_values = []
            # Network type
            vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.networktype', value='ipv4'))
            # User
            vm_option_values.append(vim.option.OptionValue(key='nuage.user', value=nuage_vm_user))
            # IP
            vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.ip', value=vc_vm_ip))
            if isinstance(nc_subnet, vsdk.NUSubnet):
                nc_zone = vsdk.NUZone(id=nc_subnet.parent_id)
                nc_zone.fetch()
                nc_domain = vsdk.NUDomain(id=nc_zone.parent_id)
                nc_domain.fetch()
                nc_enterprise = vsdk.NUEnterprise(id=nc_domain.parent_id)
                nc_enterprise.fetch()
                # Enterprise
                vm_option_values.append(vim.option.OptionValue(key='nuage.enterprise', value=nc_enterprise.name))
                # Domain
                vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.domain', value=nc_domain.name))
                # Zone
                vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.zone', value=nc_zone.name))
                # Subnet
                vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.network', value=nc_subnet.name))
            else:
                nc_enterprise = vsdk.NUEnterprise(id=nc_subnet.parent_id)
                nc_enterprise.fetch()
                # Enterprise
                vm_option_values.append(vim.option.OptionValue(key='nuage.enterprise', value=nc_enterprise.name))
                # L2Domain
                vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.l2domain', value=nc_subnet.name))

            logger.debug('Creating of config spec for VM')
            config_spec = vim.vm.ConfigSpec(extraConfig=vm_option_values)
            logger.info('Applying advanced parameters. This might take a couple of seconds')
            config_task = vc_vm.ReconfigVM_Task(spec=config_spec)
            logger.debug('Waiting for the advanced paramerter to be applied')
            run_loop = True
            while run_loop:
                info = config_task.info
                if info.state == vim.TaskInfo.State.success:
                    logger.debug('Advanced parameters applied')
                    run_loop = False
                    break
                elif info.state == vim.TaskInfo.State.error:
                    if info.error.fault:
                        logger.info('Applying advanced parameters has quit with error: %s' % info.error.fault.faultMessage)
                    else:
                        logger.info('Applying advanced parameters has quit with cancelation')
                    run_loop = False
                    break
                sleep(1)
        # Else if mode split-activation, create vPort and VM
        elif mode.lower() == 'split-activation':
            # Creating vPort
            logger.debug('Creating vPort for VM %s' % vcenter_vm)
            nc_vport = vsdk.NUVPort(name=vcenter_vm, address_spoofing='INHERITED', type='VM', description='Automatically created, do not edit.')
            nc_subnet.create_child(nc_vport)
            # Creating VM
            logger.debug('Creating a Nuage VM for VM %s' % vcenter_vm)
            nc_vm = vsdk.NUVM(name=vcenter_vm, uuid=vc_vm_uuid, interfaces=[{
                'name': vcenter_vm,
                'VPortID': nc_vport.id,
                'MAC': vc_vm_mac,
                'IPAddress': vc_vm_ip
            }])
            nc.user.create_child(nc_vm)

        # Fetching nic from the VM
        logger.debug('Searching for NIC on VM %s' % vcenter_vm)
        vc_vm_nic = None
        for device in vc_vm.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualEthernetCard):
                logger.debug('Found NIC for VM %s' % vcenter_vm)
                vc_vm_nic = device
                break

        if vc_vm_nic is None:
            logger.critical('Could not find NIC for VM %s, exiting' % vcenter_vm)
            return 1

        # Switching VM nic
        logger.debug('Creating spec to reconfigure the NIC of VM %s' % vcenter_vm)
        vc_nicspec = vim.vm.device.VirtualDeviceSpec()
        vc_nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
        vc_nicspec.device = vc_vm_nic
        vc_nicspec.device.wakeOnLanEnabled = True
        vc_nicspec.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
        vc_nicspec.device.backing.port = vim.dvs.PortConnection()
        vc_nicspec.device.backing.port.portgroupKey = vc_dvs_pg.key
        vc_nicspec.device.backing.port.switchUuid = vc_dvs_pg.config.distributedVirtualSwitch.uuid
        vc_nicspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        vc_nicspec.device.connectable.startConnected = True
        vc_nicspec.device.connectable.connected = not flush
        vc_nicspec.device.connectable.allowGuestControl = True
        vc_vm_nic_reconfig = vim.vm.ConfigSpec(deviceChange=[vc_nicspec])

        logger.info('Applying NIC changes. This might take a couple of seconds')
        config_task = vc_vm.ReconfigVM_Task(spec=vc_vm_nic_reconfig)
        logger.debug('Waiting for the nic change to be applied')
        run_loop = True
        while run_loop:
            info = config_task.info
            if info.state == vim.TaskInfo.State.success:
                logger.debug('Nic change applied')
                run_loop = False
                break
            elif info.state == vim.TaskInfo.State.error:
                if info.error.fault:
                    logger.info('Applying nic changes has quit with error: %s' % info.error.fault.faultMessage)
                else:
                    logger.info('Applying nic changes has quit with cancelation')
                run_loop = False
                break
            sleep(1)

        if flush:
            vc_nicspec = vim.vm.device.VirtualDeviceSpec()
            vc_nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
            vc_nicspec.device = vc_vm_nic 
            vc_nicspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
            vc_nicspec.device.connectable.startConnected = True
            vc_nicspec.device.connectable.connected = True
            vc_nicspec.device.connectable.allowGuestControl = True
            vc_vm_nic_reconfig = vim.vm.ConfigSpec(deviceChange=[vc_nicspec])
            logger.info('Reconnecting NIC. This might take a couple of seconds')
            config_task = vc_vm.ReconfigVM_Task(spec=vc_vm_nic_reconfig)
            logger.debug('Waiting for the nic change to be applied')
            run_loop = True
            while run_loop:
                info = config_task.info
                if info.state == vim.TaskInfo.State.success:
                    logger.debug('Nic change applied')
                    run_loop = False
                    break
                elif info.state == vim.TaskInfo.State.error:
                    if info.error.fault:
                        logger.info('Applying nic changes has quit with error: %s' % info.error.fault.faultMessage)
                    else:
                        logger.info('Applying nic changes has quit with cancelation')
                    run_loop = False
                    break
                sleep(1)

        logger.info('Succesfully attached VM %s to Nuage subnet %s, in mode %s' % (vcenter_vm, nuage_vm_subnet, mode))

    except vmodl.MethodFault, e:
        logger.critical('Caught vmodl fault: %s' % e.msg)
        return 1
    except Exception, e:
        logger.critical('Caught exception: %s' % str(e))

    return 0

# Start program
if __name__ == "__main__":
    main()
