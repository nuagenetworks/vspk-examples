import java.util.List;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Subnet;
import net.nuagenetworks.vspk.v5_0.VM;
import net.nuagenetworks.vspk.v5_0.VPort;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.SubnetsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VMsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VPortsFetcher;

/**
 * Idempotently deletes the VM and VPort objects associated with a given VSD Subnet
 * 
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Subnet matching MY_SUBNET_ID
 * Precondition - requires 0 or more existing VPorts
 * Precondition - requires 0 or more existing VMs
 */
public class DeleteVPortsAndVMsForSubnetId {
	private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final String MY_SUBNET_ID = "99142dd3-2980-40a6-8280-8ec0c0d2234d";
	private static final VSDSession session;

	static {
		session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
	}

	public static void main(String[] args) throws RestException {
        System.out.println("Deleting objects associated with Subnet " + MY_SUBNET_ID);
		session.start();
		DeleteVPortsAndVMsForSubnetId instance = new DeleteVPortsAndVMsForSubnetId();

        Subnet subnet = instance.fetchSubnetById(MY_SUBNET_ID);
        if (subnet != null) {
            instance.deleteObjectsOfSubnet(subnet);
        } else {
            System.out.println("Operation not performed due to missing Subnet " + MY_SUBNET_ID);
        }
	}

    private void deleteObjectsOfSubnet(Subnet subnet) throws RestException {
        this.deleteAllVMsOfSubnet(subnet);
        this.deleteAllVPortsOfSubnet(subnet);
    }

    private void deleteAllVMsOfSubnet(Subnet subnet) throws RestException {
        VMsFetcher fetcher = subnet.getVMs();
        List<VM> vms = fetcher.get();
        for (VM vm : vms) {
            System.out.println("Deleting VM " + vm.getName());
            vm.delete();
        }
    }

    private void deleteAllVPortsOfSubnet(Subnet subnet) throws RestException {
        VPortsFetcher fetcher = subnet.getVPorts();
        List<VPort> vPorts = fetcher.get();
        for (VPort vPort : vPorts) {
            System.out.println("Deleting VPort " + vPort.getName());
            vPort.delete();
        }
    }

    private Subnet fetchSubnetById(String id) throws RestException {
        String filter = String.format("ID == '%s'", id);
        SubnetsFetcher fetcher = session.getMe().getSubnets();
        Subnet subnet = fetcher.getFirst(filter, null, null, null, null, null, true);
        return subnet;
    }
}
