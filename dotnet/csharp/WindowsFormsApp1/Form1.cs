using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using net.nuagenetworks.vspk.v5_0;
using net.nuagenetworks.vspk.v5_0.fetchers;
using net.nuagenetworks.bambou;

namespace WindowsFormsApp1
{
    public partial class Form1 : Form
    {
        private VSDSession session;
        private List<Enterprise> enterpriseList;

        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
        }

        private string CreateEnterpriseDomainZoneSubnet(string enterprisename)
        {
            // Create an enterprise
            Enterprise enterprise = new Enterprise();
            enterprise.NUName = enterprisename;
            enterprise.NUDescription = "";
            session.getMe().createChild(session, enterprise);

            User u1 = new User();
            u1.NUUserName = "pdumais";
            u1.NUFirstName = "Patrick";
            u1.NULastName = "Dumais";
            u1.NUPassword = "123456qwerty";
            u1.NUEmail = "test@test.com";
            enterprise.createChild(session, u1);

            Group g1 = new Group();
            g1.NUName = "Group1";
            enterprise.createChild(session, g1);
            g1.assign(session, new List<User>() { u1 });

            return enterprise.NUId;
        }

        private List<Enterprise> getAllEnterprises()
        {
            EnterprisesFetcher enterprises2 = session.getMe().getEnterprises();
            List<Enterprise> list = enterprises2.fetch(session);
            return list;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            this.session = new VSDSession(textBox2.Text, textBox3.Text, textBox4.Text, textBox1.Text);
            groupBox2.Enabled = true;
            groupBox3.Enabled = true;
        }

        private void button2_Click(object sender, EventArgs e)
        {
            textBox6.Text = CreateEnterpriseDomainZoneSubnet(textBox5.Text);
        }

        private void refreshEnterprises()
        {
            listBox1.Items.Clear();
            this.enterpriseList = getAllEnterprises();
            foreach (var ent in this.enterpriseList)
            {
                listBox1.Items.Add(ent.NUName);
            }
        }

        private void button3_Click(object sender, EventArgs e)
        {
            refreshEnterprises();
        }

        private Enterprise getEnterpriseByName(string name)
        {
            foreach (var e in this.enterpriseList)
            {
                if (e.NUName == name) return e;
            }
            return null;
        }

        private void button4_Click(object sender, EventArgs e)
        {
            if (listBox1.SelectedItem == null) return;

            EnterpriseView ev = new EnterpriseView(session, getEnterpriseByName(listBox1.SelectedItem.ToString()).NUId);
            ev.ShowDialog();
        }

        private void button5_Click(object sender, EventArgs e)
        {
            if (listBox1.SelectedItem == null) return;

            int responseChoice = -1;
            Enterprise ent = getEnterpriseByName(listBox1.SelectedItem.ToString());
            try
            {
                ent.delete(this.session);
                return;
            }
            catch (RestMultipleChoiceException rme)
            {
                DialogResult r = MessageBox.Show(rme.Description, rme.Title, MessageBoxButtons.OKCancel);
                if (r == DialogResult.OK)
                {
                    foreach (var c in rme.Choices)
                    {
                        if (c.Label == "OK")
                        {
                            responseChoice = c.Id;
                        }
                    }
                }
                else if (r == DialogResult.Cancel)
                {
                    foreach (var c in rme.Choices)
                    {
                        if (c.Label == "Cancel")
                        {
                            responseChoice = c.Id;
                        }
                    }
                }
            }
            catch (RestException re)
            {
                MessageBox.Show("Can't delete enterprise. Maybe you need to delete domains in it first");
                return;
            }

            ent.delete(this.session, responseChoice);
            refreshEnterprises();
        }
    }
}
