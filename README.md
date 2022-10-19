# pfSense - Integração de Autenticação Transparente (SSO) com o Active Directory
Este projeto permite a autenticação transparente de usuários do Active Directory com o serviço de WebFilter (Squid) do Firewall pfSense.


!! Importante: Este procedimento foi homologado para o pfSense CE na versão 2.6  
Última atualização: 19/10/2022  
Responsável: Luciano Rodrigues - luciano@citrait.com.br  
  
!! Importante: O projeto é Open Source e está inteiramente disponível para uso/modificação.    


## Resumo:  
Este projeto visa permitir que quando os usuários se autentiquem na máquina integrada ao AD, um agente instalado no servidor AD irá realizar a sincronização com o firewall do login/ip deste usúario, de maneira que o serviço de webfilter não precise solicitar o usuário autenticação para registrar seus acessos.  
  
A solução é composta de 3 componentes principais:  
1- Do Firewall pfSense com o serviço de WebFilter (SQUID).  
2- Do agente SSO que é instalado no servidor de Active Directory (apenas windows server por enquanto).  
3- De alguns patches que permitem a devida integração entre os softwares acima.   


## Observações e Limitações:  
a) Os grupos serão gerenciados dentro do SquidGuard via LDAP como feito de costume.    
d) Ainda não há interface gráfica para configuração.  
f) As máquinas que se autenticam no AD deve ter endereços IP que comecem com 192. ou 172. ou 10.    



## Instalação:


### Etapas:  
1- Ajustar hostname e nome de domínio do firewall de acordo com o seu ambiente:  
1.1- A configuração é feita pelo menu System -> General Setup.  

2- Instalar o pacote Squid e SquidGuard:  
2.1- Menu System -> Package Manager -> Available Packages -> Squid e SquidGuard:  


3- Atualizar a Integração de Autenticação Captive Portal do Squid.  
3.1- Substitua o conteúdo do arquivo /usr/local/bin/check_ip.php pelo conteúdo abaixo:  
```
#!/usr/local/bin/php-cgi -q
<?php
/*
 * check_ip.php
 *
 * part of pfSense (https://www.pfsense.org)
 * Copyright (c) 2016-2022 Rubicon Communications, LLC (Netgate)
 * Copyright (c) 2013-2016 Marcello Coutinho
 * All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

require_once("config.inc");
require_once("globals.inc");
error_reporting(0);
global $config, $g;
// stdin loop
if (!defined(STDIN)) {
	define("STDIN", fopen("php://stdin", "r"));
}
if (!defined(STDOUT)) {
	define("STDOUT", fopen('php://stdout', 'w'));
}
while (!feof(STDIN)) {
	$check_ip = preg_replace('/[^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}]/', '', fgets(STDIN));
	$status = '';

       $db = "/usr/local/etc/squid/users.db";
       $status = squid_check_ip($db, $check_ip);

       if ($status) {
               fwrite(STDOUT, "OK user={$status}\n");
       } else {
               fwrite(STDOUT, "ERR\n");
	}

}

function squid_check_ip($db, $check_ip) {
       exec("/usr/local/bin/sqlite3 {$db} \"SELECT ip FROM users WHERE ip='{$check_ip}'\"", $ip);
	if ($check_ip == $ip[0]) {
               exec("/usr/local/bin/sqlite3 {$db} \"SELECT username FROM users WHERE ip='{$check_ip}'\"", $user);
		return $user[0];
	}
}

?>
```

4- Criar o banco de dados inicial de usuários:  
4.1- Vá ao menu Diagnostics -> Command Prompt e execute o comando abaixo.  
```
/usr/local/bin/sqlite3 /usr/local/etc/squid/users.db "create table users (username text, ip text);"
``` 

5- Configurar conexão ldap com o AD:   
5.1- Acesse o menu System -> User Manager -> Authentication Servers  
5.2- Clique em Add  
5.3- Em Descriptive Name preencha obrigatoriamente com pfsense-ad-auth.  
5.4- Preencha os campos apropriados de acordo com sua conexão do AD.  
5.5- Dê preferência a conexão LDAP segura (uso de SSL).  
5.6- Salve a conexão LDAP e teste a autenticação de usuários do AD (menu Diagnostics -> Authentication).  



