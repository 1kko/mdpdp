function loadChart_DetectionScore(daterange,engineName,target_id) {

	var gaugeOptions = {

		chart: {
			type: 'solidgauge',
			height: 250,
			// spacingTop:-100,
			// marginTop:-100,
		},
		credits: { enabled: 0 },
		title: null,

		pane: {
			center: ['50%', '85%'],
			size: '100%',
			startAngle: -90,
			endAngle: 90,
			background: {
				backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || '#EEE',
				innerRadius: '60%',
				outerRadius: '100%',
				shape: 'arc'
			}
		},

		tooltip: {
			enabled: true,
			followPointer: true
		},
		exporting: {
			enabled: false
		},

		// the value axis
		yAxis: {
			stops: [
				[0.1, '#DF5353'], // green
				[0.5, '#DDDF0D'], // yellow
				[0.9, '#55BF3B'] // red
			],
			lineWidth: 0,
			minorTickInterval: null,
			tickPixelInterval: 400,
			tickWidth: 0,
			title: {
				y: -70
			},
			labels: {
				y: 16
			},
			min:0,
			max:100
		},

		plotOptions: {
			solidgauge: {
				dataLabels: {
					distance: -50,
					y: 5,
					borderWidth: 0,
					useHTML: true
				}
			}
		},
	};

	$.ajax({
		url:"fetch.php?type=DetectionScore&engineName="+engineName+"&daterange="+daterange,
		dataType:"json",
		success: function(rateData, engineName) {
			switch(engineName) {
			case 'DICA':
				chartColor=Highcharts.getOptions().colors[0];
				break;
			case 'Heimdal':
				chartColor=Highcharts.getOptions().colors[1];
				break;
			case 'VirusTotal':
				chartColor=Highcharts.getOptions().colors[2];
				break;
			case 'V3':
				chartColor=Highcharts.getOptions().colors[3];
				break;
			case 'MDP_VM':
				chartColor=Highcharts.getOptions().colors[4];
				break;
			}

			// The speed gauge
			$(target_id).highcharts(Highcharts.merge(gaugeOptions, {
				yAxis: {
					title: {
						text: '<?php echo $engineName; ?>'
					},
					stops: [ 
						[0, chartColor ]
					]
				},
				series: [{
					name: '<?php echo $engineName; ?>',
					data: [rateData.percent],
					dataLabels: {
						format: '<div style="text-align:center"><span style="font-size:25px;color:' +
							((Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black') + '">'+rateData.count+'</span><br/>' +
							'<span style="font-size:12px;color:silver">out of '+rateData.total+'</span></div>'
					},
					tooltip: {
						valueSuffix: ' %'
					}
				}]
			}));
		}
	});
};