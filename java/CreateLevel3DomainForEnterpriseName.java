import java.util.Date;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Domain;
import net.nuagenetworks.vspk.v5_0.DomainTemplate;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.DomainTemplatesFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.DomainsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;

/**
 * Idempotently creates a VSD Level 3 Domain object given its parent Enterprise name and Domain Template name
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Enterprise matching MY_ENTERPRISE_NAME
 * Precondition - requires an existing Level 3 Domain Template matching MY_L3_TEMPLATE_NAME
 */
public class CreateLevel3DomainForEnterpriseName {
    private static final String MY_VSD_SERVER_PORT = "https://192.0.2.10:8443";
    private static final String MY_ENTERPRISE_NAME = "MyLittleEnterprise";
    private static final String MY_L3_TEMPLATE_NAME = "MyLittleLevel3DomainTemplate";
    private static final String MY_L3_DOMAIN_NAME = "MyLittleLevel3Domain";
    private static final VSDSession session;

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating Level 3 Domain : " + MY_L3_DOMAIN_NAME + " in Enterprise " + MY_ENTERPRISE_NAME);
        session.start();
        CreateLevel3DomainForEnterpriseName instance = new CreateLevel3DomainForEnterpriseName();
        Enterprise enterprise = instance.fetchEnterpriseByName(MY_ENTERPRISE_NAME);
        if (enterprise != null) {
            DomainTemplate template = instance.fetchLevel3DomainTemplateByNameForEnterprise(MY_L3_TEMPLATE_NAME, enterprise);
            if (template != null) {
                instance.createLevel3DomainInEnterprise(template, MY_L3_DOMAIN_NAME, enterprise);
            } else {
                System.out.println("Operation not performed due to missing L3 Domain Template " + MY_L3_TEMPLATE_NAME);
            }
        } else {
            System.out.println("Operation not performed due to missing Enterprise " + MY_ENTERPRISE_NAME);
        }
    }

    private Domain createLevel3DomainInEnterprise(DomainTemplate domainTemplate, String domainName, Enterprise enterprise) throws RestException {
        Domain domain = this.fetchLevel3DomainByNameForEnterprise(domainName, enterprise);
        if (domain == null) {
            domain = new Domain();
            domain.setName(domainName);
            domain.setTemplateID(domainTemplate.getId());
            enterprise.createChild(domain);
            Date createDate = new Date(Long.parseLong(domain.getCreationDate()));
            System.out.println("New Level 3 Domain created with id " + domain.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(domain.getCreationDate()));
            System.out.println("Old Level 3 Domain " + domain.getName() + " already created at " + createDate.toString());
        }
        return domain;
    }

    private Enterprise fetchEnterpriseByName(String enterpriseName) throws RestException {
        String filter = String.format("name == '%s'", enterpriseName);
        EnterprisesFetcher fetcher = session.getMe().getEnterprises();
        Enterprise enterprise = fetcher.getFirst(filter, null, null, null, null, null, true);
        return enterprise;
    }

    private DomainTemplate fetchLevel3DomainTemplateByNameForEnterprise(String templateName, Enterprise enterprise) throws RestException {
        String filter = String.format("name == '%s'", templateName);
        DomainTemplatesFetcher fetcher = enterprise.getDomainTemplates();
        DomainTemplate template = fetcher.getFirst(filter, null, null, null, null, null, true);
        return template;
    }

    private Domain fetchLevel3DomainByNameForEnterprise(String domainName, Enterprise enterprise) throws RestException {
        String filter = String.format("name == '%s'", domainName);
        DomainsFetcher fetcher = enterprise.getDomains();
        Domain domain = fetcher.getFirst(filter, null, null, null, null, null, true);
        return domain;
    }

}
