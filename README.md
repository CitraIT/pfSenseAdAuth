# pfSense - Integração de Autenticação Transparente (SSO) com o Active Directory
Este projeto permite a autenticação transparente de usuários do Active Directory com o serviço de WebFilter (Proxy/E2Guardian) do Firewall pfSense.


!! Importante: Este procedimento foi homologado para pfSense CE na versão 2.6  
Última atualização: 04/09/2022  
Responsável: Luciano Rodrigues - luciano@citrait.com.br


## Resumo:  
Este projeto visa permitir que quando os usuários se autentiquem na máquina integrada ao AD, um agente instalado no servidor AD irá realizar a sincronização com o firewall do login/ip deste usúario, de maneira que o serviço de webfilter não precise solicitar o usuário autenticação para registrar seus acessos.  
A solução é composta de 3 componentes principais:  
1- Do serviço de WebFilter (E2Guardian) instalado e configurado com autenticação DNS.  
2- Do agente SSO que é instalado no servidor de Active Directory.  
3- Do serviço instalado no Firewall que faz o meio de campo entre o AD e o WebFilter (e futuramente entre outros serviços como Captive Portal, Regras baseado no login do usuário, entre outros...).  


## Instalação:


### Etapas:  
1- Ajustar hostname e nome de domínio do firewall de acordo com o seu ambiente:  
1.1- A configuração é feita pelo menu System -> General Setup.  

2- Criar o arquivo de configuração externa do serviço DNS:  
2.1- Criar o arquivo /var/unbound/dnsauth.conf vazio com o comando abaixo (executar através do menu Diagnostics -> Command Prompt):  
```
echo> /var/unbound/dnsauth.conf
```
3- Configure o serviço de DNS do pfSense para incluir o arquivo dnsauth.conf.  
3.1- Acesse o menu Services -> DNS Resolver. Clique em Display Custom Options ao final da página e inclua a linha seguinte no campo de texto:  
```
include: /var/unbound/dnsauth.conf
```
4- Realize a instalação do E2Guardian:  
4.1- Vá no menu System -> Package Manager -> Available Packages e instale o pacote System_Patches.  
4.2- Acesse a página abaixo e copie todo o código:  
```
https://raw.githubusercontent.com/marcelloc/Unofficial-pfSense-packages/master/25_unofficial_packages_list.patch
```  
4.3- Acesse o menu System -> Patches. Clique em Add New Patch.  
4.4- Cole o código no campo Patch Contents.  
4.5- Em Description preencha com: Unnoficial_packages.  
4.6- No campo Path Strip Count defina com valor 1 e salve o patch (botão save ao final da página).  
4.7- Clique em apply no patch recem registrado.  
4.8- No menu Diagnostics -> Command Prompt execute o comando abaixo:  
```
fetch -q -o /usr/local/etc/pkg/repos/Unofficial.conf 
https://raw.githubusercontent.com/marcelloc/Unofficial-pfSense-packages/master/Unofficial_25.conf
```
4.9- Ainda no menu Diagnostics -> Command Prompt execute o comando abaixo:
```
pkg update
```
4.10- Acesse o menu System -> Package Manager -> Available Packages e instale o pacote E2Guardian.
