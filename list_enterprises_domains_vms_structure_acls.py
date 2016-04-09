# -*- coding: utf-8 -*-
"""
A simple script that will print out a tree structure for each enterprise the user has access to.

--- Usage ---
python list_enterprises_domains_vms_structure_acls.py

--- Author ---
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>
"""
from vspk import v4_0 as vsdk

session = vsdk.NUVSDSession(
    username='csproot',
    password='PASSWORD',
    enterprise='csp',
    api_url='https://VSD-IP:8443'
)

session.start()

user = session.user

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
