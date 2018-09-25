import java.io.File;
import java.util.List;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;

/**
 * Lists all Enterprise objects of a VSD instance after making a connection with certificate file credentials
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 */
public class ConnectToVsdUsingCertificate {

    public static void main(String[] args) throws RestException {
        String MY_VSD_SERVER_PORT = "https://135.228.4.108:7443";
        String username = "csproot";
        String organization = "csp";
        File certFile = new File("C:/Users/lpaquett/keys/csproot.pem");
        File keyFile = new File("C:/Users/lpaquett/keys/csproot-Key.pem");

        VSDSession session = new VSDSession(username, organization, MY_VSD_SERVER_PORT, certFile, keyFile);
        session.start();

        EnterprisesFetcher fetcher = session.getMe().getEnterprises();
        List<Enterprise> enterprises = fetcher.get();

        System.out.println("Number of Enterprises found : " + enterprises.size());
        for (Enterprise enterprise : enterprises) {
           System.out.println("Enterprise: " + enterprise);
        }
    }
}
