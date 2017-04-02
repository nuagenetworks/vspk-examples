import java.util.Date;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v4_0.Subnet;
import net.nuagenetworks.vspk.v4_0.VPort;
import net.nuagenetworks.vspk.v4_0.VSDSession;
import net.nuagenetworks.vspk.v4_0.fetchers.SubnetsFetcher;

/**
 * Creates a VPort for a Subnet
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Subnet matching MY_SUBNET_NAME.  See CreateSubnet.java
*/
public class CreateVPortForSubnet {
    private static final String MY_VSD_SERVER_PORT	= "https://135.121.118.59:8443";
    private static final String MY_SUBNET_NAME		= "MyLittleSubnet";
    private static final String MY_VPORT_NAME		= "MyLittleVPort";
    private static final VSDSession session;
    
    static { session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT); }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating Zone : " + MY_VPORT_NAME + " in Subnet " + MY_SUBNET_NAME);
        session.start();
        CreateVPortForSubnet	instance	= new CreateVPortForSubnet();
        Subnet					subnet		= instance.fetchSubnetByName(MY_SUBNET_NAME);
        instance.createVPortInSubnet(subnet);
    }

	private void createVPortInSubnet(Subnet subnet) throws RestException {
		VPort vPort = new VPort();
		vPort.setName(MY_VPORT_NAME);
		subnet.createChild(vPort);
	}

	private Subnet fetchSubnetByName(String subnetName) throws RestException {
        String			filter		= String.format("name == '%s'", subnetName);
    	SubnetsFetcher	fetcher		= session.getMe().getSubnets();
    	Subnet			subnet		= fetcher.getFirst(filter, null, null, null, null, null, true);
        Date			createDate	= new Date(Long.parseLong(subnet.getCreationDate()));
        System.out.println("Subnet : " + subnet.getName() + " was created at : " + createDate.toString());
        return subnet;
	}
}
