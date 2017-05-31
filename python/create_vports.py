import timeit
import sys
from vspk import v5_0 as vsdk

vsd_url = 'http://localhost:8443'
vsd_user = 'csproot'
vsd_pass = 'csproot'
vsd_enterprise = 'csp'
subnet_id = 'fc595651-8bf8-4e2c-adcd-b9aad4557267'
is_l2domain = True
do_cleanup = True
amount = 0
requests = 0
number_vports = 1000

start_time = timeit.default_timer()
nc = vsdk.NUVSDSession(username='csproot', enterprise='csp', api_url='https://localhost:8443', password='csproot')
nc.start()
requests += 1

subnet = vsdk.NUL2Domain(id='fc595651-8bf8-4e2c-adcd-b9aad4557267')
subnet.fetch()
requests += 1

vports = []
print('Creating vPorts')
for i in range(number_vports):
    vport = vsdk.NUVPort(name='vPort-{0}'.format(i))
    subnet.create_child(vport)
    vports.append(vport)
    requests += 1
    sys.stdout.write('.')
    sys.stdout.flush()

if do_cleanup:
    print('\n\nRemoving vPorts')
    for vport in vports:
        vport.delete()
        requests += 1
        sys.stdout.write('.')
        sys.stdout.flush()

print('\n\nExecuted {0} requests'.format(requests))
elapsed = timeit.default_timer() - start_time
print('Elapsed time: {0}'.format(elapsed))
