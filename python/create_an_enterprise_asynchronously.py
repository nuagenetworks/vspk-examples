from __future__ import print_function
from builtins import str
import logging

from vspk import v6 as vsdk
from vspk.utils import set_log_level

set_log_level(logging.ERROR)

# Callback method
def my_callback(current_object, connection):
    """
    Your callback method
    """
    # Do whatever you need to do here...
    print(str(current_object))
    print(str(connection))

# Create a session for CSPRoot
session = vsdk.NUVSDSession(username='csproot', password='csproot', enterprise='csp', api_url='https://localhost:8443')
session.start()
csproot = session.user

# Create an enterprise asynchronously
enterprise = vsdk.NUEnterprise(name='Async Enterprise')
csproot.create_child(enterprise, as_async=True, callback=my_callback)
