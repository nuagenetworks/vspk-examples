# -*- coding: utf-8 -*-

import sys
import logging
sys.path.append("./")

from vspk.vsdk.v3_2 import *


if __name__ == '__main__':

    # Connection with a certificate
    cert = ("/Users/chserafi/Desktop/keys/vns.pem", "/Users/chserafi/Desktop/keys/vns-Key.pem")
    session = NUVSDSession(username='vns', enterprise='csp', api_url='https://135.227.222.88:7443', certificate=cert)
    session.start()
    session.reset()

    # Connection with a user/password
    session = NUVSDSession(username="csproot", password="csproot", enterprise="csp", api_url="https://135.227.222.88:8443")
    session.start()
