# -*- coding: utf-8 -*-
"""
vsphere_activate_vm will activate a VM in a Nuage environment, it can use both split activation or metadata.

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

--- Version history ---
2017-03-26 - 1.0

--- Usage ---
run 'python vsphere_activate_vm.py -h' for an overview

--- Config file structure ----
[NUAGE]
# VSD API server
vsd_api_url = https://10.189.1.254:8443

# VSD API user
vsd_api_user = csproot

# VSD API password
vsd_api_password = csproot

# VSD API enterprise
vsd_api_enterprise = csp

[VSPHERE]
# vSphere server
vsphere_api_host = 10.189.1.21

# vSphere port
vsphere_api_port = 443

# vSphere user
vsphere_api_user = administrator@vsphere.local

# vSphere password
vsphere_api_password = vmware

[LOG]
# Log directory
# Where to store the log
directory = /var/log/nuage

# Log file
# Filename of the log
file = vsphere_activate_vm.log

# Log level
# define your level of logging, possible values:
# DEBUG, INFO, WARNING, ERROR, CRITICAL
# Warning: If you enable DEBUG, your log will get flooded with messages,
# only enable this for short amounts of time.
level = WARNING

"""
import argparse
import atexit
import ConfigParser
import ipaddress
import logging
import os
import re
import requests
import sys

from time import sleep
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
from vspk import v4_0 as vsdk


def get_args():
    parser = argparse.ArgumentParser(description="Tool to activate a VM in a Nuage environment.")
    parser.add_argument('-c', '--config-file', required=False, help='Configuration file to use, if not specified ~/.nuage/config.ini is used', dest='config_file', type=str)
    parser.add_argument('-m', '--mode', required=False, help='Mode of activation: metadata or split-activation. Default is metadata', dest='mode', choices=['metadata','split-activation'], default='metadata', type=str)
    parser.add_argument('-n', '--vm-name', required=False, help='The VM in vCenter that should be connected to Nuage', dest='vcenter_vm_name', type=str)
    parser.add_argument('-e', '--vm-enterprise', required=False, help='The Nuage enterprise to which the VM should be connected', dest='nuage_vm_enterprise', type=str)
    parser.add_argument('-d', '--vm-domain', required=False, help='The Nuage domain to which the VM should be connected', dest='nuage_vm_domain', type=str)
    parser.add_argument('-z', '--vm-zone', required=False, help='The Nuage zone to which the VM should be connected', dest='nuage_vm_zone', type=str)
    parser.add_argument('-s', '--vm-subnet', required=False, help='The Nuage subnet to which the VM should be connected', dest='nuage_vm_subnet', type=str)
    parser.add_argument('-i', '--vm-ip', required=False, help='The IP the VM should have', dest='nuage_vm_ip', type=str)
    parser.add_argument('-p', '--vm-policy-group', required=False, help='The policy group the VM should have', dest='nuage_vm_policy_group', type=str)
    parser.add_argument('-r', '--vm-redirection-target', required=False, help='The redirection target the VM should have', dest='nuage_vm_redirection_target', type=str)
    parser.add_argument('-u', '--vm-user', required=False, help='The Nuage User owning the VM', dest='nuage_vm_user', type=str)
    args = parser.parse_args()
    return args

