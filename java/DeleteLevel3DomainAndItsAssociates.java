import java.util.Date;
import java.util.List;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v4_0.Domain;
import net.nuagenetworks.vspk.v4_0.Subnet;
import net.nuagenetworks.vspk.v4_0.VPort;
import net.nuagenetworks.vspk.v4_0.VSDSession;
import net.nuagenetworks.vspk.v4_0.Zone;
import net.nuagenetworks.vspk.v4_0.fetchers.ZonesFetcher;
import net.nuagenetworks.vspk.v4_0.fetchers.DomainsFetcher;
import net.nuagenetworks.vspk.v4_0.fetchers.SubnetsFetcher;
import net.nuagenetworks.vspk.v4_0.fetchers.VPortsFetcher;

/**
 * 1. Delete all Subnets linked to a given L3 domain 2. Delete all Zones linked to a given L3 domain 3. Delete the L3 domain
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires 0 or more existing Subnets. See CreateSubnet.java
 * Precondition - requires 0 or more existing Zones. See CreateZone.java
 * Precondition - requires 0 or more existing VPorts. See CreateVPortForSubnet.java
 * Precondition - requires an existing Level 3 Domain matching MY_L3_DOMAIN_NAME. See CreateLevel3Domain.java
 */
public class DeleteLevel3DomainAndItsAssociates {
	private static final String MY_VSD_SERVER_PORT = "https://135.121.118.59:8443";
	private static final String MY_L3_DOMAIN_NAME = "MyLittleLevel3Domain";
	private static final VSDSession session;

	static {
		session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
	}

	public static void main(String[] args) throws RestException {
		System.out.println("Deleting Level 3 Domain : " + MY_L3_DOMAIN_NAME);
		session.start();
		DeleteLevel3DomainAndItsAssociates instance = new DeleteLevel3DomainAndItsAssociates();
		Domain l3Domain = instance.fetchLevel3DomainByName(MY_L3_DOMAIN_NAME);
		instance.deleteAllVPortsInDomain(l3Domain);
		instance.deleteAllSubnetsInDomain(l3Domain);
		instance.deleteAllZonesInDomain(l3Domain);
		l3Domain.delete();
	}

	private Domain fetchLevel3DomainByName(String domainName) throws RestException {
		String filter = String.format("name == '%s'", domainName);
		DomainsFetcher fetcher = session.getMe().getDomains();
		Domain l3Domain = fetcher.getFirst(filter, null, null, null, null, null, true);
		Date createDate = new Date(Long.parseLong(l3Domain.getCreationDate()));
		System.out.println("Level 3 Domain : " + l3Domain.getName() + " was created at : " + createDate.toString());
		return l3Domain;
	}

	private void deleteAllSubnetsInDomain(Domain l3Domain) throws RestException {
		SubnetsFetcher fetcher = l3Domain.getSubnets();
		List<Subnet> subnets = fetcher.get();
		for (Subnet subnet : subnets) {
			System.out.println("Deleting Subnet : " + subnet.getName());
			subnet.delete();
		}
	}

	private void deleteAllZonesInDomain(Domain l3Domain) throws RestException {
		ZonesFetcher fetcher = l3Domain.getZones();
		List<Zone> zones = fetcher.get();
		for (Zone zone : zones) {
			System.out.println("Deleting Zone : " + zone.getName());
			zone.delete();
		}
	}

	private void deleteAllVPortsInDomain(Domain l3Domain) throws RestException {
		VPortsFetcher fetcher = l3Domain.getVPorts();
		List<VPort> vPorts = fetcher.get();
		for (VPort vPort : vPorts) {
			System.out.println("Deleting VPort : " + vPort.getName());
			vPort.delete();
		}
	}
}
