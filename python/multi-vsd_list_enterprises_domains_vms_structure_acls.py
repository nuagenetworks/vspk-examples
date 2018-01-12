# -*- coding: utf-8 -*-
"""
A simple script that will print out a tree structure for each enterprise on multiple VSDs the user has access to.

This example uses 4 sessions:
    - Session 1: Certificate based authentication to VSD 1
    - Session 2: Certificate based authentication to VSD 2
    - Session 3: Username/Password authentication to VSD 1
    - Session 4: Username/Password authentication to VSD 2

Update each session's information with your setup details before you execute the script.

You can also nest the with statements to switch between sessions
--- Usage ---
python multi-vsd_list_enterprises_domains_vms_structure_acls.py

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>
"""
from vspk import v5_0 as vsdk
import sys
print(sys.version)

def print_enterprise_overview(user):
    for cur_ent in user.enterprises.get():
        print('VMs inside Enterprise %s' % cur_ent.name)
        for cur_vm in cur_ent.vms.get():
            print('|- %s' % cur_vm.name)
    
        print('\nDomains inside Enterprise %s' % cur_ent.name)
        for cur_domain in cur_ent.domains.get():
            print('|- Domain: %s' % cur_domain.name)
            for cur_zone in cur_domain.zones.get():
                print('    |- Zone: %s' % cur_zone.name)
                for cur_subnet in cur_domain.subnets.get():
                    print('        |- Subnets: %s - %s - %s' % (cur_subnet.name, cur_subnet.address, cur_subnet.netmask))
    
            for cur_acl in cur_domain.ingress_acl_templates.get():
                print('    |- Ingress ACL: %s' % cur_acl.name)
                for cur_rule in cur_acl.ingress_acl_entry_templates.get():
                    print('        |- Rule: %s' % cur_rule.description)
    
            for cur_acl in cur_domain.egress_acl_templates.get():
                print('    |- Egress ACL: %s' % cur_acl.name)
                for cur_rule in cur_acl.egress_acl_entry_templates.get():
                    print('        |- Rule: %s' % cur_rule.description)
    
        print('--------------------------------------------------------------------------------')

session_1 = vsdk.NUVSDSession(
    username='csproot',
    enterprise='csp',
    certificate=('nuage/vsd01.nuage.intern.pem', 'nuage/vsd01.nuage.intern-Key.pem'),
    api_url='https://vsd01.nuage.intern:7443'
)
session_1.start()

session_2 = vsdk.NUVSDSession(
    username='csproot',
    enterprise='csp',
    certificate=('nuage/vsd02.nuage.intern.pem', '/Users/pdellaer/nuage/vsd02.nuage.intern-Key.pem'),
    api_url='https://vsd02.nuage.intern:7443'
)
session_2.start()

session_3 = vsdk.NUVSDSession(
    username='csproot',
    password='csproot',
    enterprise='csp',
    api_url='https://vsd01.nuage.intern:8443'
)
session_3.start()

session_4 = vsdk.NUVSDSession(
    username='csproot',
    password='csproot',
    enterprise='csp',
    api_url='https://vsd02.nuage.intern:8443'
)
session_4.start()

print('================================================================================')
print('Session 1 - Intern - Certificate based')
print('================================================================================')
with session_1:
    print_enterprise_overview(session_1.user)
print('================================================================================')

print('')

print('================================================================================')
print('Session 2 - VPS - Certificate based')
print('================================================================================')
with session_2:
    print_enterprise_overview(session_2.user)
print('================================================================================')

print('')

print('================================================================================')
print('Session 3 - Intern - Password based')
print('================================================================================')
with session_3:
    print_enterprise_overview(session_3.user)
print('================================================================================')

print('')

print('================================================================================')
print('Session 4 - VPS - Password based')
print('================================================================================')
with session_4:
    print_enterprise_overview(session_4.user)
print('================================================================================')
