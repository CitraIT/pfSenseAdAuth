<#
# Citra IT - Excelência em TI
# Script para monitorar o eventlog do windows e atualizar o firewall quando um usuario realizar autenticação na rede.
# @Author: luciano@citrait.com.br
# @Version: 1.0
# @Obs.: Este é um trabalho experimental. Não utilizar em produção.
#>

$FIREWALL_IP = "10.0.1.1"
$FIREWALL_PORT = 8011


# This Script Path
$SCRIPT_PATH = Split-Path -Parent $MyInvocation.MyCommand.Path

# Connecting to EventLog Subsystem
$EventLog = new-object System.Diagnostics.EventLog "Security"

# Register to listen to new written entries in event log
# Register-ObjectEvent -InputObject $EventLog -EventName EntryWritten -Action {}
Register-ObjectEvent -InputObject $EventLog -EventName EntryWritten

While($event = Wait-Event)
{
    # $e.SourceEventArgs.Entry.EventID
    $entry = $event.SourceEventArgs.Entry
    If($entry.EventID -eq 4768)
    {
        Write-Host "$(Get-Date): Received a new kerberos auth request (evt id 4768)"
        # Write-Host $entry.Message
        $login = [Regex]::Matches($event.SourceEventArgs.Entry.Message, "Account Name:\s+(.*)`r`n").groups[1].value
        # Check if machine account
        If($login -match ".*\$")
        {
            Write-Host -Fore Yellow "Skipping machine account $login"
            Continue
        }
        $ipaddr = [Regex]::Matches($event.SourceEventArgs.Entry.Message, "Client Address:\s+.*((10|192|172)\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})").groups[1].value
        Write-Host -Fore Green "Found User $login on IP $ipaddr"

        # Notifying the firewall
        try{
            Write-Host -Fore Green "Notifying firewall on $FIREWALL_IP`:$FIREWALL_PORT"
            $tcp = new-object system.net.sockets.tcpclient($FIREWALL_IP, $FIREWALL_PORT)
            $stream = $tcp.GetStream()
            $txt = "$ipaddr,$login"
            $txtBytes = [System.Text.Encoding]::Ascii.GetBytes($txt)
            $stream.Write($txtBytes, 0, $txtBytes.Length)
            $stream.Flush()
            $tcp.Close()
            Write-Host -Fore Green "Firewall notified!"
        }Catch{
            Write-Host -Fore Red "Error contacting firewall"
        }
    }Else{
        Write-Host "Skipping event $($entry.EventID)"
    }
    $event | Remove-Event
}


Unregister-Event -SourceIdentifier *

