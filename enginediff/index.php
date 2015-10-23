<?php 
include_once("common/lib.php");
?>

<!DOCTYPE html>
<html lang="kr">
<meta charset = "utf-8">
<head>
	<title>EngineDiff - ikko</title>
	<?php include ('common/headers.php'); ?>
</head>

<body>
	<?php include ('common/nav.php'); ?>
	<div class="container">
		<div class="row">
			<div class="col-xs-12 col-sm-12 col-md-4">
				<h3><i class="axi axi-center-focus-weak"></i> Overall</h3>
				<div id="chart_Overall"></div>
			</div>
			<div class="col-xs-12 col-sm-12 col-md-8">
				<h3><i class="axi axi-dashboard2"></i> Detection Score</h3>
				<!-- <div class="col-xs-12 col-sm-6 col-md-4">
					<div id="chart_DICARate"></div>
				</div>
				<div class="col-xs-12 col-sm-6 col-md-4">
					<div id="chart_HeimdalRate"></div>
				</div>
				-->
				<div class="col-xs-12 col-sm-6 col-md-6">
					<div id="chart_V3Rate"></div>
				</div>
				<!--
				<div class="col-xs-12 col-sm-6 col-md-4">
					<div id="chart_VirusTotalRate"></div>
				</div>
				-->
				<div class="col-xs-12 col-sm-6 col-md-6">
					<div id="chart_MDP_VMRate"></div>
				</div>
			</div>
		</div>
		<div class="row">
			<div class="col-xs-12">
			<h3><i class="axi axi-settings-input-component"></i> Engine Diff Chart 
			       <small><input type="checkbox" id="toggle_value"> Show values</small></h3>
				<div id="chart_EngineDiff"></div>
			</div>
		</div>
		<div class="row">
			<div class="col-xs-12">
				<table id="resultTable"
					data-show-columns="true"
					data-click-to-select="true"
					data-pagination="true"
					data-search="true"
					data-sort-name="Date, Severity"
					data-sort-order="desc"
					data-striped="true"
					data-page-size="100"
					data-page-list="[100,200,500,1000,All]"
					data-row-style="rowStyle">
					<thead>
						<tr>
					        <th data-sortable="false" data-visible="true" data-field="state" data-checkbox="true">C</th>
							<th data-sortable="true" data-visible="true"  data-field="Date">Date</th>
							<th data-sortable="true" data-visible="false" data-field="Name">Name</th>
							<th data-sortable="true" data-visible="false" data-field="Type">Type</th>
							<th data-sortable="true" data-visible="true"  data-field="MD5">MD5</th>
							<th data-sortable="true" data-visible="true" data-field="CRC64">CRC64</th>
							<th data-sortable="true" data-visible="false" data-field="Size">Size</th>
							<th data-sortable="true" data-visible="false" data-field="Severity">Severity</th>
							<th data-sortable="true" data-visible="false"  data-field="Threat_Name">Threat Name</th>
							<th data-sortable="true" data-visible="false"  data-field="DICA_Result">DICA Result</th>
							<th data-sortable="true" data-visible="false" data-field="DICA_Reason">DICA Reason</th>
							<th data-sortable="true" data-visible="true"  data-field="MDP_VM_Result">MDP Result</th>
							<th data-sortable="true" data-visible="true" data-field="MDP_VM_Reason">MDP Reason</th>
							<th data-sortable="true" data-visible="true" data-field="V3_Result">V3 Result</th>
							<th data-sortable="true" data-visible="true" data-field="V3_Reason">V3 Reason</th>
							<th data-sortable="true" data-visible="false"  data-field="Heimdal_Result">Heimdal Result</th>
							<th data-sortable="true" data-visible="false" data-field="Heimdal_Reason">Heimdal Reason</th>
							<th data-sortable="true" data-visible="false"  data-field="VirusTotal_Result">VirusTotal Result</th>
							<th data-sortable="true" data-visible="false" data-field="VirusTotal_Reason">VirusTotal Reason</th>
						</tr>
					</thead>
				</table>
			</div>
		</div>
		<div class="row">
			<div class="col-xs-2">
			<form id="md5listForm" method="POST">
				<!-- <input name="md5listField" type="hidden" id="md5listField"> -->
			</form>
			<button class="btn btn-primary" id="sendtoanalysis">Send to Analysis</button>
			</div>
		</div>
		<!--div class="row">
			<div class="col-xs-12">
			<h3><i class="axi axi-ion-document"></i> DICA Version Chart</h3>
				<div id="chart_DICA"></div>
			</div>
		</div-->
	</div>
