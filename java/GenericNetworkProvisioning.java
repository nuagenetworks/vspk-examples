import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Domain;
import net.nuagenetworks.vspk.v5_0.DomainTemplate;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.Me;
import net.nuagenetworks.vspk.v5_0.Subnet;
import net.nuagenetworks.vspk.v5_0.VM;
import net.nuagenetworks.vspk.v5_0.VMInterface;
import net.nuagenetworks.vspk.v5_0.VPort;
import net.nuagenetworks.vspk.v5_0.VPort.AddressSpoofing;
import net.nuagenetworks.vspk.v5_0.VPort.Multicast;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.Zone;
import net.nuagenetworks.vspk.v5_0.fetchers.DomainTemplatesFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.DomainsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.SubnetsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VMsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VPortsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.ZonesFetcher;

/**
 * Idempotently populates a given VSD Enterprise with a set of Domains, Zones, Subnets, VPorts and VMs
 * 
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Enterprise matching MY_ENTERPRISE_NAME
 */
public class GenericNetworkProvisioning {
    private static final String MY_VSD_SERVER_PORT = "https://192.0.2.10:8443";
    private static final String MY_ENTERPRISE_NAME = "MyLittleEnterprise";

    private List<VMDescriptor> vmInventoryList = new ArrayList<VMDescriptor>() {
        {
            add(new VMDescriptor("Little Domain1", "Little Template", "Zone1", "Subnet1", "VPort1A", "VMInterface1", "VM1", "203.0.113.10",
                    "255.255.255.0", "11111111-1234-abcd-abcd-123456789000", "00:00:22:33:44:55"));
            add(new VMDescriptor("Little Domain1", "Little Template", "Zone1", "Subnet1", "VPort1B", "VMInterface2", "VM2", "203.0.113.10",
                    "255.255.255.0", "22222222-1234-abcd-abcd-123456789000", "00:11:22:33:44:55"));

            add(new VMDescriptor("Little Domain1", "Little Template", "Zone1", "Subnet2", "VPort2A", "VMInterface2", "VM1", "203.0.113.20",
                    "255.255.255.0", "33333333-1234-abcd-abcd-123456789000", "00:22:22:33:44:55"));
            add(new VMDescriptor("Little Domain1", "Little Template", "Zone1", "Subnet2", "VPort2B", "VMInterface1", "VM2", "203.0.113.20",
                    "255.255.255.0", "44444444-1234-abcd-abcd-123456789000", "00:33:22:33:44:55"));

            add(new VMDescriptor("Little Domain1", "Little Template", "Zone1", "Subnet3", "VPort3A", "VMInterface1", "VM1", "203.0.113.30",
                    "255.255.255.0", "55555555-1234-abcd-abcd-123456789000", "00:44:22:33:44:55"));
            add(new VMDescriptor("Little Domain1", "Little Template", "Zone1", "Subnet3", "VPort3B", "VMInterface2", "VM2", "203.0.113.30",
                    "255.255.255.0", "66666666-1234-abcd-abcd-123456789000", "00:55:22:33:44:55"));

            add(new VMDescriptor("Little Domain1", "Little Template", "Zone2", "Subnet4", "VPort4A", "VMInterface1", "VM1", "203.0.113.40",
                    "255.255.255.0", "77777777-1234-abcd-abcd-123456789000", "00:66:22:33:44:55"));
            add(new VMDescriptor("Little Domain1", "Little Template", "Zone2", "Subnet4", "VPort4B", "VMInterface2", "VM2", "203.0.113.40",
                    "255.255.255.0", "88888888-1234-abcd-abcd-123456789000", "00:77:22:33:44:55"));

            add(new VMDescriptor("Little Domain1", "Little Template", "Zone2", "Subnet5", "VPort5A", "VMInterface2", "VM1", "203.0.113.50",
                    "255.255.255.0", "99999999-1234-abcd-abcd-123456789000", "00:88:22:33:44:55"));
            add(new VMDescriptor("Little Domain1", "Little Template", "Zone2", "Subnet5", "VPort5B", "VMInterface1", "VM2", "203.0.113.50",
                    "255.255.255.0", "00000000-1234-abcd-abcd-123456789000", "00:99:22:33:44:55"));

            add(new VMDescriptor("Little Domain1", "Little Template", "Zone2", "Subnet6", "VPort6A", "VMInterface1", "VM1", "203.0.113.60",
                    "255.255.255.0", "11112222-1234-abcd-abcd-123456789000", "00:12:22:33:44:55"));
            add(new VMDescriptor("Little Domain1", "Little Template", "Zone2", "Subnet6", "VPort6B", "VMInterface2", "VM2", "203.0.113.60",
                    "255.255.255.0", "33334444-1234-abcd-abcd-123456789000", "00:34:22:33:44:55"));
        }
    };

    private static final VSDSession session;

