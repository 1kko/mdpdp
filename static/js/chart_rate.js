function loadRateChart(rateData) {
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

	// The speed gauge
	$('#chart_DICARate').highcharts(Highcharts.merge(gaugeOptions, {
		yAxis: {
			title: {
				text: 'DICA'
			},
			stops: [ 
				[0, Highcharts.getOptions().colors[0] ]
			]
		},
		series: [{
			name: 'DICA',
			data: [rateData.DICA.percent],
			dataLabels: {
				format: '<div style="text-align:center"><span style="font-size:25px;color:' +
					((Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black') + '">'+rateData.DICA.count+'</span><br/>' +
					'<span style="font-size:12px;color:silver">out of '+rateData.DICA.total+'</span></div>'
			},
			tooltip: {
				valueSuffix: ' %'
			}
		}]
	}));
	$('#chart_HeimdalRate').highcharts(Highcharts.merge(gaugeOptions, {
		yAxis: {
			title: {
				text: 'Heimdal'
			},
			stops: [ 
				[0, Highcharts.getOptions().colors[1] ]
			]
		},
		series: [{
			name: 'Heimdal',
			data: [rateData.Heimdal.percent],
			dataLabels: {
				format: '<div style="text-align:center"><span style="font-size:25px;color:' +
					((Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black') + '">'+rateData.Heimdal.count+'</span><br/>' +
					'<span style="font-size:12px;color:silver">out of '+rateData.Heimdal.total+'</span></div>'
			},
			tooltip: {
				valueSuffix: ' %'
			}
		}]
	}));
	$('#chart_V3Rate').highcharts(Highcharts.merge(gaugeOptions, {
		yAxis: {
			title: {
				text: 'V3'
			},
			stops: [ 
				[0, Highcharts.getOptions().colors[2] ]
			]
		},
		series: [{
			name: 'V3',
			data: [rateData.V3.percent],
			dataLabels: {
				format: '<div style="text-align:center"><span style="font-size:25px;color:' +
					((Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black') + '">'+rateData.V3.count+'</span><br/>' +
					'<span style="font-size:12px;color:silver">out of '+rateData.V3.total+'</span></div>'
			},
			tooltip: {
				valueSuffix: ' %'
			}
		}]
	}));
	$('#chart_VirusTotalRate').highcharts(Highcharts.merge(gaugeOptions, {
		yAxis: {
			title: {
				text: 'VirusTotal'
			},
			stops: [ 
				[0, Highcharts.getOptions().colors[3] ]
			]
		},
		series: [{
			name: 'VirusTotal',
			data: [rateData.VirusTotal.percent],
			dataLabels: {
				format: '<div style="text-align:center"><span style="font-size:25px;color:' +
					((Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black') + '">'+rateData.VirusTotal.count+'</span><br/>' +
					'<span style="font-size:12px;color:silver">out of '+rateData.VirusTotal.total+'</span></div>'
			},
			tooltip: {
				valueSuffix: ' %',
			}
		}]
	}));
	$('#chart_MDP_VMRate').highcharts(Highcharts.merge(gaugeOptions, {
		yAxis: {
			title: {
				text: 'MDP_VM'
			},
			stops: [ 
				[0, Highcharts.getOptions().colors[4] ]
			]
		},
		series: [{
			name: 'MDP_VM',
			data: [rateData.MDP_VM.percent],
			dataLabels: {
				format: '<div style="text-align:center"><span style="font-size:25px;color:' +
					((Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black') + '">'+rateData.MDP_VM.count+'</span><br/>' +
					'<span style="font-size:12px;color:silver">out of '+rateData.MDP_VM.total+'</span></div>'
			},
			tooltip: {
				valueSuffix: ' %',
			},
		}]
	}));
};