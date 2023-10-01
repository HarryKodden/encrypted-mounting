<?php
echo "<h1>Links</h1>";

echo "Here you find the links supported at this moment";

echo "<ul>";
foreach (glob("/etc/mounts/*.conf") as $filename) {
	$path = basename($filename, ".conf");
	if ($path != "admin") {
		$description = "WebDAV link: '" . $path . "'";
		$path = "webdav/" . $path;
	} else {
		$description = "Administration page";
	}
	echo "<li><a href=\"" . $_SERVER['url'] . "/" . $path . "\">" . $description . "</a></li>";

	if ($path == 'admin') {
		echo "<li><a href=\"" . $_SERVER['url'] . "/" . $path . "/api/doc\">" . $description . " (API Documentation)</a></li>";
	}
}
echo "</ul>";

echo "<h2>Authentication</h2>";

echo "The following rules for authentication apply:";

echo "<h3>Admininistration portal</h3>";
echo "Federated authentication via your institute at which you are linked to this SRAM Service";
echo "<br/>";
echo "You also need to be member of the admins groups that is registered with this SRAM Service.";

echo "<h3>WebDAV links</h3>";
echo "Authenticate with your SRAM User ID and your SRAM Token that you have registered for this SRAM Service";

// phpinfo();
?>