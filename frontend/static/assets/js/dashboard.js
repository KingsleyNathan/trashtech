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
    series: [
      { name: 'Normal', data: [] },
      { name: 'Above Normal', data: [] },
      { name: 'Toxic', data: [] }
    ],
    colors: ['#ffa726', '#ffe066', '#ef5350'], // Orange, Yellow, Red
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
      max: 2,
      tickAmount: 2,
      labels: {
        formatter: function(value) {
          if (value === 0) return 'Normal';
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
          if (y === 0) return 'Normal';
          if (y === 1) return 'Above Normal';
          if (y === 2) return 'Toxic';
          return '';
        }
      }
    },
    legend: {
      show: true
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
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(result => {
        if (result.status === 'success') {
          updateFillLevelChart(result);
        }
      })
      .catch(error => {
        console.error('Error fetching fill level history:', error);
      });
  }

  // Function to update dashboard data
  function updateDashboard() {
    fetch('/api/dashboard-data')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
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

        // Update toxic alert status
        if (data.toxic_alert && data.toxic_alert.length > 0) {
          const toxic = data.toxic_alert[0];
          console.log('Toxic alert data:', toxic);  // Debug log
          document.getElementById('toxic-status').textContent = toxic.reading_value;
          
          // Display the timestamp in its original format
          document.getElementById('toxic-timestamp').textContent = toxic.timestamp;
        } else {
          console.log('No toxic alert data found');  // Debug log
          document.getElementById('toxic-status').textContent = 'No Data';
          document.getElementById('toxic-timestamp').textContent = '';
        }

        // Update toxic alert chart
        updateToxicAlertChart(data);
      })
      .catch(error => {
        console.error('Error fetching dashboard data:', error);
      });
  }

  // Initial updates
  updateDashboard();
  updateFillLevelHistory();

  // Auto-refresh every 30 seconds
  setInterval(updateDashboard, 30000);
  // Auto-refresh history every 1 minute
  setInterval(updateFillLevelHistory, 60000);

  // Function to update toxic alert chart
  function updateToxicAlertChart(data) {
    if (!data || !data.toxic_alert_history || data.toxic_alert_history.length === 0) {
      console.log('No toxic alert history data available');
      return;
    }

    const normalData = [];
    const aboveNormalData = [];
    const toxicData = [];
    
    data.toxic_alert_history.forEach(alert => {
      const timestamp = alert.timestamp;
      const status = alert.reading_value.toUpperCase();
      const statusValue = alert.status_value;
      
      if (status === 'NORMAL' || statusValue === 0) {
        normalData.push({ x: timestamp, y: 0 });
      } else if (status === 'ABOVE NORMAL' || statusValue === 1) {
        aboveNormalData.push({ x: timestamp, y: 1 });
      } else if (status === 'TOXIC' || statusValue === 2) {
        toxicData.push({ x: timestamp, y: 2 });
      }
    });

    try {
      toxicAlertChart.updateSeries([
        { name: 'Normal', data: normalData },
        { name: 'Above Normal', data: aboveNormalData },
        { name: 'Toxic', data: toxicData }
      ]);
    } catch (error) {
      console.error('Error updating toxic alert chart:', error);
    }
  }

  // Function to update fill level chart
  function updateFillLevelChart(data) {
    if (!data || !data.data) {
      console.log('No fill level data available');
      return;
    }

    const seriesData = [
      {
        name: 'Non-Biodegradable',
        data: data.data['Non-Biodegradable'] || []
      },
      {
        name: 'Recyclable',
        data: data.data['Recyclable'] || []
      }
    ];

    try {
      fillLevelTrendChart.updateSeries(seriesData);
    } catch (error) {
      console.error('Error updating fill level chart:', error);
    }
  }
}); 