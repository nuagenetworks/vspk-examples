Nuage ACL Learner 
=================
nuage_acl_learner is a tool which can be used in a clean test environment to create a set of ACL rules which are being used by the applications running in that environment. 

After you configured your VRS's to point their flow logs to the IP of the server where you run this tool, you can start it and it will start listening for TCP connections on port 514.

At the start, the tool will investigate the specified domain and will create a set of learning ACL rules (both ingress and egress). These rules will be used to enable logging for all traffic.

Once a flow log messages is sent to the tool from a VRS, the tool will investigate the flow and will implement a matching ACL rule entry. 

The ACL rule entry will be created using either Policy Groups, Zones or Subnets, depending on the type specified at runtime. If the destination of the traffic is outside of the domain, a network macro for the destination will be created and used in the rule.

The tool can either specify 'any' as source port, or, if specified at runtime, the tool will be very strict and create a rule with the source port set to the one used in the flow. In most cases this strict policy is a bit overkill: most client connections use a random port, using a strict policy for source port would block the next traffic attempt because it is a different source port.

The original idea came from Jeroen van Bemmel, this is a python/SDK implementation.

### Author ###
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

### Version history ###
2016-01-22 - 1.0 - Only Ingress rules for now

### VRS configuration ###
To configure your VRS, you have to edit the (r)syslog configuration to send everything matching 'ACLAUDIT' to the server running this tool on port 514 via a TCP connection. 

Example rsyslogd rule if the tool is running on 10.167.43.23:

    :msg,contains,"ACLAUDIT" @@10.167.43.23:514

### Limitations ###
* When working with Policy Groups, it will only use one of the PG's for the rule
* If POLICYGROUP is specified as type, and a VM has no Policy Group assigned, no rule will be created
* Only creates ingress rules for now
* It does not use the commit/rollback system for ACLs as this is an automated tool. The rules impact traffic immediatly
* Has to be run as root (creates a socket on port 514)

### Usage ### 
    usage: nuage_acl_learner.py [-h] [-d] [-f FIRST_PRIORITY] [-l LOGFILE] -D
                                NUAGE_DOMAIN -E NUAGE_ENTERPRISE -H NUAGE_HOST
                                [-P NUAGE_PORT] [-p NUAGE_PASSWORD] -u
                                NUAGE_USERNAME [-S] [-s] -t
                                {POLICYGROUP,ZONE,SUBNET} [-v]

    Tool which will create ACLs learned from flow logs from the VRS. It will
    actively listen to incomming syslog connections on port 514.

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           Enable debug output
      -f FIRST_PRIORITY, --first-priority FIRST_PRIORITY
                            The priority of the first created rule (will be
                            incremented for each next rule), default is 100
      -l LOGFILE, --log-file LOGFILE
                            File to log to (default = stdout)
      -D NUAGE_DOMAIN, --nuage-domain NUAGE_DOMAIN
                            The domain to investigate and set ACLs on
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
      -s, --strict-source-ports
                            Use strict source ports, this will set the specific
                            source port instead of the default * setting for
                            Ingress rules.
      -t {POLICYGROUP,ZONE,SUBNET}, --type {POLICYGROUP,ZONE,SUBNET}
                            On what entity type should the ACLs be applied. Valid
                            responses: POLICYGROUP, ZONE, SUBNET
      -v, --verbose         Enable verbose output

### Example ###
#### Set non-strict source port rules using Policy Groups ####
    python nuage_acl_learner.py -d -D "Main Customer Domain" -E csp -H 10.167.43.64 -P 443 -p csproot -u csproot -S -t POLICYGROUP

### Requirements ###
* Nuage VSPK/VSDK (3.2+)