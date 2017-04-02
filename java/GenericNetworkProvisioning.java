import java.util.Date;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v4_0.Domain;
import net.nuagenetworks.vspk.v4_0.Subnet;
import net.nuagenetworks.vspk.v4_0.VPort;
import net.nuagenetworks.vspk.v4_0.VPort.AddressSpoofing;
import net.nuagenetworks.vspk.v4_0.VPort.Multicast;
import net.nuagenetworks.vspk.v4_0.VSDSession;
import net.nuagenetworks.vspk.v4_0.Zone;
import net.nuagenetworks.vspk.v4_0.fetchers.DomainsFetcher;

/**
 * Populates a given Level 3 Domain with a set of Zones, Subnets, and VPorts
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Level 3 Domain matching MY_L3_DOMAIN_NAME.  See CreateLevel3Domain.java
 */
public class GenericNetworkProvisioning {
    private static final String MY_VSD_SERVER_PORT		= "https://135.121.118.59:8443";
    private static final String MY_ZONE_NAME_PREFIX		= "MyLittleZone";
    private static final String MY_L3_DOMAIN_NAME		= "MyLittleLevel3Domain";
    private static final String[] MY_SUBNET_DEFS		= {	"10.117.18.0", "255.255.255.0", "10.117.19.0", "255.255.255.0", "10.117.20.0", "255.255.255.0",
    														"10.117.21.0", "255.255.255.0", "10.117.22.0", "255.255.255.0", "10.117.23.0", "255.255.255.0",
    														"10.117.24.0", "255.255.255.0", "10.117.25.0", "255.255.255.0", "10.117.26.0", "255.255.255.0",
															"10.117.27.0", "255.255.255.0", "10.117.28.0", "255.255.255.0", "10.117.29.0", "255.255.255.0"};
    private static final int NUMBER_OF_ZONES_IN_NETWORK	= 4;
    private static final int NUMBER_OF_SUBNETS_IN_ZONE	= 3;
    private static final int NUMBER_OF_VPORTS_IN_SUBNET	= 5;
    private static final VSDSession session;
    
    static { session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT); }

    public static void main(String[] args) throws RestException {
        System.out.println("Populating Level 3 Domain : " + MY_L3_DOMAIN_NAME);
        session.start();
        GenericNetworkProvisioning	instance	= new GenericNetworkProvisioning();
        Domain						l3Domain	= instance.fetchLevel3DomainByName(MY_L3_DOMAIN_NAME);   
        for (int i = 1; i <= NUMBER_OF_ZONES_IN_NETWORK; ++i) {
        	instance.createZoneForLevel3Domain(l3Domain, i);
        }
    }

	private void createZoneForLevel3Domain(Domain l3Domain, int zoneNumber) throws RestException {
		Zone zone = new Zone();
		zone.setName(MY_ZONE_NAME_PREFIX + zoneNumber);
		l3Domain.createChild(zone);
        System.out.println("Creating Zone : " + zone.getName());
        for (int i = 1; i <= NUMBER_OF_SUBNETS_IN_ZONE; ++i) {
        	this.createSubnetForZone(zone, zoneNumber, i);
        }
	}

	private void createSubnetForZone(Zone zone, int zoneNumber, int subnetNumber) throws RestException {
		Subnet subnet = new Subnet();
		subnet.setName(zone.getName() + " - Subnet " + subnetNumber);
		subnet.setAddress(MY_SUBNET_DEFS[((zoneNumber-1) * 6) + (subnetNumber * 2) - 2]);
		subnet.setNetmask(MY_SUBNET_DEFS[((zoneNumber-1) * 6) + (subnetNumber * 2) - 1]);
        System.out.println("Creating Subnet : " + subnet.getName());
		zone.createChild(subnet);
        for (int i = 1; i <= NUMBER_OF_VPORTS_IN_SUBNET; ++i) {
        	this.createVPortForSubnet(subnet, i);
        }
	}

	private void createVPortForSubnet(Subnet subnet, int vPortNumber) throws RestException {
		VPort vPort = new VPort();
		vPort.setName(subnet.getName() + " - VPort " + vPortNumber);
		vPort.setType(VPort.Type.VM);
		vPort.setAddressSpoofing(AddressSpoofing.INHERITED);
		vPort.setMulticast(Multicast.INHERITED);
        System.out.println("Creating Vport : " + vPort.getName());
		subnet.createChild(vPort);
	}

	private Domain fetchLevel3DomainByName(String domainName) throws RestException {
        String			filter		= String.format("name == '%s'", domainName);
    	DomainsFetcher	fetcher		= session.getMe().getDomains();
    	Domain			l3Domain	= fetcher.getFirst(filter, null, null, null, null, null, true);
        Date			createDate	= new Date(Long.parseLong(l3Domain.getCreationDate()));
        System.out.println("Level 3 Domain : " + l3Domain.getName() + " was created at : " + createDate.toString());
        return l3Domain;
	}
	
}
