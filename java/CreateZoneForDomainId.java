import java.util.Date;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Domain;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.Zone;
import net.nuagenetworks.vspk.v5_0.fetchers.DomainsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.ZonesFetcher;

/**
 * Idempotently creates a VSD Zone object given its parent Level 3 Domain ID
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Level 3 Domain matching MY_L3_DOMAIN_ID
 */
public class CreateZoneForDomainId {
    private static final String MY_VSD_SERVER_PORT = "https://192.0.2.10:8443";
    private static final String MY_L3_DOMAIN_ID = "6d3a382a-381c-4247-a16e-74e0c23aede8";
    private static final String MY_ZONE_NAME = "MyLittleZone1";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating Zone " + MY_ZONE_NAME + " in Level 3 Domain " + MY_L3_DOMAIN_ID);
        session.start();
        CreateZoneForDomainId instance = new CreateZoneForDomainId();
        Domain domain = instance.fetchLevel3DomainById(MY_L3_DOMAIN_ID);
        if (domain != null) {
            instance.createZoneInLevel3Domain(MY_ZONE_NAME, domain);
        } else {
            System.out.println("Operation not performed due to missing Domain " + MY_L3_DOMAIN_ID);
        }
    }

    private Zone createZoneInLevel3Domain(String zoneName, Domain domain) throws RestException {
        Zone zone = this.fetchZoneByNameForLevel3Domain(zoneName, domain);
        if (zone == null) {
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

    private Domain fetchLevel3DomainById(String id) throws RestException {
        String filter = String.format("ID == '%s'", id);
        DomainsFetcher fetcher = session.getMe().getDomains();
        Domain domain = fetcher.getFirst(filter, null, null, null, null, null, true);
        return domain;
    }
}
