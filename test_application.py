# -*- coding: utf-8 -*-

import sys
import logging

sys.path.append("./")

from vspk.vsdk.v3_2 import *
from vspk.vsdk.v3_2.utils import set_log_level

set_log_level(logging.INFO)

session = NUVSDSession(username=u'csproot', password=u'csproot', enterprise=u'csp', api_url=u'https://135.227.222.46:8443')

session.start()

# Fetch an enterprise
enterprise = NUEnterprise(id=u'd4ea408f-7253-4914-8b3a-36ebddc47bd8')
enterprise.fetch()

enterprise.domains.fetch()
domain = enterprise.domains[0]

app = NUApp(name='My App', associated_domain_id=domain.id, associated_domain_type="DOMAIN")
enterprise.create_child(app)