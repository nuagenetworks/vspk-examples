# -*- coding: utf-8 -*-
"""
nuage_acl_learner is a tool which can be used in a clean test environment to create a set of ACL rules which are being used by the applications running in that environment. 

After you configured your VRS's to point their flow logs to the IP of the server where you run this tool, you can start it and it will start listening for TCP connections on port 514.

At the start, the tool will investigate the specified domain and will create a set of learning ACL rules (both ingress and egress). These rules will be used to enable logging for all traffic.

Once a flow log messages is sent to the tool from a VRS, the tool will investigate the flow and will implement a matching ACL rule entry. 

The ACL rule entry will be created using either Policy Groups, Zones or Subnets, depending on the type specified at runtime. If the destination of the traffic is outside of the domain, a network macro for the destination will be created and used in the rule.

The tool can either specify 'any' as source port, or, if specified at runtime, the tool will be very strict and create a rule with the source port set to the one used in the flow. In most cases this strict policy is a bit overkill: most client connections use a random port, using a strict policy for source port would block the next traffic attempt because it is a different source port.

The original idea came from Jeroen van Bemmel.

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

--- Version history ---
2016-01-22 - 1.0 - Only Ingress rules for now

--- VRS configuration ---
To configure your VRS, you have to edit the (r)syslog configuration to send everything matching 'ACLAUDIT' to the server running this tool on port 514 via a TCP connection. 

Example rsyslogd rule if the tool is running on 10.167.43.23:
    :msg,contains,"ACLAUDIT" @@10.167.43.23:514

--- Limitations ---
- When working with Policy Groups, it will only use one of the PG's for the rule
- If POLICYGROUP is specified as type, and a VM has no Policy Group assigned, no rule will be created
- Only creates ingress rules for now
- It does not use the commit/rollback system for ACLs as this is an automated tool. The rules impact traffic immediatly

--- Usage --- 
run 'python nuage_acl_learner.py -h' for an overview

--- Documentation ---
http://github.com/nuagenetworks/vspk-examples/blob/master/docs/nuage_acl_learner.md

--- Example ---
---- Set non-strict source port rules using Policy Groups ----
python nuage_acl_learner.py -d -D "Main Customer Domain" -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -t POLICYGROUP
"""

import argparse
import getpass
import logging
import os.path
import re
import requests
import string
import SocketServer
import time

try: 
    from vspk import v3_2 as vsdk
except ImportError:
    from vspk.vsdk import v3_2 as vsdk

# Global variables
nc = None
nc_enterprise = None
nc_domain = None
nc_subnetmap = {}
nc_policygroupmap = {}
nc_vportmap = {}
nc_networkmacromap = {}
ingress_learning_acl = None
egress_learning_acl = None
logger = None
configuration = {}
flows = {}
ip_regex = re.compile('.*dir: (\w+).*ipv4\(src=([\d\.]+)[^,]*,dst=([\d\.]+)[^,]*,proto=(\w+).*')
traffic_regex = re.compile('.*(tcp|udp)\(src=(\d+)[^,]*,dst=(\d+)[^\)]*\).*')

