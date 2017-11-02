using net.nuagenetworks.vspk.v5_0;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net;
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

            if (this.enterprise.NUAvatarType == Enterprise.EAvatarType.COMPUTEDURL)
            {
                // Modify the URL in case the VSD is behind a reverse proxy
                Uri u = new Uri(this.enterprise.NUAvatarData);
                Uri u1 = new Uri(session.getRestBaseUrl());
                var builder = new UriBuilder(u);
                builder.Host = u1.Host;
                builder.Port = u1.Port;
                string imageURI = builder.Uri.ToString();

                HttpWebRequest request = (HttpWebRequest)WebRequest.Create(imageURI);
                request.ServerCertificateValidationCallback += (sender2, certificate, chain, sslPolicyErrors) => true;
                WebResponse response = request.GetResponse();
                Stream stream = response.GetResponseStream();
                Image image = Image.FromStream(stream);
                stream.Close();
                pictureBox1.Image = image;
            }

            updateDomainList();
            updateVMList();
            updateNSGs();

            this.textBox1.Text = this.enterprise.NUName;
            this.textBox2.Text = this.enterprise.NUDescription;
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
            this.enterprise.save(session,1);
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
            NetworkView.createNetwork(this.session, this.enterprise);
            updateDomainList();
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
            var n1 = treeView1.Nodes.Add(domain.NUId, domain.NUName,0,0);
            var zf = domain.getZones();
            var zones = zf.fetch(this.session);

            if (zones !=null) foreach (var z in zones)
            {
                var n2 = n1.Nodes.Add(z.NUId, z.NUName,4,4);
                var sf = z.getSubnets();
                var subnets = sf.fetch(this.session);

                if (subnets != null) foreach (var s in subnets)
                {
                    n2.Nodes.Add(s.NUId, s.NUName+" - " + s.NUAddress,1,1);
                }
            }
        }

        private void updateVMList()
        {
            treeView2.Nodes.Clear();
            var vf = this.enterprise.getVMs();
            var vms = vf.fetch(this.session);

            if (vms != null) foreach (var v in vms)
            {
                addVM(v);
            }

            treeView2.ExpandAll();
        }

        private void addVM(VM vm)
        {
            var n1 = treeView2.Nodes.Add(vm.NUId, vm.NUName,2,2);
            var viff = vm.getVMInterfaces();
            var vifs = viff.fetch(this.session);

            if (vifs != null) foreach (var vif in vifs)
            {
                n1.Nodes.Add(vif.NUId, vif.NUName,3,3);
            }
        }

        private void button4_Click(object sender, EventArgs e)
        {
            if (treeView1.SelectedNode == null || treeView1.SelectedNode.Level != 2)
            {
                MessageBox.Show("Please select a subnet in the treeview above first");
                return;
            }

            Random rd = new Random();
            string r = rd.Next().ToString();
            string mac = maskedTextBox6.Text;

            VM vm = new VM();
            vm.NUName = maskedTextBox5.Text;
            vm.NUUUID = maskedTextBox4.Text;
            VMInterface vmi = new VMInterface();
            vmi.NUAttachedNetworkType = VMInterface.EAttachedNetworkType.SUBNET;
            vmi.NUAttachedNetworkID = treeView1.SelectedNode.Name;
            vmi.NUName = mac.Replace(':', '_');
            vmi.NUMAC = mac;
            vm.NUInterfaces = new List<VMInterface>();
            vm.NUInterfaces.Add(vmi);
            session.getMe().createChild(session,vm);
            updateVMList();
        }

        private void button5_Click(object sender, EventArgs e)
        {
            if (treeView1.SelectedNode == null || treeView1.SelectedNode.Level != 2)
            {
                MessageBox.Show("Please select a subnet in the treeview first");
                return;
            }

            NetworkView.editNetwork(this.session, treeView1.SelectedNode.Name);
            updateDomainList();
        }

        private void groupBox4_Enter(object sender, EventArgs e)
        {

        }

        private void updateNSGs()
        {
            var nsgf = this.enterprise.getNSGateways();
            var nsgList = nsgf.fetch(this.session);
            if (nsgList == null) return;

            listBox1.Items.Clear();
            foreach (var nsg in nsgList)
            {
                ComboboxItem ci = new ComboboxItem();
                ci.Name = nsg.NUName;
                ci.Id = nsg.NUId;
                listBox1.Items.Add(ci);
            }
        }

        private void button6_Click(object sender, EventArgs e)
        {
            NSGView.createNSG(this.session, this.enterprise);
            this.updateNSGs();
        }

        private void button7_Click(object sender, EventArgs e)
        {
            if (listBox1.SelectedItem == null) return;
            NSGateway nsg = new NSGateway();
            nsg.NUId = ((ComboboxItem)listBox1.SelectedItem).Id;
            nsg.fetch(this.session);
            NSGView.editNSG(this.session, this.enterprise, nsg);
            updateNSGs();
        }
    }
}
