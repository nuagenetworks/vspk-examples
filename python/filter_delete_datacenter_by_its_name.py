import sys
import logging
import inspect

sys.path.append("./")

from vspk.vsdk.v3_2 import *
from vspk.vsdk.v3_2.utils import set_log_level

set_log_level(logging.ERROR)

session = NUVSDSession(username=u'csproot', password=u'csproot', enterprise=u'csp', api_url=u'https://135.227.222.112:8443', version='3.2')
session.start()
csproot = session.user

vcenter = NUVCenter(id='c7a1a893-a3ad-4844-94a6-d89537f4cd3c')

# Get the first datacenter in vcenter which name is demo.
datacenter = vcenter.vcenter_data_centers.get_first(filter='name == "demo"')

# Delete the datacenter on the backend
datacenter.delete()
