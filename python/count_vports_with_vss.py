# -*- coding: utf-8 -*-
"""
Count the number of vPorts in domains that have VSS flow gathering enabled.

--- Author ---
Philippe Dellaert <philippe.dellaert@nokia.com>

--- Version history ---
2021-07-19 1.0 Initial version

--- Usage ---
run 'python count_vports_with_vss.py -h' for an overview
"""
from builtins import str
import argparse
import getpass
import logging
import json
from prettytable import PrettyTable
from vspk import v6 as vsdk


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(
        description="vm_delete is a tool to delete a VM that was created with split activation.")
    parser.add_argument('-d', '--debug', required=False,
                        help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-j', '--json', required=False,
                        help='Print as JSON, not as a table', dest='json_output', action='store_true')
    parser.add_argument('-l', '--log-file', required=False,
                        help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-E', '--nuage-enterprise', required=True,
                        help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('-H', '--nuage-host', required=True,
                        help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('-p', '--nuage-password', required=False,
                        help='The password with which to connect to the Nuage VSD/SDK host. If not specified, the user is prompted at runtime for a password', dest='nuage_password', type=str)
    parser.add_argument('-P', '--nuage-port', required=False,
                        help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('-U', '--nuage-user', required=True,
                        help='The username with which to connect to the Nuage VSD/SDK host', dest='nuage_username', type=str)
    parser.add_argument('-v', '--verbose', required=False,
                        help='Enable verbose output', dest='verbose', action='store_true')
    args = parser.parse_args()
    return args


def main():
    """
    Main function to handle statistics
    """

    # Handling arguments
    args = get_args()
    debug = args.debug
    json_output = args.json_output
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
    verbose = args.verbose

    # Logging settings
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(
        filename=log_file, format='%(asctime)s %(levelname)s %(message)s', level=log_level)
    logger = logging.getLogger(__name__)

    # Getting user password for Nuage connection
    if nuage_password is None:
        logger.debug(
            'No command line Nuage password received, requesting Nuage password from user')
        nuage_password = getpass.getpass(
            prompt='Enter password for Nuage host {0:s} for user {1:s}: '.format(nuage_host, nuage_username))

    try:
        # Connecting to Nuage
        logger.info('Connecting to Nuage server %s:%s with username %s' %
                    (nuage_host, nuage_port, nuage_username))
        nc = vsdk.NUVSDSession(username=nuage_username, password=nuage_password,
                               enterprise=nuage_enterprise, api_url="https://{0:s}:{1:d}".format(nuage_host, nuage_port))
        nc.start()

    except Exception as e:
        logger.error('Could not connect to Nuage host {0:s} with user {1:s} and specified password'.format(
            nuage_host, nuage_username))
        logger.critical('Caught exception: {0:s}'.format(str(e)))
        return 1

    if json_output:
        logger.debug('Setting up json output')
        json_object = []
    else:
        logger.debug('Setting up basic output table')
        pt = PrettyTable(['Enterprise', 'Domain', '# vPorts'])

    logger.debug('Fetching enterprises with flow collection enabled')
    for ent in nc.user.enterprises.get(filter='flowCollectionEnabled == "ENABLED"'):
        logger.debug('Handling enterprise: {0:s}'.format(ent.name))
        for dom in ent.domains.get(filter='flowCollectionEnabled == "INHERITED" OR flowCollectionEnabled == "ENABLED"'):
            logger.debug('Handling domain: {0:s}'.format(dom.name))
            _, _, vport_count = dom.vports.count()

            if json_output:
                json_dict = {
                    'Enterprise': ent.name,
                    'Domain': dom.name,
                    '# vPorts': vport_count
                }
                json_object.append(json_dict)
            else:
                logger.debug('Add row: {0:s}, {1:s}, {2:d}'.format(
                    ent.name, dom.name, vport_count))
                pt.add_row([ent.name, dom.name, vport_count])

    if json_output:
        print(json.dumps(json_object, sort_keys=True, indent=4))
    else:
        print(pt)

    return 0


# Start program
if __name__ == "__main__":
    main()
