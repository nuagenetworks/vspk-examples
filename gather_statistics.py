# -*- coding: utf-8 -*-
"""
gather_statistics.py will gather statistics on one ore more Domains, L2 Domains, Zones, Subnets or VMs (all vm-interfaces) for a given timeframe. If the entity has a statistics_policy defined, it will use that policies statistics granularity to calculate the amount of data points. Otherwise it will use a default of 1 datapoint per minute.

The user can specify which statistics to gather, if none are specified, all of them will be gathered. Data can be presented as a table, or as JSON.

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

--- Version history ---
2016-01-26 - 1.0

--- Usage ---
run 'python gather_statistics.py -h' for an overview

--- Documentation ---
http://github.com/nuagenetworks/vspk-examples/blob/master/docs/gather_statistics.md

--- Examples ---
---- Gather all statistics for the last 10 minutes on all domains with json output ----
python gather_statistics.py -e DOMAIN -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -t 600 -j

---- Gather all statistics for the last hour (default) on one L2 domain with tabled output ----
python gather_statistics.py -e L2DOMAIN -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -n "L2 Domain Test"

---- Gather INGRESS_BYTE_COUNT and EGRESS_BYTE_COUNT for the last 120 seconds on all the Zones with json output ----
python gather_statistics.py -e ZONE -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -s INGRESS_BYTE_COUNT -s EGRESS_BYTE_COUNT -j -t 120

---- Gather PACKETS_IN statistics for the last day on all SUBNETS with json output ----
python gather_statistics.py -e SUBNET -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -t 1d -j -s PACKETS_IN

---- Gather BYTES_IN and BYTES_OUT statistics for the last hour on all VMs with tabled output ----
python gather_statistics.py -e VM -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -s BYTES_IN -s BYTES_OUT
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

try:
    from vspk import v3_2 as vsdk
except ImportError:
    from vspk.vsdk import v3_2 as vsdk

statistics_valid_types = [
    'BYTES_IN',
    'BYTES_OUT',
    'EGRESS_BYTE_COUNT',
    'EGRESS_PACKET_COUNT',
    'INGRESS_BYTE_COUNT',
    'INGRESS_PACKET_COUNT',
    'PACKETS_DROPPED_BY_RATE_LIMIT',
    'PACKETS_IN',
    'PACKETS_IN_DROPPED',
    'PACKETS_IN_ERROR',
    'PACKETS_OUT',
    'PACKETS_OUT_DROPPED',
    'PACKETS_OUT_ERROR'
]

entity_valid_types = [
    'DOMAIN',
    'L2DOMAIN',
    'ZONE',
    'SUBNET',
    'VM'
]


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="Tool to gather statistics on domains, zones, subnets or vports within a certain time frame.")
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-e', '--entity-type', required=True, help='The type of entity to gather the statistics for, can be DOMAIN, ZONE, SUBNET or VM.', dest='entity_type', type=str, choices=entity_valid_types)
    parser.add_argument('-j', '--json', required=False, help='Print as JSON, not as a table', dest='json_output', action='store_true')
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-n', '--entity-name', required=False, help='Entity name to provide statistics for. If not specified all entities of the entiy-type will be used', dest='entity_name', type=str)
    parser.add_argument('-E', '--nuage-enterprise', required=True, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('-H', '--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('-P', '--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('-p', '--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('-u', '--nuage-user', required=True, help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('-s', '--statistic-type', required=False, help='The type of statistics to gather. If not specified, all are used. Can be specified multiple times. Possible values are: BYTES_IN, BYTES_OUT, EGRESS_BYTE_COUNT, EGRESS_PACKET_COUNT, INGRESS_BYTE_COUNT, INGRESS_PACKET_COUNT, PACKETS_DROPPED_BY_RATE_LIMIT, PACKETS_IN, PACKETS_IN_DROPPED, PACKETS_IN_ERROR, PACKETS_OUT, PACKETS_OUT_DROPPED, PACKETS_OUT_ERROR', dest='statistic_types', type=str, choices=statistics_valid_types, action='append')
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect', dest='nosslcheck', action='store_true')
    parser.add_argument('-t', '--time', required=False, help='Indication of how far back in the past the statistics should go. Can be set in seconds, minutes (add m), hours (add h) or days (add d) (examples: 60, 60m, 60h or 60d, default is 3600 seconds)', dest='time_difference', type=str, default='3600')
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', action='store_true')
    args = parser.parse_args()
    return args


def main():
    """
    Main function to handle statistics
    """

    # Handling arguments
    args                = get_args()
    debug               = args.debug
    entity_type         = args.entity_type
    json_output         = args.json_output
    log_file            = None
    if args.logfile:
        log_file        = args.logfile
    entity_name         = None
    if args.entity_name:
        entity_name     = args.entity_name
    nuage_enterprise    = args.nuage_enterprise
    nuage_host          = args.nuage_host
    nuage_port          = args.nuage_port
    nuage_password      = None
    if args.nuage_password:
        nuage_password  = args.nuage_password
    nuage_username      = args.nuage_username
    statistic_types     = statistics_valid_types
    if args.statistic_types:
        statistic_types = args.statistic_types
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

    # Getting entities & defining output fields
    output_type = None
    entities = []
    output_type = entity_type.capitalize()
    search_query = 'name == "%s"' % entity_name if entity_name else None
    logger.debug('Getting %ss matching the search' % output_type)
    entities = nc.user.fetcher_for_rest_name(entity_type.lower()).get(filter=search_query)

    if entity_type == 'VM' and entities:
        vms = entities
        entities = []
        for vm in vms:
            for vm_interface in vm.vm_interfaces.get():
                entities.append(vm_interface)

    # Filling output fields
    output_fields = [
        output_type,
        'Start timestamp',
        'End timestamp',
        'Start date/time',
        'End date/time',
        '# datapoints'
    ]
    output_fields.extend(statistic_types)

    # Verifying if there are enities
    if len(entities) == 0:
        logger.critical('No matching entities found of type %s' % entity_type)
        return 1

    # Starting output
    if json_output:
        logger.debug('JSON output enabled, not setting up an output table')
        json_object = []
    else:
        logger.debug('Setting up output table')
        pt = PrettyTable(output_fields)

    # Setting general values
    stat_end_time = int(time.time())
    stat_start_time = int(stat_end_time - time_diff)
    stat_metric_types_str = ','.join(statistic_types)
    entity_data_freq = 60

    for entity in entities:
        if entity_type != 'VM' and 'BackHaul' in entity.name:
            logger.debug('Found a BackHaul %s, skipping' % output_type)
            continue

        # Getting stats collection frequency
        if entity_type != 'VM':
            logger.debug('Looking for a statistics policy on %s %s' % (output_type, entity.name))
            entity_stat_policies = entity.statistics_policies.get()
            if len(entity_stat_policies) > 0:
                logger.debug('Found at least one statistics policy on %s %s, getting data collection frequency' % (output_type, entity.name))
                entity_data_freq = entity_stat_policies[0].data_collection_frequency
            logger.debug('Data collection frequency for %s %s saved as %s' % (output_type, entity.name, entity_data_freq))

        num_data_points = int(time_diff / entity_data_freq)

        # Collecting statistics
        logger.debug('Collecting %s datapoints of statistics %s on %s %s from timestamp %s to timestamp %s' % (num_data_points, stat_metric_types_str, output_type, entity.name, stat_start_time, stat_end_time))
        stats_data = entity.statistics.get_first(query_parameters={
            'startTime': stat_start_time,
            'endTime': stat_end_time,
            'numberOfDataPoints': num_data_points,
            'metricTypes': stat_metric_types_str
        }).stats_data

        # Determining name
        output_name = entity.name
        if entity_type == "VM":
            output_name = '%s %s' % (entity.parent.name, entity.mac)

        # Generating output row
        if json_output:
            json_dict = {
                output_type: output_name,
                'Start timestamp': stat_start_time,
                'End timestamp': stat_end_time,
                'Start date/time': datetime.datetime.fromtimestamp(stat_start_time).strftime('%Y-%m-%d %H:%M:%S'),
                'End date/time': datetime.datetime.fromtimestamp(stat_end_time).strftime('%Y-%m-%d %H:%M:%S'),
                '# datapoints': num_data_points
            }
            json_dict.update(stats_data)
            json_object.append(json_dict)
        else:
            row = [
                output_name,
                stat_start_time,
                stat_end_time,
                datetime.datetime.fromtimestamp(stat_start_time).strftime('%Y-%m-%d %H:%M:%S'),
                datetime.datetime.fromtimestamp(stat_end_time).strftime('%Y-%m-%d %H:%M:%S'),
                num_data_points
            ]
            for statistic_type in statistic_types:
                row.append(stats_data[statistic_type])
            pt.add_row(row)

    logger.debug('Printing output')
    if json_output:
        print json.dumps(json_object, sort_keys=True, indent=4)
    else:
        print pt.get_string()

    return 0

# Start program
if __name__ == "__main__":
    main()
