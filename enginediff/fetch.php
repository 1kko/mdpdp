<?php
include_once("common/lib.php");
$today="2015/05/08 - 2015/05/09";
$g_daterange=isset($_GET['daterange']) ? $_GET['daterange'] : $today;

/*
	Internal Calculation functions
*/
if (!function_exists("daterangeMongo")) {
	function daterangeMongo($daterange=Null) {
		global $g_daterange;
		$daterange=isset($daterange) ? $daterange : $g_daterange;
		$intCompensationSec=32400;
		
		$strStartDate=explode(" - ",$daterange)[0];
		$strEndDate=explode(" - ",$daterange)[1];
		$intStartDate=strtotime(str_replace("/","-",$strStartDate))-$intCompensationSec;
		$intEndDate=strtotime(str_replace("/","-",$strEndDate))+$intCompensationSec;
		$mongoStartDate=new MongoDate($intStartDate);
		$mongoEndDate=new MongoDate($intEndDate);

		$retval=array(
			"str"=>array(
				"start"=>$strStartDate,
				"end"=>$strEndDate
			),
			"int"=>array(
				"start"=>$intStartDate,
				"end"=>$intEndDate
			),
			"mongo"=>array(
				"start"=>$mongoStartDate,
				"end"=>$mongoEndDate
			)
		);

		return $retval;
	}
}

if (!function_exists("getTotalPerDay")) {
	function getTotalPerDay($daterange=Null) {
		global $mongoCollection;
		$startDate = daterangeMongo($daterange)['mongo']['start'];
		$endDate = daterangeMongo($daterange)['mongo']['end'];


		$records=$mongoCollection->distinct('Date', 
			array('Date'=>
				array(
					'$gte'=>$startDate, '$lte'=>$endDate
				)
			)
		);
		// sort is not available after distinct.
		asort($records);

		$dateList=array();
		foreach($records as $r)
		{
			array_push($dateList, $r);
		}
		$uniqueDates=array_unique($dateList);

		$chartCount=array();
		foreach($uniqueDates as $uniqueDate) {
			$rcd=$mongoCollection->distinct('File.MD5', array('Date'=>$uniqueDate));
			$cnt=sizeof($rcd);
			$chartNsec=$uniqueDate->sec*1000;
			array_push($chartCount,array($chartNsec, $cnt));
		}
		return $chartCount;
	}
}

if (!function_exists("getArrayPerDay")){
	function getArrayPerDay($filter, $daterange=Null) {
		global $mongoCollection;
		$startDate = daterangeMongo($daterange)['mongo']['start'];
		$endDate = daterangeMongo($daterange)['mongo']['end'];

		$records=$mongoCollection->find(
			array('$and'=>
				array(
					$filter,
					array('Date'=>
						array(
							'$gte'=>$startDate, '$lte'=>$endDate
						)
					)
				)
			)
		)->sort(array('Date'=>1));

		$dateList=array();
		foreach($records as $r)
		{
			array_push($dateList, $r['Date']);
		}
		$uniqueDates=array_unique($dateList);

		$chartCount=array();
		foreach($uniqueDates as $uniqueDate){
			$cnt=sizeof($mongoCollection->distinct(
				'File.MD5',
				array('$and'=>array(
					$filter,
					array('Date'=>$uniqueDate)
			))));
		
			$chartNsec=$uniqueDate->sec*1000;

			array_push($chartCount,array($chartNsec, $cnt));

		}
		//$jsonChartCount=json_encode($chartCount);
		return $chartCount;
	}
}


