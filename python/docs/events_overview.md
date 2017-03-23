events_overview.py
==================
event_overview produces a table with information on the events for each enterprise the user has access to. Output can also be given in JSON format.

### Author ###
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

### Version history ###
2016-01-24 - 1.0

### Usage ### 
    usage: events_overview.py [-h] [-d] [-e] [-j] [-l LOGFILE] -E NUAGE_ENTERPRISE
                              -H NUAGE_HOST [-P NUAGE_PORT] [-p NUAGE_PASSWORD] -u
                              NUAGE_USERNAME [-S] [-t TIME_DIFFERENCE] [-v]

    Tool to list all events on the enterpises to which the user has access to.

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           Enable debug output
      -e, --extended        Enable extended output
      -j, --json            Print as JSON, not as a table
      -l LOGFILE, --log-file LOGFILE
                            File to log to (default = stdout)
      -E NUAGE_ENTERPRISE, --nuage-enterprise NUAGE_ENTERPRISE
                            The enterprise with which to connect to the Nuage
                            VSD/SDK host
      -H NUAGE_HOST, --nuage-host NUAGE_HOST
                            The Nuage VSD/SDK endpoint to connect to
      -P NUAGE_PORT, --nuage-port NUAGE_PORT
                            The Nuage VSD/SDK server port to connect to (default =
                            8443)
      -p NUAGE_PASSWORD, --nuage-password NUAGE_PASSWORD
                            The password with which to connect to the Nuage
                            VSD/SDK host. If not specified, the user is prompted
                            at runtime for a password
      -u NUAGE_USERNAME, --nuage-user NUAGE_USERNAME
                            The username with which to connect to the Nuage
                            VSD/SDK host
      -S, --disable-SSL-certificate-verification
                            Disable SSL certificate verification on connect
      -t TIME_DIFFERENCE, --time TIME_DIFFERENCE
                            Indication of how far back in the past the events list
                            should go. Can be set in seconds, minutes (add m),
                            hours (add h) or days (add d) (examples: 60, 60m, 60h
                            or 60d, default is 3600 seconds)
      -v, --verbose         Enable verbose output

### Example ###
#### Basic table output ####
    python event_overview.py -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S

#### Extended table output ####
    python event_overview.py -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -e

#### Basic JSON output ####
    python event_overview.py -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -j

#### Extended JSON output ####
    python event_overview.py -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -e -j

### Requirements ###
* Nuage VSPK/VSDK (3.2+)
* PrettyTables (pip install prettytables)