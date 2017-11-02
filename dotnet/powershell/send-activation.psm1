# Import-Module -Force .\nuage.psm1
# Send-Activation "Enterprise1" "NSG1" "User1"

[Reflection.Assembly]::LoadFrom("C:\vspk\Newtonsoft.Json.dll")
[Reflection.Assembly]::LoadFrom("C:\vspk\net.nuagenetworks.bambou.dll")
[Reflection.Assembly]::LoadFrom("C:\vspk\net.nuagenetworks.vspk.dll")

function Send-Activation($enterprise,$nsg,$username) {
    $s = new-object net.nuagenetworks.vspk.v5_0.VSDSession -argumentlist "csproot", "csproot", "csp", "https://vsd.local:8443"
    
    $ef = $s.getMe().getEnterprises();
    $e = $ef.fetch($s,"name == '$enterprise'", [NullString]::Value, $null, -1, -1, [NullString]::Value, $true)[0]    
    
    $nsgf = $e.getNSGateways();
    $nsg = $nsgf.fetch($s,"name == '$nsg'", [NullString]::Value, $null, -1, -1, [NullString]::Value, $true)[0]    

    $userf = $e.getUsers();
    $user = $userf.fetch($s,"userName == '$username'", [NullString]::Value, $null, -1, -1, [NullString]::Value, $true)[0]    
    
    $bsf = $nsg.getBootstraps()
    $bootstrap = $bsf.fetch($s)[0]
    
    $bootstrap.NUInstallerID = $user.NUId;
    $bootstrap.save($s)
    
    $job = new-object net.nuagenetworks.vspk.v5_0.Job
    $job.NUCommand = [net.nuagenetworks.vspk.v5_0.Job+ECommand]::NOTIFY_NSG_REGISTRATION
    $nsg.createChild($s,$job)
}

Export-ModuleMember -Function 'Send-Activation'


