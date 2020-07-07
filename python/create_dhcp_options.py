import logging

from vspk import v6 as vsdk
from vspk.utils import set_log_level

set_log_level(logging.ERROR)

session = vsdk.NUVSDSession(username='csproot', password='csproot', enterprise='csp', api_url='https://localhost:8443')
session.start()
csproot = session.user

# Get a subnet.
# Note: We don't need to fetch information to add a new child to this subnet
subnet = vsdk.NUSubnet(id='c7a1a893-a3ad-4844-94a6-d89537f4cd3c')

# Create a DHCP option for the given subnet
dhcp_option = vsdk.NUDHCPOption(actual_type=4, actual_values=['192.0.2.15', '198.51.100.12'])
subnet.create_child(dhcp_option)
