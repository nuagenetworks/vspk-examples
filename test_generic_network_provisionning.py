from vspk.vsdk import v3_2 as vsdk
import ipaddress

def populate_test_domain(domain, number_of_zones, number_of_subnets_per_zone, number_of_vports_per_subnet):
    """ Populate a domain with test data

        Args:
            domain (vsdk.NUDomain | vsdk.NUDomainTemplate): base domain to populate
            number_of_zones (int): number of desired zones
            number_of_subnets_per_zone (int): number of desired subnets per zone
            number_of_vports_per_subnet (int): number of desired vports per subnet (only available if domain is not a template)
    """

    # check if the domain is a template
    # if so use children template classes instead of instances
    is_template = domain.is_template()
    zone_class = vsdk.NUZoneTemplate if is_template else vsdk.NUZone
    subnet_class = vsdk.NUSubnetTemplate if is_template else vsdk.NUSubnet

    # generate a network and subnets
    network = ipaddress.ip_network(u'10.0.0.0/8')
    subnets = network.subnets(new_prefix=24)

    # create zones
    for i in range(0, number_of_zones):

        zone = zone_class(name="Zone %d" % i)
        domain.create_child(zone)
        domain.add_child(zone)

        #creates subnets
        for j in range(0, number_of_subnets_per_zone):

            # pull a subnet and get information about it
            subnetwork = subnets.next()
            ip = "%s" % subnetwork.network_address
            gw = "%s" % subnetwork.hosts().next()
            nm = "%s" % subnetwork.netmask

            subnet = subnet_class(name="Subnet %d %d" % (i, j), address=ip, netmask=nm, gateway=gw)
            zone.create_child(subnet)
            zone.add_child(subnet)

            # if the given domain is a template, we stop
            if is_template:
                break

            # Otherwise we create the VPorts
            for k in range(0, number_of_vports_per_subnet):

                vport = vsdk.NUVPort(name="VPort %d-%d-%d" % (i, j, k), type="VM", address_spoofing="INHERITED", multicast="INHERITED")
                subnet.create_child(vport)
                subnet.add_child(vport)


if __name__ == "__main__":

    session = vsdk.NUVSDSession(username='csproot', password='csproot', enterprise='csp', api_url='https://135.227.222.46:8443')
    session.start()

    # get a domain
    domain = vsdk.NUDomain(id="97c9ffac-c007-4cef-bb38-69aa91f7c258")
    domain.fetch()

    # do the job
    populate_test_domain(domain, 3, 4, 5)

    from time import sleep
    print "Sleeping..."
    sleep(6)
    for zone in domain.zones:
        zone.delete()