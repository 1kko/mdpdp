<?php
include_once("common/lib.php");


if (isset($_GET['confirm'])){
	if ($_GET['confirm']=="true"){
		$retval=$mongoCollection->drop();
	}
}

header("Content-type: application/json");
echo json_encode($retval);