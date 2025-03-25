/**
 * HiramAbiff Yield Dashboard
 * Main Dashboard JavaScript
 */

// Main dashboard class to handle all dashboard functionality
class Dashboard {
    constructor() {
        // Dashboard state
        this.currentView = 'dashboard';
        this.filters = {
            chain: '',
            project: '',
            minTvl: 0,
            minApy: 0,
            maxRisk: 10,
            limit: 20,
            sortBy: 'apy',
            sortDirection: 'desc'
        };
        this.portfolioTimeframe = '1y';
        this.marketTimeframe = '1m';
        this.darkMode = false;
        
        // Cache for data
        this.opportunitiesCache = {};
        this.dashboardData = null;
        this.portfolioData = null;
        this.marketData = null;
        
        // Chart instances
        this.portfolioChart = null;
        this.marketTvlChart = null;
        this.marketApyChart = null;
        this.riskChart = null;
        
        // Initialize dashboard
        this.init();
    }
    
    // Initialize dashboard
    init() {
        // Setup event listeners and UI interactions
        this.setupNavigation();
        this.setupDarkMode();
        this.setupWalletConnection();
        this.setupFiltering();
        
        // Load initial data
        this.loadInitialData();
        
        // Check URL parameters for specific view
        const view = this.getUrlParameter('view');
        if (view) {
            this.navigateToView(view);
        }
    }
    
