<?php
include_once("common/lib.php");
$value=file_get_contents($argv[1]);
csvToMongo($value);
?>
