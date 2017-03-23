gather_statistics.py
====================
gather_statistics.py will gather statistics on one ore more Domains, L2 Domains, Zones, Subnets or VMs (all vm-interfaces) for a given timeframe. If the entity has a statistics_policy defined, it will use that policies statistics granularity to calculate the amount of data points. Otherwise it will use a default of 1 datapoint per minute.

The user can specify which statistics to gather, if none are specified, all of them will be gathered. Data can be presented as a table, or as JSON.

### Author ###
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

### Version history ###
2016-01-29 - 1.0

### Usage ### 
    usage: gather_statistics.py [-h] [-d] -e {DOMAIN,L2DOMAIN,ZONE,SUBNET,VM} [-j]
                                [-l LOGFILE] [-n ENTITY_NAME] -E NUAGE_ENTERPRISE
                                -H NUAGE_HOST [-P NUAGE_PORT] [-p NUAGE_PASSWORD]
                                -u NUAGE_USERNAME
                                [-s {BYTES_IN,BYTES_OUT,EGRESS_BYTE_COUNT,EGRESS_PACKET_COUNT,INGRESS_BYTE_COUNT,INGRESS_PACKET_COUNT,PACKETS_DROPPED_BY_RATE_LIMIT,PACKETS_IN,PACKETS_IN_DROPPED,PACKETS_IN_ERROR,PACKETS_OUT,PACKETS_OUT_DROPPED,PACKETS_OUT_ERROR}]
                                [-S] [-t TIME_DIFFERENCE] [-v]

    Tool to gather statistics on domains, zones, subnets or vports within a
    certain time frame.

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           Enable debug output
      -e {DOMAIN,L2DOMAIN,ZONE,SUBNET,VM}, --entity-type {DOMAIN,L2DOMAIN,ZONE,SUBNET,VM}
                            The type of entity to gather the statistics for, can
                            be DOMAIN, ZONE, SUBNET or VM.
      -j, --json            Print as JSON, not as a table
      -l LOGFILE, --log-file LOGFILE
                            File to log to (default = stdout)
      -n ENTITY_NAME, --entity-name ENTITY_NAME
                            Entity name to provide statistics for. If not
                            specified all entities of the entiy-type will be used
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
      -s {BYTES_IN,BYTES_OUT,EGRESS_BYTE_COUNT,EGRESS_PACKET_COUNT,INGRESS_BYTE_COUNT,INGRESS_PACKET_COUNT,PACKETS_DROPPED_BY_RATE_LIMIT,PACKETS_IN,PACKETS_IN_DROPPED,PACKETS_IN_ERROR,PACKETS_OUT,PACKETS_OUT_DROPPED,PACKETS_OUT_ERROR}, --statistic-type {BYTES_IN,BYTES_OUT,EGRESS_BYTE_COUNT,EGRESS_PACKET_COUNT,INGRESS_BYTE_COUNT,INGRESS_PACKET_COUNT,PACKETS_DROPPED_BY_RATE_LIMIT,PACKETS_IN,PACKETS_IN_DROPPED,PACKETS_IN_ERROR,PACKETS_OUT,PACKETS_OUT_DROPPED,PACKETS_OUT_ERROR}
                            The type of statistics to gather. If not specified,
                            all are used. Can be specified multiple times.
                            Possible values are: BYTES_IN, BYTES_OUT,
                            EGRESS_BYTE_COUNT, EGRESS_PACKET_COUNT,
                            INGRESS_BYTE_COUNT, INGRESS_PACKET_COUNT,
                            PACKETS_DROPPED_BY_RATE_LIMIT, PACKETS_IN,
                            PACKETS_IN_DROPPED, PACKETS_IN_ERROR, PACKETS_OUT,
                            PACKETS_OUT_DROPPED, PACKETS_OUT_ERROR
      -S, --disable-SSL-certificate-verification
                            Disable SSL certificate verification on connect
      -t TIME_DIFFERENCE, --time TIME_DIFFERENCE
                            Indication of how far back in the past the statistics
                            should go. Can be set in seconds, minutes (add m),
                            hours (add h) or days (add d) (examples: 60, 60m, 60h
                            or 60d, default is 3600 seconds)
      -v, --verbose         Enable verbose output

### Example ###
---- Gather all statistics for the last 10 minutes on all domains with json output ----
    python gather_statistics.py -e DOMAIN -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -t 600 -j

---- Gather all statistics for the last hour (default) on one L2 domain with tabled output ----
    python gather_statistics.py -e L2DOMAIN -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -n "L2 Domain Test"

---- Gather INGRESS_BYTE_COUNT and EGRESS_BYTE_COUNT for the last 120 seconds on all the Zones with json output ----
    python gather_statistics.py -e ZONE -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -s INGRESS_BYTE_COUNT -s EGRESS_BYTE_COUNT -j -t 120

---- Gather PACKETS_IN statistics for the last day on all SUBNETS with json output ----
    python gather_statistics.py -e SUBNET -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -t 1d -j -s PACKETS_IN

---- Gather BYTES_IN and BYTES_OUT statistics for the last hour on all VMs with tabled output ----
    python gather_statistics.py -e VM -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -s BYTES_IN -s BYTES_OUT
    
### Requirements ###
* Nuage VSPK/VSDK (3.2+)
* PrettyTables (pip install prettytables)