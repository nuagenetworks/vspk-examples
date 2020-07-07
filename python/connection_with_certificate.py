from vspk import v6 as vsdk

if __name__ == '__main__':

    # Connection with a certificate
    cert = ("/path/to/csproot.pem", "/path/to/csproot-Key.pem")
    session = vsdk.NUVSDSession(username='csproot', enterprise='csp', api_url='https://localhost:7443', certificate=cert)
    session.start()

    # Reset the session to start a new one
    session.reset()

    # Connection with a user/password
    session = vsdk.NUVSDSession(username="csproot", password="csproot", enterprise="csp", api_url="https://localhost:8443")
    session.start()
