# -*- coding: utf-8 -*-

import sys
import logging

sys.path.append("./")

from vspk.vsdk.v3_2 import *
from vspk.vsdk.v3_2.utils import set_log_level

set_log_level(logging.INFO)

session = NUVSDSession(username=u'csproot', password=u'csproot', enterprise=u'csp', api_url=u'https://135.227.222.46:8443')
session.start()
csproot = session.user

# Create a vCenter
vcenter = NUVCenter(name='My vCenter')
csproot.create_child(vcenter)

# Create few data centers
for i in range(0, 2):
    datacenter = NUVCenterDataCenter(name='DC %s' % i)

    # Create few clusters
    for cluster_index in range(0, 2):
        cluster = NUVCenterCluster(name="Cluster %s" % cluster_index)
        datacenter.create_child(cluster)

        # Create an hypervisor
        hypervisor = NUVCenterHypervisor(name='HypervisorTest', hypervisor_ip='2.1.1.1', hypervisor_user='test', hypervisor_password='test')
        hypervisor.mgmt_network_portgroup = 'HYP-MGMT-Network'
        hypervisor.multicast_source_portgroup = 'multicastsource'
        hypervisor.data_network_portgroup = 'to-the-SR'
        hypervisor.vm_network_portgroup = 'vm port group'

        cluster.create_child(hyp)
