import sys
import logging

sys.path.append("./")

from vspk.vsdk.v3_2 import *
from vspk.vsdk.v3_2.utils import set_log_level

set_log_level(logging.ERROR)

session = NUVSDSession(username=u'csproot', password=u'csproot', enterprise=u'csp', api_url=u'https://135.227.222.46:8443')
session.start()
csproot = session.user

# Count will make a request to the backend to retrieve the number of enterprises
(_, _, nb_enterprises) = csproot.enterprises.count()
print 'Number of enterprises to retrieve = %s' % nb_enterprises

# Fetch will get all information of each enterprise from the server
csproot.enterprises.fetch()

for enterprise in csproot.enterprises:
    print enterprise.name
