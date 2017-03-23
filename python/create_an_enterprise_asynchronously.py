import sys
import logging

sys.path.append("./")

from vspk.vsdk.v3_2 import *
from vspk.vsdk.v3_2.utils import set_log_level

set_log_level(logging.ERROR)


# Callback method
def mycallback(current_object, connection):
    """ Your callback method

    """
    # Do whatever you need to do here...
    print str(current_object)
    print str(connection)


# Create a session for CSPRoot
session = NUVSDSession(username=u'csproot', password=u'csproot', enterprise=u'csp', api_url=u'https://135.227.222.46:8443')
session.start()
csproot = session.user

# Create an enterprise asynchronously
enterprise = NUEnterprise(name=u"Async Enterprise")
csproot.create_child(enterprise, async=True, callback=mycallback)