    public class VMDescriptor {
        public String domainName;
        public String templateName;
        public String zoneName;
        public String subnetName;
        public String vPortName;
        public String vmInterfaceName;
        public String vmName;
        public String subnetAddress;
        public String subnetNetmask;
        public String vmUUID;
        public String vmMAC;

        VMDescriptor(String domainName, String templateName, String zoneName, String subnetName, String vPortName, String vmInterfaceName,
                String vmName, String subnetAddress, String subnetNetmask, String vmUUID, String vmMAC) {
            this.domainName = domainName;
            this.templateName = templateName;
            this.zoneName = zoneName;
            this.subnetName = subnetName;
            this.vPortName = vPortName;
            this.vmInterfaceName = vmInterfaceName;
            this.vmName = vmName;
            this.subnetAddress = subnetAddress;
            this.subnetNetmask = subnetNetmask;
            this.vmUUID = vmUUID;
            this.vmMAC = vmMAC;
        }
    }

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Performing Generic Network Provisioning for Enterprise " + MY_ENTERPRISE_NAME);
        session.start();
        GenericNetworkProvisioning instance = new GenericNetworkProvisioning();
        Enterprise enterprise = instance.fetchEnterpriseByName(MY_ENTERPRISE_NAME);
        if (enterprise != null) {
            instance.createInventory(enterprise);
        } else {
            System.out.println("Provisioning operation not performed");
        }
    }

    private void createInventory(Enterprise enterprise) throws RestException {
        for (VMDescriptor vmDescriptor : this.vmInventoryList) {
            this.populateNetworkObjects(enterprise, vmDescriptor);
        }
    }

    private VM populateNetworkObjects(Enterprise enterprise, VMDescriptor vmDescriptor) throws RestException {
        DomainTemplate template = this.createLevel3DomainTemplateInEnterprise(enterprise, vmDescriptor);
        Domain l3Domain = this.createLevel3DomainForEnterprise(template, enterprise, vmDescriptor);
        Zone zone = this.createZoneForLevel3Domain(l3Domain, vmDescriptor);
        Subnet subnet = this.createSubnetForZone(zone, vmDescriptor);
        VPort vPort = this.createVPortForSubnet(subnet, vmDescriptor);
        VM vm = this.createVMForVPort(vPort, vmDescriptor);
        return vm;
    }

    private DomainTemplate createLevel3DomainTemplateInEnterprise(Enterprise enterprise, VMDescriptor vmDescriptor) throws RestException {
        DomainTemplate domainTemplate = this.fetchLevel3DomainTemplateByNameForEnterprise(vmDescriptor.templateName, enterprise);
        if (domainTemplate == null) {
            domainTemplate = new DomainTemplate();
            domainTemplate.setName(vmDescriptor.templateName);
            System.out.println("Creating Level 3 Domain Template " + domainTemplate.getName());
            enterprise.createChild(domainTemplate);
        }
        return domainTemplate;
    }

    private Domain createLevel3DomainForEnterprise(DomainTemplate domainTemplate, Enterprise enterprise, VMDescriptor vmDescriptor)
            throws RestException {
        Domain domain = this.fetchLevel3DomainByNameForEnterprise(vmDescriptor.domainName, enterprise);
        if (domain == null) {
            domain = new Domain();
            domain.setName(vmDescriptor.domainName);
            domain.setTemplateID(domainTemplate.getId());
            System.out.println("Creating Level 3 Domain " + domain.getName());
            enterprise.createChild(domain);
        }
        return domain;
    }

    private Zone createZoneForLevel3Domain(Domain l3Domain, VMDescriptor vmDescriptor) throws RestException {
        Zone zone = this.fetchZoneByNameForL3Domain(vmDescriptor.zoneName, l3Domain);
        if (zone == null) {
            zone = new Zone();
            zone.setName(vmDescriptor.zoneName);
            l3Domain.createChild(zone);
            System.out.println("Creating Zone " + zone.getName());
        }
        return zone;
    }

    private Subnet createSubnetForZone(Zone zone, VMDescriptor vmDescriptor) throws RestException {
        Subnet subnet = this.fetchSubnetByNameForZone(vmDescriptor.subnetName, zone);
        if (subnet == null) {
            subnet = new Subnet();
            subnet.setName(vmDescriptor.subnetName);
            subnet.setAddress(vmDescriptor.subnetAddress);
            subnet.setNetmask(vmDescriptor.subnetNetmask);
            System.out.println("Creating Subnet " + subnet.getName());
            zone.createChild(subnet);
        }
        return subnet;
    }

    private VPort createVPortForSubnet(Subnet subnet, VMDescriptor vmDescriptor) throws RestException {
        VPort vPort = this.fetchVPortByNameForSubnet(vmDescriptor.vPortName, subnet);
        if (vPort == null) {
            vPort = new VPort();
            vPort.setName(vmDescriptor.vPortName);
            vPort.setType(VPort.Type.VM);
            vPort.setAddressSpoofing(AddressSpoofing.INHERITED);
            vPort.setMulticast(Multicast.INHERITED);
            System.out.println("Creating Vport " + vPort.getName());
            subnet.createChild(vPort);
        }
        return vPort;
    }

    private VM createVMForVPort(VPort vPort, VMDescriptor vmDescriptor) throws RestException {
        VM vm = this.fetchVMByUUIDForVPort(vmDescriptor.vmUUID, vPort);
        if (vm == null) {
            vm = new VM();
            vm.setName(vmDescriptor.vmName);
            vm.setUUID(vmDescriptor.vmUUID);
            List<VMInterface> vmInterfaces = new ArrayList<>();
            VMInterface vmInterface = new VMInterface();
            vmInterface.setName(vmDescriptor.vmInterfaceName);
            vmInterface.setMAC(vmDescriptor.vmMAC);
            vmInterface.setVPortID(vPort.getId());
            vmInterfaces.add(vmInterface);
            vm.setInterfaces(vmInterfaces);
            System.out.println("Creating VM " + vm.getName());
            Me me = session.getMe();
            me.createChild(vm);
        }
        return vm;
    }

    private Domain fetchLevel3DomainByNameForEnterprise(String domainName, Enterprise enterprise) throws RestException {
        String filter = String.format("name == '%s'", domainName);
        DomainsFetcher fetcher = enterprise.getDomains();
        Domain l3Domain = fetcher.getFirst(filter, null, null, null, null, null, true);
        if (l3Domain != null) {
            Date createDate = new Date(Long.parseLong(l3Domain.getCreationDate()));
            System.out.println("Found Level 3 Domain " + l3Domain.getName() + " created at " + createDate.toString());
        }
        return l3Domain;
    }

    private Zone fetchZoneByNameForL3Domain(String zoneName, Domain domain) throws RestException {
        String filter = String.format("name == '%s'", zoneName);
        ZonesFetcher fetcher = domain.getZones();
        Zone zone = fetcher.getFirst(filter, null, null, null, null, null, true);
        if (zone != null) {
            Date createDate = new Date(Long.parseLong(zone.getCreationDate()));
            System.out.println("Found Zone " + zone.getName() + " created at " + createDate.toString());
        }
        return zone;
    }

    private Subnet fetchSubnetByNameForZone(String subnetName, Zone zone) throws RestException {
        String filter = String.format("name == '%s'", subnetName);
        SubnetsFetcher fetcher = zone.getSubnets();
        Subnet subnet = fetcher.getFirst(filter, null, null, null, null, null, true);
        if (subnet != null) {
            Date createDate = new Date(Long.parseLong(subnet.getCreationDate()));
            System.out.println("Found Subnet " + subnet.getName() + " created at " + createDate.toString());
        }
        return subnet;
    }

    private VPort fetchVPortByNameForSubnet(String vPortName, Subnet subnet) throws RestException {
        String filter = String.format("name == '%s'", vPortName);
        VPortsFetcher fetcher = subnet.getVPorts();
        VPort vport = fetcher.getFirst(filter, null, null, null, null, null, true);
        if (vport != null) {
            Date createDate = new Date(Long.parseLong(vport.getCreationDate()));
            System.out.println("Found VPort " + vport.getName() + " created at " + createDate.toString());
        }
        return vport;
    }

    private VM fetchVMByUUIDForVPort(String uuid, VPort vPort) throws RestException {
        String filter = String.format("UUID == '%s'", uuid);
        VMsFetcher fetcher = vPort.getVMs();
        VM vm = fetcher.getFirst(filter, null, null, null, null, null, true);
        if (vm != null) {
            Date createDate = new Date(Long.parseLong(vm.getCreationDate()));
            System.out.println("Found VM " + vm.getName() + " created at " + createDate.toString());
        }
        return vm;
    }

    private Enterprise fetchEnterpriseByName(String enterpriseName) throws RestException {
        String filter = String.format("name == '%s'", enterpriseName);
        EnterprisesFetcher fetcher = session.getMe().getEnterprises();
        Enterprise enterprise = fetcher.getFirst(filter, null, null, null, null, null, true);
        if (enterprise != null) {
            Date createDate = new Date(Long.parseLong(enterprise.getCreationDate()));
            System.out.println("Found Enterprise " + enterprise.getName() + " created at " + createDate.toString());
        } else {
            System.out.println("Enterprise " + enterpriseName + " was not found");
        }
        return enterprise;
    }

    private DomainTemplate fetchLevel3DomainTemplateByNameForEnterprise(String templateName, Enterprise enterprise) throws RestException {
        String filter = String.format("name == '%s'", templateName);
        DomainTemplatesFetcher fetcher = enterprise.getDomainTemplates();
        DomainTemplate template = fetcher.getFirst(filter, null, null, null, null, null, true);
        if (template != null) {
            Date createDate = new Date(Long.parseLong(template.getCreationDate()));
            System.out.println("Found Level 3 Domain Template : " + template.getName() + " created at : " + createDate.toString());
        }
        return template;
    }
}
