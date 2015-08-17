import sys
import logging

sys.path.append("./")

from vspk.vsdk.v3_2 import *
from vspk.vsdk.v3_2.utils import set_log_level


session = NUVSDSession(username=u'csproot', password=u'csproot', enterprise=u'csp', api_url=u'https://135.227.222.46:8443')
session.start()
csproot = session.user

# Get a subnet.
# Note: We don't need to fetch information to add a new child to this subnet
subnet = NUSubnet(id="c7a1a893-a3ad-4844-94a6-d89537f4cd3c")

# Create a DHCP option for the given subnet
dhcp_option = NUDHCPOption(actual_type=4, actual_values=['130.20.30.1', '12.1.1.1'])
subnet.create_child(dhcp_option)