5- Instale o captive portal customizado.  
5.1- Vá no menu Diagnostics -> Edit File -> No caminho insira /usr/local/www/captive.php e no conteúdo cole o seguinte:    
```
<?php
/*
 * captive.php
 *
 * part of pfSense (https://www.pfsense.org)
 * Copyright (c) 2004-2013 BSD Perimeter
 * Copyright (c) 2013-2016 Electric Sheep Fencing
 * Copyright (c) 2014-2022 Rubicon Communications, LLC (Netgate)
 * All rights reserved.
 *
 * Originally part of m0n0wall (http://m0n0.ch/wall)
 * Copyright (c) 2003-2006 Manuel Kasper <mk@neon1.net>.
 * All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
require_once("auth.inc");
require_once("citra_ad_auth.inc");


header("Expires: 0");
header("Cache-Control: no-cache, no-store, must-revalidate");
header("Pragma: no-cache");
header("Connection: close");


/* NOTE: IE 8/9 is buggy and that is why this is needed */
$orig_request = trim($_REQUEST['redirurl'], " /");

/* If the post-auth redirect is set, always use it. Otherwise take what was supplied in URL. */
if (preg_match("/redirurl=(.*)/", $orig_request, $matches)) {
        $redirurl = urldecode($matches[1]);
} elseif ($_REQUEST['redirurl']) {
        $redirurl = $_REQUEST['redirurl'];
}
/* Sanity check: If the redirect target is not a URL, do not attempt to use it like one. */
if (!is_URL(urldecode($redirurl), true)) {
        $redirurl = "";
}

$clientip = $_SERVER["REMOTE_ADDR"];

$is_user_authenticated = false;

if(isset($_POST["action"]) && $_POST["action"] == "login") {
        $post_user = strtolower($_POST["user"]);
        $post_pass = $_POST["pass"];

        // setup ldap user source
        $authcfg = NULL;
        foreach($config["system"]["authserver"] as $authserver){
          if($authserver["name"] == "pfsense-ad-auth") {
              $authcfg = $authserver;
          }
        }

        if(!$authcfg){
          die("no authentication backend configured for pfSenseAdAuth plugin");
        }
        if(authenticate_user($post_user, $post_pass, $authcfg)) {
                citra_ad_auth_add_database_entry($post_user, $clientip);
                sleep(3);
                header("Location: $redirurl");
                ob_flush();
        }else{
                $auth_error_msg = "Invalid username or password";
        }

}

?>
<!DOCTYPE html>
<html>
        <head>
                <title>Autentication</title>
                <style>
                .center-login{border:2px solid black;margin-left: auto; margin-right: auto; width: 500px; height: 250px;}
                .login-out-table{;margin-left: auto; margin-right: auto;}
                </style>
        </head>
        <body>
                <div class="center-login" >
                        <form method="POST">
                                <table class="login-out-table">
                                <tr>
                                        <td colspan="2" style="text-align:center">
                                                <h1>CITRA IT</h1>
                                                <h4 style="text-align:center">Authentication Required</h4>
                                        </td>
                                </tr>
                                <?php
                                if (isset($auth_error_msg) && $auth_error_msg != "") {
                                ?>
                                        <tr>
                                                <td colspan="2"><div style="background-color:red; color:white;font-weight:bold;text-align:center;"><?=$auth_error_msg;?></div></td>
                                        </tr>
                                <?php
                                }
                                ?>
                                <tr>
                                        <td colspan="2" ><div><span>Please enter your credentials to continue.</span></div></td>
                                </tr>
                                <tr>
                                        <td>Username</td><td><input type="text" name="user" value=""></td>
                                </tr>
                                <tr>
                                        <td>Password</td><td><input type="password" name="pass"></td>
                                </tr>
                                <tr>
                                        <td colspan="2"><input type="submit" value="continue"></td>
                                </tr>
                                <input type="hidden" name="action" value="login">
                                </table>
                        </form>

                </div>
        </body>

</html>
```
5.2- Salve o arquivo.  


6- Ajuste o direcionamento do Squid para o Captive Portal customizado.  
6.1- Acesso o menu Services -> Squid Proxy Services -> e clique no botão Show Advanced Options.  
6.2- No campo Custom Options (After Auth) insira o seguinte conteúdo:  
```
deny_info https://<ip_do_firewall>/captive.php?redirurl=%u allsrc
```
6.3- Troque <ip_do_firewall> pelo IP ou FQDN do firewall e porta usados para acessar o webconfigurator:  
6.4- Clique em Save ao final da página.  



7- Adicionar a biblioteca de integração.   
7.1- Acesse o menu Diagnostics -> Edit File, no caminho insira /etc/inc/citra_ad_auth.inc  
7.2- Insira o seguinte conteúdo no campo de texto e clique em Save.  
```
<?php
require_once("auth.inc");

/* Defines the Database location */
$squid_db_path = "/usr/local/etc/squid/users.db";


function citra_ad_auth_add_database_entry($user,$ip, $source="CaptivePortal") {
	//check if already exists
	exec("/usr/local/bin/sqlite3 /usr/local/etc/squid/users.db \"SELECT ip FROM users WHERE ip='{$ip}'\"", $check_ip);
	if ($ip == $check_ip[0]) {
		//exec("/usr/local/bin/sqlite3 /usr/local/etc/squid/users.db \"UPDATE users SET username='{$user}' WHERE ip='{$ip}'\"");
		citra_ad_auth_del_database_entry_by_ip($ip);
	}
        $msg = "{$source}: authenticated user {$user} on address {$ip}";
        log_auth($msg);
	exec("/usr/local/bin/sqlite3 /usr/local/etc/squid/users.db \"INSERT INTO users(username, ip) VALUES('{$user}', '{$ip}')\"");

}


function citra_ad_auth_del_database_entry($user, $ip) {
	exec("/usr/local/bin/sqlite3 /usr/local/etc/squid/users.db \"DELETE FROM users WHERE username='{$user}' AND ip='{$ip}'\"");
}


function citra_ad_auth_del_database_entry_by_ip($ip) {
	exec("/usr/local/bin/sqlite3 /usr/local/etc/squid/users.db \"DELETE FROM users WHERE ip='{$ip}'\"");
}


function citra_ad_auth_del_database_entry_by_user($user) {
	exec("/usr/local/bin/sqlite3 /usr/local/etc/squid/users.db \"DELETE FROM users WHERE user='{$user}'\"");
}


function citra_ad_auth_empty_database() {
	exec("/usr/local/bin/sqlite3 /usr/local/etc/squid/users.db \"DELETE FROM users\"");
}
```





