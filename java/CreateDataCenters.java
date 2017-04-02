import java.util.Date;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v4_0.VCenter;
import net.nuagenetworks.vspk.v4_0.VSDSession;
import net.nuagenetworks.vspk.v4_0.VCenterDataCenter;
import net.nuagenetworks.vspk.v4_0.fetchers.VCentersFetcher;

/**
 * Creates a set of DataCenters in an existing VCenter
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing VCenter matching MY_VCENTER_NAME.  See CreateVCenter.java
*/
public class CreateDataCenters {
    private static final String MY_VSD_SERVER_PORT	= "https://135.121.118.59:8443";
    private static final String MY_VCENTER_NAME		= "MyLittleVCenter";
    private static final String MY_DATACENTER_NAME1	= "MyLittleDataCenter1";
    private static final String MY_DATACENTER_NAME2	= "MyLittleDataCenter2";
    private static final String MY_DATACENTER_NAME3	= "MyLittleDataCenter3";
    private static final VSDSession session;
    
    static { session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT); }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating DataCenters in VCenter : " + MY_VCENTER_NAME);
        session.start();
        CreateDataCenters	instance	= new CreateDataCenters();
        VCenter				vCenter		= instance.fetchVCenterByName(MY_VCENTER_NAME);
        System.out.println("Creating DataCenter 1 : " + MY_DATACENTER_NAME1);
        instance.createDataCenterForVCenter(vCenter, MY_DATACENTER_NAME1);
        System.out.println("Creating DataCenter 2 : " + MY_DATACENTER_NAME2);
        instance.createDataCenterForVCenter(vCenter, MY_DATACENTER_NAME2);
        System.out.println("Creating DataCenter 3 : " + MY_DATACENTER_NAME3);
        instance.createDataCenterForVCenter(vCenter, MY_DATACENTER_NAME3);
    }

	private void createDataCenterForVCenter(VCenter vCenter, String dataCenterName) throws RestException {
		VCenterDataCenter dataCenter = new VCenterDataCenter();
		dataCenter.setName(dataCenterName);
		vCenter.createChild(dataCenter);
	}

	private VCenter fetchVCenterByName(String vCenterName) throws RestException {
        String			filter		= String.format("name == '%s'", vCenterName);
    	VCentersFetcher	fetcher		= session.getMe().getVCenters();
    	VCenter			vCenter		= fetcher.getFirst(filter, null, null, null, null, null, true);
        Date			createDate	= new Date(Long.parseLong(vCenter.getCreationDate()));
        System.out.println("VCenter : " + vCenter.getName() + " was created at : " + createDate.toString());
        return vCenter;
	}
}
