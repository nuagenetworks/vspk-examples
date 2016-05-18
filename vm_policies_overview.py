# -*- coding: utf-8 -*-
"""
vm_policies_overview.py is a tool to display the policies that are applied
 to one or more VMs.

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

--- Version history ---
2016-05-18 - 0.1.0 - First beta
2016-05-18 - 0.2.0 - Fix unused variable
2016-05-18 - 0.3.0 - Check location and network type and if a fixer exists
2016-05-18 - 0.4.0 - Order of table fields fix
2016-05-18 - 0.5.0 - Fix for fetching data and log output
2016-05-18 - 0.5.5 - Fix for fetching fetcher

 --- Usage ---
run 'vm_policies_overview.py -h' for an overview
"""

import argparse
import getpass
import json
import logging
import requests

from prettytable import PrettyTable
from vspk import v4_0 as vsdk


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="Tool to gather statistics on domains, zones, subnets or vports within a certain time frame.")
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
    parser.add_argument('-V', '--vm', required=False, help='The VM for which to return the applied policies (can be specified multiple times for multiple VMs), if none is specified, information for all VMs will be returned', dest='vm_names', type=str, action='append')
    args = parser.parse_args()
    return args


def main():
    """
    Main function to gather the information on the VM applied policies
    """

    # Handling arguments
    args = get_args()
    configuration = {}
    configuration['debug'] = args.debug
    configuration['json_output'] = args.json_output
    configuration['log_file'] = None
    if args.logfile:
        configuration['log_file'] = args.logfile
    configuration['nuage_enterprise'] = args.nuage_enterprise
    configuration['nuage_host'] = args.nuage_host
    configuration['nuage_port'] = args.nuage_port
    configuration['nuage_password'] = None
    if args.nuage_password:
        configuration['nuage_password'] = args.nuage_password
    configuration['nuage_username'] = args.nuage_username
    configuration['nosslcheck'] = args.nosslcheck
    configuration['verbose'] = args.verbose
    configuration['vm_names'] = []
    if args.vm_names:
        configuration['vm_names'] = args.vm_names

    # Logging settings
    if configuration['debug']:
        log_level = logging.DEBUG
    elif configuration['verbose']:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(filename=configuration['log_file'], format='%(asctime)s %(levelname)s %(message)s', level=log_level)
    logger = logging.getLogger(__name__)

    # Disabling SSL verification if set
    if configuration['nosslcheck']:
        logger.debug('Disabling SSL certificate verification.')
        requests.packages.urllib3.disable_warnings()

    # Getting user password for Nuage connection
    if configuration['nuage_password'] is None:
        logger.debug('No command line Nuage password received, requesting Nuage password from user')
        configuration['nuage_password'] = getpass.getpass(prompt='Enter password for Nuage host %s for user %s: ' % (configuration['nuage_host'], configuration['nuage_username']))

    try:
        # Connecting to Nuage
        logger.debug('Connecting to Nuage server %s:%s with username %s' % (configuration['nuage_host'], configuration['nuage_port'], configuration['nuage_username']))
        nc = vsdk.NUVSDSession(username=configuration['nuage_username'], password=configuration['nuage_password'], enterprise=configuration['nuage_enterprise'], api_url="https://%s:%s" % (configuration['nuage_host'], configuration['nuage_port']))
        nc.start()

    except Exception, e:
        logger.error('Could not connect to Nuage host %s with user %s and specified password' % (configuration['nuage_host'], configuration['nuage_username']))
        logger.critical('Caught exception: %s' % str(e))
        return 1

    # Setting output correctly
    output_fields = [
        'VM Name',
        'Interface MAC',
        'ACL type',
        'Ether type',
        'Protocol',
        'Source type',
        'Source name',
        'Destination type',
        'Destination name',
        'Source port',
        'Destination port',
        'DSCP',
        'Stateful',
        'Action'
    ]

    # Gathering VMs
    vms = []
    if configuration['vm_names']:
        for vm_name in configuration['vm_names']:
            logger.debug('Getting VMs matching the name %s' % vm_name)
            entities = nc.user.vms.get(filter='name == "%s"' % vm_name)
            vms.extend(entities)
    else:
        logger.debug('Getting all VMs')
        vms = nc.user.vms.get()

    # Gathering VM Interfaces
    vm_interfaces = []
    logger.debug('Getting all VM interfaces for the selected VMs')
    for vm in vms:
        vm_interfaces.extend(vm.vm_interfaces.get())

    # Verifying if there are enities
    if len(vm_interfaces) == 0:
        logger.critical('No matching vms found')
        return 1

    # Starting output
    if configuration['json_output']:
        logger.debug('JSON output enabled, not setting up an output table')
        json_object = []
    else:
        logger.debug('Setting up output table')
        pt = PrettyTable(output_fields)

    # Gathering ACL rules and handling them
    for vm_interface in vm_interfaces:
        logger.debug('Gathering VM interface policy decisions')
        policy_decisions = vm_interface.policy_decisions.get_first()
        ingress_acl_entries = policy_decisions.ingress_acls[0]['entries']
        egress_acl_entries = policy_decisions.egress_acls[0]['entries']
        forward_acl_entries = policy_decisions.ingress_adv_fwd[0]['entries']
        logger.debug('Found %s ingress ACLs and %s egress ACLs' % (len(ingress_acl_entries), len(egress_acl_entries)))

        logger.debug('Handling Ingress ACL entries')
        for entry in ingress_acl_entries:
            acl_rule = None

            logger.debug('Using minimal information from the policy decision entry itself')
            output = {
                'VM Name': vm_interface.parent.name,
                'Interface MAC': vm_interface.mac,
                'ACL type': 'Ingress',
                'Ether type': entry['etherType'],
                'Protocol': entry['protocol'],
                'Source type': 'VM',
                'Source name': vm_interface.parent.name,
                'Destination type': entry['destinationType'],
                'Destination name': entry['destinationValue'],
                'Source port': entry['sourcePort'],
                'Destination port': entry['destinationPort'],
                'DSCP': entry['DSCP'],
                'Stateful': '',
                'Action': entry['actionDetails']['actionType']
            }

            if entry['aclTemplateEntryId']:
                logger.debug('Finding the actual Ingress ACL Template Entry to use its data')
                # We are using this approach with the Stats ID as the aclTemplateEntryId points to the stats ID of an Ingress/Egress ACL Entry Template in the current version (bug report generated)
                acl_rule = nc.user.ingress_acl_entry_templates.get_first(filter='statsID == "%s"' % entry['aclTemplateEntryId'])

            if acl_rule:
                logger.debug('Found a matching Ingress ACL Template Entry: %s' % acl_rule.description)
                output['Ether type'] = acl_rule.ether_type
                output['Protocol'] = acl_rule.protocol
                output['Source type'] = acl_rule.location_type
                if acl_rule.location_type and nc.user.fetcher_for_rest_name(acl_rule.location_type.lower()) is not None:
                    output['Source name'] = nc.user.fetcher_for_rest_name(acl_rule.location_type.lower()).get(filter='ID == "%s"' % acl_rule.location_id).name
                output['Destination type'] = acl_rule.network_type
                if acl_rule.network_type and nc.user.fetcher_for_rest_name(acl_rule.network_type.lower()) is not None:
                    output['Destination name'] = nc.user.fetcher_for_rest_name(acl_rule.network_type.lower()).get(filter='ID == "%s"' % acl_rule.network_id).name
                output['Source port'] = acl_rule.source_port
                output['Destination port'] = acl_rule.destination_port
                output['DSCP'] = acl_rule.dscp
                output['Stateful'] = acl_rule.stateful
                output['Action'] = acl_rule.action

            logger.debug('Saving output to output object')
            if configuration['json_output']:
                json_object.append(output)
            else:
                pt.add_row([
                    output['VM Name'],
                    output['Interface MAC'],
                    output['ACL type'],
                    output['Ether type'],
                    output['Protocol'],
                    output['Source type'],
                    output['Source name'],
                    output['Destination type'],
                    output['Destination name'],
                    output['Source port'],
                    output['Destination port'],
                    output['DSCP'],
                    output['Stateful'],
                    output['Action']
                ])

        logger.debug('Handling Egress ACL entries')
        for entry in egress_acl_entries:
            acl_rule = None

            logger.debug('Using minimal information from the policy decision entry itself')
            output = {
                'VM Name': vm_interface.parent.name,
                'Interface MAC': vm_interface.mac,
                'ACL type': 'Egress',
                'Ether type': entry['etherType'],
                'Protocol': entry['protocol'],
                'Source type': 'VM',
                'Source name': vm_interface.parent.name,
                'Destination type': entry['destinationType'],
                'Destination name': entry['destinationValue'],
                'Source port': entry['sourcePort'],
                'Destination port': entry['destinationPort'],
                'DSCP': entry['DSCP'],
                'Stateful': '',
                'Action': entry['actionDetails']['actionType']
            }

            if entry['aclTemplateEntryId']:
                logger.debug('Finding the actual Egress ACL Template Entry to use its data')
                # We are using this approach with the Stats ID as the aclTemplateEntryId points to the stats ID of an Ingress/Egress ACL Entry Template in the current version (bug report generated)
                acl_rule = nc.user.egress_acl_entry_templates.get_first(filter='statsID == "%s"' % entry['aclTemplateEntryId'])

            if acl_rule:
                logger.debug('Found a matching Egress ACL Template Entry: %s' % acl_rule.description)
                output['Ether type'] = acl_rule.ether_type
                output['Protocol'] = acl_rule.protocol
                output['Source type'] = acl_rule.location_type
                if acl_rule.location_type and nc.user.fetcher_for_rest_name(acl_rule.location_type.lower()) is not None:
                    output['Source name'] = nc.user.fetcher_for_rest_name(acl_rule.location_type.lower()).get(filter='ID == "%s"' % acl_rule.location_id).name
                output['Destination type'] = acl_rule.network_type
                if acl_rule.network_type and nc.user.fetcher_for_rest_name(acl_rule.network_type.lower()) is not None:
                    output['Destination name'] = nc.user.fetcher_for_rest_name(acl_rule.network_type.lower()).get(filter='ID == "%s"' % acl_rule.network_id).name
                output['Source port'] = acl_rule.source_port
                output['Destination port'] = acl_rule.destination_port
                output['DSCP'] = acl_rule.dscp
                output['Stateful'] = acl_rule.stateful
                output['Action'] = acl_rule.action

            logger.debug('Saving output to output object')
            if configuration['json_output']:
                json_object.append(output)
            else:
                pt.add_row([
                    output['VM Name'],
                    output['Interface MAC'],
                    output['ACL type'],
                    output['Ether type'],
                    output['Protocol'],
                    output['Source type'],
                    output['Source name'],
                    output['Destination type'],
                    output['Destination name'],
                    output['Source port'],
                    output['Destination port'],
                    output['DSCP'],
                    output['Stateful'],
                    output['Action']
                ])

        logger.debug('Handling Redirect policies entries')
        for entry in forward_acl_entries:
            acl_rule = None

            logger.debug('Using minimal information from the policy decision entry itself')
            output = {
                'VM Name': vm_interface.parent.name,
                'Interface MAC': vm_interface.mac,
                'ACL type': 'Forward',
                'Ether type': entry['etherType'],
                'Protocol': entry['protocol'],
                'Source type': 'VM',
                'Source name': vm_interface.parent.name,
                'Destination type': entry['destinationType'],
                'Destination name': entry['destinationValue'],
                'Source port': entry['sourcePort'],
                'Destination port': entry['destinationPort'],
                'DSCP': entry['DSCP'],
                'Stateful': '',
                'Action': entry['actionDetails']['actionType']
            }

            if entry['ingressAdvFwdTemplateEntryId']:
                logger.debug('Finding the actual Ingress Advanced ACL Template Entry to use its data')
                # We are using this approach with the Stats ID as the ingressAdvFwdTemplateEntryId points to the stats ID of an Ingress/Egress ACL Entry Template in the current version (bug report generated)
                acl_rule = nc.user.ingress_adv_fwd_entry_templates.get_first(filter='statsID == "%s"' % entry['ingressAdvFwdTemplateEntryId'])

            if acl_rule:
                logger.debug('Found a matching Ingress Advanced ACL Template Entry: %s' % acl_rule.description)
                output['Ether type'] = acl_rule.ether_type
                output['Protocol'] = acl_rule.protocol
                output['Source type'] = acl_rule.location_type
                if acl_rule.location_type and nc.user.fetcher_for_rest_name(acl_rule.location_type.lower()) is not None:
                    output['Source name'] = nc.user.fetcher_for_rest_name(acl_rule.location_type.lower()).get(filter='ID == "%s"' % acl_rule.location_id).name
                output['Destination type'] = acl_rule.network_type
                if acl_rule.network_type and nc.user.fetcher_for_rest_name(acl_rule.network_type.lower()) is not None:
                    output['Destination name'] = nc.user.fetcher_for_rest_name(acl_rule.network_type.lower()).get(filter='ID == "%s"' % acl_rule.network_id).name
                output['Source port'] = acl_rule.source_port
                output['Destination port'] = acl_rule.destination_port
                output['DSCP'] = acl_rule.dscp
                output['Action'] = acl_rule.action

            logger.debug('Saving output to output object')
            if configuration['json_output']:
                json_object.append(output)
            else:
                pt.add_row([
                    output['VM Name'],
                    output['Interface MAC'],
                    output['ACL type'],
                    output['Ether type'],
                    output['Protocol'],
                    output['Source type'],
                    output['Source name'],
                    output['Destination type'],
                    output['Destination name'],
                    output['Source port'],
                    output['Destination port'],
                    output['DSCP'],
                    output['Stateful'],
                    output['Action']
                ])

    logger.debug('Printing output')
    if configuration['json_output']:
        print json.dumps(json_object, sort_keys=True, indent=4)
    else:
        print pt.get_string()

    return 0


# Start program
if __name__ == "__main__":
    main()
