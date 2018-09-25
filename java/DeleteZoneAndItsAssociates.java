import java.util.List;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Subnet;
import net.nuagenetworks.vspk.v5_0.VM;
import net.nuagenetworks.vspk.v5_0.VPort;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.Zone;
import net.nuagenetworks.vspk.v5_0.fetchers.SubnetsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VMsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VPortsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.ZonesFetcher;

/**
 * Idempotently deletes objects associated with a given VSD Zone such as its Subnets, VMs and VPorts, and finally the Zone itself
 * 
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Zone matching MY_ZONE_ID
 * Precondition - requires 0 or more existing VPorts
 * Precondition - requires 0 or more existing VMs
 */
public class DeleteZoneAndItsAssociates {
	private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final String MY_ZONE_ID = "db523956-4051-4c29-ba16-1f09f8eb3ca1";
	private static final VSDSession session;

	static {
		session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
	}

	public static void main(String[] args) throws RestException {
        System.out.println("Deleting objects associated with Zone " + MY_ZONE_ID);
		session.start();
		DeleteZoneAndItsAssociates instance = new DeleteZoneAndItsAssociates();

        Zone zone = instance.fetchZoneById(MY_ZONE_ID);
        if (zone != null) {
            instance.deleteObjectsOfZone(zone);
        } else {
            System.out.println("Operation not performed due to missing Zone " + MY_ZONE_ID);
        }
	}

    private void deleteObjectsOfZone(Zone zone) throws RestException {
        this.deleteAllVMsOfZone(zone);
        this.deleteAllVPortsOfZone(zone);
        this.deleteAllSubnetsOfZone(zone);
        zone.delete();
    }

    private void deleteAllVMsOfZone(Zone zone) throws RestException {
        VMsFetcher fetcher = zone.getVMs();
        List<VM> vms = fetcher.get();
        for (VM vm : vms) {
            System.out.println("Deleting VM " + vm.getName());
            vm.delete();
        }
    }

    private void deleteAllVPortsOfZone(Zone zone) throws RestException {
        VPortsFetcher fetcher = zone.getVPorts();
        List<VPort> vPorts = fetcher.get();
        for (VPort vPort : vPorts) {
            System.out.println("Deleting VPort " + vPort.getName());
            vPort.delete();
        }
    }

    private void deleteAllSubnetsOfZone(Zone zone) throws RestException {
        SubnetsFetcher fetcher = zone.getSubnets();
        List<Subnet> subnets = fetcher.get();
        for (Subnet subnet : subnets) {
            System.out.println("Deleting Subnet " + subnet.getName());
            subnet.delete();
        }
    }

    private Zone fetchZoneById(String id) throws RestException {
        String filter = String.format("ID == '%s'", id);
        ZonesFetcher fetcher = session.getMe().getZones();
        Zone zone = fetcher.getFirst(filter, null, null, null, null, null, true);
        return zone;
    }
}
