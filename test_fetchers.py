import sys
import logging

sys.path.append("./")

from vspk.vsdk.v3_2 import *
from vspk.vsdk.v3_2.utils import set_log_level

# 'Setting a log level to see what happens (Optionnal)'
set_log_level(logging.ERROR)

# 'Create a session for CSPRoot'
session = NUVSDSession(username=u'csproot', password=u'csproot', enterprise=u'csp', api_url=u'https://135.227.222.46:8443')

# 'Start using the CSPRoot session
session.start()
csproot = session.user


(_, _, nb_enterprises) = csproot.enterprises.count()
print 'Number of enterprises to retrieve = %s' % nb_enterprises

csproot.enterprises.fetch()

# ent = csproot.enterprises[1]
# ent.name = u'TOTO'
# print csproot.enterprises.index(ent)

for enterprise in csproot.enterprises:
    print enterprise.name

# for enterprise in csproot.enterprises:
#     print enterprise.name
#
# csproot.enterprises.flush()
# print csproot.enterprises

# print '-----REFETCH'
# csproot.enterprises.fetch()
# for enterprise in csproot.enterprises:
#     print enterprise
#     print enterprise.name