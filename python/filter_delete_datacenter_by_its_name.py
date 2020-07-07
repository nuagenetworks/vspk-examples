import logging

from vspk import v6 as vsdk
from vspk.utils import set_log_level

set_log_level(logging.ERROR)

session = vsdk.NUVSDSession(username='csproot', password='csproot', enterprise='csp', api_url='https://localhost:8443')
session.start()
csproot = session.user

vcenter = vsdk.NUVCenter(id='c7a1a893-a3ad-4844-94a6-d89537f4cd3c')

# Get the first datacenter in vcenter which name is demo.
datacenter = vcenter.vcenter_data_centers.get_first(filter='name == "demo"')

# Delete the datacenter on the backend
datacenter.delete()
