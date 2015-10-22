vcin_vdt_configure_from_vsphere.py
====================
vcin_vdt_configure_from_vsphere is a script which will configure the full vCenter tree of Datacenters, Clusters and Hosts into the Nuage vCenter Integration Node and the Nuage vCenter Deployment Tool. It is also capable of configuring the ESXi hosts with the correct Agent VM settings.

This script has the following features:
* Configure a vCenter structure inside the Nuage vCenter Deployment Tool
* Configure the full tree of Datacenters, Clusters and Hosts, or
* Configure a subset of the tree by specifying which:
  * Datacenters to add
  * Clusters to add
  * Hosts to add
* Host and VRS configuration values can be set per host using a CSV file.
* ESXi Host Agent VM settings can be configured per host, either by using the CSV file or automatically, in which case it will use the management network (hv-management-network) and the first available local VMFS datastore on the host.
* Data on fields that require a specific type of data (IP's, True/False fields and limited selection fields)
* It will only create those entities that are specified and do not exist yet.
* It will update existing host and VRS configurations: only the fields for which data has been provided, empty fields are not overwritten.
* Passwords that are not specified as arguments, will be prompted for (security measure)
* Provide verbose & debug logging

Check the examples for several combinations of arguments.

### CSV Strucure ###
A CSV file can be used to import individual settings for each host. The structure of this CSV looks like this (fields in <> are mandatory, fields with [] can be left blank)
(for overview purpose, each field is on it's own line. In the file itself, this should all be one line)

    "<IP>",
    "[name]",
    "[hypervisor user]",
    "[hypervisor password]",
    "[management network portgroup]",
    "[data network portgroup]",
    "[vm network portgroup]",
    "[multicast sourece portgroup]",
    "[use management DHCP (True|False)]",
    "[management IP]",
    "[management netmask (octet structure)]",
    "[management gateway]",
    "[management DNS 1]",
    "[management DNS 2]",
    "[separate data network (True|False)]",
    "[use data DHCP (True|False)]",
    "[data IP]",
    "[data netmask (octet structure)]",
    "[data gateway]",
    "[data DNS 1]",
    "[data DNS 2]",
    "[MTU]",
    "[require metadata (True|False)]",
    "[multi VM support (True|False)]",
    "[DHCP relay server (IP)]",
    "[flow eviction threshold]",
    "[datapath sync timeout]",
    "[network uplink interface]",
    "[network uplink IP]",
    "[network uplink netmask (octet structure)]",
    "[network uplink gateway]",
    "[script URL]",
    "[personality]",
    "[site ID]",
    "[NFS server address (IP)]",
    "[NFS mount path]",
    "[primay Nuage controller (IP)]",
    "[secondary Nuage controller (IP)]",
    "[primary NTP server (IP)]",
    "[secondary NTP server (IP)]",
    "[static route target IP]",
    "[static route next-hop gateway]",
    "[multicast send interface]",
    "[multicast send IP]",
    "[multicast send netmask (octet structure)]",
    "[multicast receive IP]",
    "[multicast receive netmask (octet structure)]",
    "[Host Agent VM Port Group]",
    "[Host Agent VM Datastore]"

### Limitations ###
* You can only add hosts to a cluster, not to a datacenter. vCenter supports this, but the Nuage vCenter Deployment Tool does not.
* If --all-hosts is specified, it will use the first VMkernel IP address it encounters for the Host
* Management IP address stays with the DHCP address. Even if you specify no Management DHCP and specify a specific IP, it does not set this in the VRS itself (it will in the vCenter Deployment Tool). This is a limitation/bug in the deployment tool, not in this script.
* Multicast ranges still have to be set manually for now

### Usage ###
    usage: vcin_vdt_configure_from_vsphere.py [-h] [--all-clusters] [--all-datacenters]
                                [--all-hosts] [--cluster CLUSTERS] [-d]
                                [--datacenter DATACENTERS] [--host HOSTS]
                                [--hosts-file HOSTS_FILE] [--hv-user HV_USERNAME]
                                [--hv-password HV_PASSWORD]
                                [--hv-management-network HV_MANAGEMENT_NETWORK]
                                [--hv-data-network HV_DATA_NETWORK]
                                [--hv-vm-network HV_VM_NETWORK]
                                [--hv-mc-network HV_MC_NETWORK] [-l LOGFILE]
                                --nuage-enterprise NUAGE_ENTERPRISE --nuage-host
                                NUAGE_HOST [--nuage-port NUAGE_PORT]
                                [--nuage-password NUAGE_PASSWORD] --nuage-user
                                NUAGE_USERNAME [--nuage-vrs-ovf NUAGE_VRS_OVF]
                                [-S] [-v] --vcenter-host VCENTER_HOST
                                [--vcenter-name VCENTER_NAME]
                                [--vcenter-http-port VCENTER_HTTP_PORT]
                                [--vcenter-https-port VCENTER_HTTPS_PORT]
                                [--vcenter-password VCENTER_PASSWORD]
                                --vcenter-user VCENTER_USERNAME

    Add a (sub)tree from a vCenter's structure to the Nuage vCenter Deployment
    Tool. This can be done by specifying the datacenters, clusters and hosts you
    want to add. You can also specify to include all datacenters and/or clusters
    and/or hosts, depending on your requirements. It is also possible to provide a
    CSV file containing the hosts to add and each hosts specific configuration.
    Creation will only happen if the entity doesn't exist yet in the vCenter
    Deployment Tool. Hosts will be updated with the new configuration if you run
    the script with already existsing hosts. This script is also capable of
    updating the ESXi Hosts Agent VM settings.

    optional arguments:
      -h, --help            show this help message and exit
      --all-clusters        Configure all Clusters from the selected vCenter
                            Datacenters
      --all-datacenters     Configure all vCenter Datacenters from the vCenter
      --all-hosts           Configure all Hosts from the selected Clusters
      --cluster CLUSTERS    Cluster that has to be present in the Nuage vCenter
                            Deployment Tool (can be specified multiple times)
      -d, --debug           Enable debug output
      --datacenter DATACENTERS
                            Datacenter that has to be present in the Nuage vCenter
                            Deployment Tool (can be specified multiple times)
      --host HOSTS          Host IPs that has to be present in the Nuage vCenter
                            Deployment Tool (can be specified multiple times)
      --host-configure-agent
                        Configure the VM Agent settings of the vCenter Hosts.
                        It will configure the Management network you specify
                        as an argument with --hv-management-network, or the
                        one in the CSV file if specified. For datastore it
                        will use the first available local datastore, or the
                        one specified in the CSV file if provided.
      --hosts-file HOSTS_FILE
                            CSV file which contains the configuration for each
                            hypervisor
      --hv-user HV_USERNAME
                            The ESXi hosts username
      --hv-password HV_PASSWORD
                            The ESXi hosts password. If not specified, the user is
                            prompted at runtime for a password
      --hv-management-network HV_MANAGEMENT_NETWORK
                            The ESXi hosts management network
      --hv-data-network HV_DATA_NETWORK
                            The ESXi hosts data network
      --hv-vm-network HV_VM_NETWORK
                            The ESXi hosts VM network
      --hv-mc-network HV_MC_NETWORK
                            The ESXi hosts Multicast Source network
      -l LOGFILE, --log-file LOGFILE
                            File to log to (default = stdout)
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
      --nuage-vrs-ovf NUAGE_VRS_OVF
                            The URL of the VRS OVF file
      -S, --disable-SSL-certificate-verification
                            Disable SSL certificate verification on connect
      -v, --verbose         Enable verbose output
      --vcenter-host VCENTER_HOST
                            The vCenter server to connect to, use the IP
      --vcenter-name VCENTER_NAME
                            The name of the vCenter you want in the vCenter
                            Deployment Tool
      --vcenter-http-port VCENTER_HTTP_PORT
                            The vCenter server HTTP port to connect to (default =
                            80)
      --vcenter-https-port VCENTER_HTTPS_PORT
                            The vCenter server HTTPS port to connect to (default =
                            443)
      --vcenter-password VCENTER_PASSWORD
                            The password with which to connect to the vCenter
                            host. If not specified, the user is prompted at
                            runtime for a password
      --vcenter-user VCENTER_USERNAME
                            The username with which to connect to the vCenter host

### Examples ###
#### Create all datacenters, clusters & hosts ####
```
python vcin_vdt_configure_from_vsphere.py -d --nuage-enterprise csp --nuage-host 10.167.43.52 --nuage-user csproot --nuage-vrs-ovf http://10.167.43.14/VMware-VRS/VRS_3.2.2-74.ovf -S --vcenter-host 10.167.43.24 --vcenter-user root --vcenter-name "Main vCenter" -l /tmp/populate.log --all-datacenters  --all-clusters --all-hosts --hv-user root --hv-management-network Management --hv-data-network "Data Control" --hv-vm-network 1-Compute-OVSPG --hv-mc-network 1-Compute-PG1
```

#### Create 1 datacenter, 2 clusters & all hosts - Only the hosts in the selected clusters are added in this case ####
```
python vcin_vdt_configure_from_vsphere.py -d --nuage-enterprise csp --nuage-host 10.167.43.52 --nuage-user csproot --nuage-vrs-ovf http://10.167.43.14/VMware-VRS/VRS_3.2.2-74.ovf -S --vcenter-host 10.167.43.24 --vcenter-user root --vcenter-name "Main vCenter" -l /tmp/populate.log --datacenter "Main DC" --cluster DC1-Compute --cluster DC2-Compute --all-hosts --hv-user root --hv-management-network Management --hv-data-network "Data Control" --hv-vm-network 1-Compute-OVSPG --hv-mc-network 1-Compute-PG1
```

#### Create 1 datacenter, 2 clusters & 2 hosts - Only if the host exists in one of the selected clusters, it is added to that cluster ####
```
python vcin_vdt_configure_from_vsphere.py -d --nuage-enterprise csp --nuage-host 10.167.43.52 --nuage-user csproot --nuage-vrs-ovf http://10.167.43.14/VMware-VRS/VRS_3.2.2-74.ovf -S --vcenter-host 10.167.43.24 --vcenter-user root --vcenter-name "Main vCenter" -l /tmp/populate.log --datacenter "Main DC" --cluster DC1-Compute --cluster DC2-Compute --host 10.167.43.9 --host 10.167.43.12 --hv-user root --hv-management-network Management --hv-data-network "Data Control" --hv-vm-network 1-Compute-OVSPG --hv-mc-network 1-Compute-PG1
```

#### Create 1 datacenter, 2 clusters & the hosts with their specific configuration from the hosts-file.csv in the samples folder - Only the hosts in the selected clusters are added in this case ####
```
python vcin_vdt_configure_from_vsphere.py -d --nuage-enterprise csp --nuage-host 10.167.43.52 --nuage-user csproot --nuage-vrs-ovf http://10.167.43.14/VMware-VRS/VRS_3.2.2-74.ovf -S --vcenter-host 10.167.43.24 --vcenter-user root --vcenter-name "Main vCenter" -l /tmp/populate.log --datacenter "Main DC" --cluster DC1-Compute --cluster DC2-Compute --hosts-file samples/hosts-file.csv --hv-user root --hv-management-network Management --hv-data-network "Data Control" --hv-vm-network 1-Compute-OVSPG --hv-mc-network 1-Compute-PG1
```

#### Create 1 datacenter, 2 clusters & the hosts with their specific configuration from the hosts-file.csv in the samples folder and configure the hosts Agent VM settings - Only the hosts in the selected clusters are added in this case ####
```
python vcin_vdt_configure_from_vsphere.py -d --nuage-enterprise csp --nuage-host 10.167.43.52 --nuage-user csproot --nuage-vrs-ovf http://10.167.43.14/VMware-VRS/VRS_3.2.2-74.ovf -S --vcenter-host 10.167.43.24 --vcenter-user root --vcenter-name "Main vCenter" -l /tmp/populate.log --datacenter "Main DC" --cluster DC1-Compute --cluster DC2-Compute --hosts-file samples/hosts-file.csv --hv-user root --hv-management-network Management --hv-data-network "Data Control" --hv-vm-network 1-Compute-OVSPG --hv-mc-network 1-Compute-PG1 --host-configure-agent
```

### Issues and feature requests ###
Feel free to use the [Gitlab issue tracker](http://gitlab.us.alcatel-lucent.com/pdellaer/vSphere-Nuage/issues) of the repository to post issues and feature requests.

### Requirements ###
1. [pyVmomi](https://github.com/vmware/pyvmomi)
2. Nuage VSPK/VSDK (3.2+)
2. vCenter 5+ (tested with 5.1, 5.1u1, 5.5)
3. A user in vCenter with full read rights
