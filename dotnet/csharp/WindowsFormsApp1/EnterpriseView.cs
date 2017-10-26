using net.nuagenetworks.vspk.v5_0;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    public partial class EnterpriseView : Form
    {
        private string enterpriseID;
        private VSDSession session;
        private Enterprise enterprise;
        private List<Domain> domains;

        public EnterpriseView(VSDSession session, string id)
        {
            this.enterpriseID = id;
            this.session = session;
            InitializeComponent();
        }

        private void EnterpriseView_Load(object sender, EventArgs e)
        {
            this.enterprise = new Enterprise();
            this.enterprise.NUId = enterpriseID;
            this.enterprise.fetch(this.session);

            updateDomainList();

            this.textBox1.Text = this.enterprise.NUName;
            this.textBox2.Text = this.enterprise.NUDescription;
        }


        private void CreateDomainZoneSubnet(string network, string netmask, string gateway)
        {
            Random rd = new Random();
            string r = rd.Next().ToString();

            DomainTemplate dt1 = new DomainTemplate();
            dt1.NUName = "DomainTemplate"+r;
            enterprise.createChild(session, dt1);
            if (dt1.NUParentType != typeof(Enterprise)) throw new Exception("Failed");

            Domain d1 = new Domain();
            d1.NUName = "Domain"+r;
            d1.NUTemplateID = dt1.NUId;
            enterprise.createChild(session, d1);

            Zone z1 = new Zone();
            z1.NUName = "Zone1";
            d1.createChild(session, z1);

            Subnet s1 = new Subnet();
            s1.NUName = "subnet1";
            s1.NUNetmask = netmask;
            s1.NUGateway = gateway;
            s1.NUAddress = network;
            z1.createChild(session, s1);
            if (s1.NUParentType != typeof(Zone)) throw new Exception("Failed");

            updateDomainList();
        }

        private Domain getDomainByName(string name)
        {
            foreach (var d in this.domains)
            {
                if (d.NUName == name) return d;
            }
            return null;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            this.enterprise.NUDescription = this.textBox2.Text;
            this.enterprise.save(session);
        }

        private void button2_Click(object sender, EventArgs e)
        {
            if (treeView1.SelectedNode == null) return;

            if (treeView1.SelectedNode.Level == 0)
            {
                var d = new Domain();
                d.NUId = treeView1.SelectedNode.Name;
                d.delete(this.session, 1);
            }
            if (treeView1.SelectedNode.Level == 1)
            {
                var d = new Zone();
                d.NUId = treeView1.SelectedNode.Name;
                d.delete(this.session, 1);
            }
            if (treeView1.SelectedNode.Level == 2)
            {
                var d = new Subnet();
                d.NUId = treeView1.SelectedNode.Name;
                d.delete(this.session, 1);
            }

            updateDomainList();
        }

        private void button3_Click(object sender, EventArgs e)
        {
            CreateDomainZoneSubnet(maskedTextBox1.Text, maskedTextBox2.Text, maskedTextBox3.Text);
        }

        private void updateDomainList()
        {
            treeView1.Nodes.Clear();
            var df = this.enterprise.getDomains();
            this.domains = df.fetch(this.session);

            if (this.domains != null) foreach (var d in this.domains)
            {
                addNetwork(d);
            }

            treeView1.ExpandAll();
        }

        private void addNetwork(Domain domain)
        {
            var n1 = treeView1.Nodes.Add(domain.NUId, domain.NUName);
            var zf = domain.getZones();
            var zones = zf.fetch(this.session);

            if (zones !=null) foreach (var z in zones)
            {
                var n2 = n1.Nodes.Add(z.NUId, z.NUName);
                var sf = z.getSubnets();
                var subnets = sf.fetch(this.session);

                if (subnets != null) foreach (var s in subnets)
                {
                    n2.Nodes.Add(s.NUId, s.NUName+" - " + s.NUAddress);
                }
            }
        }

    }
}
