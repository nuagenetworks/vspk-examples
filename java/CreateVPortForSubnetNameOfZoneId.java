import java.util.Date;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Subnet;
import net.nuagenetworks.vspk.v5_0.VPort;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.Zone;
import net.nuagenetworks.vspk.v5_0.fetchers.SubnetsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VPortsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.ZonesFetcher;

/**
 * Idempotently creates a VSD VPort object given its parent Subnet Name and parent Zone ID
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Zone matching MY_ZONE_ID
 * Precondition - requires an existing Subnet matching MY_SUBNET_NAME
 */
public class CreateVPortForSubnetNameOfZoneId {
    private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final String MY_ZONE_ID = "a0f6e8e6-5d3d-4387-9472-392a072f6b9f";
    private static final String MY_SUBNET_NAME = "MyLittleSubnet2";
    private static final String MY_VPORT_NAME = "MyLittleVPort2";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating VPort : " + MY_VPORT_NAME + " in Subnet " + MY_SUBNET_NAME);
        session.start();
        CreateVPortForSubnetNameOfZoneId instance = new CreateVPortForSubnetNameOfZoneId();

        Zone zone = instance.fetchZoneById(MY_ZONE_ID);
        if (zone != null) {
            Subnet subnet = instance.fetchSubnetByNameForZone(MY_SUBNET_NAME, zone);
            if (subnet != null) {
                instance.createVPortInSubnet(MY_VPORT_NAME, subnet);
            } else {
                System.out.println("Operation not performed due to missing Subnet " + MY_SUBNET_NAME);
            }
        } else {
            System.out.println("Operation not performed due to missing Zone " + MY_ZONE_ID);
        }
    }

    private VPort createVPortInSubnet(String vportName, Subnet subnet) throws RestException {
        VPort vport = this.fetchVPortByNameForSubnet(vportName, subnet);
        if (vport == null) {
            vport = new VPort();
            vport.setName(vportName);
            subnet.createChild(vport);
            Date createDate = new Date(Long.parseLong(vport.getCreationDate()));
            System.out.println("New VPort created with id " + vport.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(vport.getCreationDate()));
            System.out.println("Old VPOrt " + vport.getName() + " already created at " + createDate.toString());
        }
        return vport;
    }

    private VPort fetchVPortByNameForSubnet(String vportName, Subnet subnet) throws RestException {
        String filter = String.format("name == '%s'", vportName);
        VPortsFetcher fetcher = subnet.getVPorts();
        VPort vport = fetcher.getFirst(filter, null, null, null, null, null, true);
        return vport;
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
