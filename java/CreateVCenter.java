import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v4_0.VCenter;
import net.nuagenetworks.vspk.v4_0.Me;
import net.nuagenetworks.vspk.v4_0.VSDSession;

/**
 * Creates a VCenter object
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 */
public class CreateVCenter {
    private static final String MY_VSD_SERVER_PORT	= "https://135.121.118.59:8443";
    private static final String MY_VCENTER_ADDRESS	= "135.122.118.25";
    private static final String MY_VCENTER_OVF_URL	= "http://135.122.116.212/customers/VRS_4.0.3-28.ovf";
    private static final String MY_VCENTER_NAME		= "MyLittleVCenter";
    private static final VSDSession session;
    
    static { session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT); }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating VCenter : " + MY_VCENTER_NAME);
        session.start();
        CreateVCenter instance = new CreateVCenter();
        instance.createVCenter(MY_VCENTER_NAME, MY_VCENTER_ADDRESS, MY_VCENTER_OVF_URL);
    }

    private VCenter createVCenter(String vCenterName, String vCenterAddress, String ovfURL) throws RestException {
        Me me = session.getMe();
        VCenter vCenter = new VCenter();
        vCenter.setName(vCenterName);
        vCenter.setIpAddress(vCenterAddress);
        vCenter.setUserName("administrator@vsphere.local");
        vCenter.setPassword("MyLittlePassword");
        vCenter.setOvfURL(ovfURL);
        me.createChild(vCenter);
        return vCenter;
	}
}
