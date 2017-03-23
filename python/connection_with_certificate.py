# -*- coding: utf-8 -*-

import sys
import logging
sys.path.append("./")

from vspk.vsdk.v3_2 import *


if __name__ == '__main__':

    # Connection with a certificate
    cert = ("./keys/vns.pem", ".//keys/vns-Key.pem")
    session = NUVSDSession(username='vns', enterprise='csp', api_url='https://135.227.222.46:7443', certificate=cert)
    session.start()

    # Reset the session to start a new one
    session.reset()

    # Connection with a user/password
    session = NUVSDSession(username="csproot", password="csproot", enterprise="csp", api_url="https://135.227.222.46:8443")
    session.start()
