document.addEventListener('DOMContentLoaded', function() {
    // Set dark mode as default
    document.documentElement.classList.add('dark-mode');
    
    // Initialize theme toggle
    initThemeToggle();
    
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
    
    // Initialize prediction functionality
    initPrediction();
});

// Theme toggle functionality
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    
    if (!themeToggle) return;
    
    themeToggle.addEventListener('click', function() {
        document.documentElement.classList.toggle('dark-mode');
        updateThemeIcon();
    });
    
    // Set initial icon based on current theme
    updateThemeIcon();
}

function updateThemeIcon() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const isDarkMode = document.documentElement.classList.contains('dark-mode');
        themeToggle.innerHTML = isDarkMode ? 
            '<i class="fas fa-sun"></i>' : 
            '<i class="fas fa-moon"></i>';
        themeToggle.setAttribute('title', isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode');
    }
}

// Prediction functionality
function initPrediction() {
    const predictBtn = document.getElementById('predictBtn');
    const historicalExpenses = document.getElementById('historicalExpenses');
    const resultSection = document.getElementById('resultSection');
    const predictionResult = document.getElementById('predictionResult');
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');

    if (!predictBtn) return;

    predictBtn.addEventListener('click', async function() {
        // Hide previous results/errors
        resultSection.classList.add('d-none');
        errorSection.classList.add('d-none');

        // Get input values
        const expensesText = historicalExpenses.value.trim();
        if (!expensesText) {
            showError('Please enter historical expense values');
            return;
        }

        // Parse comma-separated values
        const expenses = expensesText.split(',')
            .map(value => parseFloat(value.trim()))
            .filter(value => !isNaN(value));

        if (expenses.length < 3) {  // Changed from 30 to 3 to match your Flask app
            showError('Please enter at least 3 valid expense values');
            return;
        }

        try {
            // Show loading state
            predictBtn.disabled = true;
            predictBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Predicting...';

            // Make API request - CORRECTED parameter name
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    expenses: expenses  // ✅ CORRECT - matches Flask app expectation
                }),
            });

            const data = await response.json();

            if (response.ok) {
                // Show prediction result - CORRECTED field name
                predictionResult.textContent = `$${data.prediction.toFixed(2)}`;  // ✅ Changed from predicted_expense to prediction
                resultSection.classList.remove('d-none');
            } else {
                showError(data.error || 'Failed to get prediction');
            }
        } catch (error) {
            showError('An error occurred while making the prediction');
            console.error(error);
        } finally {
            // Reset button state
            predictBtn.disabled = false;
            predictBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Generate Prediction';
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorSection.classList.remove('d-none');
    }
}

// Chart initialization
function initializeCharts() {
    // Set Chart.js defaults for dark mode
    Chart.defaults.color = '#a0aec0';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
    
    // Monthly spending trend chart
    const trendCtx = document.getElementById('monthlyTrendChart');
    if (trendCtx) {
        new Chart(trendCtx, {
            type: 'bar',
            data: {
                labels: ['2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12'],
                datasets: [{
                    label: 'Monthly Expenses',
                    data: [570, 580, 570, 670, 590, 575],
                    backgroundColor: 'rgba(99, 102, 241, 0.7)',
                    borderColor: '#6366f1',
                    borderWidth: 1,
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#e2e8f0',
                        bodyColor: '#e2e8f0',
                        borderColor: '#6366f1',
                        borderWidth: 1,
                        padding: 10,
                        displayColors: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(71, 85, 105, 0.2)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    // Category spending chart
    const categoryCtx = document.getElementById('categoryChart');
    if (categoryCtx) {
        new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: ['Food', 'Transport', 'Entertainment', 'Other'],
                datasets: [{
                    data: [70, 15, 10, 5],
                    backgroundColor: [
                        '#6366f1',
                        '#f59e0b',
                        '#10b981',
                        '#ef4444'
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#e2e8f0',
                        bodyColor: '#e2e8f0',
                        borderColor: '#6366f1',
                        borderWidth: 1,
                        padding: 10,
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }
}
