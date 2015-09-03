function refresh(daterange) {
	loadOverallChart(daterange, '#chart_Overall');
	loadResultTable(daterange, '#resultTable');
	loadDICAChart(daterange, '#chart_DICA');
	loadOverallChart(daterange, '#chart_Overall');
	loadRateChart(daterange);
	loadNonPeDiffChart(daterange, '#chart_EngineDiff');
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
			console.log(range);
		}
	);

	var dr=$('#daterange').data('daterangepicker');

	dr.setStartDate(startDate);
	dr.setEndDate(endDate);

	refresh(range);
});