import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v4_0.DHCPOption;
import net.nuagenetworks.vspk.v4_0.VSDSession;
import net.nuagenetworks.vspk.v4_0.Zone;
import net.nuagenetworks.vspk.v4_0.fetchers.ZonesFetcher;

/**
 * Creates a DHCP Option for DNS Servers in an existing Zone
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Zone matching MY_ZONE_NAME. See CreateZone.java
 */
public class CreateDhcpOptionForDnsServersInZone {
	private static final String MY_VSD_SERVER_PORT = "https://135.121.118.59:8443";
	private static final Long MY_DHCP_OPTION_FOR_DNS = 6L;
	private static final String MY_ZONE_NAME = "MyLittleZonexx";
	private static final VSDSession session;

	static {
		session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
	}

	public static void main(String[] args) throws RestException {
		System.out.println("Creating DHCP Option for DNS Servers in Zone : " + MY_ZONE_NAME);
		session.start();
		CreateDhcpOptionForDnsServersInZone instance = new CreateDhcpOptionForDnsServersInZone();
		Zone zone = instance.fetchZoneByName(MY_ZONE_NAME);
		instance.createDhcpOptionForZone(zone);
	}

	private void createDhcpOptionForZone(Zone zone) throws RestException {
		DHCPOption option = new DHCPOption();
		List<String> values = new ArrayList<>();
		values.add("10.100.50.50");
		values.add("10.100.60.60");
		option.setActualType(MY_DHCP_OPTION_FOR_DNS);
		option.setActualValues(values);
		zone.createChild(option);
	}

	private Zone fetchZoneByName(String zoneName) throws RestException {
		String filter = String.format("name == '%s'", zoneName);
		ZonesFetcher fetcher = session.getMe().getZones();
		Zone zone = fetcher.getFirst(filter, null, null, null, null, null, true);
		Date createDate = new Date(Long.parseLong(zone.getCreationDate()));
		System.out.println("Zone : " + zone.getName() + " was created at : " + createDate.toString());
		return zone;
	}
}
