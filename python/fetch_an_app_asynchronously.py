import sys
import logging

sys.path.append("./")

from vspk.vsdk.v3_2 import *
from vspk.vsdk.v3_2.utils import set_log_level

set_log_level(logging.ERROR)


# Callback method
def mycallback(current_object, connection):
    print str(current_object)
    print str(connection)

session = NUVSDSession(username=u'csproot', password=u'csproot', enterprise=u'csp', api_url=u'https://135.227.222.46:8443')
session.start()
csproot = session.user

# Fetch app information asynchronously
my_app = NUApp(id='9cca1662-ed66-44d6-940c-7244ffc5dca9')
my_app.fetch(async=True, callback=mycallback)