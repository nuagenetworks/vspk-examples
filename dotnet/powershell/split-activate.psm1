# Import-Module -Force .\nuage.psm1
# $sid = Find-SubnetID "test-456" "domain1" "zone1" "subnet1"
# Split-Activate $sid "6962929e-2380-4993-b75b-0b329188fbfc" "66:55:44:11:22:33"

[Reflection.Assembly]::LoadFrom("C:\vspk\Newtonsoft.Json.dll")
[Reflection.Assembly]::LoadFrom("C:\vspk\net.nuagenetworks.bambou.dll")
[Reflection.Assembly]::LoadFrom("C:\vspk\net.nuagenetworks.vspk.dll")

function Find-SubnetID($enterprise,$domain,$zone,$subnet) {
    $s = new-object net.nuagenetworks.vspk.v5_0.VSDSession -argumentlist "csproot", "csproot", "csp", "https://vsd.local:8443"
    
    $ef = $s.getMe().getEnterprises();
    $e = $ef.fetch($s,"name == '$enterprise'", [NullString]::Value, $null, -1, -1, [NullString]::Value, $true)[0]    
    
    $df = $e.getDomains();
    $d = $df.fetch($s,"name == '$domain'", [NullString]::Value, $null, -1, -1, [NullString]::Value, $true)[0]    
    
    $zf = $d.getZones();
    $z = $zf.fetch($s,"name == '$zone'", [NullString]::Value, $null, -1, -1, [NullString]::Value, $true)[0]    
    
    $sf = $z.getSubnets();
    $subnet = $sf.fetch($s,"name == '$subnet'", [NullString]::Value, $null, -1, -1, [NullString]::Value, $true)[0]    
    
    return $subnet.NUId
}

function Split-Activate($subnetid, $vmUUID, $mac) {
    $s = new-object net.nuagenetworks.vspk.v5_0.VSDSession -argumentlist "csproot", "csproot", "csp", "https://vsd.local:8443"

    $vm = new-object net.nuagenetworks.vspk.v5_0.VM
    $vm.NUName = $vmUUID
    $vm.NUUUID = $vmUUID
    $vminterface = new-object net.nuagenetworks.vspk.v5_0.VMInterface
    $vminterface.NUAttachedNetworkType = [net.nuagenetworks.vspk.v5_0.VMInterface+EAttachedNetworkType]::SUBNET
    $vminterface.NUAttachedNetworkID = $subnetid
    $vminterface.NUName = $mac.Replace(':', '_')
    $vminterface.NUMAC = $mac;
    $vm.NUInterfaces = $vminterface
    $s.getMe().createChild($s, $vm)
}

Export-ModuleMember -Function 'Split-Activate'
Export-ModuleMember -Function 'Find-SubnetID'


