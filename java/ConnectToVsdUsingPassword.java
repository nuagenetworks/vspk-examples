import java.util.List;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;

/**
 * Lists all Enterprise objects of a VSD instance after making a connection with username and password credentials
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 */
public class ConnectToVsdUsingPassword {

    public static void main(String[] args) throws RestException {
        String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
        String username = "csproot";
        String password = "csproot";
        String organization = "csp";

        VSDSession session = new VSDSession(username, password, organization, MY_VSD_SERVER_PORT);

        session.start();

        EnterprisesFetcher fetcher = session.getMe().getEnterprises();
        List<Enterprise> enterprises = fetcher.get();

        System.out.println("Number of Enterprises found : " + enterprises.size());
        for (Enterprise enterprise : enterprises) {
            System.out.println("Enterprise: " + enterprise);
        }
    }
}
