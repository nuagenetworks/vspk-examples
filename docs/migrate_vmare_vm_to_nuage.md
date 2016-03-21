migrate_vmware_vm_to_nuage.py
=============================
migrate_vmware_vm_to_nuage.py migrate a VMware VM, with VMware tools or open-vm-tools, to a Nuage VSP environment. 

In default mode it will gather the VMs IP and check if it is part of the specified subnet. If it is, it will populate the VM with the correct metadata and reconnect the interface to the OVS-PG. 

In split activation mode, it will gather the MAC, UUID and IP from the VM and create a vPort and VM before reconnecting the nic to the OVS-PG.


### Author ###
Philippe Dellaert <philippe.dellaert@nuagenetworks.net>

### Version history ###
2016-03-20 - 1.0

### Usage ### 
    usage: migrate_vmware_vm_to_nuage.py [-h] [-d] [-l LOGFILE]
                                         [-m {metadata,split-activation}]
                                         --nuage-enterprise NUAGE_ENTERPRISE
                                         --nuage-host NUAGE_HOST
                                         [--nuage-port NUAGE_PORT]
                                         [--nuage-password NUAGE_PASSWORD]
                                         --nuage-user NUAGE_USERNAME
                                         --nuage-vm-enterprise NUAGE_VM_ENTERPRISE
                                         [--nuage-vm-domain NUAGE_VM_DOMAIN]
                                         [--nuage-vm-zone NUAGE_VM_ZONE]
                                         --nuage-vm-subnet NUAGE_VM_SUBNET
                                         [--nuage-vm-user NUAGE_VM_USER] [-S] [-v]
                                         --vcenter-host VCENTER_HOST
                                         [--vcenter-port VCENTER_PORT]
                                         [--vcenter-password VCENTER_PASSWORD]
                                         --vcenter-user VCENTER_USERNAME
                                         --vcenter-port-group VCENTER_PORTGROUP
                                         --vcenter-vm VCENTER_VM

    Tool to migrate a VMware VM, with VMware tools or open-vm-tools, to a Nuage
    VSP environment. In default mode it will gather the VMs IP and check if it is
    part of the specified subnet. If it is, it will populate the VM with the
    correct metadata and reconnect the interface to the OVS-PG. In split
    activation mode, it will gather the MAC, UUID and IP from the VM and create a
    vPort and VM before reconnecting the nic to the OVS-PG

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           Enable debug output
      -l LOGFILE, --log-file LOGFILE
                            File to log to (default = stdout)
      -m {metadata,split-activation}, --mode {metadata,split-activation}
                            Select between metadata and split-activation
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
      --nuage-vm-enterprise NUAGE_VM_ENTERPRISE
                            The Nuage enterprise to which the VM should be
                            connected
      --nuage-vm-domain NUAGE_VM_DOMAIN
                            The Nuage domain to which the VM should be connected
      --nuage-vm-zone NUAGE_VM_ZONE
                            The Nuage zone to which the VM should be connected
      --nuage-vm-subnet NUAGE_VM_SUBNET
                            The Nuage subnet to which the VM should be connected
      --nuage-vm-user NUAGE_VM_USER
                            The Nuage User owning the VM
      -S, --disable-SSL-certificate-verification
                            Disable SSL certificate verification on connect
      -v, --verbose         Enable verbose output
      --vcenter-host VCENTER_HOST
                            The vCenter or ESXi host to connect to
      --vcenter-port VCENTER_PORT
                            vCenter Server port to connect to (default = 443)
      --vcenter-password VCENTER_PASSWORD
                            The password with which to connect to the vCenter
                            host. If not specified, the user is prompted at
                            runtime for a password
      --vcenter-user VCENTER_USERNAME
                            The username with which to connect to the vCenter host
      --vcenter-port-group VCENTER_PORTGROUP
                            The name of the distributed Portgroup to which the
                            interface needs to be attached.
      --vcenter-vm VCENTER_VM
                            The name of the VM to migrate
    
### Requirements ###
* Nuage VSPK/VSDK (3.2+)
* pyvmomi (5.1+)
* ipaddress (pip install ipaddress)