8- Habilitar a autenticaçaõ Captive Portal do Squid.  
8.1- Acesse o menu Services -> Squid Proxy Service -> Aba Authentication e marque a opção Captive portal e salve a configuração.  



9- Criar o arquivo (endpoint) que receberá as sincronizações do AD.  
9.1- Acesse o menu Diagnostics -> Edit File -> preencha o caminho com /usr/local/www/squid_auth_endpoint.php    
9.2- No conteúdo cole o teto abaixo.  
```
<?php
/*
  file: /usr/local/www/squid_auth_endpoint.php
 */
require_once("citra_ad_auth.inc");

$EXPLICIT_AD_SERVER = "192.168.1.100";
$adserver = $_SERVER["REMOTE_ADDR"];

if($adserver != $EXPLICIT_AD_SERVER) {
	die("This computer is not authorized to sincronize with pfSense AD Auth.");
}

// LOGON
if(isset($_GET["action"]) && $_GET["action"] == "logon") {
	$target_user = strtolower($_GET["user"]);
	$clientip = $_GET["clientip"];
	if($target_user != NULL && $clientip != NULL){
		citra_ad_auth_add_database_entry($target_user,$clientip, $source="Domain");
	}
	exit(0);
// LOGOUT
}else if(isset($_GET["action"]) && $_GET["action"] == "logout"){
	$target_user = strtolower($_GET["user"]);
	$clientip = $_GET["clientip"];
	if($target_user != NULL && $clientip != NULL){
		citra_ad_auth_del_database_entry($target_user, $clientip);
	}
	exit(0);
}
```  
9.3- Altere o endereço IP pelo IP do servidor AD autorizado a comunicar com o firewall para sincronizar os usuários.  
9.4- Clique em Save.



10- Instalar o Agente SSO no servidor Active Directory (AD).  
10.1- No servidor Windows (linux em breve...), certifique-se de ter instalador o DotNet Framework 4.7. Link para download abaixo:  
```
https://download.visualstudio.microsoft.com/download/pr/1f5af042-d0e4-4002-9c59-9ba66bcf15f6/089f837de42708daacaae7c04b7494db/ndp472-kb4054530-x86-x64-allos-enu.exe
```
10.2- Realize o download dos arquivos do serviço SSO pelo link abaixo:  
```
https://github.com/CitraIT/pfSenseAdAuth/raw/main/sso_agent/windows/pfSenseAdAuth.zip
```  

10.3- Descompacte os arquivos no servidor direto no C:\, de maneira que o arquivo pfSenseAdAuth.exe esteja dentro da pasta C:\pfSenseAdAuth\.  
10.4- Para instalar o serviço do agente, abra um prompt de comandos como Administrador e execute o comando abaixo:  
``` 
"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe" C:\pfSenseAdAuth\pfSenseAdAuth.exe  
``` 
10.5- Abra o console de serviços, localize o Serviço pfSenseAdAuth, Edite-o e marque como auto-inicializável.
 


11- Configurar o Apontamento do Firewall no SSO:  
11.1- Abra o editor de registro do Windows (regedt32.exe)  
11.2- Localize a chave: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\pfSenseAdAuth.  
11.3- Crie uma nova chave: botão direito -> New -> Key (chave) e dê o nome de Parameters.  
11.4- Clique na chave Parameters com botão direito -> New -> Multi-String Value.  
11.5- Dê o nome de FirewallList.  
11.6- Dê um duplo clique na nova chave e insira o ip do firewall, seguido de dois pontos e a porta na qual é feito o acesso webConfigurator (normalmente 443 se não tiver sido alterada):  
```
192.168.1.1:443
```



13.7- Salve o registro e feche o regedit.  
13.8- Reinicie o serviço pfSenseAdAuth.  





15- Testar  
15.1- Faça logoff e logon novamente no computador cliente (do usuário), com uma conta de domínio.  
15.2- Tente navegar em algum site. Você deve ser capaz de acessar o site requisitado.  
15.3- Faça logoff com uma conta local que não exista no domínio e tente navegar. Você deve ser direcionado para o captive portal.
15.4- Faça autenticação no captive portal para validar que os usuários conseguem autenticar com sucesso.


