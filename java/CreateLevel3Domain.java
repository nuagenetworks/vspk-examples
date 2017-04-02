import java.util.Date;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v4_0.Domain;
import net.nuagenetworks.vspk.v4_0.Domain.ApplicationDeploymentPolicy;
import net.nuagenetworks.vspk.v4_0.DomainTemplate;
import net.nuagenetworks.vspk.v4_0.Enterprise;
import net.nuagenetworks.vspk.v4_0.VSDSession;
import net.nuagenetworks.vspk.v4_0.fetchers.DomainTemplatesFetcher;
import net.nuagenetworks.vspk.v4_0.fetchers.EnterprisesFetcher;

/**
 * Creates a Level 3 Domain object using an existing Level 3 Domain Template
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires an existing Enterprise matching MY_ENTERPRISE_NAME.  See CreateEnterprise.java
 * Precondition - requires an existing Level 3 Domain Template matching MY_TEMPLATE_NAME.  See CreateLevel3DomainTemplate.java
*/
public class CreateLevel3Domain {
    private static final String MY_VSD_SERVER_PORT	= "https://135.121.118.59:8443";
    private static final String MY_ENTERPRISE_NAME	= "MyLittleEnterprise";
    private static final String MY_TEMPLATE_NAME	= "MyLittleLevel3DomainTemplate";
    private static final String MY_L3_DOMAIN_NAME	= "MyLittleLevel3Domain";
    private static final VSDSession session;
    
    static { session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT); }

    public static void main(String[] args) throws RestException {
        System.out.println("Creating Level 3 Domain : " + MY_L3_DOMAIN_NAME + " in Enterprise " + MY_ENTERPRISE_NAME);
        session.start();
        CreateLevel3Domain	instance	= new CreateLevel3Domain();
        Enterprise			enterprise	= instance.fetchEnterpriseByName(MY_ENTERPRISE_NAME);
        DomainTemplate		template	= instance.fetchLevel3DomainTemplateByName(MY_TEMPLATE_NAME, enterprise);
        instance.createLevel3DomainInEnterprise(template, enterprise);
    }

	private void createLevel3DomainInEnterprise(DomainTemplate domainTemplate, Enterprise enterprise) throws RestException {
		Domain domain = new Domain();
		domain.setName(MY_L3_DOMAIN_NAME);
		domain.setTemplateID(domainTemplate.getId());
		domain.setApplicationDeploymentPolicy(ApplicationDeploymentPolicy.NONE);
		enterprise.createChild(domain);
	}

	private Enterprise fetchEnterpriseByName(String enterpriseName) throws RestException {
        String				filter		= String.format("name == '%s'", enterpriseName);
        EnterprisesFetcher	fetcher		= session.getMe().getEnterprises();
        Enterprise			enterprise	= fetcher.getFirst(filter, null, null, null, null, null, true);
        Date				createDate	= new Date(Long.parseLong(enterprise.getCreationDate()));
        System.out.println("Enterprise : " + enterprise.getName() + " was created at : " + createDate.toString());
        return enterprise;
	}

	private DomainTemplate fetchLevel3DomainTemplateByName(String templateName, Enterprise enterprise) throws RestException {
        String					filter		= String.format("name == '%s'", templateName);
    	DomainTemplatesFetcher	fetcher		= enterprise.getDomainTemplates();
    	DomainTemplate			template	= fetcher.getFirst(filter, null, null, null, null, null, true);
        Date					createDate	= new Date(Long.parseLong(template.getCreationDate()));
        System.out.println("Level 3 Domain Template : " + template.getName() + " was created at : " + createDate.toString());
        return template;
	}
	
}