<footer>
	<?php include('common/footer.php'); ?>
</footer>
</body>

<script type="text/javascript" src="js/chart_diff.js"></script>
<!--script type="text/javascript" src="js/chart_dica.js"></script-->
<script type="text/javascript" src="js/chart_rate.js"></script>
<script type="text/javascript" src="js/chart_overall.js"></script>

<script>

function mdpdpQuery(value, row, index) {
	url = window.location.protocol + '//' + window.location.hostname + ':5000' + '/query/md5sum=' + row.MD5;
	return "<a href='"+url+"'>" + value + "</a>";
}

function rowStyle(row, index) {
   if ( 
		   (row.V3_Result=="MALICIOUS")
		// && (row.DICA_Result=="MALICIOUS")
		// && (row.Heimdal_Result=="MALICIOUS")
		// && (row.VirusTotal_Result=="MALICIOUS")
		&& (row.MDP_VM_Result=="MALICIOUS")
	) {
		return { classes: 'info' };
	} else if (
		   (row.V3_Result=="MALICIOUS")
		// || (row.DICA_Result=="MALICIOUS")
		// || (row.Heimdal_Result=="MALICIOUS")
		// || (row.VirusTotal_Result=="MALICIOUS")
		|| (row.MDP_VM_Result=="MALICIOUS")
	) {
		return { classes: 'warning' };
	} else if (
		   (row.V3_Result=="SUSPICIOUS")
		// || (row.DICA_Result=="SUSPICIOUS")
		// || (row.Heimdal_Result=="SUSPICIOUS")
		// || (row.VirusTotal_Result=="SUSPICIOUS")
	) {
		return { classes: 'danger' };
	}


	return {};
}

function refresh(daterange) {
	$.ajax({
		url:"fetch.php?type=EngineDiff&daterange="+daterange,
		dataType:"json",
		success: function(data) {
			// console.log(data);
			loadDiffChart(data);
		}
	});

	//$.ajax({
	//	url:"fetch.php?type=DICAVersions&daterange="+daterange,
	//	dataType:"json",
	//	success: function(data) {
	//		loadDICAChart(data);
	//	}
	//});

	$.ajax({
		url:"fetch.php?type=AllRate&daterange="+daterange,
		dataType:"json",
		success: function(data) {
			loadRateChart(data);
		}
	});

	$.ajax({
		url:"fetch.php?type=Overall&daterange="+daterange,
		dataType:"json",
		success: function(data) {
			loadOverallChart(data);
		}
	});

	$.ajax({
		url:"fetch.php?type=ResultTable&daterange="+daterange,
		dataType:"json",
		success: function(data) {
			$('#resultTable').bootstrapTable('destroy');
			$('#resultTable').bootstrapTable({data:data});
		}

	});
}

$(document).ready(function() { 
	var dateFormat='YYYY/MM/DD'
	var startDate=moment().add(-1,'months').format(dateFormat);
	var endDate=moment().format(dateFormat);
	var range=startDate+" - "+endDate;

	$('#daterange').daterangepicker({
			format: dateFormat,
			ranges: {
			   'Today': [moment(), moment()],
			   'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
			   'Last 7 Days': [moment().subtract(6, 'days'), moment()],
			   'Last 30 Days': [moment().subtract(29, 'days'), moment()],
			   'This Month': [moment().startOf('month'), moment().endOf('month')],
			   'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
			}
		},
		function (start, end) {
			var range=start.format(dateFormat)+" - "+end.format(dateFormat)
			refresh(range);
			// console.log(range);
		}
	);

	var dr=$('#daterange').data('daterangepicker');

	dr.setStartDate(startDate);
	dr.setEndDate(endDate);

	refresh(range);

	$('#md5listForm').attr('action', window.location.protocol + '//' + window.location.hostname + ':5000' + '/md5list/');
	$('#sendtoanalysis').on('click', function() {
		// on click should be fill up form and send to targetUrl
		// 1. get selection from table, and fill up #md5list
		var selections=$('#resultTable').bootstrapTable('getSelections');
		console.log(selections);
		var md5list="";
		for (var i in selections) {
			// 2. append inputfield and fill up
			// $('#md5listField').val(md5list);
			$("<input type='text' name='md5list[]' value='"+selections[i]['MD5']+"' />").appendTo('#md5listForm');
		}
		// 3. submit form.
		$('#md5listForm').submit();
	});
});
</script>
</html>
