import java.util.Date;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;

/**
 * Fetches a VSD Enterprise object by its name
 * 
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Enterprise matching MY_ENTERPRISE_NAME
 */
public class FetchEnterpriseByName {
    private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final String MY_ENTERPRISE_NAME = "MyLittleEnterprise";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Fetching Enterprise " + MY_ENTERPRISE_NAME);
        session.start();
        FetchEnterpriseByName instance = new FetchEnterpriseByName();
        instance.fetchEnterpriseByName(MY_ENTERPRISE_NAME);
    }

    private Enterprise fetchEnterpriseByName(String enterpriseName) throws RestException {
        String filter = String.format("name == '%s'", enterpriseName);
        EnterprisesFetcher fetcher = session.getMe().getEnterprises();
        Enterprise enterprise = fetcher.getFirst(filter, null, null, null, null, null, true);
        if (enterprise != null) {
            Date createDate = new Date(Long.parseLong(enterprise.getCreationDate()));
            System.out.println("Found Enterprise " + enterprise.getName() + " created at " + createDate.toString());
        } else {
            System.out.println("Enterprise " + enterpriseName + " was not found");
        }
        return enterprise;
    }
}
