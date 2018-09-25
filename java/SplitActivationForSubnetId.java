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
import net.nuagenetworks.vspk.v5_0.fetchers.SubnetsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VMsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VPortsFetcher;

/**
 * Idempotently creates a VPort, VMInterface, and VM object for a Subnet, as would be typical steps during Split Activation
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Subnet matching MY_SUBNET_ID
 */
public class SplitActivationForSubnetId {
	private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final String MY_SUBNET_ID = "99142dd3-2980-40a6-8280-8ec0c0d2234d";
	private static final String MY_VPORT_NAME = "MySplitActivationVPort";
    private static final String MY_VM_NAME = "MySplitActivationVM";
    private static final String MY_VM_UUID = "12345678-eeee-abcd-abcd-123456789012";
    private static final String MY_VM_INTERFACE_NAME = "MySplitActivationInterface";
    private static final String MY_VM_INTERFACE_MAC = "00:11:22:33:44:77";
    private static final String MY_VM_INTERFACE_IP = "10.117.18.5";
	private static final VSDSession session;

	static {
		session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
	}

    public static class VmDescriptor {
        public String vportName;
        public String vmUUID;
        public String vmName;
        public String vmInterfaceName;
        public String vmMAC;
        public String vmIP;

        VmDescriptor(String vportName, String vmUUID, String vmName, String vmInterfaceName, String vmMAC, String vmIP) {
            this.vportName = vportName;
            this.vmUUID = vmUUID;
            this.vmName = vmName;
            this.vmInterfaceName = vmInterfaceName;
            this.vmMAC = vmMAC;
            this.vmIP = vmIP;
        }
    }

	public static void main(String[] args) throws RestException {
		System.out.println("Creating VM " + MY_VPORT_NAME + " in Subnet " + MY_SUBNET_ID);
		session.start();
		SplitActivationForSubnetId instance = new SplitActivationForSubnetId();

		VmDescriptor vmDescriptor = new VmDescriptor(MY_VPORT_NAME, MY_VM_UUID, MY_VM_NAME, MY_VM_INTERFACE_NAME, MY_VM_INTERFACE_MAC, MY_VM_INTERFACE_IP);

        Subnet subnet = instance.fetchSubnetById(MY_SUBNET_ID);
        if (subnet != null) {
            VPort vport = instance.createVPortForSubnet(vmDescriptor, subnet);
            instance.createVMForVPort(vport, vmDescriptor);
        } else {
            System.out.println("Operation not performed due to missing Subnet " + MY_SUBNET_ID);
        }
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

    private Subnet fetchSubnetById(String id) throws RestException {
        String filter = String.format("ID == '%s'", id);
        SubnetsFetcher fetcher = session.getMe().getSubnets();
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
