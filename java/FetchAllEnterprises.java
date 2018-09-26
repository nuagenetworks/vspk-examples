import java.util.Date;
import java.util.List;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;

/**
 * Fetches all existing VSD Enterprise objects
 * 
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 */
public class FetchAllEnterprises {
    private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Fetching All Enterprises");
        session.start();
        FetchAllEnterprises instance = new FetchAllEnterprises();
        List<Enterprise> enterprises = instance.fetchAllEnterprises();
        System.out.println("Number of Enterprises found : " + enterprises.size());
        for (Enterprise enterprise : enterprises) {
            Date createDate = new Date(Long.parseLong(enterprise.getCreationDate()));
            System.out.println("Found Enterprise " + enterprise.getName() + " created at " + createDate.toString());
        }
    }

    private List<Enterprise> fetchAllEnterprises() throws RestException {
        EnterprisesFetcher fetcher = session.getMe().getEnterprises();
        List<Enterprise> enterprises = fetcher.get();
        return enterprises;
    }
}
