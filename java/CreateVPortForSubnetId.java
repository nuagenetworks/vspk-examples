import java.util.Date;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Subnet;
import net.nuagenetworks.vspk.v5_0.VPort;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.SubnetsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VPortsFetcher;

/**
 * Idempotently creates a VSD VPort object given its parent Subnet ID
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Subnet matching MY_SUBNET_ID
 */
public class CreateVPortForSubnetId {
	private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
	private static final String MY_SUBNET_ID = "e54e951d-8503-495d-9164-a3bb935fc9f1";
	private static final String MY_VPORT_NAME = "MyLittleVPort1";
	private static final VSDSession session;

	static {
		session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
	}

	public static void main(String[] args) throws RestException {
		System.out.println("Creating VPort : " + MY_VPORT_NAME + " in Subnet " + MY_SUBNET_ID);
		session.start();
		CreateVPortForSubnetId instance = new CreateVPortForSubnetId();
        Subnet subnet = instance.fetchSubnetById(MY_SUBNET_ID);
        if (subnet != null) {
            instance.createVPortInSubnet(MY_VPORT_NAME, subnet);
        } else {
            System.out.println("Operation not performed due to missing Subnet " + MY_SUBNET_ID);
        }
	}

	private VPort createVPortInSubnet(String vportName, Subnet subnet) throws RestException {
	    VPort vport = this.fetchVPortByNameForSubnet(vportName, subnet);
	    if (vport == null) {
	        vport = new VPort();
	        vport.setName(vportName);
	        subnet.createChild(vport);
            Date createDate = new Date(Long.parseLong(vport.getCreationDate()));
            System.out.println("New VPort created with id " + vport.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(vport.getCreationDate()));
            System.out.println("Old VPort " + vport.getName() + " already created at " + createDate.toString());
	    }
		return vport;
	}
	
	private VPort fetchVPortByNameForSubnet(String vportName, Subnet subnet) throws RestException {
        String filter = String.format("name == '%s'", vportName);
        VPortsFetcher fetcher = subnet.getVPorts();
        VPort vport = fetcher.getFirst(filter, null, null, null, null, null, true);
        return vport;
	}

    private Subnet fetchSubnetById(String id) throws RestException {
        String filter = String.format("ID == '%s'", id);
        SubnetsFetcher fetcher = session.getMe().getSubnets();
        Subnet subnet = fetcher.getFirst(filter, null, null, null, null, null, true);
        return subnet;
    }
}
