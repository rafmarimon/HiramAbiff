/**
 * HiramAbiff Yield Dashboard
 * Wallet Integration JavaScript
 */

// Wallet class to handle wallet connections and interactions
class WalletIntegration {
    constructor() {
        this.connected = false;
        this.address = null;
        this.walletType = null;
        this.balance = 0;
        this.tokens = [];
        
        // Initialize wallet connection
        this.init();
    }
    
    // Initialize wallet integration
    init() {
        // Check for existing wallet connection in session
        this.checkExistingConnection();
        
        // Set up event listeners
        this.setupEventListeners();
    }
    
    // Check if wallet is already connected
    checkExistingConnection() {
        fetch('/api/wallet/status')
            .then(response => response.json())
            .then(data => {
                if (data.connected) {
                    this.connected = true;
                    this.address = data.address;
                    this.walletType = data.wallet_type;
                    
                    // Update UI
                    this.updateUI();
                    
                    // Fetch wallet data
                    this.fetchWalletData();
                }
            })
            .catch(error => {
                console.error('Error checking wallet connection:', error);
            });
    }
    
    // Set up event listeners
    setupEventListeners() {
        // Handle connect wallet button
        const connectButtons = document.querySelectorAll('[id^="connectWalletBtn"]');
        connectButtons.forEach(button => {
            button.addEventListener('click', this.showWalletOptions.bind(this));
        });
        
        // Handle wallet disconnect
        const disconnectBtn = document.getElementById('disconnectWalletBtn');
        if (disconnectBtn) {
            disconnectBtn.addEventListener('click', this.disconnectWallet.bind(this));
        }
    }
    
