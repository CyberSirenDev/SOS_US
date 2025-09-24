/**
 * SOS US - Real-Time Social Sentiment Analyzer
 * Dashboard JavaScript functionality
 */

let sentimentChart;
let trendsChart;

// Initialize dashboard when page loads
$(document).ready(function() {
    initializeCharts();
    loadDashboardData();
    startLiveUpdates();
});

/**
 * Initialize Chart.js charts
 */
function initializeCharts() {
    // Sentiment Distribution Pie Chart
    const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
    sentimentChart = new Chart(sentimentCtx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Negative', 'Neutral'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(39, 174, 96, 0.8)',
                    'rgba(231, 76, 60, 0.8)',
                    'rgba(52, 152, 219, 0.8)'
                ],
                borderColor: [
                    'rgba(39, 174, 96, 1)',
                    'rgba(231, 76, 60, 1)',
                    'rgba(52, 152, 219, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            }
        }
    });

    // Trends Line Chart
    const trendsCtx = document.getElementById('trendsChart').getContext('2d');
    trendsChart = new Chart(trendsCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Positive',
                data: [],
                borderColor: 'rgba(39, 174, 96, 1)',
                backgroundColor: 'rgba(39, 174, 96, 0.1)',
                fill: true,
                tension: 0.4
            }, {
                label: 'Negative',
                data: [],
                borderColor: 'rgba(231, 76, 60, 1)',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                fill: true,
                tension: 0.4
            }, {
                label: 'Neutral',
                data: [],
                borderColor: 'rgba(52, 152, 219, 1)',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

/**
 * Load initial dashboard data
 */
function loadDashboardData() {
    updateSentimentStats();
    updateTrends();
    updateLiveFeed();
}

/**
 * Analyze sentiment of user input
 */
function analyzeSentiment() {
    const textInput = document.getElementById('textInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultBox = document.getElementById('analysisResult');
    
    const text = textInput.value.trim();
    if (!text) {
        alert('Please enter some text to analyze');
        return;
    }
    
    // Disable button during analysis
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analyzing...';
    
    // Send request to backend
    $.ajax({
        url: '/api/analyze',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ text: text }),
        success: function(response) {
            displayAnalysisResult(response);
            textInput.value = '';
            updateDashboardData();
        },
        error: function(xhr, status, error) {
            alert('Error analyzing sentiment: ' + error);
        },
        complete: function() {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analyze Sentiment';
        }
    });
}

/**
 * Display analysis result
 */
function displayAnalysisResult(result) {
    const resultBox = document.getElementById('analysisResult');
    const sentiment = result.sentiment;
    const polarity = result.polarity.toFixed(3);
    
    resultBox.className = `result-box ${sentiment}`;
    resultBox.innerHTML = `
        <h3>Analysis Result</h3>
        <p><strong>Sentiment:</strong> ${sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}</p>
        <p><strong>Polarity Score:</strong> ${polarity}</p>
        <p><strong>Text:</strong> "${result.text}"</p>
    `;
    resultBox.style.display = 'block';
    
    // Hide result after 5 seconds
    setTimeout(() => {
        resultBox.style.display = 'none';
    }, 5000);
}

/**
 * Update sentiment statistics
 */
function updateSentimentStats() {
    $.get('/api/stats', function(stats) {
        const positive = stats.positive || 0;
        const negative = stats.negative || 0;
        const neutral = stats.neutral || 0;
        
        // Update counters
        document.getElementById('positiveCount').textContent = positive;
        document.getElementById('negativeCount').textContent = negative;
        document.getElementById('neutralCount').textContent = neutral;
        
        // Update chart
        sentimentChart.data.datasets[0].data = [positive, negative, neutral];
        sentimentChart.update('none');
    });
}

/**
 * Update trends data
 */
function updateTrends() {
    $.get('/api/trends', function(trends) {
        const dates = Object.keys(trends).sort();
        const positiveData = [];
        const negativeData = [];
        const neutralData = [];
        
        dates.forEach(date => {
            positiveData.push(trends[date].positive || 0);
            negativeData.push(trends[date].negative || 0);
            neutralData.push(trends[date].neutral || 0);
        });
        
        trendsChart.data.labels = dates;
        trendsChart.data.datasets[0].data = positiveData;
        trendsChart.data.datasets[1].data = negativeData;
        trendsChart.data.datasets[2].data = neutralData;
        trendsChart.update('none');
    });
}

/**
 * Update live feed with recent posts
 */
function updateLiveFeed() {
    $.get('/api/posts', function(posts) {
        const feedContainer = document.getElementById('liveFeed');
        
        if (posts.length === 0) {
            feedContainer.innerHTML = '<div class="loading">No posts yet. Start by analyzing some text above!</div>';
            return;
        }
        
        const feedHTML = posts.slice(0, 10).map(post => {
            const timestamp = new Date(post.timestamp).toLocaleString();
            const polarity = post.polarity.toFixed(3);
            
            return `
                <div class="post-item ${post.sentiment}">
                    <div class="post-content">${escapeHtml(post.text)}</div>
                    <div class="post-meta">
                        <span class="timestamp">${timestamp}</span>
                        <span class="sentiment-badge ${post.sentiment}">
                            ${post.sentiment} (${polarity})
                        </span>
                    </div>
                </div>
            `;
        }).join('');
        
        feedContainer.innerHTML = feedHTML;
    });
}

/**
 * Update all dashboard data
 */
function updateDashboardData() {
    updateSentimentStats();
    updateTrends();
    updateLiveFeed();
}

/**
 * Start live updates every 10 seconds
 */
function startLiveUpdates() {
    setInterval(updateDashboardData, 10000);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Handle Enter key in text input
 */
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('textInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            analyzeSentiment();
        }
    });
});

// Add some sample posts on first load if database is empty
function addSamplePosts() {
    const sampleTexts = [
        "This is absolutely fantastic! Best product ever!",
        "I'm really disappointed with this service.",
        "The weather today is quite normal, nothing special.",
        "Amazing experience, would definitely recommend to others!",
        "Not what I expected, could be much better.",
    ];
    
    sampleTexts.forEach((text, index) => {
        setTimeout(() => {
            $.ajax({
                url: '/api/analyze',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ text: text }),
                success: function() {
                    if (index === sampleTexts.length - 1) {
                        setTimeout(updateDashboardData, 1000);
                    }
                }
            });
        }, index * 1000);
    });
}