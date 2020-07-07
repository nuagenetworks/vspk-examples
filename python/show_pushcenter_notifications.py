import logging

from time import sleep
from vspk import v6 as vsdk
from vspk.utils import set_log_level

set_log_level(logging.ERROR)


def did_receive_push(data):
    """ Receive delegate
    """
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)


if __name__ == '__main__':

    import sys
    sys.setrecursionlimit(50)

    # create a user session for user csproot
    session = vsdk.NUVSDSession(username="csproot", password="csproot", enterprise="csp", api_url="https://localhost:8443")

    # start the session
    # now session contains a push center and the connected user
    session.start()

    session.reset()
    session.start()

    # we get the push center from the session
    push_center = session.push_center

    # we register our delegate that will be called on each event
    push_center.add_delegate(did_receive_push)

    # and we start it
    push_center.start()

    # then we do nothing, welcome to the marvelous world of async programing ;)
    while True:
        sleep(10000)