    // Setup navigation between dashboard views
    setupNavigation() {
        // Handle navbar navigation
        document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = link.getAttribute('href').replace('/', '');
                this.navigateToView(view || 'dashboard');
            });
        });
        
        // Handle other navigation links
        document.querySelectorAll('[data-navigate]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = link.getAttribute('data-navigate');
                this.navigateToView(view);
            });
        });
    }
    
    // Navigate to a specific view
    navigateToView(view) {
        // Hide all views
        document.querySelectorAll('.dashboard-view').forEach(element => {
            element.classList.add('d-none');
        });
        
        // Show selected view
        const viewElement = document.getElementById(`${view}-view`);
        if (viewElement) {
            viewElement.classList.remove('d-none');
            
            // Update active nav item
            document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href').replace('/', '') === view || 
                    (link.getAttribute('href') === '/' && view === 'dashboard')) {
                    link.classList.add('active');
                }
            });
            
            // Update URL
            this.setUrlParameters({ view: view === 'dashboard' ? null : view });
            
            // Update current view
            this.currentView = view;
            
            // Load view-specific data
            this.loadViewData(view);
        }
    }
    
    // Load data specific to a view
    loadViewData(view) {
        switch (view) {
            case 'dashboard':
            case '':
                this.loadDashboardData();
                this.loadTopOpportunities();
                this.generateInsights();
                break;
                
            case 'market':
                this.loadMarketData();
                break;
                
            case 'portfolio':
                this.loadPortfolioData();
                break;
                
            case 'staking':
                this.loadStakingData();
                break;
        }
    }
    
    // Setup dark mode toggle
    setupDarkMode() {
        const darkModeToggle = document.getElementById('darkModeToggle');
        if (darkModeToggle) {
            // Check saved preference
            const darkModePreference = this.getCookie('darkMode');
            if (darkModePreference === 'true') {
                this.enableDarkMode();
                darkModeToggle.checked = true;
            }
            
            // Handle toggle change
            darkModeToggle.addEventListener('change', () => {
                if (darkModeToggle.checked) {
                    this.enableDarkMode();
                    this.setCookie('darkMode', 'true', 365);
                } else {
                    this.disableDarkMode();
                    this.setCookie('darkMode', 'false', 365);
                }
                
                // Update charts if they exist
                this.updateChartsTheme();
            });
        }
    }
    
    // Enable dark mode
    enableDarkMode() {
        document.body.classList.add('dark-mode');
        this.darkMode = true;
    }
    
    // Disable dark mode
    disableDarkMode() {
        document.body.classList.remove('dark-mode');
        this.darkMode = false;
    }
    
    // Update charts theme based on dark mode
    updateChartsTheme() {
        const chartTheme = this.darkMode ? 
            { color: '#f8f9fa', gridColor: '#444', axisColor: '#999' } : 
            { color: '#343a40', gridColor: '#ddd', axisColor: '#666' };
        
        // Update each chart with the theme
        if (this.portfolioChart) {
            this.portfolioChart.options.scales.x.ticks.color = chartTheme.color;
            this.portfolioChart.options.scales.y.ticks.color = chartTheme.color;
            this.portfolioChart.options.scales.x.grid.color = chartTheme.gridColor;
            this.portfolioChart.options.scales.y.grid.color = chartTheme.gridColor;
            this.portfolioChart.update();
        }
        
        if (this.marketTvlChart) {
            this.marketTvlChart.options.scales.x.ticks.color = chartTheme.color;
            this.marketTvlChart.options.scales.y.ticks.color = chartTheme.color;
            this.marketTvlChart.options.scales.x.grid.color = chartTheme.gridColor;
            this.marketTvlChart.options.scales.y.grid.color = chartTheme.gridColor;
            this.marketTvlChart.update();
        }
        
        if (this.marketApyChart) {
            this.marketApyChart.options.scales.x.ticks.color = chartTheme.color;
            this.marketApyChart.options.scales.y.ticks.color = chartTheme.color;
            this.marketApyChart.options.scales.x.grid.color = chartTheme.gridColor;
            this.marketApyChart.options.scales.y.grid.color = chartTheme.gridColor;
            this.marketApyChart.update();
        }
        
        if (this.riskChart) {
            this.riskChart.options.plugins.legend.labels.color = chartTheme.color;
            this.riskChart.update();
        }
    }
    
    // Setup wallet connection
    setupWalletConnection() {
        // Wallet connection status is handled by wallet.js
        // Here we set up listeners for wallet events
        
        // Handle wallet connected event
        document.addEventListener('walletConnected', (e) => {
            this.loadWalletData();
        });
        
        // Handle wallet disconnected event
        document.addEventListener('walletDisconnected', () => {
            // Update UI for wallet disconnected state
            this.updateWalletDisconnectedUI();
        });
        
        // Handle wallet data loaded event
        document.addEventListener('walletDataLoaded', (e) => {
            // Update UI with wallet data
            this.updateWalletUI(e.detail);
        });
    }
    
    // Update UI with wallet data
    updateWalletUI(walletData) {
        // Update wallet section in dashboard view
        const walletSection = document.getElementById('wallet-section');
        if (walletSection) {
            walletSection.classList.remove('d-none');
            
            // Update wallet balance
            const walletBalance = document.getElementById('wallet-balance');
            if (walletBalance) {
                walletBalance.textContent = '$' + formatNumber(walletData.balance);
            }
            
            // Additional wallet UI updates handled by wallet.js
        }
    }
    
    // Update UI for wallet disconnected state
    updateWalletDisconnectedUI() {
        // Hide wallet section or show connect prompt
        const walletSection = document.getElementById('wallet-section');
        if (walletSection) {
            walletSection.classList.add('d-none');
        }
        
        const walletConnectPrompt = document.getElementById('wallet-connect-prompt');
        if (walletConnectPrompt) {
            walletConnectPrompt.classList.remove('d-none');
        }
    }
    
    // Setup filtering and sorting
    setupFiltering() {
        // Chain filter
        const chainFilter = document.getElementById('chainFilter');
        if (chainFilter) {
            chainFilter.addEventListener('change', () => {
                this.filters.chain = chainFilter.value;
                this.loadOpportunities();
            });
        }
        
        // Project filter
        const projectFilter = document.getElementById('projectFilter');
        if (projectFilter) {
            projectFilter.addEventListener('change', () => {
                this.filters.project = projectFilter.value;
                this.loadOpportunities();
            });
        }
        
        // Min TVL filter
        const minTvlFilter = document.getElementById('minTvlFilter');
        if (minTvlFilter) {
            minTvlFilter.addEventListener('change', () => {
                this.filters.minTvl = parseFloat(minTvlFilter.value) || 0;
                this.loadOpportunities();
            });
        }
        
        // Min APY filter
        const minApyFilter = document.getElementById('minApyFilter');
        if (minApyFilter) {
            minApyFilter.addEventListener('change', () => {
                this.filters.minApy = parseFloat(minApyFilter.value) || 0;
                this.loadOpportunities();
            });
        }
        
        // Max Risk filter
        const maxRiskFilter = document.getElementById('maxRiskFilter');
        if (maxRiskFilter) {
            maxRiskFilter.addEventListener('change', () => {
                this.filters.maxRisk = parseFloat(maxRiskFilter.value) || 10;
                this.loadOpportunities();
            });
        }
        
        // Limit filter
        const limitFilter = document.getElementById('limitFilter');
        if (limitFilter) {
            limitFilter.addEventListener('change', () => {
                this.filters.limit = parseInt(limitFilter.value) || 20;
                this.loadOpportunities();
            });
        }
        
        // Sort options
        const sortOptions = document.querySelectorAll('[data-sort]');
        sortOptions.forEach(option => {
            option.addEventListener('click', () => {
                const sortBy = option.getAttribute('data-sort');
                
                // Toggle direction if same sort field
                if (this.filters.sortBy === sortBy) {
                    this.filters.sortDirection = this.filters.sortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    this.filters.sortBy = sortBy;
                    this.filters.sortDirection = 'desc'; // Default to descending
                }
                
                // Update active sort
                sortOptions.forEach(opt => opt.classList.remove('active'));
                option.classList.add('active');
                
                // Show sort direction
                option.querySelector('i').className = 
                    this.filters.sortDirection === 'asc' ? 'fas fa-sort-up ms-1' : 'fas fa-sort-down ms-1';
                
                this.loadOpportunities();
            });
        });
        
        // Portfolio timeframe
        const timeframeButtons = document.querySelectorAll('[data-timeframe]');
        timeframeButtons.forEach(button => {
            button.addEventListener('click', () => {
                const timeframe = button.getAttribute('data-timeframe');
                this.portfolioTimeframe = timeframe;
                
                // Update active button
                timeframeButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Update portfolio chart
                this.loadPortfolioPerformance();
            });
        });
        
        // Market timeframe
        const marketTimeframeButtons = document.querySelectorAll('[data-market-timeframe]');
        marketTimeframeButtons.forEach(button => {
            button.addEventListener('click', () => {
                const timeframe = button.getAttribute('data-market-timeframe');
                this.marketTimeframe = timeframe;
                
                // Update active button
                marketTimeframeButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Update market charts
                this.updateMarketTimeframe(timeframe);
            });
        });
    }
    
    // Load initial data
    loadInitialData() {
        // Check wallet connection status
        this.loadWalletData();
        
        // Load dashboard data
        this.loadDashboardData();
        
        // Load top opportunities for dashboard
        this.loadTopOpportunities();
        
        // Generate AI insights
        this.generateInsights();
    }
    
    // Load wallet data
    async loadWalletData() {
        try {
            const response = await fetch('/api/wallet/status');
            const data = await response.json();
            
            if (data.connected) {
                // Update UI for connected wallet
                const walletAddress = document.getElementById('walletAddress');
                if (walletAddress) {
                    walletAddress.textContent = truncateAddress(data.address);
                }
                
                // Show wallet section, hide connect prompt
                const connectWalletBtn = document.getElementById('connectWalletBtn');
                if (connectWalletBtn) {
                    connectWalletBtn.classList.add('d-none');
                }
                
                const walletInfo = document.getElementById('walletInfo');
                if (walletInfo) {
                    walletInfo.classList.remove('d-none');
                }
                
                const walletSection = document.getElementById('wallet-section');
                if (walletSection) {
                    walletSection.classList.remove('d-none');
                }
                
                const walletConnectPrompt = document.getElementById('wallet-connect-prompt');
                if (walletConnectPrompt) {
                    walletConnectPrompt.classList.add('d-none');
                }
                
                // Load wallet tokens and assets
                const walletDataResponse = await fetch('/api/wallet/data');
                const walletData = await walletDataResponse.json();
                
                if (!walletData.error) {
                    // Update wallet tokens list
                    const walletTokens = document.getElementById('wallet-tokens-list');
                    if (walletTokens && walletData.tokens) {
                        walletTokens.innerHTML = '';
                        
                        if (walletData.tokens.length === 0) {
                            walletTokens.innerHTML = `
                                <div class="text-center text-muted py-3">
                                    <p>No tokens found in wallet</p>
                                </div>
                            `;
                        } else {
                            walletData.tokens.forEach(token => {
                                const tokenItem = document.createElement('div');
                                tokenItem.className = 'token-item d-flex justify-content-between align-items-center mb-2';
                                
                                const priceChangeClass = token.price_change_24h >= 0 ? 'text-success' : 'text-danger';
                                const priceChangeIcon = token.price_change_24h >= 0 ? 'fa-caret-up' : 'fa-caret-down';
                                
                                tokenItem.innerHTML = `
                                    <div class="d-flex align-items-center">
                                        <img src="${token.logo_url || 'https://via.placeholder.com/24'}" alt="${token.symbol}" width="24" height="24" class="token-icon me-2">
                                        <div>
                                            <div class="fw-bold">${token.symbol}</div>
                                            <div class="text-muted small">${token.name}</div>
                                        </div>
                                    </div>
                                    <div class="text-end">
                                        <div>${formatNumber(token.amount)} ${token.symbol}</div>
                                        <div class="d-flex justify-content-end align-items-center">
                                            <span class="text-muted small me-2">$${formatNumber(token.value_usd)}</span>
                                            <span class="${priceChangeClass} small">
                                                <i class="fas ${priceChangeIcon}"></i> ${Math.abs(token.price_change_24h).toFixed(2)}%
                                            </span>
                                        </div>
                                    </div>
                                `;
                                
                                walletTokens.appendChild(tokenItem);
                            });
                        }
                    }
                    
                    // Update staked assets
                    const walletStaked = document.getElementById('wallet-staked-list');
                    if (walletStaked && walletData.staked) {
                        walletStaked.innerHTML = '';
                        
                        if (walletData.staked.length === 0) {
                            walletStaked.innerHTML = `
                                <div class="text-center text-muted py-3">
                                    <p>No staked assets found</p>
                                </div>
                            `;
                        } else {
                            walletData.staked.forEach(asset => {
                                const assetItem = document.createElement('div');
                                assetItem.className = 'token-item d-flex justify-content-between align-items-center mb-2';
                                
                                assetItem.innerHTML = `
                                    <div class="d-flex align-items-center">
                                        <img src="${asset.logo_url || 'https://via.placeholder.com/24'}" alt="${asset.symbol}" width="24" height="24" class="token-icon me-2">
                                        <div>
                                            <div class="fw-bold">${asset.symbol}</div>
                                            <div class="text-muted small">${asset.protocol}</div>
                                        </div>
                                    </div>
                                    <div class="text-end">
                                        <div>${formatNumber(asset.amount)} ${asset.symbol}</div>
                                        <div class="d-flex justify-content-end align-items-center">
                                            <span class="text-muted small me-2">$${formatNumber(asset.value_usd)}</span>
                                            <span class="text-success small">
                                                <i class="fas fa-chart-line"></i> ${asset.apy.toFixed(2)}%
                                            </span>
                                        </div>
                                    </div>
                                `;
                                
                                walletStaked.appendChild(assetItem);
                            });
                        }
                    }
                    
                    // Update wallet summary
                    const walletBalance = document.getElementById('wallet-balance');
                    if (walletBalance) {
                        const totalBalance = walletData.tokens.reduce((sum, token) => sum + token.value_usd, 0);
                        walletBalance.textContent = '$' + formatNumber(totalBalance);
                    }
                    
                    const walletStakedValue = document.getElementById('wallet-staked-value');
                    if (walletStakedValue) {
                        const totalStaked = walletData.staked.reduce((sum, asset) => sum + asset.value_usd, 0);
                        walletStakedValue.textContent = '$' + formatNumber(totalStaked);
                    }
                    
                    const walletYield = document.getElementById('wallet-yield');
                    if (walletYield) {
                        const totalYield = walletData.staked.reduce((sum, asset) => sum + (asset.value_usd * asset.apy / 100), 0);
                        walletYield.textContent = '$' + formatNumber(totalYield) + '/yr';
                    }
                }
            } else {
                // Update UI for disconnected wallet
                this.updateWalletDisconnectedUI();
            }
        } catch (error) {
            console.error('Error loading wallet data:', error);
        }
    }
    
    // Get URL parameter value
    getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        const results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }
    
    // Set URL parameters
    setUrlParameters(params) {
        const url = new URL(window.location);
        
        // Reset parameters if empty params object
        if (Object.keys(params).length === 0) {
            window.history.pushState({}, '', url.pathname);
            return;
        }
        
        // Update or add each parameter
        Object.keys(params).forEach(key => {
            if (params[key] === null || params[key] === undefined || params[key] === '') {
                url.searchParams.delete(key);
            } else {
                url.searchParams.set(key, params[key]);
            }
        });
        
        window.history.pushState({}, '', url);
    }
    
    // Get cookie value
    getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }
    
    // Set cookie
    setCookie(name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/";
    }
    
    // Generate insights using the API
    async generateInsights() {
        try {
            const insightsContainer = document.getElementById('insights-container');
            if (!insightsContainer) return;
            
            insightsContainer.innerHTML = `
                <div class="text-center py-4">
                    <div class="loading-spinner mb-3"></div>
                    <p class="text-muted">Generating insights...</p>
                </div>
            `;
            
            const response = await fetch('/api/generate-insights');
            const data = await response.json();
            
            if (data.error) {
                insightsContainer.innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Error generating insights: ${data.error}
                    </div>
                `;
                return;
            }
            
            // Check if there are any insights
            if (!data.insights || data.insights.length === 0) {
                insightsContainer.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-info-circle text-muted fa-3x mb-3"></i>
                        <p class="text-muted">No insights available at this time.</p>
                    </div>
                `;
                return;
            }
            
            // Render insights
            insightsContainer.innerHTML = `
                <div class="mb-3">
                    <p class="mb-3">${data.summary || 'Here are some insights based on market data and your portfolio:'}</p>
                    <div id="insights-list"></div>
                </div>
            `;
            
            const insightsList = document.getElementById('insights-list');
            
            data.insights.forEach(insight => {
                const insightCard = document.createElement('div');
                insightCard.className = 'card mb-3';
                
                // Determine icon based on insight type
                let icon = 'fa-lightbulb';
                let iconClass = 'text-warning';
                
                if (insight.type === 'trend') {
                    icon = 'fa-chart-line';
                    iconClass = 'text-primary';
                } else if (insight.type === 'opportunity') {
                    icon = 'fa-gem';
                    iconClass = 'text-success';
                } else if (insight.type === 'warning') {
                    icon = 'fa-exclamation-triangle';
                    iconClass = 'text-danger';
                } else if (insight.type === 'portfolio') {
                    icon = 'fa-briefcase';
                    iconClass = 'text-info';
                }
                
                insightCard.innerHTML = `
                    <div class="card-body">
                        <div class="d-flex">
                            <div class="me-3">
                                <i class="fas ${icon} fa-2x ${iconClass}"></i>
                            </div>
                            <div>
                                <h6 class="fw-bold">${insight.title}</h6>
                                <p>${insight.content}</p>
                            </div>
                        </div>
                    </div>
                `;
                
                insightsList.appendChild(insightCard);
            });
        } catch (error) {
            console.error('Error generating insights:', error);
            const insightsContainer = document.getElementById('insights-container');
            if (insightsContainer) {
                insightsContainer.innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Error generating insights. Please try again.
                    </div>
                `;
            }
        }
    }
}

// Initialize dashboard when document is ready
document.addEventListener('DOMContentLoaded', () => {
    // Create global dashboard instance
    window.dashboardApp = new Dashboard();
    
    console.log('HiramAbiff Yield Dashboard initialized');
});
        