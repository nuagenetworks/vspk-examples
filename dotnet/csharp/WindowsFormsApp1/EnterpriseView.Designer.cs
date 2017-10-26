namespace WindowsFormsApp1
{
    partial class EnterpriseView
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.label1 = new System.Windows.Forms.Label();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.textBox2 = new System.Windows.Forms.TextBox();
            this.button1 = new System.Windows.Forms.Button();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.groupBox2 = new System.Windows.Forms.GroupBox();
            this.button2 = new System.Windows.Forms.Button();
            this.maskedTextBox3 = new System.Windows.Forms.MaskedTextBox();
            this.label8 = new System.Windows.Forms.Label();
            this.maskedTextBox2 = new System.Windows.Forms.MaskedTextBox();
            this.maskedTextBox1 = new System.Windows.Forms.MaskedTextBox();
            this.label7 = new System.Windows.Forms.Label();
            this.label6 = new System.Windows.Forms.Label();
            this.button3 = new System.Windows.Forms.Button();
            this.treeView1 = new System.Windows.Forms.TreeView();
            this.groupBox1.SuspendLayout();
            this.groupBox2.SuspendLayout();
            this.SuspendLayout();
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(16, 22);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(35, 13);
            this.label1.TabIndex = 0;
            this.label1.Text = "Name";
            // 
            // textBox1
            // 
            this.textBox1.Location = new System.Drawing.Point(82, 19);
            this.textBox1.Name = "textBox1";
            this.textBox1.ReadOnly = true;
            this.textBox1.Size = new System.Drawing.Size(303, 20);
            this.textBox1.TabIndex = 1;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(16, 48);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(60, 13);
            this.label2.TabIndex = 3;
            this.label2.Text = "Description";
            // 
            // textBox2
            // 
            this.textBox2.Location = new System.Drawing.Point(82, 45);
            this.textBox2.Name = "textBox2";
            this.textBox2.Size = new System.Drawing.Size(299, 20);
            this.textBox2.TabIndex = 4;
            // 
            // button1
            // 
            this.button1.Location = new System.Drawing.Point(270, 71);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(111, 23);
            this.button1.TabIndex = 5;
            this.button1.Text = "Update";
            this.button1.UseVisualStyleBackColor = true;
            this.button1.Click += new System.EventHandler(this.button1_Click);
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.button1);
            this.groupBox1.Controls.Add(this.label1);
            this.groupBox1.Controls.Add(this.textBox2);
            this.groupBox1.Controls.Add(this.textBox1);
            this.groupBox1.Controls.Add(this.label2);
            this.groupBox1.Location = new System.Drawing.Point(12, 12);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(391, 111);
            this.groupBox1.TabIndex = 6;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Details";
            // 
            // groupBox2
            // 
            this.groupBox2.Controls.Add(this.treeView1);
            this.groupBox2.Controls.Add(this.button3);
            this.groupBox2.Controls.Add(this.button2);
            this.groupBox2.Controls.Add(this.maskedTextBox3);
            this.groupBox2.Controls.Add(this.maskedTextBox2);
            this.groupBox2.Controls.Add(this.label8);
            this.groupBox2.Controls.Add(this.label6);
            this.groupBox2.Controls.Add(this.label7);
            this.groupBox2.Controls.Add(this.maskedTextBox1);
            this.groupBox2.Location = new System.Drawing.Point(12, 129);
            this.groupBox2.Name = "groupBox2";
            this.groupBox2.Size = new System.Drawing.Size(391, 309);
            this.groupBox2.TabIndex = 7;
            this.groupBox2.TabStop = false;
            this.groupBox2.Text = "Networks";
            // 
            // button2
            // 
            this.button2.Location = new System.Drawing.Point(270, 110);
            this.button2.Name = "button2";
            this.button2.Size = new System.Drawing.Size(111, 23);
            this.button2.TabIndex = 6;
            this.button2.Text = "Delete";
            this.button2.UseVisualStyleBackColor = true;
            this.button2.Click += new System.EventHandler(this.button2_Click);
            // 
            // maskedTextBox3
            // 
            this.maskedTextBox3.Location = new System.Drawing.Point(82, 78);
            this.maskedTextBox3.Name = "maskedTextBox3";
            this.maskedTextBox3.Size = new System.Drawing.Size(181, 20);
            this.maskedTextBox3.TabIndex = 19;
            this.maskedTextBox3.Text = "192.168.1.1";
            // 
            // label8
            // 
            this.label8.AutoSize = true;
            this.label8.Location = new System.Drawing.Point(9, 79);
            this.label8.Name = "label8";
            this.label8.Size = new System.Drawing.Size(49, 13);
            this.label8.TabIndex = 18;
            this.label8.Text = "Gateway";
            // 
            // maskedTextBox2
            // 
            this.maskedTextBox2.Location = new System.Drawing.Point(83, 52);
            this.maskedTextBox2.Name = "maskedTextBox2";
            this.maskedTextBox2.Size = new System.Drawing.Size(181, 20);
            this.maskedTextBox2.TabIndex = 17;
            this.maskedTextBox2.Text = "255.255.255.0";
            // 
            // maskedTextBox1
            // 
            this.maskedTextBox1.Location = new System.Drawing.Point(83, 27);
            this.maskedTextBox1.Name = "maskedTextBox1";
            this.maskedTextBox1.Size = new System.Drawing.Size(181, 20);
            this.maskedTextBox1.TabIndex = 16;
            this.maskedTextBox1.Text = "192.168.1.0";
            // 
            // label7
            // 
            this.label7.AutoSize = true;
            this.label7.Location = new System.Drawing.Point(10, 53);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(33, 13);
            this.label7.TabIndex = 15;
            this.label7.Text = "Mask";
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(10, 27);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(47, 13);
            this.label6.TabIndex = 13;
            this.label6.Text = "Network";
            // 
            // button3
            // 
            this.button3.Location = new System.Drawing.Point(270, 25);
            this.button3.Name = "button3";
            this.button3.Size = new System.Drawing.Size(111, 23);
            this.button3.TabIndex = 9;
            this.button3.Text = "Create";
            this.button3.UseVisualStyleBackColor = true;
            this.button3.Click += new System.EventHandler(this.button3_Click);
            // 
            // treeView1
            // 
            this.treeView1.Location = new System.Drawing.Point(12, 104);
            this.treeView1.Name = "treeView1";
            this.treeView1.Size = new System.Drawing.Size(251, 194);
            this.treeView1.TabIndex = 24;
            // 
            // EnterpriseView
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(415, 447);
            this.Controls.Add(this.groupBox2);
            this.Controls.Add(this.groupBox1);
            this.Name = "EnterpriseView";
            this.Text = "EnterpriseView";
            this.Load += new System.EventHandler(this.EnterpriseView_Load);
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            this.groupBox2.ResumeLayout(false);
            this.groupBox2.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox textBox2;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.GroupBox groupBox2;
        private System.Windows.Forms.Button button2;
        private System.Windows.Forms.MaskedTextBox maskedTextBox3;
        private System.Windows.Forms.Label label8;
        private System.Windows.Forms.MaskedTextBox maskedTextBox2;
        private System.Windows.Forms.MaskedTextBox maskedTextBox1;
        private System.Windows.Forms.Label label7;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.Button button3;
        private System.Windows.Forms.TreeView treeView1;
    }
}