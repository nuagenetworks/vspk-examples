search_subnet_associated_with_shared_network.py
===============================================
### Description ###

search_subnet_associated_with_shared_network.py is script for searching all organization's subnets associated with shared network resources together with absolute path in VSD and print to stdout. Stdout example:
```
##########
"Subnet_1" subnet is associated with shared network "SharedNet-01"
This is full path to this subnet:
Org_1 -> Domain_1 -> Zone_1 -> Subnet_1
##########
"Subnet_2" subnet is associated with shared network "SharedNet-02"
This is full path to this subnet:
Org_2 -> Domain_2 -> Zone_2 -> Subnet_2
```

It could be useful for you when you have a lot of organization and want to delete shared network, but do not exactly which organisation uses it.
### Version history ###
2017-04-17 - 1.0 - First version
### Usage ###
    usage: search_subnet_associated_with_shared_network.py [-h] [-d] [-l LOGFILE]
                                                           [-E NUAGE_ENTERPRISE]
                                                           -H NUAGE_HOST
                                                           [-P NUAGE_PORT]
                                                           [-p NUAGE_PASSWORD]
                                                           [-u NUAGE_USERNAME]
                                                           [-S] [-v]

    Tool to list all orginization subnets assotiated to shared subnet together
    with absolute path in VSD.

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           Enable debug output
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
                            VSD/SDK host. If not specified, defualt will be used
      -u NUAGE_USERNAME, --nuage-user NUAGE_USERNAME
                            The username with which to connect to the Nuage
                            VSD/SDK host. If not specified, defualt will be used
      -S, --disable-SSL-certificate-verification
                            Disable SSL certificate verification on connect
      -v, --verbose         Enable verbose output


### Example ###
```bash
python search_subnet_associated_with_shared_network.py -H 10.166.72.100
```
### Author ###
[Aleksey Gorbachev](agorba4ev@gmail.com)