def parse_config(config_file):
    """
    Parses configuration file
    """
    cfg = ConfigParser.ConfigParser()
    cfg.read(config_file)

    # Checking the sections of the config file
    if not cfg.has_section('VSPHERE') or \
            not cfg.has_section('NUAGE') or \
            not cfg.has_section('LOG'):
        print 'Missing section in the configuration file {0:s}, please check the documentation'.format(
            config_file)
        sys.exit(1)
    # Checking the NUAGE options
    if not cfg.has_option('NUAGE', 'vsd_api_url') or \
            not cfg.has_option('NUAGE', 'vsd_api_user') or \
            not cfg.has_option('NUAGE', 'vsd_api_password') or \
            not cfg.has_option('NUAGE', 'vsd_api_enterprise'):
        print 'Missing options in the NUAGE section of configuration file {0:s}, please check the documentation'.format(
            config_file)
        sys.exit(1)
    # Checking the VSPHERE options
    if not cfg.has_option('VSPHERE', 'vsphere_api_host') or \
            not cfg.has_option('VSPHERE', 'vsphere_api_user') or \
            not cfg.has_option('VSPHERE', 'vsphere_api_password') or \
            not cfg.has_option('VSPHERE', 'vsphere_api_port'):
        print 'Missing options in the VSPHERE section of configuration file {0:s}, please check the documentation'.format(
            config_file)
        sys.exit(1)
    # Checking the LOG options
    if not cfg.has_option('LOG', 'directory') or \
            not cfg.has_option('LOG', 'file') or \
            not cfg.has_option('LOG', 'level'):
        print 'Missing options in the LOG section of configuration file {0:s}, please check the documentation'.format(
            config_file)
        sys.exit(1)

    return cfg

def clear():
    logging.debug('Clearing terminal')
    os.system(['clear', 'cls'][os.name == 'nt'])

def find_vm(vc, name):
    """
    Find a virtual machine by its name and return it
    """

    content = vc.content
    obj_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_list = obj_view.view

    for vm in vm_list:
        logging.debug('Checking virtual machine %s' % vm.name)
        if vm.name == name:
            logging.debug('Found virtual machine %s' % vm.name)
            return vm
    return None