    // Show wallet connection options
    showWalletOptions() {
        // Create modal with wallet options
        const modalHtml = `
            <div class="modal fade" id="walletModal" tabindex="-1" aria-labelledby="walletModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="walletModalLabel">Connect Wallet</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="d-flex flex-column">
                                <button class="btn btn-outline-primary mb-3 wallet-option" data-wallet="phantom">
                                    <img src="https://phantom.app/img/logo.png" alt="Phantom" width="24" height="24" class="me-2">
                                    Phantom
                                </button>
                                <button class="btn btn-outline-primary mb-3 wallet-option" data-wallet="solflare">
                                    <img src="https://solflare.com/assets/logo.svg" alt="Solflare" width="24" height="24" class="me-2">
                                    Solflare
                                </button>
                                <button class="btn btn-outline-primary wallet-option" data-wallet="mock">
                                    <i class="fas fa-wallet me-2"></i>
                                    Mock Wallet (Demo)
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to document
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHtml;
        document.body.appendChild(modalContainer);
        
        // Initialize modal
        const walletModal = new bootstrap.Modal(document.getElementById('walletModal'));
        walletModal.show();
        
        // Add event listeners to wallet options
        document.querySelectorAll('.wallet-option').forEach(option => {
            option.addEventListener('click', (event) => {
                const walletType = event.currentTarget.getAttribute('data-wallet');
                this.connectWallet(walletType);
                walletModal.hide();
            });
        });
        
        // Clean up modal when hidden
        document.getElementById('walletModal').addEventListener('hidden.bs.modal', function () {
            this.remove();
        });
    }
    
    // Connect to selected wallet
    connectWallet(walletType) {
        // Show loading indicator
        this.showLoadingIndicator();
        
        // Call API to connect wallet
        fetch('/api/wallet/connect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                wallet_type: walletType
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            this.hideLoadingIndicator();
            
            if (data.success) {
                this.connected = true;
                this.address = data.address;
                this.walletType = walletType;
                
                // Show success toast
                this.showToast('Success', `Connected to ${walletType} wallet`, 'success');
                
                // Update UI
                this.updateUI();
                
                // Fetch wallet data
                this.fetchWalletData();
                
                // Trigger wallet connected event
                const event = new CustomEvent('walletConnected', {
                    detail: {
                        address: this.address,
                        walletType: this.walletType
                    }
                });
                document.dispatchEvent(event);
            } else {
                // Show error toast
                this.showToast('Error', data.error || 'Failed to connect wallet', 'danger');
            }
        })
        .catch(error => {
            // Hide loading indicator
            this.hideLoadingIndicator();
            
            console.error('Error connecting wallet:', error);
            
            // Show error toast
            this.showToast('Error', 'Failed to connect wallet', 'danger');
        });
    }
    
    // Disconnect wallet
    disconnectWallet() {
        // Call API to disconnect wallet
        fetch('/api/wallet/disconnect', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.connected = false;
                this.address = null;
                this.walletType = null;
                this.balance = 0;
                this.tokens = [];
                
                // Show success toast
                this.showToast('Success', 'Wallet disconnected', 'success');
                
                // Update UI
                this.updateUI();
                
                // Trigger wallet disconnected event
                const event = new CustomEvent('walletDisconnected');
                document.dispatchEvent(event);
            } else {
                // Show error toast
                this.showToast('Error', data.error || 'Failed to disconnect wallet', 'danger');
            }
        })
        .catch(error => {
            console.error('Error disconnecting wallet:', error);
            
            // Show error toast
            this.showToast('Error', 'Failed to disconnect wallet', 'danger');
        });
    }
    
    // Fetch wallet data (tokens, transactions, etc.)
    fetchWalletData() {
        if (!this.connected) return;
        
        fetch('/api/wallet/data')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error fetching wallet data:', data.error);
                    return;
                }
                
                // Store wallet data
                this.tokens = data.tokens || [];
                this.staked = data.staked || [];
                this.transactions = data.transactions || [];
                this.staking = data.staking || {};
                this.fee_history = data.fee_history || [];
                
                // Calculate total balance
                this.balance = this.tokens.reduce((total, token) => total + (token.value_usd || 0), 0);
                
                // Update wallet UI
                this.updateWalletData();
                
                // Trigger wallet data loaded event
                const event = new CustomEvent('walletDataLoaded', {
                    detail: {
                        tokens: this.tokens,
                        staked: this.staked,
                        transactions: this.transactions,
                        staking: this.staking,
                        fee_history: this.fee_history,
                        balance: this.balance
                    }
                });
                document.dispatchEvent(event);
            })
            .catch(error => {
                console.error('Error fetching wallet data:', error);
            });
    }
    
    // Update UI based on connection status
    updateUI() {
        // Update nav buttons
        const connectBtns = document.querySelectorAll('[id^="connectWalletBtn"]');
        const walletInfo = document.getElementById('walletInfo');
        
        if (this.connected) {
            // Hide connect buttons
            connectBtns.forEach(btn => {
                btn.classList.add('d-none');
            });
            
            // Show wallet info
            if (walletInfo) {
                walletInfo.classList.remove('d-none');
                
                // Show truncated address
                const walletAddress = document.getElementById('walletAddress');
                if (walletAddress) {
                    const truncatedAddress = this.address.substring(0, 4) + '...' + this.address.substring(this.address.length - 4);
                    walletAddress.innerText = truncatedAddress;
                }
            }
            
            // Update wallet UI sections
            const walletConnectPrompt = document.getElementById('wallet-connect-prompt');
            const walletAssets = document.getElementById('wallet-assets');
            
            if (walletConnectPrompt && walletAssets) {
                walletConnectPrompt.classList.add('d-none');
                walletAssets.classList.remove('d-none');
            }
        } else {
            // Show connect buttons
            connectBtns.forEach(btn => {
                btn.classList.remove('d-none');
            });
            
            // Hide wallet info
            if (walletInfo) {
                walletInfo.classList.add('d-none');
            }
            
            // Update wallet UI sections
            const walletConnectPrompt = document.getElementById('wallet-connect-prompt');
            const walletAssets = document.getElementById('wallet-assets');
            
            if (walletConnectPrompt && walletAssets) {
                walletConnectPrompt.classList.remove('d-none');
                walletAssets.classList.add('d-none');
            }
        }
    }
    
    // Update wallet data in UI
    updateWalletData() {
        // Update balance
        const walletBalance = document.getElementById('wallet-balance');
        if (walletBalance) {
            walletBalance.innerText = '$' + this.formatNumber(this.balance);
        }
        
        // Update staked amount
        const walletStaked = document.getElementById('wallet-staked');
        if (walletStaked) {
            const stakedValue = this.staked.reduce((total, asset) => total + (asset.value_usd || 0), 0);
            walletStaked.innerText = '$' + this.formatNumber(stakedValue);
        }
        
        // Update annual yield
        const walletYield = document.getElementById('wallet-yield');
        if (walletYield) {
            const annualYield = this.staked.reduce((total, asset) => {
                return total + (asset.value_usd || 0) * (asset.apy || 0) / 100;
            }, 0);
            
            const yieldPercentage = (this.balance > 0) ? (annualYield / this.balance * 100) : 0;
            
            walletYield.innerText = '$' + this.formatNumber(annualYield) + 
                ' (' + yieldPercentage.toFixed(2) + '%)';
        }
        
        // Update tokens list
        const walletTokens = document.getElementById('wallet-tokens');
        if (walletTokens) {
            if (this.tokens.length === 0) {
                walletTokens.innerHTML = `
                    <div class="text-center text-muted">
                        <p>No assets found</p>
                    </div>
                `;
                return;
            }
            
            walletTokens.innerHTML = '';
            
            this.tokens.forEach(token => {
                const tokenItem = document.createElement('div');
                tokenItem.className = 'mb-3';
                
                const priceChangeClass = token.price_change_24h >= 0 ? 'text-success' : 'text-danger';
                const priceChangeIcon = token.price_change_24h >= 0 ? 'caret-up' : 'caret-down';
                
                tokenItem.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <div class="d-flex align-items-center">
                            <img src="${token.logo_url || 'https://via.placeholder.com/24'}" alt="${token.symbol}" width="24" height="24" class="me-2">
                            <span>${token.symbol}</span>
                        </div>
                        <span>${this.formatNumber(token.amount)}</span>
                    </div>
                    <div class="d-flex justify-content-between small">
                        <span class="text-muted">$${this.formatNumber(token.value_usd)}</span>
                        <span class="${priceChangeClass}">
                            <i class="fas fa-${priceChangeIcon}"></i> ${Math.abs(token.price_change_24h).toFixed(2)}%
                        </span>
                    </div>
                `;
                
                walletTokens.appendChild(tokenItem);
            });
        }
    }
    
    // Show loading indicator
    showLoadingIndicator() {
        // Create loading overlay
        const overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        overlay.style.display = 'flex';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        overlay.style.zIndex = '9999';
        
        // Create spinner
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        
        overlay.appendChild(spinner);
        document.body.appendChild(overlay);
    }
    
    // Hide loading indicator
    hideLoadingIndicator() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.remove();
        }
    }
    
    // Show toast notification
    showToast(title, message, type = 'info') {
        // Create toast container if not exists
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.id = toastId;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong>: ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Initialize and show toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 3000
        });
        bsToast.show();
        
        // Remove toast when hidden
        toast.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    }
    
    // Format number with commas and fixed decimal places
    formatNumber(number) {
        return parseFloat(number).toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
    
    // Get wallet tokens
    getTokens() {
        return this.tokens;
    }
    
    // Get staked assets
    getStakedAssets() {
        return this.staked;
    }
    
    // Get total balance
    getBalance() {
        return this.balance;
    }
    
    // Get wallet address
    getAddress() {
        return this.address;
    }
    
    // Check if wallet is connected
    isConnected() {
        return this.connected;
    }
    
    // Stake HIRAM tokens
    stakeHiram(amount) {
        if (!this.connected) {
            this.showToast('Error', 'Wallet not connected', 'danger');
            return Promise.reject(new Error('Wallet not connected'));
        }
        
        return fetch('/api/wallet/stake-hiram', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                amount: amount
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                this.showToast('Error', data.error, 'danger');
                return Promise.reject(new Error(data.error));
            }
            
            // Show success toast
            this.showToast('Success', `Staked ${amount} HIRAM tokens`, 'success');
            
            // Refresh wallet data
            this.fetchWalletData();
            
            return data;
        })
        .catch(error => {
            console.error('Error staking HIRAM:', error);
            this.showToast('Error', 'Failed to stake HIRAM tokens', 'danger');
            return Promise.reject(error);
        });
    }
    
    // Unstake HIRAM tokens
    unstakeHiram(amount) {
        if (!this.connected) {
            this.showToast('Error', 'Wallet not connected', 'danger');
            return Promise.reject(new Error('Wallet not connected'));
        }
        
        return fetch('/api/wallet/unstake-hiram', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                amount: amount
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                this.showToast('Error', data.error, 'danger');
                return Promise.reject(new Error(data.error));
            }
            
            // Show success toast
            this.showToast('Success', `Unstaked ${amount} HIRAM tokens`, 'success');
            
            // Refresh wallet data
            this.fetchWalletData();
            
            return data;
        })
        .catch(error => {
            console.error('Error unstaking HIRAM:', error);
            this.showToast('Error', 'Failed to unstake HIRAM tokens', 'danger');
            return Promise.reject(error);
        });
    }
}

// Initialize wallet integration
const wallet = new WalletIntegration(); 