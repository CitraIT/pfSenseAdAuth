# pfSense - Integração de Autenticação Transparente (SSO) com o Active Directory
Este projeto permite a autenticação transparente de usuários do Active Directory com o serviço de WebFilter (Proxy/E2Guardian) do Firewall pfSense.


!! Importante: Este procedimento foi homologado para o pfSense CE na versão 2.6  
Última atualização: 04/09/2022  
Responsável: Luciano Rodrigues - luciano@citrait.com.br  
  
Observação: Este é um projeto tocado por uma pessoa só. Não sou programador, nem administrador de redes, nem analista de segurança, quissá um desenvolvedor *Unix/Python/C#. Toda ajuda é bem vinda, toda contribuição é bem recebida. Este projeto começou como uma idéia boba, mas se materializou como uma possibilidade. Ainda é um MVP - um teste de viabilidade.


## Resumo:  
Este projeto visa permitir que quando os usuários se autentiquem na máquina integrada ao AD, um agente instalado no servidor AD irá realizar a sincronização com o firewall do login/ip deste usúario, de maneira que o serviço de webfilter não precise solicitar o usuário autenticação para registrar seus acessos.  
  
A solução é composta de 3 componentes principais:  
1- Do serviço de WebFilter (E2Guardian) instalado e configurado com autenticação DNS.  
2- Do agente SSO que é instalado no servidor de Active Directory.  
3- Do serviço instalado no Firewall que faz o meio de campo entre o AD e o WebFilter (e futuramente entre outros serviços como Captive Portal, Regras baseado no login do usuário, entre outros...).  


## Observações e Limitações:  
a) Os grupos serão gerenciados dentro do E2Guardian. Os usuários são do AD, mas você terá que criar os grupos no E2Guardian e gerenciar a associação de usuários e grupos por lá. Futuramente pretendemos fazer a sincronização de grupos com o AD. Patrocina nós que um dia a gente chega lá :D  
b) Ainda não é possível detectar o logoff de usuários (rotina em desenvolvimento).  
c) Caso o usuário não seja identificado (pelo agente SSO do AD), o captive portal apenas autenticará usuários locais do firewall.  
d) Ainda não há interface gráfica para configuração.  
e) Ainda não é um pacote oficial de fácil instalação...  
f) A rede interna deve ser 10/8 ou 172.16/12 ou 192.168/16.  



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


5- Instale o captive portal customizado.  
5.1- Execute o comando abaixo no menu Diagnostics -> Command Prompt:  
```
curl -s -o  /usr/local/www/captive.php https://raw.githubusercontent.com/CitraIT/pfSenseAdAuth/main/usr/local/www/captive.php
```
5.2- Acesse o menu Diagnostics -> Edit File.  
5.3- No caminho do arquivo insira o caminho abaixo e clique em Load para editar o modelo da tela do Captive Portal. 
```
/usr/local/www/captive.php
```  
5.4- Após as alterações na página que será exibida para o usuário, clique em Save.  


6- Ajustar o plugin de autenticação do E2Guardian.  
6.1- Acesse o menu Diagnostics -> Edit File.  
6.2- Insira no caminho do arquivo o texto abaixo e clique em Load:  
```
/usr/local/etc/e2guardian/authplugins/dnsauth.conf
```
6.3- Apague todo o texto e cole o texto abaixo:  
```
# IP/DNS-based auth plugin
#
# Obtains user and group from domain entry maintained by separate authentication# program.

plugname = 'dnsauth'

# Base domain
basedomain = "citrait.local"

# Authentication URL
authurl = "https://192.168.1.1/captive.php?redirurl"

# Prefix for auth URLs
prefix_auth = "https://192.168.1.1/"

# Redirect to auth (i.e. log-in)
#  yes - redirects to authurl to login
#  no - drops through to next auth plugin
redirect_to_auth = "yes"
```
6.4- Substitua citrait.local pelo nome de domínio do firewall (ex.: empresa.corp).  
6.5- Substitua a authurl pelo endereço/hostname do pfSense, mantendo a URL /captive.php?redirurl.
6.6- Em prefix_auth ajuste conforme a variável authurl, mas terminando na barra após a porta.  
6.7- Clique em Save para salvar o arquivo.  



7- Criar uma CA (Autoridade Certificadora) para usar na interceptação SSL/HTTPS do E2Guardian.   
7.1- Acesse o menu System -> Cert. Manager, clique em Add.  
7.2- Dê um nome descritivo para a CA (ex.: CA-E2GUARDIAN).  
7.3- Marque a caixa "Trust Store".  
7.4- Em "Common Name" preencha com um nome significativo (ex.: usar o mesmo da descrição).  
7.5- Preencha as informações organizacionais (country code, state, city...) e clique em Save.




