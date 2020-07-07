from __future__ import print_function
import logging

from vspk import v6 as vsdk
from vspk.utils import set_log_level

set_log_level(logging.ERROR)

session = vsdk.NUVSDSession(username='csproot', password='csproot', enterprise='csp', api_url='https://localhost:8443')
session.start()
csproot = session.user

# Count will make a request to the backend to retrieve the number of enterprises
(_, _, nb_enterprises) = csproot.enterprises.count()
print('Number of enterprises to retrieve = %s' % nb_enterprises)

# Fetch will get all information of each enterprise from the server
csproot.enterprises.fetch()

for enterprise in csproot.enterprises:
    print(enterprise.name)
