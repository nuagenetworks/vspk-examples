deploy_vsphere_template_with_nuage.py
=============================
deploy_vsphere_template_with_nuage is a script which allows you to deploy (or clone) a VM template (or VM) and connect it to a Nuage VSP subnet.

This can be done through either specifying all parameters through CLI, or by selecting them from lists.

Check the examples for several combinations of arguments

### Usage ###
    usage: deploy_vsphere_template_with_nuage.py [-h] [-d] [-f FOLDER] [-l LOGFILE] -n
                                         NAME --nuage-enterprise NUAGE_ENTERPRISE
                                         --nuage-host NUAGE_HOST
                                         [--nuage-port NUAGE_PORT]
                                         [--nuage-password NUAGE_PASSWORD]
                                         --nuage-user NUAGE_USERNAME
                                         [--nuage-vm-enterprise NUAGE_VM_ENTERPRISE]
                                         [--nuage-vm-domain NUAGE_VM_DOMAIN]
                                         [--nuage-vm-zone NUAGE_VM_ZONE]
                                         [--nuage-vm-subnet NUAGE_VM_SUBNET]
                                         [--nuage-vm-ip NUAGE_VM_IP]
                                         [--nuage-vm-user NUAGE_VM_USER] [-P]
                                         [-r RESOURCE_POOL] [-S] -t TEMPLATE
                                         --vcenter-host VCENTER_HOST
                                         [--vcenter-port VCENTER_PORT]
                                         [--vcenter-password VCENTER_PASSWORD]
                                         --vcenter-user VCENTER_USERNAME [-v]

    Deploy a template into into a VM with certain Nuage VSP metadata.

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           Enable debug output
      -f FOLDER, --folder FOLDER
                            The folder in which the new VM should reside (default
                            = same folder as source virtual machine)
      -l LOGFILE, --log-file LOGFILE
                            File to log to (default = stdout)
      -n NAME, --name NAME  The name of the VM to be created
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
      --nuage-vm-ip NUAGE_VM_IP
                            The IP the VM should have
      --nuage-vm-user NUAGE_VM_USER
                            The Nuage User owning the VM
      -P, --disable-power-on
                            Disable power on of cloned VMs
      -r RESOURCE_POOL, --resource-pool RESOURCE_POOL
                            The resource pool in which the new VM should reside,
                            (default = Resources, the root resource pool)
      -S, --disable-SSL-certificate-verification
                            Disable SSL certificate verification on connect
      -t TEMPLATE, --template TEMPLATE
                            Template to deploy
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
      -v, --verbose         Enable verbose output

### Examples ###
#### Deploy a template in a given Resource Pool and Folder, with given Nuage VM metadata and a fixed IP ####
```
python deploy_vsphere_template_with_nuage.py -n Test-02 --nuage-enterprise csp --nuage-host 10.167.43.64 --nuage-user csproot -S -t TestVM-Minimal-Template --vcenter-host 10.167.43.24 --vcenter-user root -r Pool -f Folder --nuage-vm-enterprise VMware-Integration --nuage-vm-domain Main --nuage-vm-zone "Zone 1" --nuage-vm-subnet "Subnet 0" --nuage-vm-ip 10.0.0.123 --nuage-vm-user vmwadmin
```

#### Deploy a template, for the Nuage VM metadata show menus to select values from ####
```
python deploy_vsphere_template_with_nuage.py -n Test-02 --nuage-enterprise csp --nuage-host 10.167.43.64 --nuage-user csproot -S -t TestVM-Minimal-Template --vcenter-host 10.167.43.24 --vcenter-user root 
```

### Issues and feature requests ###
Feel free to use the [Gitlab issue tracker](http://gitlab.us.alcatel-lucent.com/pdellaer/vSphere-Nuage/issues) of the repository to post issues and feature requests.

### Requirements ###
1. [pyVmomi](https://github.com/vmware/pyvmomi)
2. Nuage VSPK/VSDK (3.2+)
2. vCenter 5+ (tested with 5.1, 5.1u1, 5.5)
3. A user in vCenter with rights to deploy VMs from templates
