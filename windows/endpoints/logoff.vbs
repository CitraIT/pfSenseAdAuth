'-------------------------------------------------------------------------
' Citra IT - Excelencia em TI
' Script para Logoff no Firewall pfSense
' Prova de conceito - não usar em produção
' @Autor: luciano@citrait.com.br
' @Versão: 1.0
' @Uso: Este script deve ser executado como um script logout (GPO)
'-------------------------------------------------------------------------
On Error Resume Next


Dim targetURL
targetURL = "https://192.168.1.1/squid_auth_endpoint.php?"

Dim objHttp
Set objHttp = WScript.CreateObject("WinHttp.WinHttpRequest.5.1")

Dim objShell
Set objShell = CreateObject("WScript.Shell")

Dim username
username = objShell.ExpandEnvironmentStrings("%username%")


objHttp.Open "GET", targetURL & "&action=logout&user=" & username
objHttp.SetRequestHeader "Content-Type", "application/x-form-www-urlencoded"

Const WHR_SslErrorIgnoreFlags = 4
objHttp.Option(WHR_SslErrorIgnoreFlags) = &h3300

Const WHR_SecureProtocols = 9
objHttp.Option(WHR_SecureProtocols) = &h0800 + &h0200

Const WHR_EnableCertificateRevocationCheck = 18
objHttp.Option(WHR_EnableCertificateRevocationCheck) = False


objHttp.Send
objHttp.WaitForResponse

Set objHttp = Nothing
Set objShell = Nothing