# -*- coding: utf-8 -*-

import sys
import logging
from pprint import pprint

sys.path.append("./")

from vspk.vsdk.v3_2 import *
from vspk.vsdk.v3_2.utils import set_log_level

from bambou.exceptions import BambouHTTPError

# 'Setting a log level to see what happens (Optionnal)'
set_log_level(logging.INFO)

# 'Create a session for CSPRoot'
session = NUVSDSession(username=u'csproot', password=u'csproot', enterprise=u'csp', api_url=u'https://135.227.222.46:8443')

session.start()
csproot = session.user

cluster = NUVCenterCluster(id='3bcf5be7-dc95-4fe8-b03f-159993ddc407')

hyp = NUVCenterHypervisor(name='TestChris2', hypervisor_ip='2.1.1.1', hypervisor_user='test', hypervisor_password='test')
hyp.mgmt_network_portgroup = 'HYP-MGMT-Network'
hyp.multicast_source_portgroup = 'multicastsource'
hyp.data_network_portgroup = 'to-the-SR'
hyp.vm_network_portgroup = 'vm port group'

cluster.create_child(hyp)


# for i in range(0, 5):
#     datacenter = NUVCenterDataCenter(name='DC %s' % i)
#     vcenter.create_child(datacenter)
#
#     for j in range (0, 3):
#         cluster = NUVCenterCluster(name='Cluster %s' % j)
#         datacenter.create_child(cluster)

# datacenter = vcenter.vcenter_data_centers.get_first(filter='name == "demo"')
# datacenter.delete()

