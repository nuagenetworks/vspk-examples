using net.nuagenetworks.bambou;
using net.nuagenetworks.vspk.v5_0;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    public partial class NSGView : Form
    {
        private VSDSession session;
        private Enterprise enterprise;
        private NSGateway nsg;
        private List<Tuple<Subnet, List<VPort>>> subnetList;

        private NSGView()
        {
            this.nsg = null;
            this.enterprise = null;

            InitializeComponent();
        }

        public static void createNSG(VSDSession session, Enterprise enterprise)
        {
            NSGView nv = new NSGView();

            nv.session = session;
            nv.enterprise = enterprise;

            nv.ShowDialog();

        }

        public static void editNSG(VSDSession session, Enterprise enterprise, NSGateway nsg)
        {
            NSGView nv = new NSGView();

            nv.session = session;
            nv.enterprise = enterprise;
            nv.nsg = nsg;
            nv.ShowDialog();

        }

        private void NSGView_Load(object sender, EventArgs e)
        {
            var userFetcther = this.enterprise.getUsers();
            var templateFetcher = this.session.getMe().getNSGatewayTemplates();
            var userList = userFetcther.fetch(this.session);
            var templateList = templateFetcher.fetch(this.session);

            foreach (var t in templateList)
            {
                ComboboxItem ci = new ComboboxItem();
                ci.Name = t.NUName;
                ci.Id = t.NUId;
                comboBox1.Items.Add(ci);
            }

            /*foreach (var user in userList)
            {
                ComboboxItem ci = new ComboboxItem();
                ci.Name = user.NUFirstName + " " + user.NULastName;
                ci.Id = user.NUId;
                var item = comboBox2.Items.Add(ci);
                }
            }*/

           
            if (this.nsg == null)
            {
            }
            else
            {
                subnetList = new List<Tuple<Subnet, List<VPort>>>();
                var domainsList = this.enterprise.getDomains().fetch(this.session);
                if (domainsList != null)
                {
                    foreach (var d in domainsList)
                    {
                        var zones = d.getZones().fetch(this.session);
                        if (zones == null) continue;
                        foreach (var z in zones)
                        {
                            var subnets = z.getSubnets().fetch(this.session);
                            if (subnets == null) continue;
                            foreach (var s in subnets)
                            {
                                var vports = s.getVPorts().fetch(this.session);
                                subnetList.Add(new Tuple<Subnet, List<VPort>>(s,vports));
                            }
                        }
                    }
                }

                foreach (var s in subnetList)
                {
                    ComboboxItem ci = new ComboboxItem();
                    ci.Id = s.Item1.NUId;
                    ci.Name = s.Item1.NUName;
                    comboBox2.Items.Add(ci);
                }

                comboBox1.Enabled = false;
                textBox1.Text = this.nsg.NUName;
                var portsList = this.nsg.getNSPorts().fetch(this.session);

                foreach (var port in portsList)
                {
                    if (port.NUPortType != NSPort.EPortType.ACCESS) continue;

                    var n1 = treeView1.Nodes.Add(port.NUId, port.NUName, 0, 0);
                    var vlans = port.getVLANs().fetch(this.session);
                    if (vlans != null)
                    {
                        foreach (var vlan in vlans)
                        {
                            var n2 = n1.Nodes.Add(vlan.NUId, vlan.NUValue.ToString(), 1, 1);
                        }
                    }
                }
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {

            if (this.nsg == null)
            {
                NSGateway nsg = new NSGateway();
                nsg.NUName = textBox1.Text;
                ComboboxItem ci = (ComboboxItem)comboBox1.SelectedItem;
                nsg.NUTemplateID = ci.Id;
                this.enterprise.createChild(this.session, nsg);
            }
            else
            {
                this.nsg.NUName = textBox1.Text;
                this.nsg.save(this.session);

            }
            this.Close();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void treeView1_AfterSelect(object sender, TreeViewEventArgs e)
        {
            if (treeView1.SelectedNode == null || treeView1.SelectedNode.Level != 1)
            {
                button3.Enabled = false;
                return;
            }

            Subnet subnet = getSubnetAssignedToVlan(treeView1.SelectedNode.Name);
            if (subnet == null)
            {
                comboBox2.Text = "";
                button3.Enabled = true;
                button4.Enabled = false;
            }
            else
            {
                comboBox2.Text = subnet.NUName;
                button4.Enabled = true;
                button3.Enabled = false;
            }
        }

        private void button3_Click(object sender, EventArgs e)
        {
            string subnetID = ((ComboboxItem)comboBox2.SelectedItem).Id;
            string vlanID = treeView1.SelectedNode.Name;

            assignNSGVlanToSubnet(subnetID, vlanID);
        }

        private Subnet getSubnetAssignedToVlan(string vlanID)
        {
            foreach (var item in subnetList)
            {
                if (item.Item2 == null) continue;
                foreach (var vp in item.Item2)
                {
                    if (vp.NUVLANID == vlanID) return item.Item1;
                }
            }
            return null;
        }

        private void assignNSGVlanToSubnet(string subnetID, string vlanID)
        {
            Random rd = new Random();
            string r = rd.Next().ToString();

            Subnet subnet = new Subnet();
            subnet.NUId = subnetID;
            subnet.fetch(this.session);

            VPort vport = new VPort();
            vport.NUName = "vport"+r;
            vport.NUType = VPort.EType.BRIDGE;
            vport.NUVLANID = vlanID;
            vport.NUAddressSpoofing = VPort.EAddressSpoofing.ENABLED;

            try
            {
                subnet.createChild(this.session, vport);
            }
            catch (RestException re)
            {
                MessageBox.Show(re.Message, "Could not link vlan to subnet");
                return;
            }
            MessageBox.Show("Assigned!", "Success");
        }

        private void button4_Click(object sender, EventArgs e)
        {
            var vlanid = treeView1.SelectedNode.Name;

            foreach (var item in subnetList)
            {
                if (item.Item2 == null) continue;
                foreach (var vp in item.Item2)
                {
                    if (vp.NUVLANID == vlanid)
                    {
                        vp.delete(this.session,1);
                        button3.Enabled = true;
                        button4.Enabled = false;
                        comboBox2.Text = "";
                        return;
                    }
                }
            }

        }
    }

    public class ComboboxItem
    {
        public string Name { get; set; }
        public string Id { get; set; }

        public override string ToString()
        {
            return Name;
        }
    }
}
