import java.util.Date;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.VCenter;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.VCenterDataCenter;
import net.nuagenetworks.vspk.v5_0.fetchers.VCenterDataCentersFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VCentersFetcher;

/**
 * Idempotently creates a VSD Data Center object within an existing VCenter
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing VCenter matching MY_VCENTER_NAME
 */
public class CreateDataCenter {
    private static final String MY_VSD_SERVER_PORT = "https://192.0.2.10:8443";
    private static final String MY_VCENTER_NAME = "MyLittleVCenter";
    private static final String MY_DATACENTER_NAME = "MyLittleDataCenter";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating DataCenters in VCenter : " + MY_VCENTER_NAME);
        session.start();
        CreateDataCenter instance = new CreateDataCenter();
        VCenter vCenter = instance.fetchVCenterByName(MY_VCENTER_NAME);
        if (vCenter != null) {
            instance.createDataCenterForVCenter(vCenter, MY_DATACENTER_NAME);
        } else {
            System.out.println("Operation not performed due to missing VCenter " + MY_VCENTER_NAME);
        }
    }

    private void createDataCenterForVCenter(VCenter vCenter, String dataCenterName) throws RestException {
        VCenterDataCenter dataCenter = this.fetchDataCenterByNameForVCenter(dataCenterName, vCenter);
        if (dataCenter == null) {
            dataCenter = new VCenterDataCenter();
            dataCenter.setName(dataCenterName);
            vCenter.createChild(dataCenter);
            Date createDate = new Date(Long.parseLong(dataCenter.getCreationDate()));
            System.out.println("New DataCenter created with id " + dataCenter.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(dataCenter.getCreationDate()));
            System.out.println("Old DataCenter " + dataCenter.getName() + " already created at " + createDate.toString());
        }
    }

    private VCenter fetchVCenterByName(String vCenterName) throws RestException {
        String filter = String.format("name == '%s'", vCenterName);
        VCentersFetcher fetcher = session.getMe().getVCenters();
        VCenter vCenter = fetcher.getFirst(filter, null, null, null, null, null, true);
        return vCenter;
    }

    private VCenterDataCenter fetchDataCenterByNameForVCenter(String dataCenterName, VCenter vCenter) throws RestException {
        String filter = String.format("name == '%s'", dataCenterName);
        VCenterDataCentersFetcher fetcher = vCenter.getVCenterDataCenters();
        VCenterDataCenter dataCenter = fetcher.getFirst(filter, null, null, null, null, null, true);
        return dataCenter;
    }
}
