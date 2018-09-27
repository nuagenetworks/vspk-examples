import java.util.Date;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.L2Domain;
import net.nuagenetworks.vspk.v5_0.L2DomainTemplate;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.L2DomainTemplatesFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.L2DomainsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;

/**
 * Idempotently creates a VSD Level 2 Domain object given its parent Enterprise name and Domain Template name
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Enterprise matching MY_ENTERPRISE_NAME
 * Precondition - requires an existing Level 2 Domain Template matching MY_L2_TEMPLATE_NAME
 */
public class CreateLevel2DomainForEnterpriseName {
    private static final String MY_VSD_SERVER_PORT = "https://192.0.2.10:8443";
    private static final String MY_ENTERPRISE_NAME = "MyLittleEnterprise";
    private static final String MY_L2_TEMPLATE_NAME = "MyLittleLevel2DomainTemplate";
    private static final String MY_L2_DOMAIN_NAME = "MyLittleLevel2Domain";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating Level 2 Domain : " + MY_L2_DOMAIN_NAME + " in Enterprise " + MY_ENTERPRISE_NAME);
        session.start();
        CreateLevel2DomainForEnterpriseName instance = new CreateLevel2DomainForEnterpriseName();
        Enterprise enterprise = instance.fetchEnterpriseByName(MY_ENTERPRISE_NAME);
        if (enterprise != null) {
            L2DomainTemplate template = instance.fetchLevel2DomainTemplateByNameForEnterprise(MY_L2_TEMPLATE_NAME, enterprise);
            if (template != null) {
                instance.createLevel2DomainInEnterprise(template, MY_L2_DOMAIN_NAME, enterprise);
            } else {
                System.out.println("Operation not performed due to missing L2 Domain Template " + MY_L2_TEMPLATE_NAME);
            }
        } else {
            System.out.println("Operation not performed due to missing Enterprise " + MY_ENTERPRISE_NAME);
        }
    }

    private L2Domain createLevel2DomainInEnterprise(L2DomainTemplate domainTemplate, String domainName, Enterprise enterprise) throws RestException {
        L2Domain domain = this.fetchLevel2DomainByNameForEnterprise(domainName, enterprise);
        if (domain == null) {
            domain = new L2Domain();
            domain.setName(domainName);
            domain.setTemplateID(domainTemplate.getId());
            enterprise.createChild(domain);
            Date createDate = new Date(Long.parseLong(domain.getCreationDate()));
            System.out.println("New Level 2 Domain created with id " + domain.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(domain.getCreationDate()));
            System.out.println("Old Level 2 Domain " + domain.getName() + " already created at " + createDate.toString());
        }
        return domain;
    }

    private Enterprise fetchEnterpriseByName(String enterpriseName) throws RestException {
        String filter = String.format("name == '%s'", enterpriseName);
        EnterprisesFetcher fetcher = session.getMe().getEnterprises();
        Enterprise enterprise = fetcher.getFirst(filter, null, null, null, null, null, true);
        return enterprise;
    }

    private L2DomainTemplate fetchLevel2DomainTemplateByNameForEnterprise(String templateName, Enterprise enterprise) throws RestException {
        String filter = String.format("name == '%s'", templateName);
        L2DomainTemplatesFetcher fetcher = enterprise.getL2DomainTemplates();
        L2DomainTemplate template = fetcher.getFirst(filter, null, null, null, null, null, true);
        return template;
    }

    private L2Domain fetchLevel2DomainByNameForEnterprise(String domainName, Enterprise enterprise) throws RestException {
        String filter = String.format("name == '%s'", domainName);
        L2DomainsFetcher fetcher = enterprise.getL2Domains();
        L2Domain domain = fetcher.getFirst(filter, null, null, null, null, null, true);
        return domain;
    }

}