if (!function_exists("getTotalMaliciousCountArrayPerDay")){
	function getTotalMaliciousCountArrayPerDay($filter, $daterange=Null) {
		global $mongoCollection;
		$startDate = daterangeMongo($daterange)['mongo']['start'];
		$endDate = daterangeMongo($daterange)['mongo']['end'];

		$records=$mongoCollection->find(
			array('$and'=>
				array(
					$filter,
					array('Date'=>
						array(
							'$gte'=>$startDate, '$lte'=>$endDate
						)
					)
				)
			)
		)->sort(array('Date'=>1));

		$dateList=array();
		foreach($records as $r)
		{
			array_push($dateList, $r['Date']);
		}
		$uniqueDates=array_unique($dateList);

		$chartCount=array();
		foreach($uniqueDates as $uniqueDate){
			$cnt=$mongoCollection->distinct(
				'File.MD5',
				array('$and'=>
					array(
						$filter,
						array('Date'=>$uniqueDate)
					)
				)
			);
			$cnt=sizeof($cnt);
		
			$chartNsec=$uniqueDate->sec*1000;

			array_push($chartCount,array($chartNsec, $cnt));

		}
		//$jsonChartCount=json_encode($chartCount);
		return $chartCount;
	}
}

if (!function_exists("getTotalMaliciousCount")){
	function getTotalMaliciousCount($daterange=Null) {
		global $mongoCollection;
		
		$startDate = daterangeMongo($daterange)['mongo']['start'];
		$endDate = daterangeMongo($daterange)['mongo']['end'];

		$totalMa=0;
		$totalMal=sizeof(
			$mongoCollection->distinct(
				'File.MD5',

				array('$or'=>
					array(
						array('Results.DICA.Result'=>'MALICIOUS'),
						array('Results.V3.Result'=>'MALICIOUS'),
						array('Results.Heimdal.Result'=>'MALICIOUS'),
						array('Results.VirusTotal.Result'=>'MALICIOUS'),
						array('Results.MDP_VM.Result'=>'MALICIOUS')
					),
					'Date'=> array(
						'$gte'=>$startDate, '$lte'=>$endDate
					)
				)
			)
		);
		return $totalMal;
	}
}


if(!function_exists("getTotalInputCount")){
	function getTotalInputCount() {
		$totalIn=0;
		foreach (getTotalPerday() as $countAndTime) {
			$charNsec=$countAndTime[0];
			$cnt=$countAndTime[1];
			$totalIn+=$cnt;
		}
		return $totalIn;
	}
}

if(!function_exists("getDetectionEngineCount")){
	function getDetectionEngineCount($engineName="All", $daterange=Null) {
		global $mongoCollection;

		$startDate = daterangeMongo($daterange)['mongo']['start'];
		$endDate = daterangeMongo($daterange)['mongo']['end'];

		$key="Results.".$engineName.".Result";
		$engineCount=sizeof($mongoCollection->distinct(
			'File.MD5',
			array($key=>'MALICIOUS',
				'Date'=> array(
						'$gte'=>$startDate, '$lte'=>$endDate
					)
				)
			)
		);
		if (strcasecmp($engineName,"All")==0) {
			$engineCount=$total;
		}
		return $engineCount;
	}
}

/*
	Return Chart/Table Data functions
*/
if(!function_exists("returnDICAVersions")){
	function returnDICAVersions() {
		$DICA_4_1_2_1 = getArrayPerDay(
						array(
							'$and'=>array(
									array('Results.DICA.Result'=>'MALICIOUS'),
									array('Results.DICA.Version'=>'4.1.2.1')
								)
							)
						);
		$DICA_5_0_0_54= getArrayPerDay(
						array(
							'$and'=>array(
									array('Results.DICA.Result'=>'MALICIOUS'),
									array('Results.DICA.Version'=>'5.0.0.54')
								)
							)
						);
		$DICA_5_0_1_39= getArrayPerDay(
						array(
							'$and'=>array(
									array('Results.DICA.Result'=>'MALICIOUS'),
									array('Results.DICA.Version'=>'5.0.1.39')
								)
							)
						);
		$DICA_New     = getArrayPerDay(
						array(
							'$and'=>array(
									array("Results.DICA.Result"=>"MALICIOUS"),
									array("Results.DICA.Version"=>array('$ne'=>'4.1.2.1' )),
									array("Results.DICA.Version"=>array('$ne'=>'5.0.0.54')),
									array("Results.DICA.Version"=>array('$ne'=>'5.0.1.39'))
								)
							)
						);


		$retval=array_merge(
			array('v4_1_2_1'=>$DICA_4_1_2_1),
			array('v5_0_0_54'=>$DICA_5_0_0_54),
			array('v5_0_1_39'=>$DICA_5_0_1_39),
			array('Recent'=>$DICA_New)
		);
		return $retval;
	}
}

