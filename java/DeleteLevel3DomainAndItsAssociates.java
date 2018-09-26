import java.util.List;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Domain;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.Subnet;
import net.nuagenetworks.vspk.v5_0.VM;
import net.nuagenetworks.vspk.v5_0.VPort;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.Zone;
import net.nuagenetworks.vspk.v5_0.fetchers.ZonesFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.DomainsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.SubnetsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VMsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VPortsFetcher;

/**
 * Idempotently deletes objects associated with a given VSD Domain such as its VMs, VPorts, Subnets, Zones and finally the Domain itself
 * 
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Enterprise matching MY_ENTERPRISE_NAME
 * Precondition - requires an existing Level 3 Domain matching MY_L3_DOMAIN_NAME
 * Precondition - requires 0 or more existing Subnets
 * Precondition - requires 0 or more existing Zones
 * Precondition - requires 0 or more existing VPorts
 * Precondition - requires 0 or more existing VMs
 */
public class DeleteLevel3DomainAndItsAssociates {
    private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final String MY_ENTERPRISE_NAME = "MyLittleEnterprise";
    private static final String MY_L3_DOMAIN_NAME = "Little Domain1";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Deleting Level 3 Domain " + MY_L3_DOMAIN_NAME + " of Enterprise " + MY_ENTERPRISE_NAME);
        session.start();
        DeleteLevel3DomainAndItsAssociates instance = new DeleteLevel3DomainAndItsAssociates();
        Enterprise enterprise = instance.fetchEnterpriseByName(MY_ENTERPRISE_NAME);
        if (enterprise != null) {
            Domain domain = instance.fetchLevel3DomainByNameForEnterprise(MY_L3_DOMAIN_NAME, enterprise);
            if (domain != null) {
                instance.deleteObjectsOfDomainForEnterprise(domain);
                System.out.println("Operation completed for L3 domain " + MY_L3_DOMAIN_NAME);
            } else {
                System.out.println("Operation not performed due to missing L3 Domain " + MY_L3_DOMAIN_NAME);
            }

        } else {
            System.out.println("Operation not performed due to missing Enterprise " + MY_ENTERPRISE_NAME);
        }
    }

    private void deleteObjectsOfDomainForEnterprise(Domain l3Domain) throws RestException {
        this.deleteAllVMsOfDomain(l3Domain);
        this.deleteAllVPortsOfDomain(l3Domain);
        this.deleteAllSubnetsOfDomain(l3Domain);
        this.deleteAllZonesOfDomain(l3Domain);
        l3Domain.delete();
    }

    private Domain fetchLevel3DomainByNameForEnterprise(String domainName, Enterprise enterprise) throws RestException {
        String filter = String.format("name == '%s'", domainName);
        DomainsFetcher fetcher = enterprise.getDomains();
        Domain domain = fetcher.getFirst(filter, null, null, null, null, null, true);
        return domain;
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

    private Enterprise fetchEnterpriseByName(String enterpriseName) throws RestException {
        String filter = String.format("name == '%s'", enterpriseName);
        EnterprisesFetcher fetcher = session.getMe().getEnterprises();
        Enterprise enterprise = fetcher.getFirst(filter, null, null, null, null, null, true);
        return enterprise;
    }

}
