import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;

/**
 * Idempotently deletes a VSD Enterprise object
 * 
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Enterprise matching MY_ENTERPRISE_NAME
 */
public class DeleteEnterprise {
    private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final String MY_ENTERPRISE_NAME = "MyLittleEnterprise";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Deleting Enterprise " + MY_ENTERPRISE_NAME);
        session.start();
        DeleteEnterprise instance = new DeleteEnterprise();
        Enterprise enterprise = instance.fetchEnterpriseByName(MY_ENTERPRISE_NAME);
        if (enterprise != null) {
            instance.deleteEnterprise(enterprise);
            System.out.println("Operation completed for enterprise " + MY_ENTERPRISE_NAME);
        } else {
            System.out.println("Operation not performed due to missing Enterprise " + MY_ENTERPRISE_NAME);
        }
    }

    private void deleteEnterprise(Enterprise enterprise) throws RestException {
        enterprise.delete();
    }

    private Enterprise fetchEnterpriseByName(String enterpriseName) throws RestException {
        String filter = String.format("name == '%s'", enterpriseName);
        EnterprisesFetcher fetcher = session.getMe().getEnterprises();
        Enterprise enterprise = fetcher.getFirst(filter, null, null, null, null, null, true);
        return enterprise;
    }

}
