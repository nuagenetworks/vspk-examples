package main

import (
	"fmt"
	"os"

	"github.com/nuagenetworks/go-bambou/bambou"
	"github.com/nuagenetworks/vspk-go/vspk"
)

var vsdUrl string = "https://localhost:8443"
var vsdUser string = "csproot"
var vsdPass string = "csproot"
var vsdEnterprise string = "csp"

func handleError(err *bambou.Error, t string) {
	if err != nil {
		fmt.Println("Unable to fetch" + t + ": " + err.Description)
		os.Exit(1)
	}
}

func main() {
	mysession, root := vspk.NewSession(vsdUser, vsdPass, vsdEnterprise, vsdUrl)
	if err := mysession.Start(); err != nil {
		fmt.Println("Unable to connect to Nuage VSD: " + err.Description)
		os.Exit(1)
	}

	enterprises, err := root.Enterprises(nil)
	handleError(err, "enterprises")

	for _, enterprise := range enterprises {
		fmt.Print("VMs inside Enterprise ")
		fmt.Println(enterprise.Name)
		vms, err := enterprise.VMs(nil)
		handleError(err, "VMs")
		for _, vm := range vms {
			fmt.Println("|- " + vm.Name)
		}

		fmt.Println("")
		fmt.Print("Domains inside Enterprise ")
		fmt.Println(enterprise.Name)
		domains, err := enterprise.Domains(nil)
		handleError(err, "domains")
		for _, domain := range domains {
			fmt.Println("|- Domain: " + domain.Name)

			zones, err := domain.Zones(nil)
			handleError(err, "zones")
			for _, zone := range zones {
				fmt.Println("   |- Zone: " + zone.Name)

				subnets, err := zone.Subnets(nil)
				handleError(err, "subnets")
				for _, subnet := range subnets {
					fmt.Println("      |- Subnet: " + subnet.Name + " - " + subnet.Address + " - " + subnet.Netmask)
				}
			}

			ingressACLs, err := domain.IngressACLTemplates(nil)
			handleError(err, "ingress ACLs")
			for _, ingressACL := range ingressACLs {
				fmt.Println("   |- Ingress ACL: " + ingressACL.Name)

				rules, err := ingressACL.IngressACLEntryTemplates(nil)
				handleError(err, "Ingress ACL rules")
				for _, rule := range rules {
					fmt.Println("      |- Rule: " + rule.Description)
				}
			}

			egressACLs, err := domain.EgressACLTemplates(nil)
			handleError(err, "egress ACLs")
			for _, egressACL := range egressACLs {
				fmt.Println("   |- Egress ACL: " + egressACL.Name)

				rules, err := egressACL.EgressACLEntryTemplates(nil)
				handleError(err, "Engress ACL rules")
				for _, rule := range rules {
					fmt.Println("      |- Rule: " + rule.Description)
				}
			}
		}
	}
}
