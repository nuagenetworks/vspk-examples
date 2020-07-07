from __future__ import print_function
from builtins import str
import argparse
import logging
import requests

from vspk import v6 as vspk

def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="Tool to list all orginization subnets assotiated to shared subnet together with absolute path in VSD.")
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-l', '--log-file', required=False, help='File to log to (default = stdout)', dest='logfile', type=str)
    parser.add_argument('-E', '--nuage-enterprise', required=False, help='The enterprise with which to connect to the Nuage VSD/SDK host', dest='nuage_enterprise', type=str)
    parser.add_argument('-H', '--nuage-host', required=True, help='The Nuage VSD/SDK endpoint to connect to', dest='nuage_host', type=str)
    parser.add_argument('-P', '--nuage-port', required=False, help='The Nuage VSD/SDK server port to connect to (default = 8443)', dest='nuage_port', type=int, default=8443)
    parser.add_argument('-p', '--nuage-password', required=False, help='The password with which to connect to the Nuage VSD/SDK host. If not specified, defualt will be used', dest='nuage_password', type=str)
    parser.add_argument('-u', '--nuage-user', required=False, help='The username with which to connect to the Nuage VSD/SDK host. If not specified, defualt will be used', dest='nuage_username', type=str)
    parser.add_argument('-S', '--disable-SSL-certificate-verification', required=False, help='Disable SSL certificate verification on connect (deprecated)', dest='nosslcheck', action='store_true')
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', action='store_true')
    args = parser.parse_args()
    return args

def get_vsd_objects(obj, _path=None):
    '''
    Function recursively search absolute path for VSD object up to the top level
    :param obj: VSD object for which full path is going to be searched
    :param _path: initial path list. should not be changed
    :return: list with full path
    '''
    if _path is None:
        _path = list()
    if obj is not None:
        if obj.parent_id is not None:
            _path.append(obj.name)
            parrent_obj = nuage_user.fetcher_for_rest_name(obj.parent_type).get_first(obj.parent_id)
            return get_vsd_objects(parrent_obj, _path)
        else:
            _path.append(obj.name)
    return list(reversed((_path[:])))

'''Main function'''
# Handling arguments
args             = get_args()
debug            = args.debug
if args.logfile:
    log_file     = args.logfile
else:
    log_file     = None
#nosslcheck       = args.nosslcheck
verbose          = args.verbose

# Logging settings
if debug:
    log_level = logging.DEBUG
elif verbose:
    log_level = logging.INFO
else:
    log_level = logging.WARNING
logging.basicConfig(filename=log_file, format='%(asctime)s %(levelname)s %(message)s', level=log_level)
logger = logging.getLogger(__name__)

# Getting username for Nuage connection
if args.nuage_username is None:
    logger.debug('No command line Nuage user received, default will be used.')
    nuage_username = 'csproot'
else:
    nuage_username = args.nuage_username

# Getting user password for Nuage connection
if args.nuage_password is None:
    logger.debug('No command line Nuage password received, default will be used.')
    nuage_password = 'csproot'
else:
    nuage_password = args.nuage_password

# Getting user enterprise for Nuage connection
if args.nuage_enterprise is None:
    logger.debug('No command line Nuage enterprise received, default will be used.')
    nuage_enterprise = 'csp'
else:
    nuage_enterprise = args.nuage_enterprise

# Getting host for Nuage connection
nuage_host          = args.nuage_host

# Getting host port for Nuage connection
if args.nuage_port is None:
    logger.debug('No command line Nuage host port received, default will be used.')
    nuage_port = 8443
else:
    nuage_port = args.nuage_port

try:
    logger.info('Connecting to Nuage server %s:%s with username %s' % (nuage_host, nuage_port, nuage_username))
    nc = vspk.NUVSDSession(username=nuage_username,
                           password=nuage_password,
                           enterprise=nuage_enterprise,
                           api_url="https://{0}:{1}".format(nuage_host,nuage_port))
    nc.start()
    nuage_user = nc.user
except Exceptione as e:
    logger.error(
        'Could not connect to Nuage host %s with user %s and specified password' % (nuage_host, nuage_username))
    logger.critical('Caught exception: %s' % str(e))
    exit()
# Main logic
for subnet in nuage_user.subnets.get():
    if subnet.associated_shared_network_resource_id is not None:
        shared_net_obj = vspk.NUSharedNetworkResource(id=subnet.associated_shared_network_resource_id).fetch()[0]
        print('#'*10+'\n"{0}" subnet is associated with shared network "{1}"'.format(subnet.name,
                                                                                     shared_net_obj.name))
        print("This is full path to this subnet:\n{0}".format(' -> '.join(get_vsd_objects(subnet))))
