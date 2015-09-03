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
			<h3>PE File Detection Report</h3>
			<hr>
		</div>
		<div class="row">
			<div class="col-xs-12 col-sm-12 col-md-4">
				<h3><i class="axi axi-center-focus-weak"></i> Overall</h3>
				<div id="chart_Overall"></div>
			</div>
			<div class="col-xs-12 col-sm-12 col-md-8">
				<h3><i class="axi axi-dashboard2"></i> Detection Score</h3>
				<div class="col-xs-12 col-sm-6 col-md-4">
					<div id="chart_MDP_VMRate"></div>
				</div>
			</div>
		</div>
		<div class="row">
			<div class="col-xs-12">
			<h3><i class="axi axi-settings-input-component"></i> Engine Diff Chart</h3>
				<div id="chart_EngineDiff"></div>
			</div>
		</div>
		<div class="row">
			<div class="col-xs-12">
				<table id="resultTable"
					data-show-columns="true"
					data-pagination="true"
					data-search="true"
					data-sort-name="Date"
					data-sort-order="desc"
					data-striped="true"
					data-row-style="rowStyle">
					<thead>
						<tr>
							<th data-sortable="true" data-visible="true"  data-field="Date">Date</th>
							<th data-sortable="true" data-visible="false" data-field="Name">Name</th>
							<th data-sortable="true" data-visible="false" data-field="Type">Type</th>
							<th data-sortable="true" data-visible="true"  data-field="MD5">MD5</th>
							<th data-sortable="true" data-visible="false" data-field="CRC64">CRC64</th>
							<th data-sortable="true" data-visible="false" data-field="Size">Size</th>
							<th data-sortable="true" data-visible="false" data-field="Severity">Severity</th>
							<th data-sortable="true" data-visible="true"  data-field="Threat_Name">Threat Name</th>
							<th data-sortable="true" data-visible="true"  data-field="MDP_VM_Result">MDP_VM Result</th>
							<th data-sortable="true" data-visible="false" data-field="MDP_VM_Reason">MDP_VM Reason</th>
						</tr>
					</thead>
				</table>
			</div>
		</div>
	</div>
<footer>
	<?php include('common/footer.php'); ?>
</footer>
</body>

<script type="text/javascript" src="js/chart_pe.js"></script>
<script type="text/javascript" src="js/chart_rate.js"></script>
<script type="text/javascript" src="js/chart_overall.js"></script>
<script type="text/javascript" src="js/table_result.js"></script>
<script type="text/javascript" src="js/table_style.js"></script>
<script type="text/javascript" src="js/date_selector.js"></script>
</html>
