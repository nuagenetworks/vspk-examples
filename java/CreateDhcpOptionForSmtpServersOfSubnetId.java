import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.DHCPOption;
import net.nuagenetworks.vspk.v5_0.Subnet;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.DHCPOptionsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.SubnetsFetcher;

/**
 * Idempotently creates a DHCP Option for SMTP Servers in an existing Subnet
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Subnet matching MY_SUBNET_ID
 */
public class CreateDhcpOptionForSmtpServersOfSubnetId {
	private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final String MY_DHCP_OPTION_FOR_SMTP_AS_HEX = "45";
	private static final String MY_SUBNET_ID = "eb788945-d6f3-4fcf-af01-34e24395a0f4";
	private static final List<String> MY_SMTPS = new ArrayList<>(Arrays.asList("10.100.10.10", "10.100.10.11", "10.100.10.12", "10.100.10.13"));
	private static final VSDSession session;

	static {
		session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
	}

	public static void main(String[] args) throws RestException {
		System.out.println("Creating DHCP Option for SMTP Servers in Subnet : " + MY_SUBNET_ID);
		session.start();
		CreateDhcpOptionForSmtpServersOfSubnetId instance = new CreateDhcpOptionForSmtpServersOfSubnetId();

		Subnet subnet = instance.fetchSubnetById(MY_SUBNET_ID);
        if (subnet != null) {
            instance.createDhcpOptionForSubnet(MY_DHCP_OPTION_FOR_SMTP_AS_HEX, MY_SMTPS, subnet);
        } else {
            System.out.println("Operation not performed due to missing Subnet " + MY_SUBNET_ID);
        }
	}

	private DHCPOption createDhcpOptionForSubnet(String hexOptionType, List<String> servers, Subnet subnet) throws RestException {
        DHCPOption option = this.fetchDHCPOptionByNameForSubnet(hexOptionType, subnet);
        if (option == null) {
            option = new DHCPOption();
            Long decOptionType = Long.parseLong(hexOptionType, 16);
            option.setActualType(decOptionType);
            option.setActualValues(servers);
            subnet.createChild(option);
            Date createDate = new Date(Long.parseLong(option.getCreationDate()));
            System.out.println("New DHCP Option created with id " + option.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(option.getCreationDate()));
            System.out.println("Old DHCP Option " + option.getActualType() + " already created at " + createDate.toString());
        }
        return option;
	}

    private DHCPOption fetchDHCPOptionByNameForSubnet(String hexOptionType, Subnet subnet) throws RestException {
        String filter = String.format("type == '%s'", hexOptionType);
        DHCPOptionsFetcher fetcher = subnet.getDHCPOptions();
        DHCPOption option = fetcher.getFirst(filter, null, null, null, null, null, true);
        return option;
    }

    private Subnet fetchSubnetById(String id) throws RestException {
        String filter = String.format("ID == '%s'", id);
        SubnetsFetcher fetcher = session.getMe().getSubnets();
        Subnet subnet = fetcher.getFirst(filter, null, null, null, null, null, true);
        return subnet;
    }
}
