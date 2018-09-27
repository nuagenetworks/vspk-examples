import java.util.Date;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.Me;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;

/**
 * Idempotently creates a VSD Enterprise object
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 */
public class CreateEnterprise {
    private static final String MY_VSD_SERVER_PORT = "https://192.0.2.10:8443";
    private static final String MY_ENTERPRISE_NAME = "MyLittleEnterprise";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating Enterprise " + MY_ENTERPRISE_NAME);
        session.start();
        CreateEnterprise instance = new CreateEnterprise();
        instance.createEnterprise(MY_ENTERPRISE_NAME);
    }

    private Enterprise createEnterprise(String enterpriseName) throws RestException {
        Enterprise enterprise = this.fetchEnterpriseByName(enterpriseName);
        if (enterprise == null) {
            Me me = session.getMe();
            enterprise = new Enterprise();
            enterprise.setName(enterpriseName);
            me.createChild(enterprise);
            Date createDate = new Date(Long.parseLong(enterprise.getCreationDate()));
            System.out.println("New Enterprise created with id " + enterprise.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(enterprise.getCreationDate()));
            System.out.println("Old Enterprise " + enterprise.getName() + " already created at " + createDate.toString());
        }
        return enterprise;
    }

    private Enterprise fetchEnterpriseByName(String enterpriseName) throws RestException {
        String filter = String.format("name == '%s'", enterpriseName);
        EnterprisesFetcher fetcher = session.getMe().getEnterprises();
        Enterprise enterprise = fetcher.getFirst(filter, null, null, null, null, null, true);
        return enterprise;
    }

}
