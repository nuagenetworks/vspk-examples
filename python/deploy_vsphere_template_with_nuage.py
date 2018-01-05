# -*- coding: utf-8 -*-
"""
deploy_vsphere_template_with_nuage is a script which allows you to deploy (or clone) a VM template (or VM) and connect it to a Nuage VSP subnet.

This can be done through either specifying all parameters through CLI, or by selecting them from lists.

Check the examples for several combinations of arguments

--- Usage ---
Run 'python deploy_vsphere_template_with_nuage.py -h' for an overview

--- Documentation ---
http://github.com/nuagenetworks/vspk-examples/blob/master/docs/deploy_vsphere_template_with_nuage.md

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

--- Examples ---
---- Deploy a template in a given Resource Pool and Folder, with given Nuage VM metadata and a fixed IP ----
python deploy_vsphere_template_with_nuage.py -n Test-02 --nuage-enterprise csp --nuage-host 10.167.43.64 --nuage-user csproot -S -t TestVM-Minimal-Template --vcenter-host 10.167.43.24 --vcenter-user root -r Pool -f Folder --nuage-vm-enterprise VMware-Integration --nuage-vm-domain Main --nuage-vm-zone "Zone 1" --nuage-vm-subnet "Subnet 0" --nuage-vm-ip 10.0.0.123 --nuage-vm-user vmwadmin

---- Deploy a template, for the Nuage VM metadata show menus to select values from ----
python deploy_vsphere_template_with_nuage.py -n Test-02 --nuage-enterprise csp --nuage-host 10.167.43.64 --nuage-user csproot -S -t TestVM-Minimal-Template --vcenter-host 10.167.43.24 --vcenter-user root
"""
import argparse
import atexit
import getpass
import ipaddress
import logging
import os.path
import requests

from time import sleep
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
from vspk import v5_0 as vsdk


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="Deploy a template into into a VM with certain Nuage VSP metadata.")
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-f', '--folder', required=False, help='The folder in which the new VM should reside (default = same folder as source virtual machine)', dest='folder', type=str)
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-n', '--name', required=True, help='The name of the VM to be created', dest='name', type=str)
    parser.add_argument('--nuage-enterprise', required=True, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('--nuage-user', required=True, help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('--nuage-vm-enterprise', required=False, help='The Nuage enterprise to which the VM should be connected', dest='nuage_vm_enterprise', type=str)
    parser.add_argument('--nuage-vm-domain', required=False, help='The Nuage domain to which the VM should be connected', dest='nuage_vm_domain', type=str)
    parser.add_argument('--nuage-vm-zone', required=False, help='The Nuage zone to which the VM should be connected', dest='nuage_vm_zone', type=str)
    parser.add_argument('--nuage-vm-subnet', required=False, help='The Nuage subnet to which the VM should be connected', dest='nuage_vm_subnet', type=str)
    parser.add_argument('--nuage-vm-ip', required=False, help='The IP the VM should have', dest='nuage_vm_ip', type=str)
    parser.add_argument('--nuage-vm-user', required=False, help='The Nuage User owning the VM', dest='nuage_vm_user', type=str)
    parser.add_argument('-P', '--disable-power-on', required=False, help='Disable power on of cloned VMs', dest='nopoweron', action='store_true')
    parser.add_argument('-r', '--resource-pool', required=False, help='The resource pool in which the new VM should reside, (default = Resources, the root resource pool)', dest='resource_pool', type=str, default='Resources')
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect', dest='nosslcheck', action='store_true')
    parser.add_argument('-t', '--template', required=True, help='Template to deploy', dest='template', type=str)
    parser.add_argument('--vcenter-host', required=True, help='The vCenter or ESXi host to connect to', dest='vcenter_host', type=str)
    parser.add_argument('--vcenter-port', required=False, help='vCenter Server port to connect to (default = 443)', dest='vcenter_port', type=int, default=443)
    parser.add_argument('--vcenter-password', required=False, help='The password with which to connect to the vCenter host. If not specified, the user is prompted at runtime for a password', dest='vcenter_password', type=str)
    parser.add_argument('--vcenter-user', required=True, help='The username with which to connect to the vCenter host', dest='vcenter_username', type=str)
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', action='store_true')

    args = parser.parse_args()
    return args


def clear(logger):
    """
    Clears the terminal
    """
    if logger:
        logger.debug('Clearing terminal')
    os.system(['clear', 'cls'][os.name == 'nt'])


def find_vm(vc, logger, name):
    """
    Find a virtual machine by its name and return it
    """

    content = vc.content
    obj_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_list = obj_view.view

    for vm in vm_list:
        logger.debug('Checking virtual machine %s' % vm.name)
        if vm.name == name:
            logger.debug('Found virtual machine %s' % vm.name)
            return vm
    return None


def find_resource_pool(vc, logger, name):
    """
    Find a resource pool by its name and return it
    """

    content = vc.content
    obj_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.ResourcePool], True)
    rp_list = obj_view.view

    for rp in rp_list:
        logger.debug('Checking resource pool %s' % rp.name)
        if rp.name == name:
            logger.debug('Found resource pool %s' % rp.name)
            return rp
    return None


