import java.util.Date;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v4_0.Domain;
import net.nuagenetworks.vspk.v4_0.VSDSession;
import net.nuagenetworks.vspk.v4_0.Zone;
import net.nuagenetworks.vspk.v4_0.fetchers.DomainsFetcher;

/**
 * Creates a Zone for a Level 3 Domain
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Level 3 Domain matching MY_L3_DOMAIN_NAME.  See CreateLevel3Domain.java
*/
public class CreateZone {
    private static final String MY_VSD_SERVER_PORT	= "https://135.121.118.59:8443";
    private static final String MY_L3_DOMAIN_NAME	= "MyLittleLevel3Domain";
    private static final String MY_ZONE_NAME		= "MyLittleZone";
    private static final VSDSession session;
    
    static { session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT); }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating Zone : " + MY_ZONE_NAME + " in Level 3 Domain " + MY_L3_DOMAIN_NAME);
        session.start();
        CreateZone	instance	= new CreateZone();
        Domain		l3Domain	= instance.fetchLevel3DomainByName(MY_L3_DOMAIN_NAME);
        instance.createZoneInLevel3Domain(l3Domain);
    }

	private void createZoneInLevel3Domain(Domain l3Domain) throws RestException {
		Zone zone = new Zone();
		zone.setName(MY_ZONE_NAME);
		l3Domain.createChild(zone);
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
