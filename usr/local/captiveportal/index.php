--- /usr/local/captiveportal/index.php.orig      2022-05-23 02:09:28.841088000 -0300
+++ /usr/local/captiveportal/index.php   2022-05-23 01:44:49.312992000 -0300
@@ -266,6 +266,10 @@
        if ($auth_result['result']) {
                captiveportal_logportalauth($user, $clientmac, $clientip, $auth_result['login_status']);
                portal_allow($clientip, $clientmac, $user, $passwd, $redirurl, $auth_result['attributes'], $pipeno, $auth_result['auth_method'], $context);
+               $s = fsockopen("127.0.0.1",6544);
+               fwrite($s, "$clientip,$user");
+               fclose($s);

        } else {
                captiveportal_free_dn_ruleno($pipeno);
