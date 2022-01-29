package main

import (
	"fmt"
	"os"
	"io/ioutil"
	"flag"
	"strings"
	"time"
	"github.com/nuagenetworks/go-bambou/bambou"
	"github.com/nuagenetworks/vspk-go/vspk"
)

var vsdURL = "https://localhost:8443"
var vsdUser = "csproot"
var vsdPass = "csproot"
var vsdEnterprise = "csp"
var notificationType = "NOTIFY_NSG_REGISTRATION"
var success = false

func handleError(err *bambou.Error, t string, o string) {
	if err != nil {
		fmt.Println("Unable to " + o + " \"" + t + "\": " + err.Description)
		os.Exit(1)
	}
}

func SaveToFile(name string, data string){
	tstr := time.Now().Format("2006_01_02_")
	name = strings.Trim(name," ")
    err := ioutil.WriteFile(tstr+name+".txt", []byte(data), 0644)
    if(err != nil){
		fmt.Printf("\nError saving url to text file with name %s.txt\n",tstr+name)
	}else{
		fmt.Printf("\nUrl stored on file %s.txt\n",tstr+name)
	}
}

func main() {

	urlPtr := flag.String("url", vsdURL, "VSD Url")
	usrPtr := flag.String("usr", vsdUser, "VSD User")
	passPtr := flag.String("pwd", vsdPass, "VSD Password")
	orgPtr := flag.String("org", vsdEnterprise, "VSD Organization")
	nsgPtr := flag.String("nsg", "", "NSG Name")

	flag.Parse()

	fmt.Printf("Connecting %s@%s ... \n", *usrPtr, *urlPtr)
	s, root := vspk.NewSession(*usrPtr, *passPtr, *orgPtr, *urlPtr)
	if err := s.Start(); err != nil {
		fmt.Println("Unable to connect to Nuage VSD: " + err.Description)
		os.Exit(1)
	}

	pushC := bambou.NewPushCenter(s)
	urlGatherer := func(e *bambou.Event) {
		if (e.EntityType == "nsgnotification" && e.Type=="CREATE"){
			data := e.DataMap
			if (data[0]["notificationType"] == notificationType){
				message, _ := data[0]["message"].(map[string]interface{})
				link, _ := message["link"].(string)
				fmt.Printf("URL:\n%s\n", link)
				SaveToFile(*nsgPtr, link)
				success = true
			}
		}
	}
	pushC.RegisterHandlerForIdentity(urlGatherer, bambou.AllIdentity)
	if err := pushC.Start(); err != nil {
		fmt.Println("Unable to Start PushCenter")
		os.Exit(1)
	}
	
	enterprises, err := root.Enterprises(nil)
	if err != nil {
		fmt.Println("Unable to fetch enterprises", err.Description)
		os.Exit(1)
	}
	fmt.Printf("%d enterprises retrieved\n" , len(enterprises))

	for _, enterprise := range enterprises {
		ops, err := enterprise.NSGateways(&bambou.FetchingInfo{Filter: *nsgPtr})
		handleError(err, "Gathering NSG", "READ")
		if (len(ops) == 1){
			nsg := ops[0]
			fmt.Printf("Found NSGateway on %s with name \"%s\"\nNSG ID: %s \n", enterprise.Name, *nsgPtr, nsg.ID)
			boostrapJob := vspk.NewJob()
			boostrapJob.Command = notificationType
			err := nsg.CreateJob(boostrapJob)
			if err != nil {
				fmt.Println("Error adding boostraping job\n", err.Description)
				os.Exit(1)
			}
			for(!success){

			}
		}else{
			fmt.Printf("More than one NSG with name %s\n", *nsgPtr)
		}
	}
}
