package main

import (
	"fmt"
	"os"
	"strconv"
	"time"

	"github.com/nuagenetworks/go-bambou/bambou"
	"github.com/nuagenetworks/vspk-go/vspk"
)

var vsdUrl string = "https://localhost:8443"
var vsdUser string = "csproot"
var vsdPass string = "csproot"
var vsdEnterprise string = "csp"
var subnetId string = "fc595651-8bf8-4e2c-adcd-b9aad4557267"
var isL2Domain bool = true
var doCleanup bool = true
var amount int
var requests int = 0

type VPortsParent interface {
	vspk.VPortsParent
	Fetch() *bambou.Error
}

func handleVPorts(s VPortsParent) {
	if err := s.Fetch(); err != nil {
		fmt.Println("Unable to fetch the Nuage subnet: " + err.Description)
		os.Exit(1)
	}
	requests++

	var vPorts []*vspk.VPort

	fmt.Println("Creating vPorts")
	for i := 0; i < amount; i++ {
		vport := vspk.NewVPort()
		vport.Name = "vPort-" + strconv.Itoa(i)
		if err := s.CreateVPort(vport); err != nil {
			fmt.Println("Unable to create a vPort: " + err.Description)
			os.Exit(1)
		}
		vPorts = append(vPorts, vport)
		requests++
		fmt.Print(".")
	}
	fmt.Println("")

	if doCleanup {
		fmt.Println("Cleaning up vPorts")
		for _, vPort := range vPorts {
			if err := vPort.Delete(); err != nil {
				fmt.Println("Unable to delete vPort for the subnet: " + err.Description)
				os.Exit(1)
			}
			requests++
			fmt.Print(".")
		}
		fmt.Println("")
	}
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Please provide an amount of vPorts to create")
		os.Exit(1)
	}

	a, err := strconv.Atoi(os.Args[1])
	if err != nil {
		fmt.Println("Unknown integer value for number of vPorts")
		os.Exit(1)
	}
	amount = a

	start := time.Now()

	mysession, _ := vspk.NewSession(vsdUser, vsdPass, vsdEnterprise, vsdUrl)
	if err := mysession.Start(); err != nil {
		fmt.Println("Unable to connect to Nuage VSD: " + err.Description)
		os.Exit(1)
	}
	requests++

	if isL2Domain {
		s := vspk.NewL2Domain()
		s.ID = subnetId
		handleVPorts(s)
	} else {
		s := vspk.NewSubnet()
		s.ID = subnetId
		handleVPorts(s)
	}

	fmt.Printf("Executed requests: %d\n", requests)
	elapsed := time.Since(start)
	fmt.Printf("Elapsed time: %.2f seconds\n", elapsed.Seconds())
}
