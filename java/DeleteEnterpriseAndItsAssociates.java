import java.util.List;
import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Domain;
import net.nuagenetworks.vspk.v5_0.DomainTemplate;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.L2Domain;
import net.nuagenetworks.vspk.v5_0.L2DomainTemplate;
import net.nuagenetworks.vspk.v5_0.Subnet;
import net.nuagenetworks.vspk.v5_0.VM;
import net.nuagenetworks.vspk.v5_0.VPort;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.Zone;
import net.nuagenetworks.vspk.v5_0.fetchers.ZonesFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.DomainTemplatesFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.DomainsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.L2DomainTemplatesFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.L2DomainsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.SubnetsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VMsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VPortsFetcher;

/**
 * Idempotently deletes objects associated with a given VSD Enterprise such as its VMs, VPorts, Subnets, Zones, Domains, Domain
 *      Templates and finally the Enterprise itself
 * 
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Enterprise matching MY_ENTERPRISE_NAME
 * Precondition - requires 0 or more existing L2 Domains Precondition - requires 0 or more existing L2 Domain Templates
 * Precondition - requires 0 or more existing L3 Domains Precondition - requires 0 or more existing L3 Domain Templates
 * Precondition - requires 0 or more existing Zones
 * Precondition - requires 0 or more existing Subnets
 * Precondition - requires 0 or more existing VPorts
 * Precondition - requires 0 or more existing VMs
 */
public class DeleteEnterpriseAndItsAssociates {
    private static final String MY_VSD_SERVER_PORT = "https://192.0.2.10:8443";
    private static final String MY_ENTERPRISE_NAME = "MyLittleEnterprise";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Deleting objects associated with Enterprise " + MY_ENTERPRISE_NAME);
        session.start();
        DeleteEnterpriseAndItsAssociates instance = new DeleteEnterpriseAndItsAssociates();
        Enterprise enterprise = instance.fetchEnterpriseByName(MY_ENTERPRISE_NAME);
        if (enterprise != null) {
            instance.deleteEnterprise(enterprise);
            System.out.println("Delete operation completed for enterprise " + MY_ENTERPRISE_NAME);
        } else {
            System.out.println("Delete operation not performed due to missing Enterprise " + MY_ENTERPRISE_NAME);
        }
    }

    private void deleteEnterprise(Enterprise enterprise) throws RestException {
        this.deleteAllLevel3DomainsOfEnterprise(enterprise);
        this.deleteAllLevel3DomainTemplatesOfEnterprise(enterprise);
        this.deleteAllLevel2DomainsOfEnterprise(enterprise);
        this.deleteAllLevel2DomainTemplatesOfEnterprise(enterprise);
        enterprise.delete();
    }

    private Enterprise fetchEnterpriseByName(String enterpriseName) throws RestException {
        String filter = String.format("name == '%s'", enterpriseName);
        EnterprisesFetcher fetcher = session.getMe().getEnterprises();
        Enterprise enterprise = fetcher.getFirst(filter, null, null, null, null, null, true);
        return enterprise;
    }

    private void deleteAllLevel3DomainsOfEnterprise(Enterprise enterprise) throws RestException {
        DomainsFetcher fetcher = enterprise.getDomains();
        List<Domain> l3Domains = fetcher.get();
        for (Domain l3Domain : l3Domains) {
            this.deleteAllVMsOfDomain(l3Domain);
            this.deleteAllVPortsOfDomain(l3Domain);
            this.deleteAllSubnetsOfDomain(l3Domain);
            this.deleteAllZonesOfDomain(l3Domain);
            System.out.println("Deleting Level 3 Domain " + l3Domain.getName());
            l3Domain.delete();
        }
    }

    private void deleteAllLevel3DomainTemplatesOfEnterprise(Enterprise enterprise) throws RestException {
        DomainTemplatesFetcher templatesFetcher = enterprise.getDomainTemplates();
        List<DomainTemplate> templates = templatesFetcher.get();
        for (DomainTemplate template : templates) {
            System.out.println("Deleting Level 3 Domain Template " + template.getName());
            template.delete();
        }
    }

    private void deleteAllLevel2DomainsOfEnterprise(Enterprise enterprise) throws RestException {
        L2DomainsFetcher fetcher = enterprise.getL2Domains();
        List<L2Domain> l2Domains = fetcher.get();
        for (L2Domain l2Domain : l2Domains) {
            System.out.println("Deleting Level 2 Domain " + l2Domain.getName());
            l2Domain.delete();
        }
    }

    private void deleteAllLevel2DomainTemplatesOfEnterprise(Enterprise enterprise) throws RestException {
        L2DomainTemplatesFetcher templatesFetcher = enterprise.getL2DomainTemplates();
        List<L2DomainTemplate> templates = templatesFetcher.get();
        for (L2DomainTemplate template : templates) {
            System.out.println("Deleting Level 2 Domain Template " + template.getName());
            template.delete();
        }
    }

    private void deleteAllVMsOfDomain(Domain l3Domain) throws RestException {
        VMsFetcher fetcher = l3Domain.getVMs();
        List<VM> vms = fetcher.get();
        for (VM vm : vms) {
            System.out.println("Deleting VM " + vm.getName());
            vm.delete();
        }
    }

    private void deleteAllVPortsOfDomain(Domain l3Domain) throws RestException {
        VPortsFetcher fetcher = l3Domain.getVPorts();
        List<VPort> vPorts = fetcher.get();
        for (VPort vPort : vPorts) {
            System.out.println("Deleting VPort " + vPort.getName());
            vPort.delete();
        }
    }

    private void deleteAllSubnetsOfDomain(Domain l3Domain) throws RestException {
        SubnetsFetcher fetcher = l3Domain.getSubnets();
        List<Subnet> subnets = fetcher.get();
        for (Subnet subnet : subnets) {
            System.out.println("Deleting Subnet " + subnet.getName());
            subnet.delete();
        }
    }

    private void deleteAllZonesOfDomain(Domain l3Domain) throws RestException {
        ZonesFetcher fetcher = l3Domain.getZones();
        List<Zone> zones = fetcher.get();
        for (Zone zone : zones) {
            System.out.println("Deleting Zone " + zone.getName());
            zone.delete();
        }
    }

}
