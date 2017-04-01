package main

import (
	"fmt"
	"os"
	"strconv"

	"github.com/nuagenetworks/vspk-go/vspk"
)

var vsdUrl string = "https://localhost:8443"
var vsdUser string = "csproot"
var vsdPass string = "csproot"
var vsdEnterprise string = "csp"

func main() {
	mysession, root := vspk.NewSession(vsdUser, vsdPass, vsdEnterprise, vsdUrl)
	if err := mysession.Start(); err != nil {
		fmt.Println("Unable to connect to Nuage VSD: " + err.Description)
		os.Exit(1)
	}

	enterprises, err := root.Enterprises(nil)
	if err != nil {
		fmt.Println("Unable to fetch enterprises: " + err.Description)
		os.Exit(1)
	}
	fmt.Println("Number of enterprises retrieved: " + strconv.Itoa(len(enterprises)))

	for _, enterprise := range enterprises {
		fmt.Println(enterprise.Name)
	}
}
