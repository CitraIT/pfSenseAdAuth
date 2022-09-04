<?php
require_once("auth.inc");
require_once("util.inc");
require_once("functions.inc");
require_once("captiveportal.inc");

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

        if(authenticate_user($post_user, $post_pass)) {
                /* Citra IT modifications */

                $AdAuthSocket = fsockopen("127.0.0.1", "6544");
                fwrite($AdAuthSocket, "$clientip,$post_user");
                fclose($AdAuthSocket);
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
<title>autentication page</title>
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
        <h1>Citra IT</h1>
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