def find_folder(vc, logger, name):
    """
    Find a folder by its name and return it
    """

    content = vc.content
    obj_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Folder], True)
    folder_list = obj_view.view

    for folder in folder_list:
        logger.debug('Checking folder %s' % folder.name)
        if folder.name == name:
            logger.debug('Found folder %s' % folder.name)
            return folder
    return None


def main():
    """
    Manage the vCenter Integration Node configuration
    """

    # Handling arguments
    args                = get_args()
    debug               = args.debug
    folder_name = None
    if args.folder:
        folder_name = args.folder
    log_file            = None
    if args.logfile:
        log_file        = args.logfile
    name                = args.name
    nuage_enterprise    = args.nuage_enterprise
    nuage_host          = args.nuage_host
    nuage_port          = args.nuage_port
    nuage_password      = None
    if args.nuage_password:
        nuage_password  = args.nuage_password
    nuage_username      = args.nuage_username
    nuage_vm_enterprise = None
    if args.nuage_vm_enterprise:
        nuage_vm_enterprise = args.nuage_vm_enterprise
    nuage_vm_domain     = None
    if args.nuage_vm_domain:
        nuage_vm_domain = args.nuage_vm_domain
    nuage_vm_zone       = None
    if args.nuage_vm_zone:
        nuage_vm_zone   = args.nuage_vm_zone
    nuage_vm_subnet     = None
    if args.nuage_vm_subnet:
        nuage_vm_subnet = args.nuage_vm_subnet
    nuage_vm_ip         = None
    if args.nuage_vm_ip:
        nuage_vm_ip     = args.nuage_vm_ip
    nuage_vm_user       = None
    if args.nuage_vm_user:
        nuage_vm_user   = args.nuage_vm_user
    power_on            = not args.nopoweron
    resource_pool_name  = None
    if args.resource_pool:
        resource_pool_name = args.resource_pool
    nosslcheck          = args.nosslcheck
    template            = args.template
    vcenter_host        = args.vcenter_host
    vcenter_port        = args.vcenter_port
    vcenter_password    = None
    if args.vcenter_password:
        vcenter_password = args.vcenter_password
    vcenter_username    = args.vcenter_username
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
        try:
            logger.info('Connecting to Nuage server %s:%s with username %s' % (nuage_host, nuage_port, nuage_username))
            nc = vsdk.NUVSDSession(username=nuage_username, password=nuage_password, enterprise=nuage_enterprise, api_url="https://%s:%s" % (nuage_host, nuage_port))
            nc.start()
        except IOError, e:
            pass

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

        # Verifying the Nuage Enterprise existence or selecting it
        if nuage_vm_enterprise:
            logger.debug('Finding Nuage enterprise %s' % nuage_vm_enterprise)
            vm_enterprise = nc.user.enterprises.get_first(filter="name == '%s'" % nuage_vm_enterprise)
            if vm_enterprise is None:
                logger.error('Unable to find Nuage enterprise %s' % nuage_vm_enterprise)
                return 1
            logger.info('Nuage enterprise %s found' % nuage_vm_enterprise)
        else:
            clear(logger)
            print('Please select your enterprise:')
            index = 0
            all_ent = nc.user.enterprises.get()
            for cur_ent in all_ent:
                print('%s. %s' % (index + 1, cur_ent.name))
                index += 1
            vm_enterprise = None
            while vm_enterprise is None:
                choice = raw_input('Please enter the number of the enterprise [1-%s]: ' % len(all_ent))
                choice = int(choice)
                if choice > 0 and choice - 1 < len(all_ent):
                    vm_enterprise = all_ent[choice - 1]
                    break
                print('Invalid choice, please try again')

        # Verifying the Nuage User existence or selecting it
        if nuage_vm_user:
            logger.debug('Finding Nuage user %s' % nuage_vm_user)
            vm_user = vm_enterprise.users.get_first(filter="userName == '%s'" % nuage_vm_user)
            if vm_user is None:
                logger.error('Unable to find Nuage user %s' % nuage_vm_user)
                return 1
            logger.info('Nuage user %s found' % nuage_vm_user)
        else:
            clear(logger)
            print('Enterprise: %s' % vm_enterprise.name)
            print(80 * '-')
            print('Please select your user:')
            index = 0
            all_users = vm_enterprise.users.get()
            for cur_user in all_users:
                print('%s. %s' % (index + 1, cur_user.user_name))
                index += 1
            vm_user = None
            while vm_user is None:
                choice = raw_input('Please enter the number of the user [1-%s]: ' % len(all_users))
                choice = int(choice)
                if choice > 0 and choice - 1 < len(all_users):
                    vm_user = all_users[choice - 1]
                    break
                print('Invalid choice, please try again')

        # Verifying the Nuage Domain existence or selecting it
        if nuage_vm_domain:
            logger.debug('Finding Nuage domain %s' % nuage_vm_domain)
            vm_domain = vm_enterprise.domains.get_first(filter="name == '%s'" % nuage_vm_domain)
            if vm_domain is None:
                logger.error('Unable to find Nuage domain %s' % nuage_vm_domain)
                return 1
            logger.info('Nuage domain %s found' % nuage_vm_domain)
        else:
            clear(logger)
            print('Enterprise: %s' % vm_enterprise.name)
            print('User: %s' % vm_user.user_name)
            print(80 * '-')
            print('Please select your domain:')
            index = 0
            all_dom = vm_enterprise.domains.get()
            for cur_dom in all_dom:
                print('%s. %s' % (index + 1, cur_dom.name))
                index += 1
            vm_domain = None
            while vm_domain is None:
                choice = raw_input('Please enter the number of the domain [1-%s]: ' % len(all_dom))
                choice = int(choice)
                if choice > 0 and choice - 1 < len(all_dom):
                    vm_domain = all_dom[choice - 1]
                    break
                print('Invalid choice, please try again')

        # Verifying the Nuage Zone existence or selecting it
        if nuage_vm_zone:
            logger.debug('Finding Nuage zone %s' % nuage_vm_zone)
            vm_zone = vm_domain.zones.get_first(filter="name == '%s'" % nuage_vm_zone)
            if vm_zone is None:
                logger.error('Unable to find Nuage zone %s' % nuage_vm_zone)
                return 1
            logger.info('Nuage zone %s found' % nuage_vm_zone)
        else:
            clear(logger)
            print('Enterprise: %s' % vm_enterprise.name)
            print('User: %s' % vm_user.user_name)
            print('Domain: %s' % vm_domain.name)
            print(80 * '-')
            print('Please select your zone:')
            index = 0
            all_zone = vm_domain.zones.get()
            for cur_zone in all_zone:
                print('%s. %s' % (index + 1, cur_zone.name))
                index += 1
            vm_zone = None
            while vm_zone is None:
                choice = raw_input('Please enter the number of the zone [1-%s]: ' % len(all_zone))
                choice = int(choice)
                if choice > 0 and choice - 1 < len(all_zone):
                    vm_zone = all_zone[choice - 1]
                    break
                print('Invalid choice, please try again')

        # Verifying the Nuage Subnet existence or selecting it
        if nuage_vm_subnet:
            logger.debug('Finding Nuage subnet %s' % nuage_vm_subnet)
            vm_subnet = vm_zone.subnets.get_first(filter="name == '%s'" % nuage_vm_subnet)
            if vm_subnet is None:
                logger.error('Unable to find Nuage subnet %s' % nuage_vm_subnet)
                return 1
            logger.info('Nuage subnet %s found' % nuage_vm_subnet)
        else:
            clear(logger)
            print('Enterprise: %s' % vm_enterprise.name)
            print('User: %s' % vm_user.user_name)
            print('Domain: %s' % vm_domain.name)
            print('Zone: %s' % vm_zone.name)
            print(80 * '-')
            print('Please select your subnet:')
            index = 0
            all_subnet = vm_zone.subnets.get()
            for cur_subnet in all_subnet:
                print('%s. %s - %s/%s' % (index + 1, cur_subnet.name, cur_subnet.address, cur_subnet.netmask))
                index += 1
            vm_subnet = None
            while vm_subnet is None:
                choice = raw_input('Please enter the number of the subnet [1-%s]: ' % len(all_subnet))
                choice = int(choice)
                if choice > 0 and choice - 1 < len(all_subnet):
                    vm_subnet = all_subnet[choice - 1]
                    break
                print('Invalid choice, please try again')

        # Verifying the IP or asking for it
        if nuage_vm_ip:
            logger.debug('Verifying if IP %s is inside Nuage subnet %s range' % (nuage_vm_ip, vm_subnet.name))
            if not ipaddress.ip_address(nuage_vm_ip) in ipaddress.ip_network('%s/%s' % (vm_subnet.address, vm_subnet.netmask)):
                logger.error('IP %s is not part of subnet %s with netmask %s' % (nuage_vm_ip, vm_subnet.address, vm_subnet.netmask))
                return 1
            vm_ip = nuage_vm_ip
        else:
            clear(logger)
            print('Enterprise: %s' % vm_enterprise.name)
            print('User: %s' % vm_user.user_name)
            print('Domain: %s' % vm_domain.name)
            print('Zone: %s' % vm_zone.name)
            print('Subnet: %s - %s/%s' % (vm_subnet.name, vm_subnet.address, vm_subnet.netmask))
            print(80 * '-')
            print('If you want a static IP, please enter it. Or press enter for a DHCP assigned IP.')
            vm_ip = None
            while vm_ip is None:
                choice = raw_input('Please enter the IP or press enter for a DHCP assigned IP: ')
                if not choice or ipaddress.ip_address(choice) in ipaddress.ip_network('%s/%s' % (vm_subnet.address, vm_subnet.netmask)):
                    vm_ip = choice
                    break
                print('Invalid choice, please try again')

        logger.info('Using following Nuage values:')
        logger.info('Enterprise: %s' % vm_enterprise.name)
        logger.info('User: %s' % vm_user.user_name)
        logger.info('Domain: %s' % vm_domain.name)
        logger.info('Zone: %s' % vm_zone.name)
        logger.info('Subnet: %s - %s/%s' % (vm_subnet.name, vm_subnet.address, vm_subnet.netmask))
        if vm_ip:
            logger.info('Static IP: %s' % vm_ip)

        # Find the correct VM
        logger.debug('Finding template %s' % template)
        template_vm = find_vm(vc, logger, template)
        if template_vm is None:
            logger.error('Unable to find template %s' % template)
            return 1
        logger.info('Template %s found' % template)

        # Find the correct Resource Pool
        resource_pool = None
        if resource_pool_name is not None:
            logger.debug('Finding resource pool %s' % resource_pool_name)
            resource_pool = find_resource_pool(vc, logger, resource_pool_name)
            if resource_pool is None:
                logger.critical('Unable to find resource pool %s' % resource_pool_name)
                return 1
            logger.info('Resource pool %s found' % resource_pool_name)

        # Find the correct folder
        folder = None
        if folder_name is not None:
            logger.debug('Finding folder %s' % folder_name)
            folder = find_folder(vc, logger, folder_name)
            if folder is None:
                logger.critical('Unable to find folder %s' % folder_name)
                return 1
            logger.info('Folder %s found' % folder_name)
        else:
            logger.info('Setting folder to template folder as default')
            folder = template_vm.parent

        # Creating necessary specs
        logger.debug('Creating relocate spec')
        if resource_pool is not None:
            logger.debug('Resource pool found, using')
            relocate_spec = vim.vm.RelocateSpec(pool=resource_pool)
        else:
            logger.debug('No resource pool found, continuing without it')
            relocate_spec = vim.vm.RelocateSpec()

        logger.debug('Creating clone spec')
        clone_spec = vim.vm.CloneSpec(powerOn=False, template=False, location=relocate_spec)

        run_loop = True
        vm = None
        logger.info('Trying to clone %s to new virtual machine' % template)

        if find_vm(vc, logger, name):
            logger.warning('Virtual machine already exists, not creating')
            run_loop = False
        else:
            logger.debug('Creating clone task')
            task = template_vm.Clone(name=name, folder=folder, spec=clone_spec)
            logger.info('Cloning task created')
            logger.info('Checking task for completion. This might take a while')

        while run_loop:
            info = task.info
            logger.debug('Checking clone task')
            if info.state == vim.TaskInfo.State.success:
                logger.info('Cloned and running')
                vm = info.result
                run_loop = False
                break
            elif info.state == vim.TaskInfo.State.running:
                logger.debug('Cloning task is at %s percent' % info.progress)
            elif info.state == vim.TaskInfo.State.queued:
                logger.debug('Cloning task is queued')
            elif info.state == vim.TaskInfo.State.error:
                if info.error.fault:
                    logger.info('Cloning task has quit with error: %s' % info.error.fault.faultMessage)
                else:
                    logger.info('Cloning task has quit with cancelation')
                run_loop = False
                break
            logger.debug('Sleeping 10 seconds for new check')
            sleep(10)

        # If the VM does not exist, cloning failed and the script is terminated
        if not vm:
            logger.error('Clone failed')
            return 1

        # Setting Nuage metadata
        logger.info('Setting Nuage Metadata')
        vm_option_values = []
        # Enterprise
        vm_option_values.append(vim.option.OptionValue(key='nuage.enterprise', value=vm_enterprise.name))
        # Domain
        vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.domain', value=vm_domain.name))
        # Zone
        vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.zone', value=vm_zone.name))
        # Subnet
        vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.network', value=vm_subnet.name))
        # Network type
        vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.networktype', value='ipv4'))
        # User
        vm_option_values.append(vim.option.OptionValue(key='nuage.user', value=vm_user.user_name))
        # IP
        if vm_ip:
            vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.ip', value=vm_ip))

        logger.debug('Creating of config spec for VM')
        config_spec = vim.vm.ConfigSpec(extraConfig=vm_option_values)
        logger.info('Applying advanced parameters. This might take a couple of seconds')
        config_task = vm.ReconfigVM_Task(spec=config_spec)
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
            sleep(5)

        if power_on:
            logger.info('Powering on VM. This might take a couple of seconds')
            power_on_task = vm.PowerOn()
            logger.debug('Waiting fo VM to power on')
            run_loop = True
            while run_loop:
                info = power_on_task.info
                if info.state == vim.TaskInfo.State.success:
                    run_loop = False
                    break
                elif info.state == vim.TaskInfo.State.error:
                    if info.error.fault:
                        logger.info('Power on has quit with error: %s' % info.error.fault.faultMessage)
                    else:
                        logger.info('Power on has quit with cancelation')
                    run_loop = False
                    break
                sleep(5)

    except vmodl.MethodFault, e:
        logger.critical('Caught vmodl fault: %s' % e.msg)
        return 1
    except Exception, e:
        logger.critical('Caught exception: %s' % str(e))
        return 1

# Start program
if __name__ == "__main__":
    main()
