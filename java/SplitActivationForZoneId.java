import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Me;
import net.nuagenetworks.vspk.v5_0.Subnet;
import net.nuagenetworks.vspk.v5_0.VM;
import net.nuagenetworks.vspk.v5_0.VMInterface;
import net.nuagenetworks.vspk.v5_0.VPort;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.Zone;
import net.nuagenetworks.vspk.v5_0.fetchers.SubnetsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VMsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VPortsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.ZonesFetcher;

/**
 * Idempotently creates a Subnet, VPort, VMInterface, and VM object for a Zone, as would be typical steps during Split Activation
 * 
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Zone matching MY_ZONE_ID
 */
public class SplitActivationForZoneId {
    private static final String MY_VSD_SERVER_PORT = "https://192.0.2.10:8443";
    private static final String MY_ZONE_ID = "75e99dea-8a05-4c57-92c3-2cb00c42415f";
    private static final String MY_SUBNET_NAME = "MyLittleSubnet1";
    private static final String MY_SUBNET_ADDRESS = "203.0.113.0";
    private static final String MY_SUBNET_NETMASK = "255.255.255.0";
    private static final String MY_VPORT_NAME = "MySplitActivationVPort";
    private static final String MY_VM_NAME = "MySplitActivationVM";
    private static final String MY_VM_UUID = "12345678-eeee-abcd-abcd-123456789012";
    private static final String MY_VM_INTERFACE_NAME = "MySplitActivationInterface";
    private static final String MY_VM_INTERFACE_MAC = "00:11:22:33:44:77";
    private static final String MY_VM_INTERFACE_IP = "203.0.113.5";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static class VmDescriptor {
        public String subnetName;
        public String subnetAddress;
        public String subnetNetmask;
        public String vportName;
        public String vmUUID;
        public String vmName;
        public String vmInterfaceName;
        public String vmMAC;
        public String vmIP;

        VmDescriptor(String subnetName, String subnetAddress, String subnetNetmask, String vportName, String vmUUID, String vmName,
                String vmInterfaceName, String vmMAC, String vmIP) {
            this.subnetName = subnetName;
            this.subnetAddress = subnetAddress;
            this.subnetNetmask = subnetNetmask;
            this.vportName = vportName;
            this.vmUUID = vmUUID;
            this.vmName = vmName;
            this.vmInterfaceName = vmInterfaceName;
            this.vmMAC = vmMAC;
            this.vmIP = vmIP;
        }
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating VM " + MY_VM_NAME + " in Zone " + MY_ZONE_ID);
        session.start();
        SplitActivationForZoneId instance = new SplitActivationForZoneId();

        VmDescriptor vmDescriptor = new VmDescriptor(MY_SUBNET_NAME, MY_SUBNET_ADDRESS, MY_SUBNET_NETMASK, MY_VPORT_NAME, MY_VM_UUID, MY_VM_NAME,
                MY_VM_INTERFACE_NAME, MY_VM_INTERFACE_MAC, MY_VM_INTERFACE_IP);

        Zone zone = instance.fetchZoneById(MY_ZONE_ID);
        if (zone != null) {
            Subnet subnet = instance.createSubnetForZone(vmDescriptor, zone);
            VPort vport = instance.createVPortForSubnet(vmDescriptor, subnet);
            instance.createVMForVPort(vport, vmDescriptor);
        } else {
            System.out.println("Operation not performed due to missing Zone " + MY_ZONE_ID);
        }
    }

    private Subnet createSubnetForZone(VmDescriptor vmDescriptor, Zone zone) throws RestException {
        Subnet subnet = this.fetchSubnetByNameForZone(vmDescriptor.subnetName, zone);
        if (subnet == null) {
            subnet = new Subnet();
            subnet.setName(vmDescriptor.subnetName);
            subnet.setAddress(vmDescriptor.subnetAddress);
            subnet.setNetmask(vmDescriptor.subnetNetmask);
            zone.createChild(subnet);
            Date createDate = new Date(Long.parseLong(subnet.getCreationDate()));
            System.out.println("New Subnet created with id " + subnet.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(subnet.getCreationDate()));
            System.out.println("Old Subnet " + subnet.getName() + " already created at " + createDate.toString());
        }
        return subnet;
    }

    private VPort createVPortForSubnet(VmDescriptor vmDescriptor, Subnet subnet) throws RestException {
        VPort vport = this.fetchVPortByNameForSubnet(vmDescriptor.vportName, subnet);
        if (vport == null) {
            vport = new VPort();
            vport.setName(vmDescriptor.vportName);
            vport.setType(VPort.Type.VM);
            subnet.createChild(vport);
            Date createDate = new Date(Long.parseLong(vport.getCreationDate()));
            System.out.println("New VPort created with id " + vport.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(vport.getCreationDate()));
            System.out.println("Old VPort " + vport.getName() + " already created at " + createDate.toString());
        }
        return vport;
    }

    private VM createVMForVPort(VPort vPort, VmDescriptor vmDescriptor) throws RestException {
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
            vmInterface.setIPAddress(vmDescriptor.vmIP);
            vm.setInterfaces(vmInterfaces);
            System.out.println("Creating VM " + vm.getName());
            Me me = session.getMe();
            me.createChild(vm);
            Date createDate = new Date(Long.parseLong(vm.getCreationDate()));
            System.out.println("New VM created with id " + vm.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(vm.getCreationDate()));
            System.out.println("Old VM " + vm.getName() + " already created at " + createDate.toString());
        }
        return vm;
    }

    private Zone fetchZoneById(String id) throws RestException {
        String filter = String.format("ID == '%s'", id);
        ZonesFetcher fetcher = session.getMe().getZones();
        Zone zone = fetcher.getFirst(filter, null, null, null, null, null, true);
        return zone;
    }

    private Subnet fetchSubnetByNameForZone(String subnetName, Zone zone) throws RestException {
        String filter = String.format("name == '%s'", subnetName);
        SubnetsFetcher fetcher = zone.getSubnets();
        Subnet subnet = fetcher.getFirst(filter, null, null, null, null, null, true);
        return subnet;
    }

    private VPort fetchVPortByNameForSubnet(String vportName, Subnet subnet) throws RestException {
        String filter = String.format("name == '%s'", vportName);
        VPortsFetcher fetcher = subnet.getVPorts();
        VPort vport = fetcher.getFirst(filter, null, null, null, null, null, true);
        return vport;
    }

    private VM fetchVMByUUIDForVPort(String uuid, VPort vPort) throws RestException {
        String filter = String.format("UUID == '%s'", uuid);
        VMsFetcher fetcher = vPort.getVMs();
        VM vm = fetcher.getFirst(filter, null, null, null, null, null, true);
        return vm;
    }

}