class ACLTCPHandler(SocketServer.StreamRequestHandler):
    """
    Will handle ACL log messages and create appropriate ACLs
    """

    def handle(self):
        global flows, nc_networkmacromap, configuration

        data = self.rfile.readline().strip()
        logger.debug('Received message from %s: %s' % (self.client_address[0], data))

        # Parsing message
        ip_matches = ip_regex.match(data)
        if ip_matches is None:
            logger.debug('No valid stream found')
            return 0
        
        flow_matches = traffic_regex.match(data)
        if flow_matches is None:
            logger.debug('No valid TCP/UDP stream found')
            return 0

        stream_type = flow_matches.group(1)
        stream_direction = ip_matches.group(1)
        stream_src_ip = ip_matches.group(2)
        stream_src_port = flow_matches.group(2)
        stream_dst_ip = ip_matches.group(3)
        stream_dst_port = flow_matches.group(3)
        stream_protocol = ip_matches.group(4)

        logger.debug('Found %s stream: direction %s - source ip %s - source port %s - destination ip %s - destination port %s - protocol %s' % (stream_type, stream_direction, stream_src_ip, stream_src_port, stream_dst_ip, stream_dst_port, stream_protocol))

        if configuration['strictsource']:
            flow_id = '%s_%s_%s_%s_%s' % (stream_type, stream_src_ip, stream_src_port, stream_dst_ip, stream_dst_port)
        else: 
            flow_id = '%s_%s_%s_%s' % (stream_type, stream_src_ip, stream_dst_ip, stream_dst_port)
            stream_src_port = '*'

        if flow_id in flows:
            logger.info('ACL already exists in the known flows, skipping handling it.')
            return 0

        src_vport = None
        dst_vport = None
        src_subnet = None
        dst_subnet = None
        src_pg = None
        dst_pg = None
        dst_nm = None
        if stream_src_ip in nc_vportmap:
            src_vport = nc_vportmap[stream_src_ip]
            logger.debug('Found source vPort for IP %s with MAC %s' % (stream_src_ip, src_vport['mac']))
            if configuration['acl_type'] == 'SUBNET' or configuration['acl_type'] == 'ZONE':
                src_subnet = nc_subnetmap[src_vport['subnet']]
                logger.debug('Found source subnet for IP %s: %s-%s' % (stream_src_ip, src_subnet['address'], src_subnet['netmask']))
            if configuration['acl_type'] == 'POLICYGROUP':
                if src_vport['policygroups'] > 0:
                    src_pg = src_vport['policygroups'][0]
                    logger.debug('Found source Policy Group %s for IP %s' % (src_pg['name'], stream_src_ip))
                else:
                    logger.error('Source vPort with IP %s does not have a Policy Group assigned, can not create ACL rules' % stream_src_ip)
                    return 1
        else: 
            logger.error('Unknown vPort for source IP %s, skipping this flow' % stream_src_ip)
            return 1

        if stream_dst_ip in nc_vportmap:
            dst_vport = nc_vportmap[stream_dst_ip]
            logger.debug('Found destination vPort for IP %s with MAC %s' % (stream_dst_ip, dst_vport['mac']))
            if configuration['acl_type'] == 'SUBNET' or configuration['acl_type'] == 'ZONE':
                dst_subnet = nc_subnetmap[dst_vport['subnet']]
                logger.debug('Found destination subnet for IP %s: %s-%s' % (stream_dst_ip, dst_subnet['address'], dst_subnet['netmask']))
            if configuration['acl_type'] == 'POLICYGROUP':
                if dst_vport['policygroups'] > 0:
                    dst_pg = dst_vport['policygroups'][0]
                    logger.debug('Found destination Policy Group %s for IP %s' % (dst_pg['name'], stream_dst_ip))
                else:
                    logger.error('Destination vPort with IP %s does not have a Policy Group assigned, can not create ACL rules' % stream_src_ip)
                    return 1
        elif '%s-255.255.255.255' % stream_dst_ip in nc_networkmacromap:
            logger.debug('vPort for destination IP %s does not exist, using existing /32 Network Macro' % stream_dst_ip)
            dst_nm = nc_networkmacromap['%s-255.255.255.255' % stream_dst_ip]
            logger.debug('Found destination network macro for IP %s' % stream_dst_ip)
        else:
            logger.debug('vPort or Network Macro for destination IP %s does not exist, creating a /32 Network Macro' % stream_dst_ip)
            temp_nm_name = string.replace('%s-255.255.255.255' % stream_dst_ip, '.','_')
            temp_nm = vsdk.NUEnterpriseNetwork(
                name=temp_nm_name,
                address=stream_dst_ip,
                netmask='255.255.255.255'
                )
            nc_enterprise.create_child(temp_nm)
            logger.info('Created new Network Macro for destination IP %s' % stream_dst_ip)
            dst_nm = {
            'id': temp_nm.id,
            'address': stream_dst_ip,
            'netmask': '255.255.255.255'
            }
            nc_networkmacromap['%s-255.255.255.255' % stream_dst_ip] = dst_nm

        src_type = None
        src_id = None
        if configuration['acl_type'] == 'ZONE':
            src_type = 'ZONE'
            src_id = src_subnet['zone']
        elif configuration['acl_type'] == 'SUBNET':
            src_type = 'SUBNET'
            src_id = src_subnet['id']
        elif configuration['acl_type'] == 'POLICYGROUP':
            src_type = 'POLICYGROUP'
            src_id = src_pg['id']

        dst_type = None
        dst_id = None
        if dst_vport is not None and configuration['acl_type'] == 'ZONE':
            dst_type = 'ZONE'
            dst_id = dst_subnet['zone']
        elif dst_vport is not None and configuration['acl_type'] == 'SUBNET':
            dst_type = 'SUBNET'
            dst_id = dst_subnet['id']
        elif dst_vport is not None and configuration['acl_type'] == 'POLICYGROUP':
            dst_type = 'POLICYGROUP'
            dst_id = dst_pg['id']
        else:
            dst_type = 'ENTERPRISE_NETWORK'
            dst_id = dst_nm['id']

        stream_protocol = '17'
        if stream_type == 'tcp':
            stream_protocol = '6'

        logger.debug('Creating new Ingress ACL rule with values: action FORWARD - ether_type 0x0800 - location_type %s - location_id %s - network_type %s - network_id %s - protocol %s - source_port %s - destination_port %s - dscp * - reflexive True - priority %s' % (src_type, src_id, dst_type, dst_id, stream_protocol, stream_src_port, stream_dst_port, configuration['next_priority']))

        ingress_acl_entry = vsdk.NUIngressACLEntryTemplate(
            action='FORWARD',
            description='Learned - %s %s:%s to %s:%s' % (stream_type, stream_src_ip, stream_src_port, stream_dst_ip, stream_dst_port),
            ether_type='0x0800',
            location_type=src_type,
            location_id=src_id,
            network_type=dst_type,
            network_id=dst_id,
            protocol=stream_protocol,
            source_port=stream_src_port,
            destination_port=stream_dst_port,
            dscp='*',
            reflexive=True,
            priority=configuration['next_priority']
            )

        # For now we work without jobs, way easier... 
        #job = vsdk.NUJob(command='BEGIN_POLICY_CHANGES')
        #wait_for_job(nc_domain, job)
        ingress_learning_acl.create_child(ingress_acl_entry, async=False)
        #job = vsdk.NUJob(command='APPLY_POLICY_CHANGES')
        #wait_for_job(nc_domain, job)

        flows[flow_id] = {
        'action': 'FORWARD',
        'description': 'Learned - %s %s:%s to %s:%s' % (stream_type, stream_src_ip, stream_src_port, stream_dst_ip, stream_dst_port),
        'ether_type': '0x0800',
        'location_type': src_type,
        'location_id': src_id,
        'network_type': dst_type,
        'network_id': dst_id,
        'protocol': stream_protocol,
        'source_port': stream_src_port,
        'destination_port': stream_dst_port,
        'dscp': '*',
        'reflexive': True,
        'priority': configuration['next_priority']
        }

        configuration['next_priority'] += 1
        return 0

