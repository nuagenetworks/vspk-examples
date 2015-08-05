import sys
import logging
import inspect

sys.path.append("./")

from vspk.vsdk.v3_2 import *
from vspk.vsdk.v3_2.utils import set_log_level

# 'Setting a log level to see what happens (Optionnal)'
set_log_level(logging.ERROR)

# 'Create a session for CSPRoot'
session = NUVSDSession(username=u'csproot', password=u'csproot', enterprise=u'csp', api_url=u'https://135.227.222.112:8443', version='3.2')

# 'Start using the CSPRoot session
session.start()
csproot = session.user

f = inspect.currentframe()


import inspect
import traceback
class Person(object):
    def speak(self):
        print traceback.format_list(traceback.extract_stack())
        return inspect.currentframe()

p = Person()
x = p.speak()
print x
