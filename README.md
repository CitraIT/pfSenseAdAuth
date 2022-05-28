# transparent_dnsauth
pfSense transparent authentication project for e2guardian  
&nbsp;  
//todo  
&nbsp;  
&nbsp;  

Instalação:
1. Instalar o pacote System Patches
2. Aplicar o patch de marcelloc disponível em: https://github.com/marcelloc/Unofficial-pfSense-packages
4. Instalar o E2Guardian
5. Nas opções avançadas do DNS Resolver, adicionar a linha
```
include: /var/unbound/dnsauth.conf
```
&nbsp;  
6. Habilitar o E2Guardian  
7. Adicionar regra allow LAN -> This Firewall portas 8080 e 8081 caso usando proxy transparent  
8. Editar o arquivo dnsauth.conf com o conteúdo deste repositório e fazer ajustes necessários  
9. Habilitar de autenticação DNSAuth do E2Guardian  
10. Criar os grupos e usuários através das configurações do E2Guardian  
  
Habilitar a autenticação pelo plugin DNS no E2Guardia.  

&nbsp;  

