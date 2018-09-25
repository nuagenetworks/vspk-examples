import java.util.Date;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Subnet;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.Zone;
import net.nuagenetworks.vspk.v5_0.fetchers.SubnetsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.ZonesFetcher;

/**
 * Idempotently creates a VSD Subnet object given its parent Zone ID
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Zone matching MY_ZONE_ID
 */
public class CreateSubnetForZoneId {
    private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final String MY_ZONE_ID = "db523956-4051-4c29-ba16-1f09f8eb3ca1";
    private static final String MY_SUBNET_NAME = "MyLittleSubnet1";
    private static final String MY_SUBNET_ADDRESS = "10.117.18.0";
    private static final String MY_SUBNET_NETMASK = "255.255.255.0";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static class SubnetDescriptor {
        public String subnetName;
        public String subnetAddress;
        public String subnetNetmask;

        SubnetDescriptor(String subnetName, String subnetAddress, String subnetNetmask) {
            this.subnetName = subnetName;
            this.subnetAddress = subnetAddress;
            this.subnetNetmask = subnetNetmask;
        }
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating Subnet : " + MY_SUBNET_NAME + " in Zone " + MY_ZONE_ID);
        session.start();
        CreateSubnetForZoneId instance = new CreateSubnetForZoneId();
        SubnetDescriptor subnetDescriptor = new SubnetDescriptor(MY_SUBNET_NAME, MY_SUBNET_ADDRESS, MY_SUBNET_NETMASK);
        Zone zone = instance.fetchZoneById(MY_ZONE_ID);
        if (zone != null) {
            instance.createSubnetForZone(subnetDescriptor, zone);
        } else {
            System.out.println("Operation not performed due to missing Zone " + MY_ZONE_ID);
        }
    }
    
    private Subnet createSubnetForZone(SubnetDescriptor subnetDescriptor, Zone zone) throws RestException {
        Subnet subnet = this.fetchSubnetByNameForZone(subnetDescriptor.subnetName, zone);
        if (subnet == null) {
            subnet = new Subnet();
            subnet.setName(subnetDescriptor.subnetName);
            subnet.setAddress(subnetDescriptor.subnetAddress);
            subnet.setNetmask(subnetDescriptor.subnetNetmask);
            zone.createChild(subnet);
            Date createDate = new Date(Long.parseLong(subnet.getCreationDate()));
            System.out.println("New Subnet created with id " + subnet.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(subnet.getCreationDate()));
            System.out.println("Old Subnet " + subnet.getName() + " already created at " + createDate.toString());
        }
        return subnet;
    }

    private Subnet fetchSubnetByNameForZone(String subnetName, Zone zone) throws RestException {
        String filter = String.format("name == '%s'", subnetName);
        SubnetsFetcher fetcher = zone.getSubnets();
        Subnet subnet = fetcher.getFirst(filter, null, null, null, null, null, true);
        return subnet;
    }

    private Zone fetchZoneById(String id) throws RestException {
        String filter = String.format("ID == '%s'", id);
        ZonesFetcher fetcher = session.getMe().getZones();
        Zone zone = fetcher.getFirst(filter, null, null, null, null, null, true);
        return zone;
    }
}
