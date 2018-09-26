import java.util.ArrayList;
import java.util.List;

import net.nuagenetworks.bambou.RestException;
import net.nuagenetworks.vspk.v5_0.Domain;
import net.nuagenetworks.vspk.v5_0.Enterprise;
import net.nuagenetworks.vspk.v5_0.Subnet;
import net.nuagenetworks.vspk.v5_0.VM;
import net.nuagenetworks.vspk.v5_0.VMInterface;
import net.nuagenetworks.vspk.v5_0.VPort;
import net.nuagenetworks.vspk.v5_0.VSDSession;
import net.nuagenetworks.vspk.v5_0.Zone;
import net.nuagenetworks.vspk.v5_0.fetchers.DomainsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.EnterprisesFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.SubnetsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VMsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.VPortsFetcher;
import net.nuagenetworks.vspk.v5_0.fetchers.ZonesFetcher;

/**
 * For each existing Enterprise, fetch its associated Level 3 Domains, Zones, Subnets, VPorts and VMs. Output collected data in CSV format.
 * 
 * Precondition - requires a running VSD server at port matching MY_VSD_SERVER_PORT
 * Precondition - requires 0 or more existing Enterprises
 * Precondition - requires 0 or more existing Level 3 Domains
 * Precondition - requires 0 or more existing Zones
 * Precondition - requires 0 or more existing Subnets
 * Precondition - requires 0 or more existing VPorts
 * Precondition - requires 0 or more existing VMs
 */
public class ListAllEnterprisesAndTheirAssociatesAsCSV {
    private static final String MY_VSD_SERVER_PORT = "https://135.228.4.108:8443";
    private static final VSDSession session;

    public class InventoryItem implements Cloneable {
        public int enterpriseNumber;
        public String enterpriseName;
        public int domainNumber;
        public String domainName;
        public String domainDescription;
        public int zoneNumber;
        public String zoneName;
        public int subnetNumber;
        public String subnetName;
        public String subnetAddress;
        public String subnetNetmask;
        public int vPortNumber;
        public String vPortName;
        public int vmNumber;
        public String vmName;
        public String vmUUID;
        public int vmInterfaceNumber;
        public String vmInterfaceName;
        public String vmInterfaceMAC;

        @Override
        protected Object clone() throws CloneNotSupportedException {
            return super.clone();
        }
    }

    static {
        session = new VSDSession("csproot", "csproot", "csp", MY_VSD_SERVER_PORT);
    }

    public static void main(String[] args) throws RestException, CloneNotSupportedException {
        System.out.println("Listing all Enterprises and their associated network objects");
        session.start();
        ListAllEnterprisesAndTheirAssociatesAsCSV instance = new ListAllEnterprisesAndTheirAssociatesAsCSV();
        List<Enterprise> enterprises = instance.gatherAllEnterpriseObjects();
        List<InventoryItem> inventoryItems = instance.buildInventory(enterprises);
        instance.dumpInventoryAsCSV(inventoryItems);

    }

    private List<Enterprise> gatherAllEnterpriseObjects() throws RestException {
        EnterprisesFetcher fetcher = session.getMe().getEnterprises();
        List<Enterprise> enterprises = fetcher.get();
        return enterprises;
    }

    private void dumpInventoryAsCSV(List<InventoryItem> inventoryItems) {
        System.out.println("\nNumber of Inventory Items found : " + inventoryItems.size());
        System.out.println("Record Number,Enterprise Number,Enterprise Name,Domain Number,Domain Name,Domain Description,Zone Number,Zone Name,"
                + "Subnet Number,Subnet Name,Subnet Address,Subnet Netmask,VPort Number,VPort Name,"
                + "VM Number,VM Name,VM UUID,VM Interface Number,VM Interface Name,VM Interface MAC");
        int ctr = 0;
        for (InventoryItem item : inventoryItems) {
            System.out.println(++ctr + "," + item.enterpriseNumber + ",'" + item.enterpriseName + "'," + item.domainNumber + ",'" + item.domainName
                    + "','" + item.domainDescription + "'," + item.zoneNumber + ",'" + item.zoneName + "'," + item.subnetNumber + ",'"
                    + item.subnetName + "','" + item.subnetAddress + "','" + item.subnetNetmask + "'" + item.vPortNumber + ",'" + item.vPortName
                    + "'," + item.vmNumber + ",'" + item.vmName + "','" + item.vmUUID + "'," + item.vmInterfaceNumber + ",'" + item.vmInterfaceName
                    + "','" + item.vmInterfaceMAC + "'");
        }
    }

