vcenter_vm_os_to_nuage_policygroups.py
========================================
vcenter_vm_os_to_nuage_policygroups is a script that will translate vCenter VM OS to Policy groups on that VM in Nuage for VMs in a certain set of Clusters.

This script has the following features:
* Assings Policy Groups depending on regular expressions matching the VM OS in vCenter
* Supports multiple Policy Groups per VM/vPort (will match multiple regular expressions on the same VM and assign all Policy Groups)
* Run only for VMs on a certain set of clusters
* Remove policy groups that are not valid according to the regex's (if option is enabled)
* Validates if the VM is attached to a valid Nuage L2 or L3 domain (checks Nuage metadata on the VM)
* Validates if the Policy Group is valid in the domain to which the VM/vPort is attached

### Author ###
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

### Version history ###
2016-10-16 - 1.0

### CSV ###
It requires a mapping file which is a CSV, configured with the following fields (fields with <> surrounding them are mandatory):
"<vCenter VM OS regex>","<Policy Group>"

Example CSV content:
".*Windows.*","Windows"
".*Centos.*","Centos"
".*Ubuntu.*","Ubuntu"

All the VMware VMs which are attached to a Nuage domain (L2 or L3) in the provided list of clusters and which operating system contains 'Windows', will get the Windows Policy group (if that policy group exists for that domain)

### Limitations ###
- Only supports VMs with one interface

### Usage ###
    usage: vcenter_vm_os_to_nuage_policygroups.py [-h] -c CLUSTERS [-d]
                                                    [-l LOGFILE] -m MAPPING_FILE
                                                    --nuage-enterprise
                                                    NUAGE_ENTERPRISE --nuage-host
                                                    NUAGE_HOST
                                                    [--nuage-port NUAGE_PORT]
                                                    [--nuage-password NUAGE_PASSWORD]
                                                    --nuage-user NUAGE_USERNAME
                                                    [-r] [-S] [-v] --vcenter-host
                                                    VCENTER_HOST
                                                    [--vcenter-port VCENTER_HTTPS_PORT]
                                                    [--vcenter-password VCENTER_PASSWORD]
                                                    --vcenter-user
                                                    VCENTER_USERNAME

    Script which will apply policy groups on VMs depending on the VM OS in
    vCenter for a certain set of Clusters

    optional arguments:
      -h, --help            show this help message and exit
      -c CLUSTERS, --cluster CLUSTERS
                            Cluster that has to be scanned for VMs (can be
                            specified multiple times)
      -d, --debug           Enable debug output
      -l LOGFILE, --log-file LOGFILE
                            File to log to (default = stdout)
      -m MAPPING_FILE, --mapping-file MAPPING_FILE
                            CSV file which contains the mapping of vCenter OS's
                            to policy groups
      --nuage-enterprise NUAGE_ENTERPRISE
                            The enterprise with which to connect to the Nuage
                            VSD/SDK host
      --nuage-host NUAGE_HOST
                            The Nuage VSD/SDK endpoint to connect to
      --nuage-port NUAGE_PORT
                            The Nuage VSD/SDK server port to connect to (default =
                            8443)
      --nuage-password NUAGE_PASSWORD
                            The password with which to connect to the Nuage
                            VSD/SDK host. If not specified, the user is prompted
                            at runtime for a password
      --nuage-user NUAGE_USERNAME
                            The username with which to connect to the Nuage
                            VSD/SDK host
      -r, --remove-policygroups
                            Remove policygroups from all VMs before adding the
                            correct matching ones.
      -S, --disable-SSL-certificate-verification
                            Disable SSL certificate verification on connect
      -v, --verbose         Enable verbose output
      --vcenter-host VCENTER_HOST
                            The vCenter server to connect to, use the IP
      --vcenter-port VCENTER_HTTPS_PORT
                            The vCenter server HTTPS port to connect to (default =
                            443)
      --vcenter-password VCENTER_PASSWORD
                            The password with which to connect to the vCenter
                            host. If not specified, the user is prompted at
                            runtime for a password
      --vcenter-user VCENTER_USERNAME
                            The username with which to connect to the vCenter host

### Example ###
#### All VMs in two clusters, with debug output to a log file ####
    python vcenter_vm_os_to_nuage_policygroups.py -c DC1-Compute -c DC2-Compute -d -l /tmp/PG-set.log -m vm-os_policy-groups.csv --nuage-enterprise csp --nuage-host 192.168.1.10 --nuage-port 443 --nuage-password csproot --nuage-user csproot -r -S --vcenter-host 192.168.1.20 --vcenter-port 443 --vcenter-password vmware --vcenter-user root

### Requirements ###
1. [pyVmomi](https://github.com/vmware/pyvmomi)
2. Nuage VSPK/VSDK (4.0+)
2. vCenter 5+ (tested 5.5, 6.0)
3. A user in vCenter with full read rights