if(!function_exists("returnEngineRate")){
	function returnEngineRate($engineName) {
		$totalMal           = getTotalMaliciousCount();
		$totalEngine        = getDetectionEngineCount($engineName);
		$engineVsMalPercent = round($totalEngine/$totalMal*100,2);
		$retval             = array(
			$engineName=>array(
				"percent"=>$engineVsMalPercent, "count"=>$totalEngine, "total"=>$totalMal
			)
		);
		return $retval;		
	}
}

if(!function_exists("returnOverall")){
	function returnOverall(){
		$totalMal           = getTotalMaliciousCount();
		$totalIn            = getTotalInputCount();
		$retval             = array("Malicious"=>$totalMal, "Input"=>$totalIn);
		return $retval;
	}
}

if(!function_exists("returnAllRate")){
	function returnAllRate(){
		$retval=array();
		$totalMal           = getTotalMaliciousCount();
		foreach (array("DICA", "V3", "Heimdal", "VirusTotal", "MDP_VM") as $engineName) {
			$totalEngine    = getDetectionEngineCount($engineName);
			$retval         = array_merge(
				$retval,array(
					$engineName=> array(
						"percent"  => round($totalEngine/$totalMal*100,2),
						"count"    => $totalEngine,
						"total"    => $totalMal
					)
				)
			);
		}
		return $retval;
	}
}

if(!function_exists("calculateDailyPercent")){
	function calculateDailyPercent($numerator, $denominator) {
		$numerSize=sizeof($numerator)-1;
		$denomSize=sizeof($denominator)-1;
		$retval=array();

		// printf("<pre>");
		for ($i=0;$i<=$denomSize;$i++){
			$ts_d=$denominator[$i][0];
			// printf($ts_d+"\n");
			for ($j=0;$j<=$numerSize;$j++){
				$ts_n=$numerator[$j][0];
				if ($ts_d==$ts_n) {
					// printf("\n denom_ts, numer_ts\n");
					// printf($ts_d, $ts_n);
					// printf("\n countData: numer, denum, percent\n");
					// printf($numerator[$j], $denominator[$i], $numerator[$j][1]/$denominator[$i][1]*100);
					// printf("\n");
					// Timestamp Match!
					array_push($retval, array($ts_d, $numerator[$j][1]/$denominator[$i][1]*100));
					break;
				}
			}
		}
		return $retval;
	}
}

if(!function_exists("returnEngineDiff")){
	function returnEngineDiff(){
		// $Total_Data=getArrayPerDay(array('File.Size'=>array('$gt'=>0)));
		$Total_Data=getTotalPerDay();
		$DICA_Data=getArrayPerDay(
			array('$and'=>array(
					array("Results.DICA.Result"=>"MALICIOUS"),
					array("Results.DICA.Version"=>array('$ne'=>'4.1.2.1' )),
					array("Results.DICA.Version"=>array('$ne'=>'5.0.0.54')),
					array("Results.DICA.Version"=>array('$ne'=>'5.0.1.39'))
				)
			)
		);
		$V3_Data=getArrayPerDay(array('Results.V3.Result'=>'MALICIOUS'));
		$VirusTotal_Data=getArrayPerDay(array('Results.VirusTotal.Result'=>'MALICIOUS'));
		$Heimdal_Data=getArrayPerDay(array('Results.Heimdal.Result'=>'MALICIOUS'));
		$MDP_VM_Data=getArrayPerDay(array('Results.MDP_VM.Result'=>'MALICIOUS'));
		$Total_Malware_Data=getTotalMaliciousCountArrayPerDay(
			array('$or'=>
				array(
					array('Results.DICA.Result'=>'MALICIOUS'),
					array('Results.V3.Result'=>'MALICIOUS'),
					array('Results.Heimdal.Result'=>'MALICIOUS'),
					array('Results.VirusTotal.Result'=>'MALICIOUS'),
					array('Results.MDP_VM.Result'=>'MALICIOUS')
				)
			)
		);

		$DICA_percent=calculateDailyPercent($DICA_Data, $Total_Malware_Data);
		$V3_percent=calculateDailyPercent($V3_Data, $Total_Malware_Data);
		$VirusTotal_percent=calculateDailyPercent($VirusTotal_Data, $Total_Malware_Data);
		$Heimdal_percent=calculateDailyPercent($Heimdal_Data, $Total_Malware_Data);
		$MDP_VM_percent=calculateDailyPercent($MDP_VM_Data, $Total_Malware_Data);

		$retval=array_merge(
			array('Total'=>$Total_Data),
			array('TotalMalicious'=>$Total_Malware_Data),
			array('DICA'=>$DICA_Data),
			array('DICA_percent'=>$DICA_percent),
			array('V3'=>$V3_Data),
			array('V3_percent'=>$V3_percent),
			array('VirusTotal'=>$VirusTotal_Data),
			array('VirusTotal_percent'=>$VirusTotal_percent),
			array('Heimdal'=>$Heimdal_Data),
			array('Heimdal_percent'=>$Heimdal_percent),
			array('MDP_VM'=>$MDP_VM_Data),
			array('MDP_VM_percent'=>$MDP_VM_percent)
		);
		return $retval;
	}
}

