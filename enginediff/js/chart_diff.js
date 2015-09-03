function loadDiffChart(Diff_data_array) {
	//return new Highcharts.Chart({
    Highcharts.setOptions({
		lang: {
			thousandsSep: ''
		}
	});
    
	$('#chart_EngineDiff').highcharts({
		credits: { enabled: 0 },
		chart: {
			renderTo:'chart_EngineDiff',
			type: 'column',
			backgroundColor: null,
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
				fillOpacity: 0.5,
				dataLabels: {
					enabled: true,
					color: '#eee',
					symbol: 'circle'
				},
				lineColor: 'rgba(91,192,222,0.3)',
				fillColor: 'rgba(91,192,222,0.3)',
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
							// console.debug("req---"+engineName+" "+fetchDate);
							$.ajax({
								url:"fetch.php?type=ResultTable&date="+fetchDate+"&engine="+engineName,
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
			name: 'Total',
			type: 'areaspline',
			data: Diff_data_array.Total,
			zIndex: 0,
			lineWidth: 0,

			marker: {
				fillColor: 'white',
				lineWidth: 1,
				lineColor: '#ccc'
			},
			color: 'rgba(91,192,222,0.3)',

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
			zIndex: 2,
			lineWidth: 2,
			lineColor: Highcharts.getOptions().colors[2],
			opacity: 0.3,
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
		 	zIndex: 1,
		 	lineWidth: 2,
		 	lineColor: Highcharts.getOptions().colors[4],
		 	opacity: 0.3,
		 	marker: {
		 		fillColor: 'white',
		 		lineWidth: 1,
		 		lineColor: Highcharts.getOptions().colors[4]
		 	}
		}]
	});
};
