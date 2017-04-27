import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v4_0.Enterprise;
import net.nuagenetworks.vspk.v4_0.Me;
import net.nuagenetworks.vspk.v4_0.VSDSession;

/**
 * Creates an Enterprise object
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 */
public class CreateEnterprise {
	private static final String MY_VSD_SERVER_PORT = "https://135.121.118.59:8443";
	private static final String MY_ENTERPRISE_NAME = "MyLittleEnterprise";
	private static final VSDSession session;

	static {
		session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
	}

	public static void main(String[] args) throws RestException {
		System.out.println("Creating Enterprise : " + MY_ENTERPRISE_NAME);
		session.start();
		CreateEnterprise instance = new CreateEnterprise();
		instance.createEnterprise(MY_ENTERPRISE_NAME);
	}

	private Enterprise createEnterprise(String enterpriseName) throws RestException {
		Me me = session.getMe();
		Enterprise enterprise = new Enterprise();
		enterprise.setName(enterpriseName);
		me.createChild(enterprise);
		return enterprise;
	}
}
