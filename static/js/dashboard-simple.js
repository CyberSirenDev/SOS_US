/**
 * SOS US - Real-Time Social Sentiment Analyzer
 * Simplified Dashboard JavaScript (No external dependencies)
 */

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    startLiveUpdates();
    
    // Add enter key support for text input
    document.getElementById('textInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            analyzeSentiment();
        }
    });
});

/**
 * Load initial dashboard data
 */
function loadDashboardData() {
    updateSentimentStats();
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
    fetch('/api/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.json())
    .then(data => {
        displayAnalysisResult(data);
        textInput.value = '';
        setTimeout(updateDashboardData, 1000);
    })
    .catch(error => {
        alert('Error analyzing sentiment: ' + error);
    })
    .finally(() => {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyze Sentiment';
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
        <p><strong>Text:</strong> "${escapeHtml(result.text)}"</p>
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
    fetch('/api/stats')
        .then(response => response.json())
        .then(stats => {
            const positive = stats.positive || 0;
            const negative = stats.negative || 0;
            const neutral = stats.neutral || 0;
            
            // Update counters
            document.getElementById('positiveCount').textContent = positive;
            document.getElementById('negativeCount').textContent = negative;
            document.getElementById('neutralCount').textContent = neutral;
            
            // Update simple chart visualization
            updateSimpleChart(positive, negative, neutral);
        });
}

/**
 * Update simple visual chart without Chart.js
 */
function updateSimpleChart(positive, negative, neutral) {
    const canvas = document.getElementById('sentimentChart');
    const ctx = canvas.getContext('2d');
    const total = positive + negative + neutral;
    
    if (total === 0) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#e0e0e0';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#666';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('No data yet', canvas.width/2, canvas.height/2);
        return;
    }
    
    // Calculate percentages
    const posPercent = positive / total;
    const negPercent = negative / total;
    const neuPercent = neutral / total;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw simple bar chart
    const barWidth = canvas.width / 3 - 20;
    const maxHeight = canvas.height - 60;
    
    // Positive bar
    const posHeight = posPercent * maxHeight;
    ctx.fillStyle = 'rgba(39, 174, 96, 0.8)';
    ctx.fillRect(10, canvas.height - posHeight - 30, barWidth, posHeight);
    ctx.fillStyle = '#27ae60';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Positive', 10 + barWidth/2, canvas.height - 10);
    ctx.fillText(positive.toString(), 10 + barWidth/2, canvas.height - posHeight - 35);
    
    // Negative bar
    const negHeight = negPercent * maxHeight;
    ctx.fillStyle = 'rgba(231, 76, 60, 0.8)';
    ctx.fillRect(barWidth + 20, canvas.height - negHeight - 30, barWidth, negHeight);
    ctx.fillStyle = '#e74c3c';
    ctx.fillText('Negative', barWidth + 20 + barWidth/2, canvas.height - 10);
    ctx.fillText(negative.toString(), barWidth + 20 + barWidth/2, canvas.height - negHeight - 35);
    
    // Neutral bar
    const neuHeight = neuPercent * maxHeight;
    ctx.fillStyle = 'rgba(52, 152, 219, 0.8)';
    ctx.fillRect(2 * barWidth + 30, canvas.height - neuHeight - 30, barWidth, neuHeight);
    ctx.fillStyle = '#3498db';
    ctx.fillText('Neutral', 2 * barWidth + 30 + barWidth/2, canvas.height - 10);
    ctx.fillText(neutral.toString(), 2 * barWidth + 30 + barWidth/2, canvas.height - neuHeight - 35);
}

/**
 * Update trends chart with simple visualization
 */
function updateTrendsChart() {
    const canvas = document.getElementById('trendsChart');
    const ctx = canvas.getContext('2d');
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#e0e0e0';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#666';
    ctx.font = '16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Trend data will appear here', canvas.width/2, canvas.height/2);
}

/**
 * Update live feed with recent posts
 */
function updateLiveFeed() {
    fetch('/api/posts')
        .then(response => response.json())
        .then(posts => {
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
    updateTrendsChart();
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