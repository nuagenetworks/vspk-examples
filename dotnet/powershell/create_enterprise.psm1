[Reflection.Assembly]::LoadFrom("C:\vspk\Newtonsoft.Json.dll")
[Reflection.Assembly]::LoadFrom("C:\vspk\net.nuagenetworks.bambou.dll")
[Reflection.Assembly]::LoadFrom("C:\vspk\net.nuagenetworks.vspk.dll")

function New-Enterprise($name) {
    $s = new-object net.nuagenetworks.vspk.v5_0.VSDSession -argumentlist "csproot", "csproot", "csp", "https://vsd.local:8443"
    $e = new-object net.nuagenetworks.vspk.v5_0.Enterprise
    $e.NUName = $name
    $s.getMe().createChild($s,$e);
    return $e.NUId
}

function New-Network($enterprise,$subnet,$netmask,$gateway) {
    $s = new-object net.nuagenetworks.vspk.v5_0.VSDSession -argumentlist "csproot", "csproot", "csp", "https://vsd.local:8443"
    $e = new-object net.nuagenetworks.vspk.v5_0.Enterprise
    $e.NUId = $enterprise
    $e.fetch($s)
    
    $dt = new-object net.nuagenetworks.vspk.v5_0.DomainTemplate
    $dt.NUName = "domaintemplate1"
    $e.createChild($s,$dt)

    $d = new-object net.nuagenetworks.vspk.v5_0.Domain
    $d.NUName = "domain1"
    $d.NUTemplateID = $dt.NUId
    $e.createChild($s,$d)

    $z = new-object net.nuagenetworks.vspk.v5_0.Zone
    $z.NUName = "zone1"
    $d.createChild($s,$z)

    $sub = new-object net.nuagenetworks.vspk.v5_0.Subnet
    $sub.NUName = "subnet1";
    $sub.NUNetmask = $netmask
    $sub.NUGateway = $gateway
    $sub.NUAddress = $subnet
    $z.createChild($s,$sub)
}

Export-ModuleMember -Function 'New-Enterprise'
Export-ModuleMember -Function 'New-Network'


