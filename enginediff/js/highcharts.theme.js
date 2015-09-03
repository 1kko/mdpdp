Highcharts.theme = {
    colors: ['#5cb85c', '#5bc0de', '#f0ad4e', '#D9534f', '#8D5DB8','#B8B841','#B85D33', '#a9a98b','#5cb7b8','#a9de5b','#d988aa','#cfc398','#f0ad4e','#d978af', '#f5f5f5'],
    chart: {
        backgroundColor: 'rgba(255,255,255,0)',
        borderWidth: 0

    },
    title: {
        style: {
            color: '#000',
            font: 'bold 16px "Trebuchet MS", Verdana, sans-serif'
        }
    },
    subtitle: {
        style: {
            color: '#666666',
            font: 'bold 12px "Trebuchet MS", Verdana, sans-serif'
        }
    },

    legend: {
        itemStyle: {
            font: '9pt Trebuchet MS, Verdana, sans-serif',
            color: 'black'
        },
        itemHoverStyle:{
            color: 'black'
        }   
    },

};

// Apply the theme
Highcharts.setOptions(Highcharts.theme);
