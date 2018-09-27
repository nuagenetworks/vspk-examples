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
 * Idempotently deletes objects associated with a given VSD Subnet such as its VMs and VPorts, and finally the Subnet itself
 * 
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Subnet matching MY_SUBNET_ID
 * Precondition - requires 0 or more existing VPorts
 * Precondition - requires 0 or more existing VMs
 */
public class DeleteSubnetAndItsAssociates {
    private static final String MY_VSD_SERVER_PORT = "https://192.0.2.10:8443";
    private static final String MY_SUBNET_ID = "e54e951d-8503-495d-9164-a3bb935fc9f1";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Deleting objects associated with Subnet " + MY_SUBNET_ID);
        session.start();
        DeleteSubnetAndItsAssociates instance = new DeleteSubnetAndItsAssociates();

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
        subnet.delete();
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
