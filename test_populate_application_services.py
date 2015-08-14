import requests
import csv
from vspk.vsdk import v3_2 as vsdk

def import_known_application_services(session):

    # pip install requests

    protocols = requests.get('http://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv').content
    csvreader = csv.reader(protocols.split('\r\n'))

    cpt = 0

    for row in csvreader:

        cpt = cpt + 1
        if cpt >= 10:
            continue

        try:
            port_number = row[1]
            proto = "6" if row[2] is "tcp" else "17"
            desc = row[3]
            name = "%s - %s - %s " % (proto, port_number, row[0])

            if not name:
                continue;

            appservice = vsdk.NUApplicationService(name=name, protocol=proto, destination_port=port_number, description=desc, direction="REFLEXIVE",\
                                                   ether_type="0x0800", source_port="*", dscp="*")

            session.user.create_child(appservice)

        except Exception as ex:
            print ex;


if __name__ == "__main__":

    session = vsdk.NUVSDSession(username='csproot', password='csproot', enterprise='csp', api_url='https://135.227.222.46:8443')
    session.start()
    import_known_application_services(session)

    from time import sleep
    print "Sleeping..."
    sleep(6)

    session.user.application_services.fetch()
    for appservice in session.user.application_services:
        appservice.delete()