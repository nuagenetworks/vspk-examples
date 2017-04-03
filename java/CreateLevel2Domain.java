import java.util.Date;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v4_0.L2Domain;
import net.nuagenetworks.vspk.v4_0.L2DomainTemplate;
import net.nuagenetworks.vspk.v4_0.Enterprise;
import net.nuagenetworks.vspk.v4_0.VSDSession;
import net.nuagenetworks.vspk.v4_0.fetchers.L2DomainTemplatesFetcher;
import net.nuagenetworks.vspk.v4_0.fetchers.EnterprisesFetcher;

/**
 * Creates a Level 2 Domain object using an existing Level 2 Domain Template
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Enterprise matching MY_ENTERPRISE_NAME. See CreateEnterprise.java
 * Precondition - requires an existing Level 2 Domain Template matching MY_TEMPLATE_NAME. See CreateLevel2DomainTemplate.java
 */
public class CreateLevel2Domain {
	private static final String MY_VSD_SERVER_PORT = "https://135.121.118.59:8443";
	private static final String MY_ENTERPRISE_NAME = "MyLittleEnterprise";
	private static final String MY_TEMPLATE_NAME = "MyLittleLevel2DomainTemplate";
	private static final String MY_DOMAIN_NAME = "MyLittleLevel2Domain";
	private static final VSDSession session;

	static {
		session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
	}

	public static void main(String[] args) throws RestException {
		System.out.println("Creating Level 2 Domain : " + MY_DOMAIN_NAME + " in Enterprise " + MY_ENTERPRISE_NAME);
		session.start();
		CreateLevel2Domain instance = new CreateLevel2Domain();
		Enterprise enterprise = instance.fetchEnterpriseByName(MY_ENTERPRISE_NAME);
		L2DomainTemplate template = instance.fetchLevel2DomainTemplateByName(MY_TEMPLATE_NAME, enterprise);
		instance.createLevel2DomainInEnterprise(template, enterprise);
	}

	private void createLevel2DomainInEnterprise(L2DomainTemplate domainTemplate, Enterprise enterprise) throws RestException {
		L2Domain domain = new L2Domain();
		domain.setName(MY_DOMAIN_NAME);
		domain.setTemplateID(domainTemplate.getId());
		enterprise.createChild(domain);
	}

	private Enterprise fetchEnterpriseByName(String enterpriseName) throws RestException {
		String filter = String.format("name == '%s'", enterpriseName);
		EnterprisesFetcher fetcher = session.getMe().getEnterprises();
		Enterprise enterprise = fetcher.getFirst(filter, null, null, null, null, null, true);
		Date createDate = new Date(Long.parseLong(enterprise.getCreationDate()));
		System.out.println("Enterprise : " + enterprise.getName() + " was created at : " + createDate.toString());
		return enterprise;
	}

	private L2DomainTemplate fetchLevel2DomainTemplateByName(String templateName, Enterprise enterprise) throws RestException {
		String filter = String.format("name == '%s'", templateName);
		L2DomainTemplatesFetcher fetcher = enterprise.getL2DomainTemplates();
		L2DomainTemplate template = fetcher.getFirst(filter, null, null, null, null, null, true);
		Date createDate = new Date(Long.parseLong(template.getCreationDate()));
		System.out.println("Level 2 Domain Template : " + template.getName() + " was created at : " + createDate.toString());
		return template;
	}
}
