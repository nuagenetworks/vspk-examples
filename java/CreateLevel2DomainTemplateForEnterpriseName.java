import java.util.Date;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.L2DomainTemplate;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.L2DomainTemplatesFetcher;

/**
 * Idempotently creates a VSD Level 2 Domain Template object within an existing Enterprise
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Enterprise matching MY_ENTERPRISE_NAME
 */
public class CreateLevel2DomainTemplateForEnterpriseName {
	private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
	private static final String MY_ENTERPRISE_NAME = "MyLittleEnterprise";
	private static final String MY_L2_TEMPLATE_NAME = "MyLittleLevel2DomainTemplate";
	private static final VSDSession session;

	static {
		session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
	}

	public static void main(String[] args) throws RestException {
        System.out.println("Creating Level 2 Domain Template : " + MY_L2_TEMPLATE_NAME + " in Enterprise " + MY_ENTERPRISE_NAME);
        session.start();
        CreateLevel2DomainTemplateForEnterpriseName instance = new CreateLevel2DomainTemplateForEnterpriseName();
        Enterprise enterprise = instance.fetchEnterpriseByName(MY_ENTERPRISE_NAME);
        if (enterprise != null) {
            instance.createLevel2DomainTemplateInEnterprise(MY_L2_TEMPLATE_NAME, enterprise);
        } else {
            System.out.println("Operation not performed due to missing Enterprise " + MY_ENTERPRISE_NAME);
        }
	}

	private L2DomainTemplate createLevel2DomainTemplateInEnterprise(String templateName, Enterprise enterprise) throws RestException {
	    L2DomainTemplate template = this.fetchLevel2DomainTemplateByNameForEnterprise(templateName, enterprise);
        if (template == null) {
            template = new L2DomainTemplate();
            template.setName(templateName);
            enterprise.createChild(template);
            Date createDate = new Date(Long.parseLong(template.getCreationDate()));
            System.out.println("New Level 2 Domain Template created with id " + template.getId() + " at " + createDate.toString());
        } else {
            Date createDate = new Date(Long.parseLong(template.getCreationDate()));
            System.out.println("Old Level 2 Domain Template " + template.getName() + " already created at " + createDate.toString());
        }
        return template;
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
}
