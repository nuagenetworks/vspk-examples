# -*- coding: utf-8 -*-
"""
event_overview produces a table with information on the events for each enterprise the user has access to. Output can also be given in JSON format.

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

--- Version history ---
2016-01-26 - 1.0

--- Usage ---
run 'python event_overview.py -h' for an overview

--- Documentation ---
http://github.com/nuagenetworks/vspk-examples/blob/master/docs/events_overview.md

--- Example ---
---- Basic table output ----
python event_overview.py -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S

---- Extended table output ----
python event_overview.py -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -e

---- Basic JSON output ----
python event_overview.py -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -j

---- Extended JSON output ----
python event_overview.py -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -e -j

"""

import argparse
import datetime
import getpass
import json
import logging
import re
import requests
import time

from prettytable import PrettyTable
from vspk import v4_0 as vsdk


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="Tool to list all events on the enterpises to which the user has access to.")
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-e', '--extended', required=False, help='Enable extended output', dest='extended', action='store_true')
    parser.add_argument('-j', '--json', required=False, help='Print as JSON, not as a table', dest='json_output', action='store_true')
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-E', '--nuage-enterprise', required=True, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('-H', '--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('-P', '--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('-p', '--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('-u', '--nuage-user', required=True, help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect', dest='nosslcheck', action='store_true')
    parser.add_argument('-t', '--time', required=False, help='Indication of how far back in the past the events list should go. Can be set in seconds, minutes (add m), hours (add h) or days (add d) (examples: 60, 60m, 60h or 60d, default is 3600 seconds)', dest='time_difference', type=str, default='3600')
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
    extended            = args.extended
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
    time_difference     = args.time_difference
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

    # Validating time_difference input
    time_check = re.compile('^([0-9]+)([m|h|d]?)$')
    time_matches = time_check.match(time_difference)
    if time_matches is None:
        logger.critical('The time indication %s is an invalid value, exiting' % time_difference)
        return 1

    time_diff = int(float(time_matches.group(1)))
    if time_matches.group(2) == 'm':
        logger.debug('Found m in the time difference, multiplying integer by 60')
        time_diff *= 60
    elif time_matches.group(2) == 'h':
        logger.debug('Found h in the time difference, multiplying integer by 3600')
        time_diff *= 3600
    elif time_matches.group(2) == 'd':
        logger.debug('Found d in the time difference, multiplying integer by 86400')
        time_diff *= 86400

    logger.debug('Time difference set to %s seconds' % time_diff)

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
        logger.debug('JSON output enabled, not setting up an output table')
        json_object = []
    elif extended:
        logger.debug('Setting up extended output table')
        pt = PrettyTable(['Enterprise', 'Timestamp', 'Date/Time', 'Type', 'Entity', 'Entity parent', 'Extended info'])
    else:
        logger.debug('Setting up basic output table')
        pt = PrettyTable(['Enterprise', 'Timestamp', 'Date/Time', 'Type', 'Entity', 'Entity parent'])

    unix_check_time = time.time() - time_diff
    logger.debug('Gathering all events from after UNIX timestamp %s' % unix_check_time)

    for ent in nc.user.enterprises.get():
        logger.debug('Gathering events for enterprise %s' % ent.name)
        for event in ent.event_logs.get(filter="eventReceivedTime >= '%s'" % int(unix_check_time * 1000)):
            logger.debug('Found event of type %s with timestamp %s' % (event.type, event.event_received_time))
            clean_time = datetime.datetime.fromtimestamp(int(event.event_received_time / 1000)).strftime('%Y-%m-%d %H:%M:%S')

            if json_output:
                json_dict = {
                    'Enterprise': ent.name,
                    'Timestamp': event.event_received_time,
                    'Date/Time': clean_time,
                    'Type': event.type,
                    'Entity': event.entity_type,
                    'Entity parent': event.entity_parent_type
                }
                if extended:
                    json_dict['Extended info'] = event.entities
                json_object.append(json_dict)
            elif extended:
                pt.add_row([ent.name, event.event_received_time, clean_time, event.type, event.entity_type, event.entity_parent_type, json.dumps(event.entities)])
            else:
                pt.add_row([ent.name, event.event_received_time, clean_time, event.type, event.entity_type, event.entity_parent_type])

    logger.debug('Printing output')
    if json_output:
        print json.dumps(json_object, sort_keys=True, indent=4)
    else:
        print pt.get_string(sortby='Timestamp')

    return 0

# Start program
if __name__ == "__main__":
    main()
