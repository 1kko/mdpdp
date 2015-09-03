function loadDICAChart(DICA_data_array) {
	//return new Highcharts.Chart({
	$('#chart_DICA').highcharts({
		credits: { enabled: 0 },
		chart: {
			renderTo: 'chart_DICA',
			type: 'column',
			backgroundColor: '#fff',
			borderWidth: null,
			zoomType: 'xy',
			style: {
				color: '#fff'
			}
		},
		title: {
			text: ""
		},
		subtitle: {
			text: ""
		},
		exporting: {
			width: 1024
		},
		xAxis: {
			type:'datetime',
			minTickInterval: 24 * 3600 *1000,
			dateTimeLabelFormats: {
				hour:"%m/%e, %a",
				day: "%m/%e, %a",
				month: "%m/%e"
			}
		},
		legend: {
			navigation: {
				activeColor: '#fff',
				inactiveColor: '#aaa',
				animation: true,
				style: {
					color: '#fff'
				}
			}
		},
		yAxis: {
			title: { text: null },
			labels: { enabled: false }
		},
		tooltip: {
			crosshairs: true,
		},
		plotOptions: {
			areaspline: {
				dataLabels: {
					enabled: true,
					color: '#eee',
					symbol: 'circle'
				}
			},
			spline: {
				dataLabels: {
					enabled: true,
					color: '#ddd',
				}
			},
			column: {
				dataLabels: {
					enabled: true,
					color: '#ddd',
				},
			}
		},
		colors: ['rgba(92,184,92,0.9)','rgba(92,184,92,0.7)','rgba(92,184,92,0.4)','rgba(92,184,92,0.1)'],
		series: [
		{
			name: 'Recent',
			//type: 'spline',
			data: DICA_data_array.Recent,
		},{ 
			name: '5.0.1.39',
			data: DICA_data_array.v5_0_1_39,
		},{ 
			name: '5.0.0.54',
			data: DICA_data_array.v5_0_0_54,
		},{ 
			name: '4.1.2.1',
			data: DICA_data_array.v4_1_2_1,
		}]
	});
};
