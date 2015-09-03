<?php
$mongo=new MongoClient();
$mongodb=$mongo->selectDB("enginediff");
$mongoCollection=$mongodb->enginediff;
$ABS_FileUploadPath=realpath(dirname(__FILE__)).'/../uploads/';


function logerr($str) {
	file_put_contents('php://stderr',$str);
}

function csvToJson($csv) {
	$rows = explode("\n", trim(str_replace(", ",",",$csv)));
	$data = array_slice($rows, 1);
	$keys = array_fill(0, count($data), $rows[0]);
	$json = array_map(
		function ($row, $key) {
			return array_combine(str_getcsv($key), str_getcsv($row));
		}, $data, $keys);
	$ret=json_encode($json);
	return $ret;
}

function csvToMongo($csv){
	//$csv=file_get_contents("csv/150323_mds2000.csv");
	global $mongoCollection;
	$json=csvToJson($csv);
	$data=json_decode($json);
	$ret=array();

	foreach ($data as $elem) {
		/***** PreProcessing Rule *****/
		// Date: Change to MongoDate
		$dt=new DateTime(date('Y-m-d',strtotime($elem->Date)), new DateTimeZone('UTC'));
		$ts=$dt->getTimestamp();
		$elem->Date=new MongoDate($ts);

		// FileSize: always Integer.
		$elem->Size=(int)$elem->Size;

		// Severity: always Integer
		$elem->Severity=(int)$elem->Severity;

		// Threat_Name
		if (($elem->Threat_Name=="None" ) ||
			($elem->Threat_Name=="none") ||
			($elem->Threat_Name=="")
			) { 
			$elem->Threat_Name=null;
		}

		/***** Saving to Array *****/
		$Date=$elem->Date;
		unset($elem->Date);

		$File=array(
			"Name" =>$elem->FileName,
			"Type" =>$elem->Type,
			"MD5"  =>$elem->MD5,
			"CRC64"=>$elem->CRC64,
			"Size" =>$elem->Size,
		);
		unset($elem->FileName);
		unset($elem->Type);
		unset($elem->MD5);
		unset($elem->CRC64);
		unset($elem->Size);

		$Threat=array(
			"Severity"=>$elem->Severity,
			"Name"    =>$elem->Threat_Name
		);
		unset($elem->Severity);
		// Unset for VM Result
		//unset($elem->Threat_Name);

		// $VirusTotal=$elem->VirusTotal;
		// unset($elem->VirusTotal);


		// FIXME: Since, engine names are always different. Such as DICA_5.0.1.42,
		// we unset $elem->objs previously.
		// remaining keys are considered as EngineNames.
		foreach($elem as $key=>$val)
		{
			$Results=array();
			// result(BENIGN|MALICIOUS|SUSPICIOUS) categorization
			if($val=="MALICOUS") {$val="MALICIOUS";}
			if( 
				($val=="not found") ||
				($val=="Not found") ||
				($val=="None") ||
				($val=="none") ||
				($val=="Clean") ||
				($val=="BENIGN") ||
				($val=="")
			) {
				$result="BENIGN";
				$reason=$val;
			}
			else {
			 	$result=$val;
			 	$reason=$val;			
			}

			// for better Engine categorization data structure.
			if(strpos($key,"DICA")!==false) {
				$Engine="DICA";
				$EngineVersion=str_replace("DICA_","",$key);
				$Result=$result;
				$Reason=$reason;
			} elseif (strpos($key,"VM_Threat_Name")!==false) {
				$Engine="MDP_VM";
				if(strpos($val,"/")!==false) {
					// Use Engine Counts as EngineVersion.
					$EngineVersion=0;
					if ($reason!="None") {
						$Result="MALICIOUS";
					} else {
						$Result="BENIGN";
					}
					$Reason=explode("/",$reason)[1];
				} else {
					$EngineVersion=0;
					$Result="BENIGN";
					$Reason=0;
				}
			} elseif ((strpos($key,"AhnLab-V3")!==false) || (strpos($key,"Threat_Name")!==false)) {
				$Engine="V3";
				$EngineVersion=$key;
				if ($result!=="BENIGN") {
					$Result="MALICIOUS";
				} else {
					$Result=$result;
				}
				$Reason=$reason;
			} elseif (strpos($key,"Heimdal")!==false) {
				$Engine="Heimdal";
				$EngineVersion=$key;
				$Result=$result;
				$Reason=$reason;
				if(strpos($reason,"/")!==false) {
					$Result=explode("/",$result)[0];
					$Reason=explode("/",$result)[1];
				}
			} elseif (strpos($key,"VirusTotal")!==false) {
				$Engine="VirusTotal";
				if(strpos($val,"/")!==false) {
					// Use Engine Counts as EngineVersion.
					$EngineVersion=explode("/",$reason)[1];
					if ((int)explode("/",$reason)[0]>0) {
						$Result="MALICIOUS";
					} else {
						$Result="BENIGN";
					}
					$Reason=(int)explode("/",$reason)[1];
				} else {
					$EngineVersion=0;
					$Result="BENIGN";
					$Reason=0;
				}
			}else {
				$Engine=$key;
				$EngineVersion=$key;
				$Result=$result;
				$Reason=$reason;
			}
			array_push($Results,
				array(
					 $Engine=>array(
						"Version"=>$EngineVersion,
						"Result" =>$Result,
						"Reason" =>$Reason
					)
				)
			);
			unset($elem->$key);



			$retval=array(
				"Date"      => $Date,
				"File"      => $File,
				"Threat"    => $Threat,
				"Results"   => $Results
				);

			// Insert Data to Mongo
			$mongoCollection->insert($retval);
		}


		// save Data to (array)$ret
		array_push($ret,$retval);

		// Example: $retval 
		/* 
		Array (
		[Date] => MongoDate Object
			(
				[sec] => 1426431600
				[usec] => 0
			)

		[File] => Array
			(
				[Name] => 19a0fddb4355626b71a7e02c78232bb1_SS150316AACYP-000001.pdf
				[Type] => pdf
				[MD5] => 19a0fddb4355626b71a7e02c78232bb1
				[CRC64] => 371a94f7abc1566d
				[Size] => 27527
			)

		[Threat] => Array
			(
				[Severity] => 10
				[Name] => Exploit/PDF.MalJScript
			)

		[Results] => Array
			(
				[0] => Array
					(
						[Engine] => V3
						[Version] => AhnLab-V3
						[Result] => BENIGN
						[Reason] => 
					)

				[1] => Array
					(
						[Engine] => VirusTotal
						[Version] => 57
						[Result] => MALICIOUS
						[Reason] => 25
					)

				[2] => Array
					(
						[Engine] => DICA
						[Version] => 5.0.1.42
						[Result] => MALICIOUS
						[Reason] => 
					)

				[3] => Array
					(
						[Engine] => DICA
						[Version] => 4.1.2.1
						[Result] => BENIGN
						[Reason] => 
					)

				[4] => Array
					(
						[Engine] => DICA
						[Version] => 5.0.0.54
						[Result] => BENIGN
						[Reason] => 
					)

				[5] => Array
					(
						[Engine] => DICA
						[Version] => 5.0.1.39
						[Result] => MALICIOUS
						[Reason] => 
					)

				[6] => Array
					(
						[Engine] => Heimdal
						[Version] => Heimdal
						[Result] => SUSPICIOUS
						[Reason] => Timeout
					)

			)

		[_id] => MongoId Object
			(
				[$id] => 5515031a3789c999568b4569
			)

	)
*/
	}
	return $ret;
}


?>
