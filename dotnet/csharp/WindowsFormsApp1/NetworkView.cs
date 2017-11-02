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
    public partial class NetworkView : Form
    {
        private Enterprise enterprise;
        private Subnet subnet;
        private VSDSession session;


        private NetworkView()
        {
            InitializeComponent();
        }

        public static void editNetwork(VSDSession s, string networkID)
        {
            NetworkView nv = new NetworkView();
            nv.session = s;
            nv.subnet = new Subnet();
            nv.subnet.NUId = networkID;
            nv.subnet.fetch(s);
            nv.enterprise = null;
            nv.ShowDialog();
        }

        public static void createNetwork(VSDSession s, Enterprise enterprise)
        {
            NetworkView nv = new NetworkView();
            nv.enterprise = enterprise;
            nv.subnet = null;
            nv.session = s;
            nv.ShowDialog();
        }

        private void NetworkView_Load(object sender, EventArgs e)
        {
            if (this.subnet != null)
            {
                maskedTextBox4.Text = this.subnet.NUName;
                maskedTextBox2.Text = this.subnet.NUNetmask;
                maskedTextBox3.Text = this.subnet.NUGateway;
                maskedTextBox1.Text = this.subnet.NUAddress;

                var vf = this.subnet.getVPorts();
                var vportlist = vf.fetch(this.session);
                if (vportlist != null)
                {
                    foreach (var v in vportlist)
                    {
                        listView1.Items.Add(v.NUId, v.NUName, 0);
                    }
                }
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (this.enterprise != null)
            {
                Random rd = new Random();
                string r = rd.Next().ToString();

                DomainTemplate dt1 = new DomainTemplate();
                dt1.NUName = "DomainTemplate" + r;
                enterprise.createChild(session, dt1);
                if (dt1.NUParentType != typeof(Enterprise)) throw new Exception("Failed");

                Domain d1 = new Domain();
                d1.NUName = "Domain" + r;
                d1.NUTemplateID = dt1.NUId;
                enterprise.createChild(session, d1);

                Zone z1 = new Zone();
                z1.NUName = "Zone1";
                d1.createChild(session, z1);

                Subnet s1 = new Subnet();
                s1.NUName = maskedTextBox4.Text;
                s1.NUNetmask = maskedTextBox2.Text;
                s1.NUGateway = maskedTextBox3.Text;
                s1.NUAddress = maskedTextBox1.Text;
                z1.createChild(session, s1);
                if (s1.NUParentType != typeof(Zone)) throw new Exception("Failed");
            }
            else if (this.subnet != null)
            {
                this.subnet.NUName = maskedTextBox4.Text;
                this.subnet.NUNetmask = maskedTextBox2.Text;
                this.subnet.NUGateway = maskedTextBox3.Text;
                this.subnet.NUAddress = maskedTextBox1.Text;

                try
                {
                    this.subnet.save(this.session);
                }
                catch (RestException re)
                {
                    MessageBox.Show(re.Message, "Can't save network");
                }
            }

            this.Close();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            this.Close();
        }
    }
}
