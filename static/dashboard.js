class StockDashboard {
    constructor() {
        this.currentSymbol = '';
        this.refreshInterval = null;
        this.init();
    }
    
    init() {
        this.loadWatchlist();
        this.loadPortfolio();
        this.setupAutoRefresh();
    }
    
    setupAutoRefresh() {
        // Refresh data every 5 minutes
        this.refreshInterval = setInterval(() => {
            this.loadWatchlist();
            this.loadPortfolio();
        }, 300000);
    }
    
    searchStock() {
        const symbol = document.getElementById('stockInput').value.toUpperCase().trim();
        if (!symbol) {
            this.showError('Please enter a stock symbol');
            return;
        }
        
        this.currentSymbol = symbol;
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = '<p class="loading">Loading...</p>';
        
        fetch(`/api/stock/${symbol}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    resultDiv.innerHTML = `<p class="error">${data.error}</p>`;
                } else {
                    this.displayStockInfo(data, resultDiv);
                    document.getElementById('historyBtn').style.display = 'inline-block';
                    document.getElementById('watchlistBtn').style.display = 'inline-block';
                    document.getElementById('portfolioBtn').style.display = 'inline-block';
                }
            })
            .catch(error => {
                console.error('Search error:', error);
                resultDiv.innerHTML = `<p class="error">Failed to fetch stock data: ${error.message}</p>`;
            });
    }
    
    displayStockInfo(data, container) {
        const changeIndicator = data.previous_close ? 
            (data.price > data.previous_close ? '↗' : '↘') : '';
        const changeClass = data.previous_close ? 
            (data.price > data.previous_close ? 'positive' : 'negative') : '';
        
        container.innerHTML = `
            <div class="stock-info">
                <h2>${data.symbol}</h2>
                <p class="price ${changeClass}">$${data.price.toFixed(2)} ${changeIndicator}</p>
                <p class="currency">${data.currency}</p>
                <p class="market-state">Market: ${data.market_state}</p>
                ${data.previous_close ? `<p class="prev-close">Previous Close: $${data.previous_close.toFixed(2)}</p>` : ''}
            </div>
        `;
    }
    
    showHistory() {
        if (!this.currentSymbol) return;
        
        const historyDiv = document.getElementById('history');
        historyDiv.innerHTML = '<p class="loading">Loading history...</p>';
        historyDiv.style.display = 'block';
        
        fetch(`/api/history/${this.currentSymbol}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    historyDiv.innerHTML = `<p class="error">${data.error}</p>`;
                } else {
                    this.displayHistory(data, historyDiv);
                }
            })
            .catch(error => {
                console.error('History error:', error);
                historyDiv.innerHTML = '<p class="error">Failed to fetch history</p>';
            });
    }
    
    displayHistory(data, container) {
        let historyHTML = `<h3>Price History for ${data.symbol}</h3><div class="history-list">`;
        data.history.slice(0, 10).forEach(entry => {
            const date = new Date(entry.timestamp).toLocaleString();
            historyHTML += `
                <div class="history-item">
                    <span class="hist-price">$${entry.price.toFixed(2)}</span>
                    <span class="hist-time">${date}</span>
                </div>
            `;
        });
        historyHTML += '</div>';
        container.innerHTML = historyHTML;
    }
    
    loadWatchlist() {
        fetch('/api/watchlist')
            .then(response => response.json())
            .then(data => {
                const watchlistDiv = document.getElementById('watchlist');
                if (data.length === 0) {
                    watchlistDiv.innerHTML = '<p class="empty-watchlist">No stocks in watchlist</p>';
                    return;
                }
                
                let watchlistHTML = '';
                data.forEach(item => {
                    watchlistHTML += `
                        <div class="watchlist-item">
                            <span class="symbol" onclick="dashboard.quickSearch('${item.symbol}')">${item.symbol}</span>
                            <span class="target-price">${item.target_price ? '$' + item.target_price.toFixed(2) : 'No target'}</span>
                            <span class="alert-status ${item.alert_enabled ? 'enabled' : 'disabled'}">
                                ${item.alert_enabled ? 'Alert ON' : 'Alert OFF'}
                            </span>
                            <button onclick="dashboard.removeFromWatchlist('${item.symbol}')" class="remove-btn">Remove</button>
                        </div>
                    `;
                });
                watchlistDiv.innerHTML = watchlistHTML;
            })
            .catch(error => {
                console.error('Watchlist error:', error);
                document.getElementById('watchlist').innerHTML = '<p class="error">Failed to load watchlist</p>';
            });
    }
    
    loadPortfolio() {
        fetch('/api/portfolio')
            .then(response => response.json())
            .then(data => {
                this.displayPortfolio(data);
            })
            .catch(error => {
                console.error('Portfolio error:', error);
                const portfolioDiv = document.getElementById('portfolio');
                if (portfolioDiv) {
                    portfolioDiv.innerHTML = '<p class="error">Failed to load portfolio</p>';
                }
            });
    }
    
    displayPortfolio(data) {
        const portfolioDiv = document.getElementById('portfolio');
        if (!portfolioDiv) return;
        
        if (data.positions && data.positions.length === 0) {
            portfolioDiv.innerHTML = '<p class="empty-portfolio">No positions in portfolio</p>';
            return;
        }
        
        let portfolioHTML = '<h3>Portfolio Summary</h3>';
        
        if (data.summary) {
            const summary = data.summary;
            const profitClass = summary.total_profit_loss >= 0 ? 'positive' : 'negative';
            
            portfolioHTML += `
                <div class="portfolio-summary">
                    <div class="summary-item">
                        <span>Total Invested:</span>
                        <span>$${summary.total_invested.toFixed(2)}</span>
                    </div>
                    <div class="summary-item">
                        <span>Current Value:</span>
                        <span>$${summary.total_current_value.toFixed(2)}</span>
                    </div>
                    <div class="summary-item ${profitClass}">
                        <span>Total P&L:</span>
                        <span>$${summary.total_profit_loss.toFixed(2)} (${summary.total_profit_loss_pct.toFixed(2)}%)</span>
                    </div>
                </div>
            `;
        }
        
        if (data.positions) {
            portfolioHTML += '<div class="portfolio-positions">';
            data.positions.forEach(position => {
                const profitClass = position.profit_loss >= 0 ? 'positive' : 'negative';
                portfolioHTML += `
                    <div class="portfolio-item">
                        <div class="position-header">
                            <span class="symbol" onclick="dashboard.quickSearch('${position.symbol}')">${position.symbol}</span>
                            <span class="shares">${position.shares} shares</span>
                        </div>
                        <div class="position-details">
                            <span>Avg: $${position.avg_price.toFixed(2)}</span>
                            <span>Current: $${position.current_price.toFixed(2)}</span>
                            <span class="${profitClass}">P&L: $${position.profit_loss.toFixed(2)} (${position.profit_loss_pct.toFixed(2)}%)</span>
                        </div>
                    </div>
                `;
            });
            portfolioHTML += '</div>';
        }
        
        portfolioDiv.innerHTML = portfolioHTML;
    }
    
    quickSearch(symbol) {
        document.getElementById('stockInput').value = symbol;
        this.searchStock();
    }
    
    showError(message) {
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = `<p class="error">${message}</p>`;
    }
    
    addToWatchlist() {
        if (!this.currentSymbol) {
            this.showError('Search for a stock first');
            return;
        }
        
        const targetPrice = prompt(`Enter target price for ${this.currentSymbol} (optional):`);
        const payload = { symbol: this.currentSymbol };
        
        if (targetPrice && !isNaN(parseFloat(targetPrice))) {
            payload.target_price = parseFloat(targetPrice);
        }
        
        fetch('/api/watchlist', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                alert(data.message);
                this.loadWatchlist();
            }
        })
        .catch(error => {
            console.error('Watchlist add error:', error);
            alert('Failed to add to watchlist');
        });
    }
    
    removeFromWatchlist(symbol) {
        if (!confirm(`Remove ${symbol} from watchlist?`)) return;
        
        fetch(`/api/watchlist/${symbol}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    this.loadWatchlist();
                }
            })
            .catch(error => {
                console.error('Watchlist remove error:', error);
                alert('Failed to remove from watchlist');
            });
    }
    
    addToPortfolio() {
        if (!this.currentSymbol) {
            this.showError('Search for a stock first');
            return;
        }
        
        const shares = prompt(`Enter number of shares for ${this.currentSymbol}:`);
        if (!shares || isNaN(parseFloat(shares))) {
            alert('Invalid number of shares');
            return;
        }
        
        const price = prompt(`Enter purchase price per share:`);
        if (!price || isNaN(parseFloat(price))) {
            alert('Invalid price');
            return;
        }
        
        const notes = prompt('Enter notes (optional):') || '';
        
        const payload = {
            symbol: this.currentSymbol,
            shares: parseFloat(shares),
            price: parseFloat(price),
            notes: notes
        };
        
        fetch('/api/portfolio', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                alert(data.message);
                this.loadPortfolio();
            }
        })
        .catch(error => {
            console.error('Portfolio add error:', error);
            alert('Failed to add to portfolio');
        });
    }
    
    cleanup() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Initialize dashboard
const dashboard = new StockDashboard();

// Cleanup on page unload
window.addEventListener('beforeunload', () => dashboard.cleanup());