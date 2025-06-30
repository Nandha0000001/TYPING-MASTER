// Charts Module for Progress Visualization
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const wpmChartCanvas = document.getElementById('wpm-chart');
    const accuracyChartCanvas = document.getElementById('accuracy-chart');
    const errorChartCanvas = document.getElementById('error-chart');
    const refreshBtn = document.getElementById('refresh-stats-btn');
    const predictionSection = document.getElementById('prediction-section');
    
    // Chart instances
    let wpmChart = null;
    let accuracyChart = null;
    let errorChart = null;
    
    // Initialize the charts module
    function initialize() {
        // Set up event listeners
        if (refreshBtn) {
            refreshBtn.addEventListener('click', loadUserProgress);
        }
        
        // Load progress data on page load
        loadUserProgress();
    }
    
    // Load user progress data from the server
    function loadUserProgress() {
        fetch('/api/user-progress')
            .then(response => response.json())
            .then(data => {
                displayProgressCharts(data);
                displayPrediction(data);
            })
            .catch(error => {
                console.error('Error loading progress data:', error);
                displayNoDataMessage();
            });
    }
    
    // Display a message when no data is available
    function displayNoDataMessage() {
        const messageHTML = `
            <div class="alert alert-info mt-3">
                <h4>No Data Available</h4>
                <p>Complete some typing tests or lessons to see your progress charts.</p>
            </div>
        `;
        
        if (wpmChartCanvas) {
            wpmChartCanvas.insertAdjacentHTML('afterend', messageHTML);
        }
        
        if (predictionSection) {
            predictionSection.innerHTML = `
                <div class="alert alert-info">
                    <p>Complete more typing tests to receive performance predictions.</p>
                </div>
            `;
        }
    }
    
    // Display progress charts
    function displayProgressCharts(data) {
        if (!data) return;
        
        const wpmHistory = data.wpm_history || [];
        const accuracyHistory = data.accuracy_history || [];
        const errorStats = data.error_statistics || {};
        
        // Only proceed if we have data
        if (wpmHistory.length === 0 && accuracyHistory.length === 0) {
            displayNoDataMessage();
            return;
        }
        
        // Create WPM chart
        createWpmChart(wpmHistory);
        
        // Create accuracy chart
        createAccuracyChart(accuracyHistory);
        
        // Create error statistics chart
        createErrorChart(errorStats);
    }
    
    // Create WPM history chart
    function createWpmChart(wpmHistory) {
        if (!wpmChartCanvas || wpmHistory.length === 0) return;
        
        // Prepare data
        const labels = wpmHistory.map((entry, index) => {
            // Format timestamp or use test number
            if (entry.timestamp) {
                const date = new Date(entry.timestamp);
                return date.toLocaleDateString();
            }
            return `Test ${index + 1}`;
        });
        
        const wpmData = wpmHistory.map(entry => entry.wpm);
        
        // Calculate moving average if we have enough data points
        let movingAverages = [];
        if (wpmData.length >= 3) {
            const windowSize = 3;
            for (let i = 0; i <= wpmData.length - windowSize; i++) {
                const window = wpmData.slice(i, i + windowSize);
                const avg = window.reduce((sum, val) => sum + val, 0) / windowSize;
                movingAverages.push(avg);
            }
            
            // Pad start with nulls to align with original data
            movingAverages = Array(windowSize - 1).fill(null).concat(movingAverages);
        }
        
        // Destroy existing chart if it exists
        if (wpmChart) {
            wpmChart.destroy();
        }
        
        // Create new chart
        wpmChart = new Chart(wpmChartCanvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'WPM',
                        data: wpmData,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    },
                    {
                        label: 'Trend (3-test average)',
                        data: movingAverages,
                        borderColor: 'rgb(153, 102, 255)',
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        borderDashed: [5, 5],
                        tension: 0.3,
                        pointRadius: 0,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'WPM History',
                        color: '#f5f5f5'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        labels: {
                            color: '#f5f5f5'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Words Per Minute',
                            color: '#f5f5f5'
                        },
                        ticks: {
                            color: '#f5f5f5'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Test Date',
                            color: '#f5f5f5'
                        },
                        ticks: {
                            color: '#f5f5f5'
                        }
                    }
                }
            }
        });
    }
    
    // Create accuracy history chart
    function createAccuracyChart(accuracyHistory) {
        if (!accuracyChartCanvas || accuracyHistory.length === 0) return;
        
        // Prepare data
        const labels = accuracyHistory.map((entry, index) => {
            // Format timestamp or use test number
            if (entry.timestamp) {
                const date = new Date(entry.timestamp);
                return date.toLocaleDateString();
            }
            return `Test ${index + 1}`;
        });
        
        const accuracyData = accuracyHistory.map(entry => entry.accuracy);
        
        // Destroy existing chart if it exists
        if (accuracyChart) {
            accuracyChart.destroy();
        }
        
        // Create new chart
        accuracyChart = new Chart(accuracyChartCanvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Accuracy',
                    data: accuracyData,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Accuracy History',
                        color: '#f5f5f5'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        labels: {
                            color: '#f5f5f5'
                        }
                    }
                },
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Accuracy (%)',
                            color: '#f5f5f5'
                        },
                        ticks: {
                            color: '#f5f5f5'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Test Date',
                            color: '#f5f5f5'
                        },
                        ticks: {
                            color: '#f5f5f5'
                        }
                    }
                }
            }
        });
    }
    
    // Create error statistics chart
    function createErrorChart(errorStats) {
        if (!errorChartCanvas || !errorStats || !errorStats.most_common_errors) return;
        
        // Prepare data
        const errors = Object.entries(errorStats.most_common_errors);
        if (errors.length === 0) return;
        
        errors.sort((a, b) => b[1] - a[1]); // Sort by frequency (descending)
        const topErrors = errors.slice(0, 10); // Get top 10
        
        const labels = topErrors.map(entry => {
            const errorType = entry[0];
            // Make error patterns more readable
            return errorType.replace('->', ' → ').replace('∅', '_');
        });
        
        const data = topErrors.map(entry => entry[1]);
        
        // Create a color array
        const backgroundColors = [
            'rgba(255, 99, 132, 0.7)',
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)',
            'rgba(199, 199, 199, 0.7)',
            'rgba(83, 102, 255, 0.7)',
            'rgba(40, 159, 64, 0.7)',
            'rgba(210, 199, 199, 0.7)'
        ];
        
        // Destroy existing chart if it exists
        if (errorChart) {
            errorChart.destroy();
        }
        
        // Create new chart
        errorChart = new Chart(errorChartCanvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Error Frequency',
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors.map(color => color.replace('0.7', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Most Common Typing Errors',
                        color: '#f5f5f5'
                    },
                    legend: {
                        display: false,
                        labels: {
                            color: '#f5f5f5'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Frequency: ${context.raw}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Frequency',
                            color: '#f5f5f5'
                        },
                        ticks: {
                            color: '#f5f5f5'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Error Pattern',
                            color: '#f5f5f5'
                        },
                        ticks: {
                            color: '#f5f5f5'
                        }
                    }
                }
            }
        });
    }
    
    // Display prediction information
    function displayPrediction(data) {
        if (!predictionSection) return;
        
        // Fetch a WPM prediction
        fetch('/api/predict-wpm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                partial_text: '',
                time_elapsed: 0
            })
        })
        .then(response => response.json())
        .then(predictionData => {
            if (predictionData && predictionData.predicted_wpm) {
                // Calculate improvement percentage
                const currentWpm = predictionData.current_wpm || 0;
                const predictedWpm = predictionData.predicted_wpm;
                const improvementPct = currentWpm > 0 
                    ? Math.round(((predictedWpm - currentWpm) / currentWpm) * 100) 
                    : 0;
                
                // Format prediction message
                let message = `
                    <div class="card">
                        <div class="card-body">
                            <h4 class="card-title">Your Typing Speed Prediction</h4>
                            <p class="card-text">Based on your typing history, we predict:</p>
                            <ul>
                                <li>Current average speed: <strong>${Math.round(currentWpm)} WPM</strong></li>
                                <li>Predicted future speed: <strong>${Math.round(predictedWpm)} WPM</strong></li>
                    `;
                
                if (improvementPct > 0) {
                    message += `<li>Potential improvement: <strong>${improvementPct}%</strong></li>`;
                }
                
                message += `
                            </ul>
                            <p class="card-text">Continue practicing to improve your typing speed!</p>
                        </div>
                    </div>
                `;
                
                predictionSection.innerHTML = message;
            } else {
                predictionSection.innerHTML = `
                    <div class="alert alert-info">
                        <p>Complete more typing tests to receive a personalized speed prediction.</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error getting prediction:', error);
            predictionSection.innerHTML = `
                <div class="alert alert-warning">
                    <p>Unable to generate prediction. Please try again later.</p>
                </div>
            `;
        });
    }
    
    // Initialize the module
    initialize();
});