if(!function_exists("returnResultTable")){
	function returnResultTable($fetchDate=null, $fetchEngine=null, $daterange=null){
		global $mongoCollection;

		$startDate = daterangeMongo($daterange)['mongo']['start'];
		$endDate = daterangeMongo($daterange)['mongo']['end'];

 		// if ( (isset($fetchDate)!=null) && ($fetchEngine=="Total") ) {
		if (isset($fetchDate)!=null) {
			$fetchDate = new MongoDate($fetchDate/1000);
			$t=$mongoCollection->aggregate(array(
				array(
					'$match'=>array(
						'$and'=>array(
							array('Date'=>$fetchDate),
						)
					)
				), 
				array(
					'$group'=>array(
						'_id'    => '$File.MD5',
						'Date'   => array('$push'=>'$Date'),
						'File'   => array('$push'=>'$File'),
						'Threat' => array('$push'=>'$Threat'),
						'Results'=> array('$push'=>'$Results'),
					)
				),
				array(
					'$sort' => array('Date'=>-1)
				),
				array(
					'$limit' => 10000
				)
			), array('allowDiskUse'=>true));
			/* Mogodb Query example
			db.enginediff.aggregate([
			    {
			        '$match':{ 
			            '$and':[
			                {'Date': '1427068800'},
			                {'Results.DICA.Result':'MALICIOUS'}
			            ]
			        }
			    },
			    {
			        '$group': 
			        {
			        '_id':'$File.MD5',
			        'Date':{'$push':'$Date'},
			        }
			    }
			])
			*/

		}
		else {
			$t=null;
			$t=$mongoCollection->aggregate(array(
				array(
					'$match'=>array(
						'$and'=>array(
							array(
								'Date'=>array(
									'$gte'=>$startDate, '$lte'=>$endDate
								)
							)
						)
					)
				), 
				array('$group'=>array(
					'_id'    => '$File.MD5',
					'Date'   => array('$push'=>'$Date'),
					'File'   => array('$push'=>'$File'),
					'Threat' => array('$push'=>'$Threat'),
					'Results'=> array('$push'=>'$Results'),
					)
				),
				array(
					'$sort'=> array('Date'=>-1)
				),
				array(
					'$limit' => 10000
				)
			), array('allowDiskUse'=>true));
		}


		$retval=array();
		if ($t!=null) {
			foreach($t['result'] as $d){
				$D=$d['Results'];
				$results=array();
				foreach ($D as $r) {
					// return isset($r[0]['DICA']);

					if (isset($r[0]['DICA'])){
						$dica      =$r[0]['DICA'];
					}
					if (isset($r[0]['V3'])){
						$v3        =$r[0]['V3'];
					}
					if (isset($r[0]['VirusTotal'])){
						$virustotal=$r[0]['VirusTotal'];
					}
					if (isset($r[0]['Heimdal'])){
						$heimdal   =$r[0]['Heimdal'];
					}
					if (isset($r[0]['MDP_VM'])){
						$mdp_vm   =$r[0]['MDP_VM'];
					}

					if (isset($dica['Result'])) {
						if (isset($dica['Reason'])==null) {$dica['Reason']=null;}
						## exclude following DICA version
						## '4.1.2.1','5.0.0.54','5.0.1.39'
						if ( ($dica['Version']!='4.1.2.1')
						  || ($dica['Version']!='5.0.0.54')
						  || ($dica['version']!='5.0.1.39')
						) {
							$results=array_merge($results,
								array("DICA_Result"=>$dica['Result'], "DICA_Reason"=>$dica['Reason'])
							); 
						}
					}
					if (isset($v3['Result'])) {
						if (isset($v3['Reason'])==null) {$v3['Reason']=null;}
						$results=array_merge($results,
							array("V3_Result"=>$v3['Result'], "V3_Reason"=>$v3['Reason'])
						); 
					}
					if (isset($virustotal['Result'])) {
						if (isset($virustotal['Reason'])==null) {$virustotal['Reason']=null;}
						$results=array_merge($results,
							array("VirusTotal_Result"=>$virustotal['Result'], "VirusTotal_Reason"=>$virustotal['Reason'])
						); 
					}
					if (isset($heimdal['Result'])) {
						if (isset($heimdal['Reason'])==null) {$heimdal['Reason']=null;}
						$results=array_merge($results,
							array("Heimdal_Result"=>$heimdal['Result'], "Heimdal_Reason"=>$heimdal['Reason'])
						); 
					}
					if (isset($mdp_vm['Result'])) {
						if (isset($mdp_vm['Reason'])==null) {$mdp_vm['Reason']=null;}
						$results=array_merge($results,
							array("MDP_VM_Result"=>$mdp_vm['Result'], "MDP_VM_Reason"=>$mdp_vm['Reason'])
						); 
					}
				}

				$info=array(
					"Date"=>date('Y-m-d', $d['Date'][0]->sec),
					"Name"=>$d['File'][0]['Name'],
					"Type"=>$d['File'][0]['Type'],
					"MD5"=>$d['File'][0]['MD5'],
					"CRC64"=>$d['File'][0]['CRC64'],
					"Size"=>$d['File'][0]['Size'],
					"Severity"=>$d['Threat'][0]['Severity'],
					"Threat_Name"=>$d['Threat'][0]['Name'],
				);
				$retr=array_merge($info,$results);
				array_push($retval, $retr);
			}
		}
		return $retval;
	}
}



