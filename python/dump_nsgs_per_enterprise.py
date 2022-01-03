# Generates a CSV file listing NSGs per enterprise.
# Tested with python 3.6, vspk==20.10.6 and VSD 20.10.R1
# should work with other versions as well, but not tested

import argparse
import csv
import time
import logging

EXCEPTION_ENTERPRISES = [ "Audit Enterprise", "Shared Infrastructure" ]

try:
    # Importing Nuage SDK for Nuage R5.x. Adjust accordingly to your release
    from vspk import v6 as vsdk
    from vspk.utils import set_log_level
    # VSPK and Bambou log level
    set_log_level(logging.WARNING)

except ImportError:
    logging.error('Module \'vspk\' not foud. Install and try again.')
    logging.error('A \'pip install vspk\' should take care of it.')
    logging.error('For more information, check \'https://pypi.org/project/vspk/\' and '
        + '\'https://github.com/nuagenetworks/vspk-examples\'')
    logging.error('Make sure you install the proper version for your Nuage Release.')
    exit(-1)

def nuage_login(user='csproot', password='csproot', org='csp',vsdhost='vsd.mydomain.com:8443'):
    session = vsdk.NUVSDSession(
        username=user,
        password=password,
        enterprise=org,
        api_url="https://" + vsdhost
    )
    try:
        logging.info('Establishing session to VSD %s as User %s', vsdhost, user)
        session.start()
        logging.info('Logged to VSD successfully')
    except:
        logging.error('Failed to start a Session to VSD')
        exit(-1)
    return session.user

def get_nsg_data(nsg):
    nsgdata = dict()
    nsgdata['name'] = nsg.name
    nsgdata['uuid'] = nsg.id
    nsgdata['mac_address'] = nsg.mac_address
    nsgdata['system_id'] = nsg.system_id
    nsgdata['bootstrap_status'] = nsg.bootstrap_status
    nsgdata['family'] = nsg.family
    nsgdata['product_name'] = nsg.product_name
    nsgdata['operation_mode'] = nsg.operation_mode
    nsgdata['operation_status'] = nsg.operation_status
    nsgdata['nsg_version'] = nsg.nsg_version
    nsgdata['network_acceleration'] = nsg.network_acceleration
    nsgdata['tcpmss_enabled'] = nsg.tcpmss_enabled
    nsgdata['tcp_maximum_segment_size'] = nsg.tcp_maximum_segment_size
    nsgdata['tpm_status'] = nsg.tpm_status
    nsgdata['nsg_version'] = nsg.nsg_version
    nsgdata['ssh_service'] = nsg.ssh_service
    nsgdata['gateway_connected'] = nsg.gateway_connected
    nsgdata['redundancy_group_id'] = nsg.redundancy_group_id
    nsgdata['pending'] = nsg.pending
    nsgdata['serial_number'] = nsg.serial_number
    nsgdata['location_id'] = nsg.location_id
    nsgdata['configuration_reload_state'] = nsg.configuration_reload_state
    nsgdata['configuration_status'] = nsg.configuration_status
    nsgdata['personality'] = nsg.personality
    return nsgdata

def get_ent_nsgs(nusession):
    nsgsperenterprise = []

    logging.info('Getting list of Enterprises')
    enterprises = nusession.enterprises.get()
    for enterprise in enterprises:
        if enterprise.name not in EXCEPTION_ENTERPRISES:
            logging.info('Getting list of NSGs for Enterprise %s', enterprise.name)
            nsgs = enterprise.ns_gateways.get()
            for nsg in nsgs:
                if nsg.entity_scope == 'ENTERPRISE':
                    nsgdata = get_nsg_data(nsg)
                    nsgdata['enterprise'] = enterprise.name
                    nsgdata['enterprise_id'] = enterprise.id
                    nsgsperenterprise.append(nsgdata)
    return nsgsperenterprise

def get_csp_nsgs(nusession, nsglist):
    updated_nsg_list = nsglist
    logging.info('Getting the list of CSP NSGs')

    csp_nsgs = nusession.ns_gateways.get()

    for nsg in csp_nsgs:
        nsgdata = get_nsg_data(nsg)
        nsgdata['enterprise'] = 'CSP'
        nsgdata['enterprise_id'] = ''
        updated_nsg_list.append(nsgdata)
    return updated_nsg_list

def dumpascsv(objlist=None, filename='output.csv'):
    if objlist is None:
        logging.error('List of objects not provided. no CSV to generate')
        return
    logging.info('Opening file %s to write CSV file', filename)
    headers = objlist[0].keys()
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for line in objlist:
            writer.writerow(line)


def main(args):
    vsdhost = args.vsd + ":" + str(args.port)
    vsduser = args.user
    vsdpass = args.password
    vsdorg = args.org
    curr_time = time.time()
    curr_time = int(curr_time)
    outputfile = "nsg-list-per-enterprise-" + str(curr_time) + ".csv"

    nusession = nuage_login(user=vsduser, password=vsdpass, org=vsdorg, vsdhost=vsdhost)

    nsglist = get_ent_nsgs(nusession)
    nsglist = get_csp_nsgs(nusession, nsglist)

    dumpascsv(nsglist,outputfile)

if __name__ == '__main__':
    logging.basicConfig(level='INFO')

    # Parse CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("vsd", help="VSD IP or hostname. Eg: 192.168.1.1")
    parser.add_argument("-P", "--port", help="VSD Port. Defaults to 8443", 
                        type=int, default=8443)
    parser.add_argument("-u", "--user", type=str, default="csproot",
                        help="VSD User Name. Defaults to 'csproot'.")
    parser.add_argument("-p", "--password", type=str, default="csproot",
                        help="VSD User Password. Defaults to 'csproot'.")
    parser.add_argument("-o", "--org", type=str, default="csp",
                        help="VSD Organization. Defaults to 'csp'.")
    args = parser.parse_args()

    # Invoke main function
    main(args)