    private List<InventoryItem> buildInventory(List<Enterprise> enterprises) throws CloneNotSupportedException, RestException {
        List<InventoryItem> inventoryItems = new ArrayList<>();
        for (int i = 0; i < enterprises.size(); i++) {
            Enterprise enterprise = enterprises.get(i);
            InventoryItem item = new InventoryItem();
            item.enterpriseNumber = i + 1;
            item.enterpriseName = enterprise.getName();
            inventoryItems.add(item);

            this.addDomainsForEnterpriseToInventory(enterprise, item, inventoryItems);
        }
        return inventoryItems;
    }

    private void addDomainsForEnterpriseToInventory(Enterprise enterprise, InventoryItem currentItem, List<InventoryItem> inventoryItems)
            throws CloneNotSupportedException, RestException {
        DomainsFetcher fetcher = enterprise.getDomains();
        List<Domain> domains = fetcher.get();
        InventoryItem item;

        for (int i = 0; i < domains.size(); i++) {
            if (i > 0) {
                item = (InventoryItem) currentItem.clone();
                inventoryItems.add(item);
            } else {
                item = currentItem;
            }
            Domain domain = domains.get(i);
            item.domainNumber = i + 1;
            item.domainName = domain.getName();
            item.domainDescription = domain.getDescription();
            this.addZonesForDomainToInventory(domain, item, inventoryItems);
        }
    }

    private void addZonesForDomainToInventory(Domain domain, InventoryItem currentItem, List<InventoryItem> inventoryItems)
            throws CloneNotSupportedException, RestException {
        ZonesFetcher fetcher = domain.getZones();
        List<Zone> zones = fetcher.get();
        InventoryItem item;

        for (int i = 0; i < zones.size(); i++) {
            if (i > 0) {
                item = (InventoryItem) currentItem.clone();
                inventoryItems.add(item);
            } else {
                item = currentItem;
            }
            Zone zone = zones.get(i);
            item.zoneNumber = i + 1;
            item.zoneName = zone.getName();
            this.addSubnetsForZoneToInventory(zone, item, inventoryItems);
        }
    }

    private void addSubnetsForZoneToInventory(Zone zone, InventoryItem currentItem, List<InventoryItem> inventoryItems)
            throws CloneNotSupportedException, RestException {
        SubnetsFetcher fetcher = zone.getSubnets();
        List<Subnet> subnets = fetcher.get();
        InventoryItem item;

        for (int i = 0; i < subnets.size(); i++) {
            if (i > 0) {
                item = (InventoryItem) currentItem.clone();
                inventoryItems.add(item);
            } else {
                item = currentItem;
            }
            Subnet subnet = subnets.get(i);
            item.subnetNumber = i + 1;
            item.subnetName = subnet.getName();
            item.subnetAddress = subnet.getAddress();
            item.subnetNetmask = subnet.getNetmask();
            this.addVPortsForSubnetToInventory(subnet, item, inventoryItems);
        }
    }

    private void addVPortsForSubnetToInventory(Subnet subnet, InventoryItem currentItem, List<InventoryItem> inventoryItems)
            throws CloneNotSupportedException, RestException {
        VPortsFetcher fetcher = subnet.getVPorts();
        List<VPort> vPorts = fetcher.get();
        InventoryItem item;

        for (int i = 0; i < vPorts.size(); i++) {
            if (i > 0) {
                item = (InventoryItem) currentItem.clone();
                inventoryItems.add(item);
            } else {
                item = currentItem;
            }
            VPort vPort = vPorts.get(i);
            item.vPortNumber = i + 1;
            item.vPortName = vPort.getName();
            this.addVMsForVPortToInventory(vPort, item, inventoryItems);
        }
    }

    private void addVMsForVPortToInventory(VPort vPort, InventoryItem currentItem, List<InventoryItem> inventoryItems)
            throws CloneNotSupportedException, RestException {
        VMsFetcher fetcher = vPort.getVMs();
        List<VM> vms = fetcher.get();
        InventoryItem item;

        for (int i = 0; i < vms.size(); i++) {
            if (i > 0) {
                item = (InventoryItem) currentItem.clone();
                inventoryItems.add(item);
            } else {
                item = currentItem;
            }
            VM vm = vms.get(i);
            item.vmNumber = i + 1;
            item.vmName = vm.getName();
            item.vmUUID = vm.getUUID();
            this.addVMInterfacesForVMToInventory(vm, item, inventoryItems);
        }
    }

    private void addVMInterfacesForVMToInventory(VM vm, InventoryItem currentItem, List<InventoryItem> inventoryItems)
            throws CloneNotSupportedException {
        List<VMInterface> list = vm.getInterfaces();
        InventoryItem item;

        for (int i = 0; i < list.size(); i++) {
            if (i > 0) {
                item = (InventoryItem) currentItem.clone();
                inventoryItems.add(item);
            } else {
                item = currentItem;
            }
            VMInterface vmInterface = list.get(i);
            item.vmInterfaceNumber = i + 1;
            item.vmInterfaceName = vmInterface.getName();
            item.vmInterfaceMAC = vmInterface.getMAC();
        }
    }
}