def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="Tool which will create ACLs learned from flow logs from the VRS. It will actively listen to incomming syslog connections on port 514.")
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-f', '--first-priority', required=False, help='The priority of the first created rule (will be incremented for each next rule), default is 100', dest='first_priority', type=int, default=100)
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-D', '--nuage-domain', required=True, help='The domain to investigate and set ACLs on', dest='nuage_domain', type=str)
    parser.add_argument('-E', '--nuage-enterprise', required=True, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('-H', '--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('-P', '--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('-p', '--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('-u', '--nuage-user', required=True, help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect', dest='nosslcheck', action='store_true')
    parser.add_argument('-s', '--strict-source-ports', required=False, help='Use strict source ports, this will set the specific source port instead of the default * setting for Ingress rules.', dest='strictsource', action='store_true')
    parser.add_argument('-t', '--type', required=True, help='On what entity type should the ACLs be applied. Valid responses: POLICYGROUP, ZONE, SUBNET', dest='acl_type', type=str, choices=['POLICYGROUP','ZONE','SUBNET'])
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', action='store_true')
    args = parser.parse_args()
    return args

def wait_for_job(parent, job):
    logger.debug('Creating Job with command %s' % job.command)
    parent.create_child(job)
    while True:
        logger.debug('Fetching update on the job with command %s' % job.command)
        job.fetch()
        if job.status == 'SUCCESS':
            logger.debug('Job with command %s executed succesfully returning result %s' % (job.command, job.result))
            return job.result
        elif job.status != 'RUNNING':
            logger.error('Job with command %s failed, status is %s, returning False' % (job.command, job.status))
            return False
        time.sleep(1)

def main():
    """
    Main function to handle vcenter vm names and the mapping to a policy group
    """
    global logger, configuration, nc, nc_enterprise, nc_domain, nc_subnetmap, nc_policygroupmap, nc_vportmap, nc_networkmacromap, ingress_learning_acl, egress_learning_acl

    # Handling arguments
    args                = get_args()
    configuration['debug']               = args.debug
    configuration['next_priority']       = args.first_priority
    configuration['log_file']            = None
    if args.logfile:
        configuration['log_file']        = args.logfile
    configuration['nuage_domain']        = args.nuage_domain
    configuration['nuage_enterprise']    = args.nuage_enterprise
    configuration['nuage_host']          = args.nuage_host
    configuration['nuage_port']          = args.nuage_port
    configuration['nuage_password']      = None
    if args.nuage_password:
        configuration['nuage_password']  = args.nuage_password
    configuration['nuage_username']      = args.nuage_username
    configuration['strictsource']        = args.strictsource
    configuration['nosslcheck']          = args.nosslcheck
    configuration['acl_type']            = args.acl_type
    configuration['verbose']             = args.verbose

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
    ssl_context = None
    if configuration['nosslcheck']:
        logger.debug('Disabling SSL certificate verification.')
        requests.packages.urllib3.disable_warnings()

    # Getting user password for Nuage connection
    if configuration['nuage_password'] is None:
        logger.debug('No command line Nuage password received, requesting Nuage password from user')
        configuration['nuage_password'] = getpass.getpass(prompt='Enter password for Nuage host %s for user %s: ' % (configuration['nuage_host'], configuration['nuage_username']))

    try:
        # Connecting to Nuage 
        logger.info('Connecting to Nuage server %s:%s with username %s' % (configuration['nuage_host'], configuration['nuage_port'], configuration['nuage_username']))
        nc = vsdk.NUVSDSession(username=configuration['nuage_username'], password=configuration['nuage_password'], enterprise=configuration['nuage_enterprise'], api_url="https://%s:%s" % (configuration['nuage_host'], configuration['nuage_port']))
        nc.start()

    except Exception, e:
        logger.error('Could not connect to Nuage host %s with user %s and specified password' % (configuration['nuage_host'], configuration['nuage_username']))
        logger.critical('Caught exception: %s' % str(e))
        return 1

    # Finding domain
    logger.debug('Finding domain %s' % configuration['nuage_domain'])
    nc_domain = nc.user.domains.get_first(filter="name == '%s'" % configuration['nuage_domain'])
    if nc_domain is None:
        logger.critical('Unable to find domain %s, quiting' % configuration['nuage_domain'])
        return 1
    logger.info('Found domain %s' % nc_domain.name)

    # Getting enterprise
    logger.debug('Getting enterprise for domain %s' % nc_domain.name)
    nc_enterprise = vsdk.NUEnterprise(id=nc_domain.parent_id)
    nc_enterprise.fetch()

    if configuration['acl_type'] == 'SUBNET' or configuration['acl_type'] == 'ZONE':
        # Mapping subnets
        logger.debug('Mapping subnets for domain %s' % nc_domain.name)
        for nc_subnet in nc_domain.subnets.get():
            logger.debug('Found subnet with network %s/%s in domain %s' % (nc_subnet.address, nc_subnet.netmask, nc_domain.name))
            nc_subnetmap[nc_subnet.id] = {
            'id': nc_subnet.id,
            'address': nc_subnet.address,
            'netmask': nc_subnet.netmask,
            'zone': nc_subnet.parent_id
            }

    if configuration['acl_type'] == 'POLICYGROUP':
        # Mapping policy groups
        logger.debug('Mapping policy groups for domain %s' % nc_domain.name)
        for nc_policygroup in nc_domain.policy_groups.get():
            logger.debug('Found policy group %s in domain %s' % (nc_policygroup.name, nc_domain.name))
            nc_policygroupmap[nc_policygroup.id] = {
            'id': nc_policygroup.id,
            'name': nc_policygroup.name
            }

    # Mapping vPorts
    logger.debug('Mapping vPorts for domain %s' % nc_domain.name)
    for nc_vport in nc_domain.vports.get():
        logger.debug('Found vPort with IP %s and MAC %s in domain %s' % (nc_vport.vm_interfaces.get_first().ip_address, nc_vport.vm_interfaces.get_first().mac, nc_domain.name))
        nc_vportmap[nc_vport.vm_interfaces.get_first().ip_address] = {
        'id': nc_vport.id,
        'mac': nc_vport.vm_interfaces.get_first().mac,
        'subnet': nc_vport.parent_id,
        'policygroups': []
        }
        for nc_policygroup in nc_vport.policy_groups.get():
            logger.debug('Found policy group %s for vPort with %s and MAC %s in domain %s' % (nc_policygroup.name, nc_vport.vm_interfaces.get_first().ip_address, nc_vport.vm_interfaces.get_first().mac, nc_domain.name))
            nc_vportmap[nc_vport.vm_interfaces.get_first().ip_address]['policygroups'].append({
            'id': nc_policygroup.id,
            'name': nc_policygroup.name
            })

    # Mapping Network Macros
    logger.debug('Mapping Network Macros for enterprise %s' % nc_enterprise.name)
    for nc_networkmacro in nc_enterprise.enterprise_networks.get():
        logger.debug('Found Network Macro with IP %s and netmask %s for Enterprise %s' % (nc_networkmacro.address, nc_networkmacro.netmask, nc_enterprise.name))
        nc_networkmacromap['%s-%s' % (nc_networkmacro.address, nc_networkmacro.netmask)] = {
        'id': nc_networkmacro.id,
        'address': nc_networkmacro.address,
        'netmask': nc_networkmacro.netmask
        }

    # Checking if ACL logging rules are present
    ingress_learning_acl = nc_domain.ingress_acl_templates.get_first(filter="name == 'Ingress Learning ACLs'")
    egress_learning_acl = nc_domain.egress_acl_templates.get_first(filter="name == 'Egress Learning ACLs'")

    if ingress_learning_acl is None:
        logger.info('Creating Ingress Learning ACLs')
        #job = vsdk.NUJob(command='BEGIN_POLICY_CHANGES')
        #wait_for_job(nc_domain, job)
        ingress_learning_acl = vsdk.NUIngressACLTemplate(
            name='Ingress Learning ACLs',
            priority_type='NONE',
            priority=100,
            default_allow_non_ip=False,
            default_allow_ip=False,
            allow_l2_address_spoof=False,
            active=True
            )
        nc_domain.create_child(ingress_learning_acl, async=False)
        logger.debug('Creating Ingress ACL TCP rule')
        ingress_acl_entry_1 = vsdk.NUIngressACLEntryTemplate(
            action='FORWARD',
            description='Learning ACL for TCP traffic',
            ether_type='0x0800',
            flow_logging_enabled=True,
            location_type='ANY',
            network_type='ANY',
            priority=1000,
            protocol=6,
            reflexive=True,
            source_port='*',
            destination_port='*',
            dscp='*'
            )
        ingress_learning_acl.create_child(ingress_acl_entry_1, async=False)
        logger.debug('Creating Ingress ACL UDP rule')
        ingress_acl_entry_2 = vsdk.NUIngressACLEntryTemplate(
            action='FORWARD',
            description='Learning ACL for UDP traffic',
            ether_type='0x0800',
            flow_logging_enabled=True,
            location_type='ANY',
            network_type='ANY',
            priority=1001,
            protocol=17,
            reflexive=True,
            source_port='*',
            destination_port='*',
            dscp='*'
            )
        ingress_learning_acl.create_child(ingress_acl_entry_2, async=False)
        logger.debug('Creating Ingress ACL other rule')
        ingress_acl_entry_3 = vsdk.NUIngressACLEntryTemplate(
            action='FORWARD',
            description='Learning ACL for other traffic',
            ether_type='0x0800',
            flow_logging_enabled=True,
            location_type='ANY',
            network_type='ANY',
            priority=1002,
            protocol='ANY',
            source_port=None,
            destination_port=None,
            dscp='*'
            )
        ingress_learning_acl.create_child(ingress_acl_entry_3, async=False)
        #job = vsdk.NUJob(command='APPLY_POLICY_CHANGES')
        #wait_for_job(nc_domain, job)
        #ingress_learning_acl = nc_domain.ingress_acl_templates.get_first(filter="name == 'Ingress Learning ACLs'")
        logger.info('Ingress ACL rules created')

    if egress_learning_acl is None:
        logger.info('Creating Egress Learning ACLs')
        #job = vsdk.NUJob(command='BEGIN_POLICY_CHANGES')
        #wait_for_job(nc_domain, job)
        egress_learning_acl = vsdk.NUEgressACLTemplate(
            name='Egress Learning ACLs',
            priority_type='NONE',
            priority=100,
            default_allow_non_ip=False,
            default_allow_ip=False,
            default_install_acl_implicit_rules=True,
            active=True
            )
        nc_domain.create_child(egress_learning_acl, async=False)
        logger.debug('Creating Egress ACL TCP rule')
        egress_acl_entry_1 = vsdk.NUEgressACLEntryTemplate(
            action='FORWARD',
            description='ACL for TCP traffic',
            ether_type='0x0800',
            flow_logging_enabled=True,
            location_type='ANY',
            network_type='ANY',
            priority=1000,
            protocol=6,
            reflexive=True,
            source_port='*',
            destination_port='*',
            dscp='*'
            )
        egress_learning_acl.create_child(egress_acl_entry_1, async=False)
        logger.debug('Creating Egress ACL UDP rule')
        egress_acl_entry_2 = vsdk.NUEgressACLEntryTemplate(
            action='FORWARD',
            description='ACL for UDP traffic',
            ether_type='0x0800',
            flow_logging_enabled=True,
            location_type='ANY',
            network_type='ANY',
            priority=1001,
            protocol=17,
            reflexive=True,
            source_port='*',
            destination_port='*',
            dscp='*'
            )
        egress_learning_acl.create_child(egress_acl_entry_2, async=False)
        logger.debug('Creating Egress ACL other rule')
        egress_acl_entry_3 = vsdk.NUEgressACLEntryTemplate(
            action='FORWARD',
            description='ACL for other traffic',
            ether_type='0x0800',
            flow_logging_enabled=True,
            location_type='ANY',
            network_type='ANY',
            priority=1002,
            protocol='ANY',
            source_port=None,
            destination_port=None,
            dscp='*'
            )
        egress_learning_acl.create_child(egress_acl_entry_3, async=False)
        #job = vsdk.NUJob(command='APPLY_POLICY_CHANGES')
        #wait_for_job(nc_domain, job)
        #egress_learning_acl = nc_domain.egress_acl_templates.get_first(filter="name == 'Egress Learning ACLs'")
        logger.info('Egress ACL rules created')

    logger.info('Starting capture server on port 514')
    capture_server = SocketServer.TCPServer(('0.0.0.0', 514), ACLTCPHandler)

    try: 
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        capture_server.serve_forever()
    except KeyboardInterrupt:
        logger.info('Received interrupt, finishing up')
        capture_server.shutdown()

    logger.info('All done!')
    return 1

# Start program
if __name__ == "__main__":
    main()
