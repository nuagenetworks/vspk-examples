import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.DHCPOption;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.Zone;
import net.nuagenetworks.vspk.v5_0.fetchers.DHCPOptionsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.ZonesFetcher;

/**
 * Idempotently creates a DHCP Option for DNS Servers in an existing Zone
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Zone matching MY_ZONE_ID
 */
public class CreateDhcpOptionForDnsServersOfZoneId {
    private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final String MY_DHCP_OPTION_FOR_DNS_AS_HEX = "06";
    private static final String MY_ZONE_ID = "a0f6e8e6-5d3d-4387-9472-392a072f6b9f";
    private static final List<String> MY_DNS_SERVERS = new ArrayList<>(Arrays.asList("10.100.50.50", "10.100.60.60"));
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating DHCP Option for DNS Servers in Zone : " + MY_ZONE_ID);
        session.start();
        CreateDhcpOptionForDnsServersOfZoneId instance = new CreateDhcpOptionForDnsServersOfZoneId();

        Zone zone = instance.fetchZoneById(MY_ZONE_ID);
        if (zone != null) {
            instance.createDhcpOptionForZone(MY_DHCP_OPTION_FOR_DNS_AS_HEX, MY_DNS_SERVERS, zone);
        } else {
            System.out.println("Operation not performed due to missing Zone " + MY_ZONE_ID);
        }
    }

    private DHCPOption createDhcpOptionForZone(String hexOptionType, List<String> servers, Zone zone) throws RestException {
        DHCPOption option = this.fetchDHCPOptionByNameForZone(hexOptionType, zone);
        if (option == null) {
            option = new DHCPOption();
            Long decOptionType = Long.parseLong(hexOptionType, 16);
            option.setActualType(decOptionType);
            option.setActualValues(servers);
            zone.createChild(option);
            Date createDate = new Date(Long.parseLong(option.getCreationDate()));
            System.out.println("New DHCP Option created with id " + option.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(option.getCreationDate()));
            System.out.println("Old DHCP Option " + option.getActualType() + " already created at " + createDate.toString());
        }
        return option;
    }

    private DHCPOption fetchDHCPOptionByNameForZone(String hexOptionType, Zone zone) throws RestException {
        String filter = String.format("type == '%s'", hexOptionType);
        DHCPOptionsFetcher fetcher = zone.getDHCPOptions();
        DHCPOption option = fetcher.getFirst(filter, null, null, null, null, null, true);
        return option;
    }

    private Zone fetchZoneById(String id) throws RestException {
        String filter = String.format("ID == '%s'", id);
        ZonesFetcher fetcher = session.getMe().getZones();
        Zone zone = fetcher.getFirst(filter, null, null, null, null, null, true);
        return zone;
    }
}
