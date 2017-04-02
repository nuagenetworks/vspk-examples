import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v4_0.DHCPOption;
import net.nuagenetworks.vspk.v4_0.Subnet;
import net.nuagenetworks.vspk.v4_0.VSDSession;
import net.nuagenetworks.vspk.v4_0.fetchers.SubnetsFetcher;

/**
 * Creates a DHCP Option for SMTP Servers in an existing Subnet
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Subnet matching MY_SUBNET_NAME.  See CreateSubnet.java
*/
public class CreateDhcpOptionForSmtpServersInSubnet {
    private static final String MY_VSD_SERVER_PORT		= "https://135.121.118.59:8443";
    private static final Long MY_DHCP_OPTION_FOR_SMTP	= 69L;
    private static final String MY_SUBNET_NAME			= "MyLittleSubnet";
    private static final VSDSession session;
    
    static { session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT); }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating DHCP Option for SMTP Servers in Subnet : " + MY_SUBNET_NAME);
        session.start();
        CreateDhcpOptionForSmtpServersInSubnet	instance	= new CreateDhcpOptionForSmtpServersInSubnet();
        Subnet									subnet		= instance.fetchSubnetByName(MY_SUBNET_NAME);
        instance.createDhcpOptionForSubnet(subnet);
    }

	private void createDhcpOptionForSubnet(Subnet subnet) throws RestException {
		DHCPOption option = new DHCPOption();
		List<String> values = new ArrayList<>();
		values.add("10.100.10.10");
		values.add("10.100.10.11");
		values.add("10.100.10.12");
		values.add("10.100.10.13");
		option.setActualType(MY_DHCP_OPTION_FOR_SMTP);
		option.setActualValues(values);
		subnet.createChild(option);
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