/* MAIN Entry HERE */
$fetchType=$_GET['type'];
if(isset($_GET['date'])) { $fetchDate=$_GET['date']; } else {$fetchDate=null;}
if(isset($_GET['engine'])) { $fetchEngine=$_GET['engine']; } else {$fetchEngine=null;}

switch ($fetchType) {
	case 'DICAVersions':
		$retval=returnDICAVersions();
		break;
	case 'DICARate':
		$engineName="DICA";
		$retval=returnEngineRate($engineName);
		break;
	case "V3Rate":
		$engineName="V3";
		$retval=returnEngineRate($engineName);
		break;
	case "HeimdalRate":
		$engineName="Heimdal";
		$retval=returnEngineRate($engineName);
		break;
	case "VirusTotalRate":
		$engineName="VirusTotal";
		$retval=returnEngineRate($engineName);
		break;
	case "MDP_VMRate":
		$engineName="MDP_VM";
		$retval=returnEngineRate($engineName);
		break;
	case "Overall":
		$retval=returnOverall();
		break;
	case "AllRate":
		$retval=returnAllRate();
		break;
	case "ResultTable":
		$retval=returnResultTable($fetchDate, $fetchEngine);
		break;
	case "test":
		$retval=returnResultTable();
		echo "<pre>";
		print_r($retval);
		echo "</pre>";
		exit(0);
		break;
	case "EngineDiff":
	default:
		$retval=returnEngineDiff();
		break;
}


header("Content-type: application/json");
echo json_encode($retval);
?>
