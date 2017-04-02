import java.util.Date;
import java.util.List;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v4_0.VCenter;
import net.nuagenetworks.vspk.v4_0.VCenterDataCenter;
import net.nuagenetworks.vspk.v4_0.VSDSession;
import net.nuagenetworks.vspk.v4_0.fetchers.VCentersFetcher;
import net.nuagenetworks.vspk.v4_0.fetchers.VCenterDataCentersFetcher;

/**
 * 1. Fetch a list of all dataCenters in a given vCenter  2. Lookup each dataCenter by name and then delete it
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires 0 or more existing data centers.  See CreateDataCenters.java
 * Precondition - requires an existing VCenter matching MY_VCENTER_NAME.  See CreateVCenter.java
 */
public class FilterAndDeleteDataCenterByName {
    private static final String MY_VSD_SERVER_PORT	= "https://135.121.118.59:8443";
    private static final String MY_VCENTER_NAME		= "MyLittleVCenter";
    private static final VSDSession session;
    
    static { session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT); }

    public static void main(String[] args) throws RestException {
        System.out.println("Deleting all Data Centers in VCenter : " + MY_VCENTER_NAME);
        session.start();
        FilterAndDeleteDataCenterByName	instance	= new FilterAndDeleteDataCenterByName();
        VCenter							vCenter		= instance.fetchVCenterByName(MY_VCENTER_NAME);
        List<VCenterDataCenter>			dataCenters	= instance.fetchAllDataCentersForVCenter(vCenter);
        for (VCenterDataCenter dc : dataCenters) {
            System.out.println("Deleting Data Center : " + dc.getName());
        	VCenterDataCenter dataCenterToDelete = instance.fetchDataCenterByName(dc.getName(), vCenter);
        	dataCenterToDelete.delete();
        }
    }

	private List<VCenterDataCenter> fetchAllDataCentersForVCenter(VCenter vCenter) throws RestException {
    	VCenterDataCentersFetcher	fetcher	= vCenter.getVCenterDataCenters();
    	List<VCenterDataCenter>		list	= fetcher.get();
        return list;
	}

	private VCenter fetchVCenterByName(String vCenterName) throws RestException {
        String			filter		= String.format("name == '%s'", vCenterName);
    	VCentersFetcher	fetcher		= session.getMe().getVCenters();
    	VCenter			vCenter		= fetcher.getFirst(filter, null, null, null, null, null, true);
        Date			createDate	= new Date(Long.parseLong(vCenter.getCreationDate()));
        System.out.println("VCenter : " + vCenter.getName() + " was created at : " + createDate.toString());
        return vCenter;
	}

	private VCenterDataCenter fetchDataCenterByName(String dataCenterName, VCenter vCenter) throws RestException {
        String						filter		= String.format("name == '%s'", dataCenterName);
        VCenterDataCentersFetcher	fetcher		= vCenter.getVCenterDataCenters();
        VCenterDataCenter			dataCenter	= fetcher.getFirst(filter, null, null, null, null, null, true);
        Date						createDate	= new Date(Long.parseLong(dataCenter.getCreationDate()));
        System.out.println("Data Center : " + dataCenter.getName() + " was created at : " + createDate.toString());
        return dataCenter;
	}
}
