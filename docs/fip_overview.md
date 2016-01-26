fip_overview.py
===============
fip_overview produces a table with information on all VMs with a FIP attached. Output can also be given in JSON format.

### Author ###
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

### Version history ###
2016-01-24 - 1.0
2016-01-26 - 1.1 - JSON output supported

### Usage ### 
    usage: fip_overview.py [-h] [-d] [-j] [-l LOGFILE] -E NUAGE_ENTERPRISE -H
                           NUAGE_HOST [-P NUAGE_PORT] [-p NUAGE_PASSWORD] -u
                           NUAGE_USERNAME [-S] [-v]

    Tool to list all FIPs attached to the VMs to which the user has access to.

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           Enable debug output
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
      -v, --verbose         Enable verbose output

### Example ###
    python fip_overview.py -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S
    
### Requirements ###
* Nuage VSPK/VSDK (3.2+)
* PrettyTables (pip install prettytables)