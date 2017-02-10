from vspk.v4_0 import *
import logging
import argparse
import re

replace_fields = ["network_uplink_interface", "multicast_receive_interface", "multicast_send_interface"]
interface_replacements = {"eth0": "ens160", "eth1": "ens192", "eth2": "ens224", "eth3": "ens256"}

def replace_interfaces(logger, entity):
    """ Replaces the old interface names from the Ubuntu image with the new versions of the CentOS interfaces """
    entity_changed = False
    for field in replace_fields:
        logger.debug("Checking field %s for entitiy %s" % (field, entity.name))
        if getattr(entity, field):
            orig_content = getattr(entity, field)
            logger.debug("Found value %s for field %s for entity %s" % (orig_content, field, entity.name))
            pattern = re.compile('|'.join(interface_replacements.keys()))
            new_content = pattern.sub(lambda x: interface_replacements[x.group()], orig_content)
            if orig_content != new_content:
                logger.info("Replacing entity %s field %s content %s with new content %s" % (entity.name, field, orig_content, new_content))
                setattr(entity, field, new_content)
                entity_changed = True

    if entity_changed:
        logger.info("Saving entity %s" % entity.name)
        entity.save()

def get_args():
    """ Function to get command line arguments to run the script """
    parser = argparse.ArgumentParser(description="To change incorrect interface name")
    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug', action='store_true')
    parser.add_argument('-I', '--ip', nargs=1, required=True, help='VCIN IP', dest='ip', type=str, default=[1])
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', action='store_true')
    args = parser.parse_args()
    return args

def main():
    args = get_args()
    ip = args.ip[0]
    debug = args.debug
    verbose = args.verbose

    # Logging settings
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=log_level)
    logger = logging.getLogger(__name__)
    
    nc = None

    # Connecting to Nuage
    try:
        logger.info('Connecting to Nuage server %s as csproot' % ip)
        nc = NUVSDSession(username=u'csproot', password=u'csproot', enterprise=u'csp', api_url=u'https://%s:8443' % ip)
        nc.start()
    except IOError, e:
        pass

    if not nc or not nc.is_current_session():
        logger.error('Could not connect to Nuage host %s with user csproot' % ip)
        return 1

    logger.info('Connected to Nuage')

    for vcenter in nc.user.vcenters.get():
        logger.info("Checking values on vCenter %s" % vcenter.name)
        replace_interfaces(logger, vcenter)

        for datacenter in vcenter.vcenter_data_centers.get():
            logger.info("Checking values on datacenter %s" % datacenter.name)
            replace_interfaces(logger, datacenter)

            for hypervisor in datacenter.vcenter_hypervisors.get():
                logger.info("Checking values for standalone hypervisor %s" % hypervisor.name)
                replace_interfaces(logger, hypervisor)

            for cluster in datacenter.vcenter_clusters.get():
                logger.info("Checking values for cluster %s" % cluster.name)
                replace_interfaces(logger, cluster)

                for hypervisor in cluster.vcenter_hypervisors.get():
                    logger.info("Checking values for hypervisor %s" % hypervisor.name)
                    replace_interfaces(logger, hypervisor)

    return 0


if __name__ == "__main__":
    main()

