import java.util.Date;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Domain;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.Zone;
import net.nuagenetworks.vspk.v5_0.fetchers.DomainsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.ZonesFetcher;

/**
 * Idempotently creates a VSD Zone object given its parent Level 3 Domain Name and parent Enterprise ID
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Enterprise matching MY_ENTERPRISE_ID
 * Precondition - requires an existing Level 3 Domain matching MY_L3_DOMAIN_NAME
 */
public class CreateZoneForDomainNameOfEnterpriseId {
	private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final String MY_ENTERPRISE_ID = "454125d0-0b55-4fd3-9349-afab655a16c6";
    private static final String MY_L3_DOMAIN_NAME = "MyLittleLevel3Domain";
	private static final String MY_ZONE_NAME = "MyLittleZone2";
	private static final VSDSession session;

	static {
		session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
	}

	public static void main(String[] args) throws RestException {
		System.out.println("Creating Zone " + MY_ZONE_NAME + " in Level 3 Domain " + MY_L3_DOMAIN_NAME);
		session.start();
		CreateZoneForDomainNameOfEnterpriseId instance = new CreateZoneForDomainNameOfEnterpriseId();

        Enterprise enterprise = instance.fetchEnterpriseById(MY_ENTERPRISE_ID);
        if (enterprise != null) {
            Domain domain = instance.fetchLevel3DomainByNameForEnterprise(MY_L3_DOMAIN_NAME, enterprise);
            if (domain != null) {
                instance.createZoneInLevel3Domain(MY_ZONE_NAME, domain);
            } else {
                System.out.println("Operation not performed due to missing Domain " + MY_L3_DOMAIN_NAME);
            }
        } else {
            System.out.println("Operation not performed due to missing Enterprise " + MY_ENTERPRISE_ID);
        }
	}
	
	private Zone createZoneInLevel3Domain(String zoneName, Domain domain) throws RestException {
	    Zone zone = this.fetchZoneByNameForLevel3Domain(zoneName, domain);
	    if (zone ==  null) {
	        zone = new Zone();
	        zone.setName(zoneName);
	        domain.createChild(zone);
            Date createDate = new Date(Long.parseLong(zone.getCreationDate()));
            System.out.println("New Zone created with id " + zone.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(zone.getCreationDate()));
            System.out.println("Old Zone " + zone.getName() + " already created at " + createDate.toString());
	    }
		return zone;
	}

	private Zone fetchZoneByNameForLevel3Domain(String zoneName, Domain domain) throws RestException {
        String filter = String.format("name == '%s'", zoneName);
        ZonesFetcher fetcher = domain.getZones();
        Zone zone = fetcher.getFirst(filter, null, null, null, null, null, true);
        return zone;
	}

    private Domain fetchLevel3DomainByNameForEnterprise(String domainName, Enterprise enterprise) throws RestException {
        String filter = String.format("name == '%s'", domainName);
        DomainsFetcher fetcher = enterprise.getDomains();
        Domain domain = fetcher.getFirst(filter, null, null, null, null, null, true);
        return domain;
    }

    private Enterprise fetchEnterpriseById(String id) throws RestException {
        String filter = String.format("ID == '%s'", id);
        EnterprisesFetcher fetcher = session.getMe().getEnterprises();
        Enterprise enterprise = fetcher.getFirst(filter, null, null, null, null, null, true);
        return enterprise;
    }
}