8- Configurar o E2Guardian.  
8.1- Acesse o menu Services -> E2Guardian Proxy.  
8.2- Marque a caixa "Enable e2guardian".  
8.3- Selecione as interfaces LAN e Loopback.  
8.4- Marque a caixa "Transparent HTTP Proxy".  
8.5- Marque a opção "Bypass Proxy for Private Address Destination".  
8.6- Marque a opção "Enable SSL support".  
8.7- Selecione a CA que criou na etapa acima.  
8.8- Clique em Save. 


9- Habilitar a autenticação no E2Guardian.  
9.1- Acesso o menu Services -> E2Guardian Proxy -> Guia General.  
9.2- No campo "Auth Plugins" selecione apenas DNS.  
9.3- Clique em Save ao final da Página. 



10- Configurar um usuário e grupo de teste.  
10.1- Acesso o menu Services -> E2Guardian Proxy -> Guia Groups e clique em Add.  
10.2- Dê um nome e uma descrição para o grupo (ex.: ti / ti).  
10.3- Clique em Save ao final da página.  
10.4- Acesse a aba Users.  
10.5- No campo com o nome do grupo (ex.: ti) referente ao grupo ti, insira o login do usuário (ex.: luciano, que deve ser um login válido no AD).  
10.6- Clique em Save ao final da página.  
10.7- Clique em Apply Changes (botão verde que aparece no topo após salvar a configuração).  


11- Instalar o serviço de sincronização no Firewall.  
11.1- No menu Diagnostics -> Command Prompt, execute os comandos abaixo:
```
curl -s -o /usr/local/etc/rc.d/adauth.sh https://raw.githubusercontent.com/CitraIT/pfSenseAdAuth/main/usr/local/etc/rc.d/adauth.sh
```  
```
chmod +x /usr/local/etc/rc.d/adauth.sh
```  
```
curl -s -o /usr/local/sbin/adauth.py https://raw.githubusercontent.com/CitraIT/pfSenseAdAuth/main/usr/local/sbin/adauth.py
``` 
```
chmod +x /usr/local/sbin/adauth.py
```  
11.2- Ainda no menu Command Prompt, execute o comando abaixo para inicializar o serviço:  
```
service adauth.sh start
```  


12- Instalar o Agente SSO no servidor Active Directory (AD).  
12.1- No servidor Windows (linux em breve...), certifique-se de ter instalador o DotNet Framework 4.7. Link para download abaixo:  
```
https://download.visualstudio.microsoft.com/download/pr/1f5af042-d0e4-4002-9c59-9ba66bcf15f6/089f837de42708daacaae7c04b7494db/ndp472-kb4054530-x86-x64-allos-enu.exe
```
12.2- Realize o download dos arquivos do serviço SSO pelo link abaixo:  
```
https://github.com/CitraIT/pfSenseAdAuth/raw/main/sso_agent/windows/pfSenseAdAuth.zip
```  

12.3- Descompacte os arquivos no servidor direto no C:\, de maneira que o arquivo pfSenseAdAuth.exe esteja dentro da pasta C:\pfSenseAdAuth\.  
12.4- Para instalar o serviço do agente, abra um prompt de comandos como Administrador e execute o comando abaixo:  
``` 
"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe" C:\pfSenseAdAuth\pfSenseAdAuth.exe  
``` 
12.5- Abra o console de serviços, localize o Serviço pfSenseAdAuth e inicialize-o.  

13- Configurar o Apontamento do Firewall no SSO:  
13.1- Abra o editor de registro do Windows (regedt32.exe)  
13.2- Localize a chave: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\pfSenseAdAuth.  
13.3- Crie uma nova chave: botão direito -> New -> Key (chave) e dê o nome de Parameters.  
13.4- Clique na chave Parameters com botão direito -> New -> Multi-String Value.  
13.5- Dê o nome de FirewallList.  
13.6- Dê um duplo clique na nova chave e insira o ip do firewall, seguido de dois pontos e a porta 6544 como abaixo:  
```
192.168.1.1:6544
```
![image](https://user-images.githubusercontent.com/91758384/188525821-e3a82d45-d3a6-467e-afaa-32ff9e2d2b37.png)



13.7- Salve o registro e feche o regedit.  
13.8- Reinicie o serviço pfSenseAdAuth.  

14- Testar  
14.1- Faça logoff e logon novamente no computador cliente (do usuário), com uma conta de domínio.  
14.2- Tente navegar em algum site. Você deve ser capaz de acessar o site requisitado.  

![image](https://user-images.githubusercontent.com/91758384/188525901-df42787f-1ad9-4995-ba71-7d5485e09ae0.png)

Se o computador não estiver no AD, irá ser redirecionado para o Captive Portal:  
![image](https://user-images.githubusercontent.com/91758384/188526700-30566f40-56a7-4f53-87b9-d7a1746a7b88.png)



15- Seja feliz e me pague uma breja, o Open Source agradece :D  











