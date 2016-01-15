function loadDiffChart(Diff_data_array) {
	//return new Highcharts.Chart({
    Highcharts.setOptions({
		lang: {
			thousandsSep: ''
		},
		timezoneOffset: 9*60,
	});
    
	$('#chart_EngineDiff').highcharts({
		credits: { enabled: 0 },
		chart: {
			renderTo:'chart_EngineDiff',
			type: 'column',
			backgroundColor: null,
			borderWidth: null,
			zoomType: 'x',
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
			},
			itemHiddenStyle:{
				color:'#222'
			},
			itemHoverStyle:{
				color:'#555'
			},
			itemStyle: {
				color:'#ccc'
			},
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
				fillOpacity: 0.5,
				dataLabels: {
					enabled: true,
					color: '#eee',
					symbol: 'circle',
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
			},
			series: {
				cursor: 'pointer',
				point: {
					events: {
						click: function() {
							//console.log(this);
							//console.debug('engine: '+this.series.name+', date: '+this.category+', value: '+this.y);
							var engineName=this.series.name;
							var fetchDate=this.category;
							engineName=engineName.replace(/\.%$/,"");
							console.debug("req---"+engineName+" "+fetchDate);


							$.ajax({
								url:"/fetch/ResultTable/?date="+fetchDate+"&engine="+engineName,
								dataType:"json",
								success: function(data) {
									// console.debug("rx----");
									// console.debug(data);
									// $('#resultTable').attr('data-sort-name',engineName);
									$('#resultTable').bootstrapTable('load', data);
									// $('#resultTable').sortName(engineName);
									// console.debug($('#resultTable').bootstrapTable('getOptions'));

								}
							});

						}
					}
				}
			}
		},
		series: [{
		// 	name: 'Total',
		// 	type: 'areaspline',
		// 	data: Diff_data_array.Total,
		// 	zIndex: 0,
		// 	lineWidth: 0,

		// 	marker: {
		// 		fillColor: 'white',
		// 		lineWidth: 1,
		// 		lineColor: '#ccc'
		// 	},
		// 	color: 'rgba(91,192,222,0.3)',
		// 	lineColor: 'rgba(91,192,222,0.3)',
		// 	fillColor: 'rgba(91,192,222,0.3)',

		// }, { 
			name: 'Malicious',
			type: 'areaspline',
			data: Diff_data_array.TotalMalicious,
			visible: false,
			zIndex: 1,
			lineWidth: 0,
			marker: {
				fillColor: 'white',
				lineWidth: 1,
				lineColor: 'rgba(192,0,50,0.3)'
			},
			color: 'rgba(192,0,50,0.3)',
			lineColor: 'rgba(192,0,50,0.3)',
			fillColor: 'rgba(192,0,50,0.3)',

		}, {
/*			name: 'DICA',
			data: Diff_data_array.DICA,
			zIndex: 4,
			lineWidth: 2,
			lineColor: Highcharts.getOptions().colors[0],
			opacity: 0.3,
			marker: {
				fillColor: 'white',
				lineWidth: 1,
				lineColor: Highcharts.getOptions().colors[0]
			}
		}, { 
			name: 'VirusTotal',
			data: Diff_data_array.VirusTotal,
			zIndex: 3,
			lineWidth: 2,
			lineColor: Highcharts.getOptions().colors[1],
			opacity: 0.3,
			marker: {
				fillColor: 'white',
				lineWidth: 1,
				lineColor: Highcharts.getOptions().colors[1]
			}
		}, { 
*/			name: 'V3',
			data: Diff_data_array.V3,
			visible: false,
			zIndex: 2,
			lineWidth: 2,
			lineColor: Highcharts.getOptions().colors[2],
			opacity: 0.3,
			color: Highcharts.getOptions().colors[2],
			marker: {
				fillColor: 'white',
				lineWidth: 1,
				lineColor: Highcharts.getOptions().colors[2]
			}
		}, { 
/*			name: 'Heimdal',
			data: Diff_data_array.Heimdal,
			zIndex: 1,
			lineWidth: 2,
			lineColor: Highcharts.getOptions().colors[3],
			opacity: 0.3,
			marker: {
				fillColor: 'white',
				lineWidth: 1,
				lineColor: Highcharts.getOptions().colors[3]
			}
		}, { 
*/			name: 'MDP_VM',
		 	data: Diff_data_array.MDP_VM,
		 	visible: false,
		 	zIndex: 1,
		 	lineWidth: 2,
		 	lineColor: Highcharts.getOptions().colors[4],
		 	color: Highcharts.getOptions().colors[4],
		 	opacity: 0.3,
		 	marker: {
		 		fillColor: 'white',
		 		lineWidth: 1,
		 		lineColor: Highcharts.getOptions().colors[4]
		 	}
		}, { 
			name: 'V3.%',
			data: Diff_data_array.V3_percent,
			zIndex: 2,
			lineWidth: 2,
			lineColor: Highcharts.getOptions().colors[2],
			opacity: 0.3,
			color: Highcharts.getOptions().colors[2],
			marker: {
				fillColor: 'white',
				lineWidth: 1,
				lineColor: Highcharts.getOptions().colors[2]
			},
			dataLabels:{
				format: '{y:.2f}',
			}
		}, {
			name: 'MDP_VM.%',
		 	data: Diff_data_array.MDP_VM_percent,
		 	zIndex: 1,
		 	lineWidth: 2,
		 	lineColor: Highcharts.getOptions().colors[4],
		 	color: Highcharts.getOptions().colors[4],
		 	opacity: 0.3,
		 	marker: {
		 		fillColor: 'white',
		 		lineWidth: 1,
		 		lineColor: Highcharts.getOptions().colors[4]
		 	},
		 	dataLabels:{
		 		format: '{y:.2f}',
		 	}
		}]
	});

	function series(name) {
		var chart=$('#chart_EngineDiff').highcharts().series;
		for (var i=0; i<$('#chart_EngineDiff').highcharts().series.length;i++) {
			// console.log(chart[i].name, name);
			if (chart[i].name===name) {
				// console.log(chart[i].name);
				return chart[i];
			}
		}
	}

	$('#toggle_value').on('click', function(e) {
		if ($(this).is(':checked')) {
			series('MDP_VM').show();
			series('V3').show();
			series('Malicious').show();
			series('MDP_VM.%').hide();
			series('V3.%').hide();
		} else {
			series('MDP_VM').hide();
			series('V3').hide();
			series('Malicious').hide();
			series('MDP_VM.%').show();
			series('V3.%').show();
		}
	});
};
