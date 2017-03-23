# -*- coding: utf8 -*-

from vspk.vsdk.v3_1 import NUVSDSession as NUVSDSession_v3_1
from vspk.vsdk.v3_2 import NUVSDSession as NUVSDSession_v3_2
import os


def shell_variable(value_name):
    value = os.environ.get(value_name)
    if value:
        return value
    else:
        print "Please have %s specified when executing this program." % value_name
        exit(-1)


def itemize(item, name, description):
    if name and description:
        return str(item.name) + ', ' + str(item.description)
    elif name:
        return str(item.name)
    elif description:
        return str(item.description)
    else:
        exit(-1)


def print_items(header, item_list, name=False, description=False):
    print header
    print '\n'.join(itemize(item, name, description) for item in item_list)


def inspect_topology(username, password, enterprise, api_url, api_version):
    if api_version == "3.1":
        session = NUVSDSession_v3_1(
            username=username, password=password, enterprise=enterprise, api_url=api_url)
    elif api_version == "3.2":
        session = NUVSDSession_v3_2(
            username=username, password=password, enterprise=enterprise, api_url=api_url)
    else:
        return

    session.start()
    user = session.user
    print "User:\n=====\nname: %s, role: %s" % (user.user_name, user.role)

    print_items("\nEnterprises:\n============", user.enterprises.get(), name=True)
    print_items("\nDomains:\n========", user.domains.get(), name=True, description=True)
    print_items("\nL2Domains:\n==========", user.l2_domains.get(), name=True, description=True)


if __name__ == "__main__":

    api_url     = shell_variable("VSD_API_URL")
    api_version = shell_variable("VSD_API_VERSION")
    username    = shell_variable("VSD_USERNAME")
    password    = shell_variable("VSD_PASSWORD")
    enterprise  = shell_variable("VSD_ENTERPRISE")

    inspect_topology(username=username, password=password, enterprise=enterprise,
                     api_url=api_url, api_version=api_version)