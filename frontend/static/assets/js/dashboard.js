// Track last sent alerts using localStorage
function getLastSentAlerts() {
  const stored = localStorage.getItem('lastSentAlerts');
  return stored ? JSON.parse(stored) : {
    toxic: null,
    nonbio: null,
    recyclable: null
  };
}

function updateLastSentAlert(type, value) {
  const alerts = getLastSentAlerts();
  alerts[type] = value;
  localStorage.setItem('lastSentAlerts', JSON.stringify(alerts));
}

document.addEventListener("DOMContentLoaded", function () {
  // Initialize charts
  const trashCountsChart = new ApexCharts(document.querySelector("#trash-counts-chart"), {
    chart: { 
      type: 'bar',
      height: 350,
      animations: {
        enabled: true
      }
    },
    series: [{
      name: 'Count',
      data: [0, 0, 0]  // Initialize with zeros
    }],
    xaxis: { 
      categories: ['Recyclable', 'Biodegradable', 'Non-Biodegradable']
    },
    colors: ['#42a5f5', '#66bb6a', '#ffa726'],
    plotOptions: {
      bar: {
        distributed: true,
        columnWidth: '50%',
      }
    },
    legend: {
      show: false
    }
  });
  trashCountsChart.render();

  const expectedCategories = ['Recyclable', 'Biodegradable', 'Non-Biodegradable'];
  const classificationChart = new ApexCharts(document.querySelector("#classification-distribution-chart"), {
    chart: { 
      type: 'pie',
      height: 350
    },
    series: [0, 0, 0],  // Initialize with zeros
    labels: expectedCategories,
    colors: ['#42a5f5', '#66bb6a', '#ffa726'],
    legend: {
      position: 'bottom'
    }
  });
  classificationChart.render();

  // Initialize Toxic Alert Chart
  let toxicAlertChart = new ApexCharts(document.querySelector("#toxic-alert-chart"), {
    chart: {
      type: 'line',
      height: 200,
      animations: {
        enabled: true,
        easing: 'linear',
        dynamicAnimation: {
          speed: 1000
        }
      },
      toolbar: {
        show: true
      },
      zoom: {
        enabled: true
      }
    },
    series: [{
      name: 'Toxic Status',
      data: []
    }],
    colors: ['#ffa726', '#ef5350'], // Orange for Above Normal, Red for Toxic
    stroke: {
      curve: 'smooth',
      width: 3
    },
    markers: {
      size: 4,
      hover: {
        size: 6
      }
    },
    xaxis: {
      type: 'datetime',
      title: {
        text: 'Time'
      },
      labels: {
        datetimeFormatter: {
          year: 'yyyy',
          month: "MMM 'yy",
          day: 'dd MMM',
          hour: 'HH:mm'
        }
      }
    },
    yaxis: {
      min: 1,
      max: 2,
      tickAmount: 1,
      labels: {
        formatter: function(value) {
          if (value === 1) return 'Above Normal';
          if (value === 2) return 'Toxic';
          return '';
        }
      },
      title: {
        text: 'Status Level'
      }
    },
    tooltip: {
      shared: true,
      intersect: false,
      x: {
        format: 'dd MMM yyyy HH:mm'
      },
      y: {
        formatter: function (y) {
          if (y === 1) return 'Above Normal';
          if (y === 2) return 'Toxic';
          return '';
        }
      }
    },
    legend: {
      show: false
    }
  });
  toxicAlertChart.render();

  // Initialize Fill Level Trend Chart
  const fillLevelTrendChart = new ApexCharts(document.querySelector("#fill-level-trend-chart"), {
    chart: {
      type: 'line',
      height: 350,
      animations: {
        enabled: true,
        easing: 'linear',
        dynamicAnimation: {
          speed: 1000
        }
      },
      toolbar: {
        show: true
      },
      zoom: {
        enabled: true
      }
    },
    series: [{
      name: 'Non-Biodegradable',
      data: []
    }, {
      name: 'Recyclable',
      data: []
    }],
    colors: ['#ffa726', '#42a5f5'],
    stroke: {
      curve: 'smooth',
      width: 3
    },
    markers: {
      size: 4,
      hover: {
        size: 6
      }
    },
    xaxis: {
      type: 'datetime',
      title: {
        text: 'Time'
      },
      labels: {
        datetimeFormatter: {
          year: 'yyyy',
          month: "MMM 'yy",
          day: 'dd MMM',
          hour: 'HH:mm'
        }
      }
    },
    yaxis: {
      min: 0,
      max: 100,
      title: {
        text: 'Fill Level (%)'
      }
    },
    tooltip: {
      shared: true,
      intersect: false,
      x: {
        format: 'dd MMM yyyy HH:mm'
      },
      y: {
        formatter: function (y) {
          return y + '%'
        }
      }
    }
  });
  fillLevelTrendChart.render();

  // Function to fetch and update fill level history
  function updateFillLevelHistory() {
    fetch('/api/fill-level-history')
      .then(response => response.json())
      .then(result => {
        if (result.status === 'success') {
          const data = result.data;
          fillLevelTrendChart.updateSeries([
            {
              name: 'Non-Biodegradable',
              data: data['Non-Biodegradable']
            },
            {
              name: 'Recyclable',
              data: data['Recyclable']
            }
          ]);
        } else {
          console.error('Error fetching fill level history:', result.message);
        }
      })
      .catch(error => {
        console.error('Error fetching fill level history:', error);
      });
  }

  // Function to update dashboard data
  function updateDashboard() {
    fetch('/api/dashboard-data')
      .then(response => response.json())
      .then(data => {
        console.log('Received dashboard data:', data);  // Debug log

        // Calculate total counts for each category
        const totalCounts = {
          'Recyclable': 0,
          'Biodegradable': 0,
          'Non-Biodegradable': 0
        };

        if (data.classification_distribution && Array.isArray(data.classification_distribution)) {
          data.classification_distribution.forEach(item => {
            if (item.category && typeof item.count === 'number') {
              totalCounts[item.category] = item.count;
            }
          });
        }

        // Update trash counts chart
        const trashCountsData = [
          totalCounts['Recyclable'],
          totalCounts['Biodegradable'],
          totalCounts['Non-Biodegradable']
        ];
        trashCountsChart.updateSeries([{
          name: 'Count',
          data: trashCountsData
        }]);

        // Update classification distribution chart
        const distributionData = [
          totalCounts['Recyclable'],
          totalCounts['Biodegradable'],
          totalCounts['Non-Biodegradable']
        ];
        classificationChart.updateSeries(distributionData);

        // Update fill levels based on counts
        const nonBioFillLevel = Math.min(Math.round((totalCounts['Non-Biodegradable'] / 100) * 100), 100);
        const recyclableFillLevel = Math.min(Math.round((totalCounts['Recyclable'] / 100) * 100), 100);
        
        // Show latest non-bio reading value and timestamp
        if (data.non_bio_alert && data.non_bio_alert.length > 0) {
          const nonBio = data.non_bio_alert[0];
          document.getElementById('nonbio-fill-level').textContent = nonBio.reading_value + '%';
          document.getElementById('nonbio-timestamp').textContent = nonBio.timestamp;
        } else {
          document.getElementById('nonbio-fill-level').textContent = 'No Data';
          document.getElementById('nonbio-timestamp').textContent = '';
        }

        // Show latest recyclable reading value and timestamp
        if (data.recyclable_alert && data.recyclable_alert.length > 0) {
          const recyclable = data.recyclable_alert[0];
          document.getElementById('recyclable-fill-level').textContent = recyclable.reading_value + '%';
          document.getElementById('recyclable-timestamp').textContent = recyclable.timestamp;
        } else {
          document.getElementById('recyclable-fill-level').textContent = 'No Data';
          document.getElementById('recyclable-timestamp').textContent = '';
        }

        // Update fill level trend chart with latest data point
        if (data.non_bio_alert && data.non_bio_alert.length > 0 && 
            data.recyclable_alert && data.recyclable_alert.length > 0) {
          
          // Update trend chart
          const timestamp = new Date().getTime();
          fillLevelTrendChart.appendData([{
            seriesIndex: 0,
            data: [{
              x: timestamp,
              y: parseInt(data.non_bio_alert[0].reading_value)
            }]
          }, {
            seriesIndex: 1,
            data: [{
              x: timestamp,
              y: parseInt(data.recyclable_alert[0].reading_value)
            }]
          }]);
        }

        // Update toxic alert status
        if (data.toxic_alert && data.toxic_alert.length > 0) {
          const toxic = data.toxic_alert[0];
          document.getElementById('toxic-status').textContent = toxic.reading_value;
          document.getElementById('toxic-timestamp').textContent = toxic.timestamp;
        } else {
          document.getElementById('toxic-status').textContent = 'No Data';
          document.getElementById('toxic-timestamp').textContent = '';
        }

        // Update toxic alert chart with historical data
        if (data.toxic_alert_history && data.toxic_alert_history.length > 0) {
          const toxicData = data.toxic_alert_history
            .filter(alert => {
              const status = alert.reading_value.toUpperCase();
              return status === 'ABOVE NORMAL' || status === 'TOXIC';
            })
            .map(alert => {
              const timestamp = new Date(alert.timestamp).getTime();
              let statusValue;
              switch(alert.reading_value.toUpperCase()) {
                case 'ABOVE NORMAL':
                  statusValue = 1;
                  break;
                case 'TOXIC':
                  statusValue = 2;
                  break;
                default:
                  statusValue = null;
              }
              return {
                x: timestamp,
                y: statusValue
              };
            });
          toxicAlertChart.updateSeries([{
            name: 'Toxic Status',
            data: toxicData
          }]);
        }
      });
  }

  // Initial updates
  updateDashboard();
  updateFillLevelHistory();

  // Auto-refresh every 5 minutes
  setInterval(updateDashboard, 300000);
  // Auto-refresh history every 15 minutes
  setInterval(updateFillLevelHistory, 900000);
}); 