from builtins import range
import logging

from vspk import v6 as vsdk
from vspk.utils import set_log_level

set_log_level(logging.ERROR)

session = vsdk.NUVSDSession(username='csproot', password='csproot', enterprise='csp', api_url='https://localhost:8443')
session.start()
csproot = session.user


# Create a vCenter
vcenter = vsdk.NUVCenter(name='My vCenter')
csproot.create_child(vcenter)

# Create few data centers
for i in range(0, 2):
    datacenter = vsdk.NUVCenterDataCenter(name='DC %s' % i)

    # Create few clusters
    for cluster_index in range(0, 2):
        cluster = vsdk.NUVCenterCluster(name="Cluster %s" % cluster_index)
        datacenter.create_child(cluster)

        # Create an hypervisor
        hypervisor = vsdk.NUVCenterHypervisor(name='HypervisorTest', hypervisor_ip='2.1.1.1', hypervisor_user='test', hypervisor_password='test')
        hypervisor.mgmt_network_portgroup = 'HYP-MGMT-Network'
        hypervisor.multicast_source_portgroup = 'multicastsource'
        hypervisor.data_network_portgroup = 'to-the-SR'
        hypervisor.vm_network_portgroup = 'vm port group'

        cluster.create_child(hypervisor)
