package main

import (
	"fmt"
	"os"

	"github.com/nuagenetworks/go-bambou/bambou"
	"github.com/nuagenetworks/vspk-go/vspk"
)

var vsdURL = "https://localhost:8443"
var vsdUser = "csproot"
var vsdPass = "csproot"
var vsdEnterprise = "csp"

func handleError(err *bambou.Error, t string, o string) {
	if err != nil {
		fmt.Println("Unable to " + o + " \"" + t + "\": " + err.Description)
		os.Exit(1)
	}
}

func main() {
	s, root := vspk.NewSession(vsdUser, vsdPass, vsdEnterprise, vsdURL)
	if err := s.Start(); err != nil {
		fmt.Println("Unable to connect to Nuage VSD: " + err.Description)
		os.Exit(1)
	}

	//======================================
	//         CREATE OPERATION
	//======================================
	opName := "VSPK_GO_Profile"
	// create a new EnterpriseProfile struct, set a mandatory `Name` attribute and get the pointer
	op := &vspk.EnterpriseProfile{Name: opName}

	// place a new child EnterpriseProfile under the root
	err := root.CreateEnterpriseProfile(op)
	handleError(err, "Organization Profile", "CREATE")

	//======================================
	//         READ OPERATION
	//======================================
	// get a list of Enterprise Profiles using the filtering feature
	ops, err := root.EnterpriseProfiles(&bambou.FetchingInfo{Filter: opName})
	handleError(err, "Organization Profile", "READ")

	fmt.Printf("Organization Profiles fetched by a filter 'Name == %s' has the %s identifier\n", opName, ops[0].ID)

	//======================================
	//         UPDATE OPERATION
	//======================================
	// update the description attribute of the Org Profile
	op.Description = "VSPK GO Description"

	op.Save()

	//======================================
	//         DELETE OPERATION
	//======================================
	// delete Org Profile created in the previous steps
	op.Delete()
	ops, err = root.EnterpriseProfiles(&bambou.FetchingInfo{Filter: opName})
	// verify that no Org Profiles exists after the delete operation
	fmt.Printf("Num of Org Profiles matched by a filter 'Name == %s': %d", opName, len(ops))
}
