import java.util.List;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.VCenter;
import net.nuagenetworks.vspk.v5_0.VCenterDataCenter;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.VCenterDataCentersFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VCentersFetcher;

/**
 * Idempotently deletes a VSD VCenter object and its attached Data Center objects
 * 
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing VCenter matching MY_VCENTER_NAME
 */
public class DeleteVCenterAndItsAssociates {
    private static final String MY_VSD_SERVER_PORT = "https://192.0.2.10:8443";
    private static final String MY_VCENTER_NAME = "MyLittleVCenter";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Deleting VCenter " + MY_VCENTER_NAME);
        session.start();
        DeleteVCenterAndItsAssociates instance = new DeleteVCenterAndItsAssociates();
        VCenter vCenter = instance.fetchVCenterByName(MY_VCENTER_NAME);
        if (vCenter != null) {
            instance.deleteAllDatacentersOfVCenter(vCenter);
            vCenter.delete();
            System.out.println("Operation completed for VCenter " + MY_VCENTER_NAME);
        } else {
            System.out.println("Operation not performed due to missing VCenter " + MY_VCENTER_NAME);
        }
    }

    private void deleteAllDatacentersOfVCenter(VCenter vCenter) throws RestException {
        VCenterDataCentersFetcher fetcher = vCenter.getVCenterDataCenters();
        List<VCenterDataCenter> datacenters = fetcher.get();
        for (VCenterDataCenter datacenter : datacenters) {
            System.out.println("Deleting datacenter " + datacenter.getName());
            datacenter.delete();
        }
    }

    private VCenter fetchVCenterByName(String vCenterName) throws RestException {
        String filter = String.format("name == '%s'", vCenterName);
        VCentersFetcher fetcher = session.getMe().getVCenters();
        VCenter vCenter = fetcher.getFirst(filter, null, null, null, null, null, true);
        return vCenter;
    }
}
