var app = angular.module('SFHomelessnessApp', ['nvd3']);

app.controller('MainCtrl', function($scope) {
    $scope.options = {
        chart: {
            type: 'scatterChart',
            height: 450,
            color: ['#00e3e5', '#29d500', '#c67800', '#bf0000'],
            scatter: {
                onlyCircles: false
            },
            showDistX: true,
            showDistY: true,
            useInteractiveGuideline: false,
            interactive: true,
            tooltips: true,
            tooltip: {
              contentGenerator: function(d) {
                return '<p>Subjectivity index: ' + d.point.subjectivity + ' ('+ d.series[0].key + ')</p>' +
                '<p>Times RTed: ' + d.point.size + '</p>' +
                '<p>Sentiment polarity: ' + d.series[0].value + '</p>' +
                '<p>Tweeted text: ' + d.point.text + '</p>';
              }
            },
            tooltipContent: function(key){
              return '<p>holla</p>' + '<h1>' + key + '</h1>';
            },
            duration: 350,
            xAxis: {
                axisLabel: 'Datetime',
                tickFormat: function(date){
                    return d3.time.format('%H:%M:%S')(new Date(date));
                }
            },
            yAxis: {
                axisLabel: 'Sentiment Polarity',
                tickFormat: function(d){
                    return d3.format('.02f')(d);
                },
                axisLabelDistance: -5
            },
            zoom: {
                //NOTE: All attributes below are optional
                enabled: false,
                scaleExtent: [1, 10],
                useFixedDomain: false,
                useNiceScale: false,
                horizontalOff: false,
                verticalOff: false,
                unzoomEventType: 'dblclick.zoom'
            }
        }
    };

    $scope.data = getData();

    function getData(){
        data = [0.25, 0.5, 0.75, 1.0].map(function(cutoff, idx){
          return {
            key: ["Highly Objective", "Slightly Objective", "Slightly Subjective", "Highly Subjective"][idx],
            values: sfHomelessData.filter(function(d){
              return (d[2] < cutoff) && (d[2] >= cutoff - 0.25)
            }).map(function(d){
              return {
                x: d[0]
                , y: d[1]
                , size: d[3]
                , shape: 'circle'
                , subjectivity: d[2]
                , text: d[4]
              }
            })
          }
        })
        return data;
    }
});
