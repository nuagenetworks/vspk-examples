import java.util.Date;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v4_0.Subnet;
import net.nuagenetworks.vspk.v4_0.VSDSession;
import net.nuagenetworks.vspk.v4_0.Zone;
import net.nuagenetworks.vspk.v4_0.fetchers.ZonesFetcher;

/**
 * Creates a Subnet in an existing Zone
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Zone matching MY_ZONE_NAME.  See CreateZone.java
*/
public class CreateSubnet {
    private static final String MY_VSD_SERVER_PORT	= "https://135.121.118.59:8443";
    private static final String MY_ZONE_NAME		= "MyLittleZone";
    private static final String MY_SUBNET_NAME		= "MyLittleSubnet";
    private static final VSDSession session;
    
    static { session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT); }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating Subnet : " + MY_SUBNET_NAME + " in Zone " + MY_ZONE_NAME);
        session.start();
        CreateSubnet	instance	= new CreateSubnet();
        Zone			zone		= instance.fetchZoneByName(MY_ZONE_NAME);
        instance.createSubnetForZone(zone);
    }

	private void createSubnetForZone(Zone zone) throws RestException {
		Subnet subnet = new Subnet();
		subnet.setName(MY_SUBNET_NAME);
		subnet.setAddress("10.117.18.0");
		subnet.setNetmask("255.255.255.0");
		zone.createChild(subnet);
	}

	private Zone fetchZoneByName(String zoneName) throws RestException {
        String			filter		= String.format("name == '%s'", zoneName);
    	ZonesFetcher	fetcher		= session.getMe().getZones();
    	Zone			zone		= fetcher.getFirst(filter, null, null, null, null, null, true);
        Date			createDate	= new Date(Long.parseLong(zone.getCreationDate()));
        System.out.println("Zone : " + zone.getName() + " was created at : " + createDate.toString());
        return zone;
	}
}