def main():
    """
    Manage the activation of a vSphere VM
    """
    # Handling arguments
    args = get_args()

    if args.config_file:
        cfg = parse_config(args.config_file)
    elif os.path.isfile('{0:s}/.nuage/config.ini'.format(os.path.expanduser('~'))):
        cfg = parse_config('{0:s}/.nuage/config.ini'.format(os.path.expanduser('~')))
    else:
        print 'Missing config file'
        return 1

    mode = args.mode

    nuage_vm_enterprise = None
    if args.nuage_vm_enterprise:
        nuage_vm_enterprise = args.nuage_vm_enterprise
    nuage_vm_domain = None
    if args.nuage_vm_domain:
        nuage_vm_domain = args.nuage_vm_domain
    nuage_vm_zone = None
    if args.nuage_vm_zone:
        nuage_vm_zone = args.nuage_vm_zone
    nuage_vm_subnet = None
    if args.nuage_vm_subnet:
        nuage_vm_subnet = args.nuage_vm_subnet
    nuage_vm_ip = None
    if args.nuage_vm_ip:
        nuage_vm_ip = args.nuage_vm_ip
    nuage_vm_user = None
    if args.nuage_vm_user:
        nuage_vm_user = args.nuage_vm_user
    nuage_vm_policy_group = None
    if args.nuage_vm_policy_group:
        nuage_vm_user = args.nuage_vm_policy_group
    nuage_vm_redirection_target = None
    if args.nuage_vm_redirection_target:
        nuage_vm_user = args.nuage_vm_redirection_target
    vcenter_vm_name = None
    if args.vcenter_vm_name:
        vcenter_vm_name = args.vcenter_vm_name

    # Handling logging
    log_dir = cfg.get('LOG', 'directory')
    log_file = cfg.get('LOG', 'file')
    log_level = cfg.get('LOG', 'level')

    if not log_level:
        log_level = 'ERROR'

    log_path = None
    if log_dir and log_file and os.path.isdir(log_dir) and os.access(log_dir, os.W_OK):
        log_path = os.path.join(log_dir, log_file)

    logging.basicConfig(filename=log_path, format='%(asctime)s %(levelname)s - %(name)s - %(message)s', level=log_level)
    logging.info('Logging initiated')

    # Disabling SSL verification if set
    logging.debug('Disabling SSL certificate verification.')
    requests.packages.urllib3.disable_warnings()

    try:
        vc = None
        nc = None

        # Connecting to Nuage
        try:
            logging.info('Connecting to Nuage server {0:s} with username {1:s} and enterprise {2:s}'.format(cfg.get('NUAGE', 'vsd_api_url'), cfg.get('NUAGE', 'vsd_api_user'), cfg.get('NUAGE', 'vsd_api_enterprise')))
            nc = vsdk.NUVSDSession(username=cfg.get('NUAGE', 'vsd_api_user'), password=cfg.get('NUAGE', 'vsd_api_password'), enterprise=cfg.get('NUAGE', 'vsd_api_enterprise'), api_url=cfg.get('NUAGE', 'vsd_api_url'))
            nc.start()
        except IOError, e:
            pass

        if not nc or not nc.is_current_session():
            logging.error('Could not connect to Nuage host {0:s} with user {1:s}, enterprise {2:s} and specified password'.format(cfg.get('NUAGE', 'vsd_api_url'), cfg.get('NUAGE', 'vsd_api_user'), cfg.get('NUAGE', 'vsd_api_enterprise')))
            return 1

        # Connecting to vCenter
        try:
            logging.info('Connecting to vCenter server {0:s} with username {1:s}'.format(cfg.get('VSPHERE', 'vsphere_api_host'), cfg.get('VSPHERE', 'vsphere_api_user')))
            vc = SmartConnect(host=cfg.get('VSPHERE', 'vsphere_api_host'), user=cfg.get('VSPHERE', 'vsphere_api_user'), pwd=cfg.get('VSPHERE', 'vsphere_api_password'), port=int(cfg.get('VSPHERE', 'vsphere_api_port')))
        except IOError, e:
            pass

        if not vc:
            logging.error('Could not connect to vCenter host {0:s} with user {1:s} and specified password'.format(cfg.get('VSPHERE', 'vsphere_api_host'), cfg.get('VSPHERE', 'vsphere_api_user')))
            return 1

        logging.info('Connected to both Nuage & vCenter servers')

        logging.debug('Registering vCenter disconnect at exit')
        atexit.register(Disconnect, vc)

        vcenter_vm = None
        vm_enterprise = None
        vm_user = None
        vm_domain = None
        vm_is_l2domain = False
        vm_zone = None
        vm_subnet = None
        vm_ip = None
        vm_policy_group = None
        vm_redirection_target = None
        # Verifying the vCenter VM existence or selecting it
        if vcenter_vm_name:
            vcenter_vm = find_vm(vc, vcenter_vm_name)
            if vcenter_vm is None:
                logging.critical('Unable to find specified VM with name {0:s}'.format(vcenter_vm_name))
                return 1
        else:
            logging.debug('Offering a choice of which VM to activate')
            content = vc.content
            obj_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
            vm_list = obj_view.view
            clear()
            print('Please select your VM:')
            index = 0
            for cur_vm in vm_list:
                print('%s. %s' % (index + 1, cur_vm.name))
                index += 1
            while vcenter_vm is None:
                choice = raw_input('Please enter the number of the VM [1-%s]: ' % len(vm_list))
                choice = int(choice)
                if choice > 0 and choice - 1 < len(vm_list):
                    vcenter_vm = vm_list[choice - 1]
                    break
                print('Invalid choice, please try again')

        # Verifying the Nuage Enterprise existence or selecting it
        if nuage_vm_enterprise:
            logging.debug('Finding Nuage enterprise %s' % nuage_vm_enterprise)
            vm_enterprise = nc.user.enterprises.get_first(filter="name == '%s'" % nuage_vm_enterprise)
            if vm_enterprise is None:
                logging.error('Unable to find Nuage enterprise %s' % nuage_vm_enterprise)
                return 1
            logging.info('Nuage enterprise %s found' % nuage_vm_enterprise)
        else:
            clear()
            print('VM: %s' % vcenter_vm.name)
            print(80 * '-')
            print('Please select your enterprise:')
            index = 0
            all_ent = nc.user.enterprises.get()
            for cur_ent in all_ent:
                print('%s. %s' % (index + 1, cur_ent.name))
                index += 1
            while vm_enterprise is None:
                choice = raw_input('Please enter the number of the enterprise [1-%s]: ' % len(all_ent))
                choice = int(choice)
                if choice > 0 and choice - 1 < len(all_ent):
                    vm_enterprise = all_ent[choice - 1]
                    break
                print('Invalid choice, please try again')

        # Verifying the Nuage User existence or selecting it
        if nuage_vm_user:
            logging.debug('Finding Nuage user %s' % nuage_vm_user)
            vm_user = vm_enterprise.users.get_first(filter="userName == '%s'" % nuage_vm_user)
            if vm_user is None:
                logging.error('Unable to find Nuage user %s' % nuage_vm_user)
                return 1
            logging.info('Nuage user %s found' % nuage_vm_user)
        else:
            clear()
            print('VM: %s' % vcenter_vm.name)
            print('Enterprise: %s' % vm_enterprise.name)
            print(80 * '-')
            print('Please select your user:')
            index = 0
            all_users = vm_enterprise.users.get()
            for cur_user in all_users:
                print('%s. %s' % (index + 1, cur_user.user_name))
                index += 1
            while vm_user is None:
                choice = raw_input('Please enter the number of the user [1-%s]: ' % len(all_users))
                choice = int(choice)
                if choice > 0 and choice - 1 < len(all_users):
                    vm_user = all_users[choice - 1]
                    break
                print('Invalid choice, please try again')

        # Verifying the Nuage Domain existence or selecting it
        if nuage_vm_domain:
            logging.debug('Finding Nuage domain %s' % nuage_vm_domain)
            vm_domain = vm_enterprise.domains.get_first(filter="name == '%s'" % nuage_vm_domain)
            if vm_domain is None:
                logging.debug('Unable to find the domain {0:s} as an L3 domain'.format(nuage_vm_domain))
                vm_domain = vm_enterprise.l2_domains.get_first(filter="name == '%s'" % nuage_vm_domain)
                vm_is_l2domain = True
                if vm_domain is None:
                    logging.error('Unable to find Nuage domain {0:s}'.format(nuage_vm_domain))
                    return 1
            logging.info('Nuage domain %s found' % nuage_vm_domain)
        else:
            clear()
            print('VM: %s' % vcenter_vm.name)
            print('Enterprise: %s' % vm_enterprise.name)
            print('User: %s' % vm_user.user_name)
            print(80 * '-')
            print('Please select your domain:')
            index = 0
            all_l3_dom = vm_enterprise.domains.get()
            all_l2_dom = vm_enterprise.l2_domains.get()
            all_dom = all_l2_dom + all_l3_dom
            for cur_dom in all_l2_dom:
                print('%s. L2 %s - %s/%s' % (index + 1, cur_dom.name, cur_dom.address, cur_dom.netmask))
                index += 1
            for cur_dom in all_l3_dom:
                print('%s. L3 - %s' % (index + 1, cur_dom.name))
                index += 1
            while vm_domain is None:
                choice = raw_input('Please enter the number of the domain [1-%s]: ' % len(all_dom))
                choice = int(choice)
                if choice > 0 and choice - 1 < len(all_dom):
                    vm_domain = all_dom[choice - 1]
                    if type(vm_domain) is vsdk.NUL2Domain:
                        vm_is_l2domain = True
                    break
                print('Invalid choice, please try again')

        # Verifying the Nuage Zone existence or selecting it
        if not vm_is_l2domain and nuage_vm_zone:
            logging.debug('Finding Nuage zone %s' % nuage_vm_zone)
            vm_zone = vm_domain.zones.get_first(filter="name == '%s'" % nuage_vm_zone)
            if vm_zone is None:
                logging.error('Unable to find Nuage zone %s' % nuage_vm_zone)
                return 1
            logging.info('Nuage zone %s found' % nuage_vm_zone)
        elif not vm_is_l2domain:
            clear()
            print('VM: %s' % vcenter_vm.name)
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
            while vm_zone is None:
                choice = raw_input('Please enter the number of the zone [1-%s]: ' % len(all_zone))
                choice = int(choice)
                if choice > 0 and choice - 1 < len(all_zone):
                    vm_zone = all_zone[choice - 1]
                    break
                print('Invalid choice, please try again')

        # Verifying the Nuage Subnet existence or selecting it
        if not vm_is_l2domain and nuage_vm_subnet:
            logging.debug('Finding Nuage subnet %s' % nuage_vm_subnet)
            vm_subnet = vm_zone.subnets.get_first(filter="name == '%s'" % nuage_vm_subnet)
            if vm_subnet is None:
                logging.error('Unable to find Nuage subnet %s' % nuage_vm_subnet)
                return 1
            logging.info('Nuage subnet %s found' % nuage_vm_subnet)
        elif not vm_is_l2domain:
            clear()
            print('VM: %s' % vcenter_vm.name)
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
            while vm_subnet is None:
                choice = raw_input('Please enter the number of the subnet [1-%s]: ' % len(all_subnet))
                choice = int(choice)
                if choice > 0 and choice - 1 < len(all_subnet):
                    vm_subnet = all_subnet[choice - 1]
                    break
                print('Invalid choice, please try again')

        # Verifying the IP or asking for it
        if nuage_vm_ip:
            logging.debug('Verifying if IP %s is inside Nuage subnet %s range' % (nuage_vm_ip, vm_subnet.name))
            if not ipaddress.ip_address(nuage_vm_ip) in ipaddress.ip_network('%s/%s' % (vm_subnet.address, vm_subnet.netmask)):
                logging.error('IP %s is not part of subnet %s with netmask %s' % (nuage_vm_ip, vm_subnet.address, vm_subnet.netmask))
                return 1
            vm_ip = nuage_vm_ip
        else:
            clear()
            print('VM: %s' % vcenter_vm.name)
            print('Enterprise: %s' % vm_enterprise.name)
            print('User: %s' % vm_user.user_name)
            if not vm_is_l2domain:
                print('Domain: %s' % vm_domain.name)
                print('Zone: %s' % vm_zone.name)
                print('Subnet: %s - %s/%s' % (vm_subnet.name, vm_subnet.address, vm_subnet.netmask))
            else:
                print('Domain: %s - %s/%s' % (vm_domain.name, vm_domain.address, vm_domain.netmask))
            print(80 * '-')
            print('If you want a static IP, please enter it. Or press enter for a DHCP assigned IP.')
            while vm_ip is None:
                choice = raw_input('Please enter the IP or press enter for a DHCP assigned IP: ')
                if not choice or ipaddress.ip_address(choice) in ipaddress.ip_network('%s/%s' % (vm_subnet.address, vm_subnet.netmask)):
                    vm_ip = choice
                    break
                print('Invalid choice, please try again')

        # Verifying the Nuage policy group existence or selecting it
        if nuage_vm_policy_group:
            logging.debug('Finding Nuage policy group %s' % nuage_vm_policy_group)
            vm_policy_group = vm_domain.policy_groups.get_first(filter="name == '%s'" % nuage_vm_policy_group)
            if vm_policy_group is None:
                logging.error('Unable to find Nuage policy group {0:s}'.format(nuage_vm_policy_group))
                return 1
            logging.info('Nuage policy group %s found' % nuage_vm_policy_group)
        else:
            clear()
            print('VM: %s' % vcenter_vm.name)
            print('Enterprise: %s' % vm_enterprise.name)
            print('User: %s' % vm_user.user_name)
            if not vm_is_l2domain:
                print('Domain: %s' % vm_domain.name)
                print('Zone: %s' % vm_zone.name)
                print('Subnet: %s - %s/%s' % (vm_subnet.name, vm_subnet.address, vm_subnet.netmask))
            else:
                print('Domain: %s - %s/%s' % (vm_domain.name, vm_domain.address, vm_domain.netmask))
            if vm_ip:
                print('IP: {0:s}'.format(vm_ip))
            print(80 * '-')
            print('Please select your policy group:')
            index = 0
            all_pg = vm_domain.policy_groups.get()
            print('0. None')
            for cur_pg in all_pg:
                print('%s. %s' % (index + 1, cur_pg.name))
                index += 1
            while vm_policy_group is None:
                choice = raw_input('Please enter the number of the policy group [0-%s]: ' % len(all_pg))
                choice = int(choice)
                if choice == 0:
                    vm_policy_group = None
                    break
                elif choice > 0 and choice - 1 < len(all_pg):
                    vm_policy_group = all_pg[choice - 1]
                    break
                print('Invalid choice, please try again')

        # Verifying the Nuage redirection target existence or selecting it
        if nuage_vm_redirection_target:
            logging.debug('Finding Nuage redirection target %s' % nuage_vm_redirection_target)
            vm_redirection_target = vm_domain.redirection_targets.get_first(filter="name == '%s'" % nuage_vm_redirection_target)
            if vm_redirection_target is None:
                logging.error('Unable to find Nuage redirection target {0:s}'.format(nuage_vm_redirection_target))
                return 1
            logging.info('Nuage redirection target %s found' % nuage_vm_redirection_target)
        else:
            clear()
            print('VM: %s' % vcenter_vm.name)
            print('Enterprise: %s' % vm_enterprise.name)
            print('User: %s' % vm_user.user_name)
            if not vm_is_l2domain:
                print('Domain: %s' % vm_domain.name)
                print('Zone: %s' % vm_zone.name)
                print('Subnet: %s - %s/%s' % (vm_subnet.name, vm_subnet.address, vm_subnet.netmask))
            else:
                print('Domain: %s - %s/%s' % (vm_domain.name, vm_domain.address, vm_domain.netmask))
            if vm_ip:
                print('IP: {0:s}'.format(vm_ip))
            if vm_policy_group:
                print('Policy group: {0:s}'.format(vm_policy_group.name))
            print(80 * '-')
            print('Please select your redirection target:')
            index = 0
            all_rt = vm_domain.redirection_targets.get()
            print('0. None')
            for cur_rt in all_rt:
                print('%s. %s' % (index + 1, cur_rt.name))
                index += 1
            while vm_redirection_target is None:
                choice = raw_input('Please enter the number of the redirection target [0-%s]: ' % len(all_rt))
                choice = int(choice)
                if choice == 0:
                    vm_redirection_target = None
                    break
                elif choice > 0 and choice - 1 < len(all_rt):
                    vm_redirection_target = all_rt[choice - 1]
                    break
                print('Invalid choice, please try again')

        logging.info('Using following Nuage values:')
        logging.info('Enterprise: %s' % vm_enterprise.name)
        logging.info('User: %s' % vm_user.user_name)
        if not vm_is_l2domain:
            logging.info('Domain: %s' % vm_domain.name)
            logging.info('Zone: %s' % vm_zone.name)
            logging.info('Subnet: %s - %s/%s' % (vm_subnet.name, vm_subnet.address, vm_subnet.netmask))
        else:
            logging.info('Domain: %s - %s/%s' % (vm_domain.name, vm_domain.address, vm_domain.netmask))
        if vm_ip:
            logging.info('Static IP: %s' % vm_ip)
        if vm_policy_group:
            logging.info('Policy group: {0:s}'.format(vm_policy_group.name))
        if vm_redirection_target:
            logging.info('Redirection target: {0:s}'.format(vm_redirection_target.name))

        clear()

        if mode == 'metadata':
            print('Setting Nuage Metadata on VM')
            # Setting Nuage metadata
            logging.info('Setting Nuage Metadata')
            vm_option_values = []
            # Enterprise
            vm_option_values.append(vim.option.OptionValue(key='nuage.enterprise', value=vm_enterprise.name))
            if vm_is_l2domain:
                # L2 Domain
                vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.l2domain', value=vm_domain.name))
            else:
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
            # Policy group
            if vm_policy_group:
                vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.policy-group', value=vm_policy_group.name))
            # Redirection target
            if vm_redirection_target:
                vm_option_values.append(vim.option.OptionValue(key='nuage.nic0.redirection-target', value=vm_redirection_target.name))

            logging.debug('Creating of config spec for VM')
            config_spec = vim.vm.ConfigSpec(extraConfig=vm_option_values)
            logging.info('Applying advanced parameters. This might take a couple of seconds')
            config_task = vcenter_vm.ReconfigVM_Task(spec=config_spec)
            logging.debug('Waiting for the advanced paramerter to be applied')
            run_loop = True
            while run_loop:
                info = config_task.info
                if info.state == vim.TaskInfo.State.success:
                    logging.debug('Advanced parameters applied')
                    run_loop = False
                    break
                elif info.state == vim.TaskInfo.State.error:
                    if info.error.fault:
                        logging.info('Applying advanced parameters has quit with error: %s' % info.error.fault.faultMessage)
                    else:
                        logging.info('Applying advanced parameters has quit with cancelation')
                    run_loop = False
                    break
                sleep(5)

        elif mode == 'split-activation':
            print('Creating vPort and VM in VSD for split activation')
            logging.debug('Starting split activation')

            # Getting VM UUID
            logging.debug('Getting VM UUID, MAC & IP')
            vcenter_vm_uuid = vcenter_vm.config.uuid
            logging.debug('Found UUID %s for VM %s' % (vcenter_vm_uuid, vcenter_vm.name))
            vcenter_vm_mac = None
            vcenter_vm_hw = vcenter_vm.config.hardware
            for dev in vcenter_vm_hw.device:
                if isinstance(dev, vim.vm.device.VirtualEthernetCard):
                    if dev.macAddress:
                        logging.debug('Found MAC {0:s} for VM {1:s}'.format(dev.macAddress, vcenter_vm.name))
                        vcenter_vm_mac = dev.macAddress
                        break

            if vcenter_vm_mac is None:
                logging.critical('Unable to find a valid mac address for VM')
                return 1

            # Creating vPort
            logging.debug('Creating vPort for VM %s' % vcenter_vm.name)
            nc_vport = vsdk.NUVPort(name='{0:s}-vport'.format(vcenter_vm.name), address_spoofing='INHERITED', type='VM',
                                    description='Automatically created, do not edit.')
            if vm_is_l2domain:
                vm_domain.create_child(nc_vport)
            else:
                vm_subnet.create_child(nc_vport)

            # Creating VM
            logging.debug('Creating a Nuage VM for VM %s' % vcenter_vm)
            nc_vm = vsdk.NUVM(name=vcenter_vm.name, uuid=vcenter_vm_uuid, interfaces=[{
                'name': vcenter_vm_mac,
                'VPortID': nc_vport.id,
                'MAC': vcenter_vm_mac
            }])
            nc.user.create_child(nc_vm)
            
        else:
            logging.critical('Invalid mode')
            return 1

    except vmodl.MethodFault, e:
        logging.critical('Caught vmodl fault: {0:s}'.format(e.msg))
        return 1
    except Exception, e:
        logging.critical('Caught exception: {0:s}'.format(str(e)))
        return 1

    print('Activation of VM finished')

# Start program
if __name__ == "__main__":
    main()
