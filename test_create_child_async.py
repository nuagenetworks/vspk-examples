import sys
import logging

sys.path.append("./")

from vspk.vsdk.v3_2 import *
from vspk.vsdk.v3_2.utils import set_log_level

# Callback method
def mycallback(current_object, connection):
    print str(current_object)
    print str(connection)

# 'Setting a log level to see what happens (Optionnal)'
set_log_level(logging.ERROR)

# 'Create a session for CSPRoot'
session = NUVSDSession(username=u'csproot', password=u'csproot', enterprise=u'csp', api_url=u'https://135.227.222.46:8443')

# 'Start using the CSPRoot session
session.start()
csproot = session.user

enterprise = NUEnterprise(name=u"Async Enterprise")
csproot.create_child(enterprise, async=True, callback=mycallback)
