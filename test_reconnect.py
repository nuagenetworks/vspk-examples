import sys
import logging

sys.path.append("./")

from vspk.vsdk.v3_2 import *
from vspk.vsdk.v3_2.utils import set_log_level
from time import sleep
from bambou.exceptions import BambouHTTPError

# 'Setting a log level to see what happens (Optionnal)'
set_log_level(logging.INFO)

# 'Create a session for CSPRoot'
session = NUVSDSession(username=u'csproot', password=u'csproot', enterprise=u'csp', api_url=u'https://135.227.222.88:8443')

# 'Start using the CSPRoot session
session.start()
csproot = session.user

sleep(700)

enterprise = NUEnterprise(id='b12f73fe-e9bb-4027-aa44-72e0da2d5e75')

try:
    enterprise.fetch()
except BambouHTTPError as error:
    print error.connection.response.errors
    print error.connection.response.data
