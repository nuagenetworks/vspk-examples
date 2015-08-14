from vspk.vsdk import v3_2 as vsdk

import logging
from vspk.vsdk.v3_2.utils import set_log_level
# 'Setting a log level to see what happens (Optionnal)'
set_log_level(logging.INFO)

def create_datacenter_gateway_template(name, personality, network_port_names, access_port_names, vlan_range, vlans_values, vsdsession, description=None):
    """ Creates a DC Gateway template

        Args:
            name (string): the name of the gateway template
            personality (string): the personality of the gateway template
            description (string): the description of the gateway template
            network_port_names (list): list of string representing the physical names of the network ports to create
            access_port_names (list): list of string representing the physical names of the access ports to create
            vlan_range (string): the default VLAN range for the access ports
            vlans_values (list): list of int representing the value of the VLAN to create in each access port
            vsdsession (vsdk.NUVSDSession): the VSD session to use

        Returns:
            vsdk.NUGatewayTemplate: the newly created gateway template.
    """

    # create the gateway template
    gateway_template = vsdk.NUGatewayTemplate(name=name, personality=personality, description=description)

    vsdsession.user.create_child(gateway_template)

    # create a network port for each given network_port_names
    for network_port_name in network_port_names:

        network_port_template = vsdk.NUPortTemplate(name=network_port_name, physical_name=network_port_name, port_type="NETWORK")
        gateway_template.create_child(network_port_template)


    # create an access port for each given access_port_names
    for access_port_name in access_port_names:

        access_port_template = vsdk.NUPortTemplate(name=access_port_name, physical_name=access_port_name, port_type="ACCESS", vlan_range=vlan_range)
        gateway_template.create_child(access_port_template)

        # create a VLAN for each given vlans_values
        for vlan_value in vlans_values:

            vlan = vsdk.NUVLANTemplate(value=vlan_value)
            access_port_template.create_child(vlan)

    return gateway_template


def create_datacenter_gateway(name, system_id, gateway_template, enterprise, vsdsession, permission="USE"):
    """ Creates a gateway instance from a gateway template, and gives given permission to given enterprise

        Args:
            name (string): the gateway name
            gateway_template (vsdk.NUGatewayTemplate): the gateway template to use
            enterprise (vsdk.NUEnterprise): the enterprise to give permission to
            permission (string): the permission to give (default: "USE")
            vsdsession (vsdk.NUVSDSession): the VSD session to use

        Returns:
            vsdk.NUGateway: the newly created gateway.
    """

    gateway = vsdk.NUGateway(name=name, system_id=system_id)
    vsdsession.user.instantiate_child(gateway, gateway_template)
    permission = vsdk.NUEnterprisePermission(permitted_action=permission, permitted_entity_id=enterprise.id)
    gateway.create_child(permission)

    return gateway

if __name__ == "__main__":

    # start the session
    session = vsdk.NUVSDSession(username='csproot', password='csproot', enterprise='csp', api_url='https://135.227.222.46:8443')
    session.start()

    # get an enterprise
    enterprise = session.user.enterprises.get_first(filter="name == 'Triple A'")

    # create a gateway template
    gw_tmpl = create_datacenter_gateway_template("my template", "VRSG", ["port0"], ["port1", "port2"], "0-400", [100, 200], session)

    # instantiate a gateway from the template and give USE permission to enterprise
    gw = create_datacenter_gateway("gateway 1", "id1", gw_tmpl, enterprise, session)

    from time import sleep
    print "Sleeping..."
    sleep(6)
    gw_tmpl.delete()