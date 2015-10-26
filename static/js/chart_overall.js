

function loadOverallChart(overallData){
	$('#chart_Overall').highcharts({
		credits: { enabled: 0 },
		chart: {
			plotBackgroundColor: null,
			type: 'pie',
			options3d: {
				enabled: true,
				alpha: 50,
				beta: 0,
				depth: 35,
				viewDistance: 0
			}
		},
		exporting:{
			enabled: false
		},
		title: {
			text: ''
		},
		tooltip: {
			enabled: true,
			pointFormat: '{series.name}: <b>{point.y} ({point.percentage:.1f}%)</b>'
		},
		plotOptions: {
			pie: {
				colors: [Highcharts.getOptions().colors[1], Highcharts.getOptions().colors[3] ],
				allowPointSelect: true,
				cursor: 'pointer',
				depth: 35,
				dataLabels: {
					enabled: true,
					formatter: function (){ 
						ret=this.point.name+": "+this.y;
						//ret+={this.point.percentage:.1f}; 
						return ret;
					},
					distance: -50,
				},
				showInLegend: true
			}
		},
		series: [{
			type: 'pie',
			name: 'Detection Rate',
			data: [
				['Remains', overallData.Input-overallData.Malicious],
				['Malicious', overallData.Malicious],
			],
		}]
	});
};
