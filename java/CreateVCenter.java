import java.util.Date;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.VCenter;
import net.nuagenetworks.vspk.v5_0.Me;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.VCentersFetcher;

/**
 * Idempotently creates a VCenter object
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 */
public class CreateVCenter {
	private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final String MY_VCENTER_NAME = "MyLittleVCenter";
    private static final String MY_VCENTER_IP = "135.122.118.25";
    private static final String MY_VCENTER_USER = "administrator@vsphere.local";
    private static final String MY_VCENTER_PASS = "MyLittlePassword";
    private static final String MY_VCENTER_OVF = "http://135.122.116.212/customers/VRS_4.0.3-28.ovf";
	private static final VSDSession session;

	static {
		session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
	}

    public static class VCenterDescriptor {
        public String name;
        public String ipAddress;
        public String username;
        public String password;
        public String ovfURL;

        VCenterDescriptor(String name, String ipAddress, String username, String password, String ovfURL) {
            this.name = name;
            this.ipAddress = ipAddress;
            this.username = username;
            this.password = password;
            this.ovfURL = ovfURL;
        }
    }

	public static void main(String[] args) throws RestException {
		System.out.println("Creating VCenter : " + MY_VCENTER_NAME);
		session.start();
		CreateVCenter instance = new CreateVCenter();
		VCenterDescriptor descriptor = new VCenterDescriptor(MY_VCENTER_NAME, MY_VCENTER_IP, MY_VCENTER_USER, MY_VCENTER_PASS, MY_VCENTER_OVF);
		instance.createVCenter(descriptor);
	}

	private VCenter createVCenter(VCenterDescriptor descriptor) throws RestException {
	    VCenter vCenter = this.fetchVCenterByName(descriptor.name);
	    if (vCenter == null) {
	        Me me = session.getMe();
	        vCenter = new VCenter();
	        vCenter.setName(descriptor.name);
	        vCenter.setIpAddress(descriptor.ipAddress);
	        vCenter.setUserName(descriptor.username);
	        vCenter.setPassword(descriptor.password);
	        vCenter.setOvfURL(descriptor.ovfURL);
	        me.createChild(vCenter);
            Date createDate = new Date(Long.parseLong(vCenter.getCreationDate()));
            System.out.println("New VCenter created with id " + vCenter.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(vCenter.getCreationDate()));
            System.out.println("Old VCenter " + vCenter.getName() + " already created at " + createDate.toString());
	    }
		return vCenter;
	}
	
	private VCenter fetchVCenterByName(String vCenterName) throws RestException {
        String filter = String.format("name == '%s'", vCenterName);
        VCentersFetcher fetcher = session.getMe().getVCenters();
        VCenter vCenter = fetcher.getFirst(filter, null, null, null, null, null, true);
        return vCenter;
	}
}
