'-------------------------------------------------------------------------
' Citra IT - Excelencia em TI
' Script para Logon no Firewall pfSense
' Prova de conceito - não usar em produção
' @Autor: luciano@citrait.com.br
' @Versão: 1.0
' @Uso: Este script deve ser executado como um script logon (GPO)
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


objHttp.Open "GET", targetURL & "&action=logon&user=" & username
objHttp.SetRequestHeader "Content-Type", "application/x-form-www-urlencoded"
objHttp.Option(4) = &H3300
objHttp.Send
objHttp.WaitForResponse

Set objHttp = Nothing
Set objShell = Nothing