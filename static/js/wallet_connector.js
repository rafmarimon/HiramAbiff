/**
 * Wallet Connector for HiramAbiff
 * 
 * This script provides functionality for connecting to Solana wallets like
 * Phantom and Solflare. It handles wallet connection, data retrieval, and
 * transaction simulation.
 */

// Define the HiramAbiff namespace
window.hiramWallet = window.hiramWallet || {};

// Wallet connector initialization
(function() {
    // Keep track of connection state
    let connectedWallet = null;
    let connectedWalletType = null;
    
    /**
     * Check if Phantom wallet is installed
     * @returns {boolean} True if Phantom is installed, false otherwise
     */
    function isPhantomInstalled() {
        const provider = window.solana;
        return provider && provider.isPhantom;
    }
    
    /**
     * Check if Solflare wallet is installed
     * @returns {boolean} True if Solflare is installed, false otherwise
     */
    function isSolflareInstalled() {
        const provider = window.solflare;
        return provider && provider.isSolflare;
    }
    
    /**
     * Connect to Phantom wallet
     * @returns {Promise<Object>} Connection result
     */
    hiramWallet.connectPhantom = async function() {
        if (!isPhantomInstalled()) {
            return JSON.stringify({
                success: false,
                message: "Phantom wallet is not installed. Please install the Phantom browser extension.",
                walletType: "phantom"
            });
        }
        
        try {
            const provider = window.solana;
            
            // Check if already connected
            if (connectedWallet && connectedWalletType === "phantom") {
                return JSON.stringify({
                    success: true,
                    publicKey: connectedWallet,
                    walletType: "phantom",
                    message: "Already connected to Phantom wallet."
                });
            }
            
            // Connect to wallet
            // In a real implementation, this would be:
            // const resp = await provider.connect();
            // const publicKey = resp.publicKey.toString();
            
            // For demo, we'll simulate a successful connection
            // with a mock Solana public key
            const mockPublicKey = "4Zw8jUGuvHwJZqgyniVa9M3VTsNDRzTHFRFPsGX2cLdH";
            
            // Store connection info
            connectedWallet = mockPublicKey;
            connectedWalletType = "phantom";
            
            console.log("Connected to Phantom wallet:", mockPublicKey);
            
            return JSON.stringify({
                success: true,
                publicKey: mockPublicKey,
                walletType: "phantom"
            });
        } catch (err) {
            console.error("Error connecting to Phantom wallet:", err);
            return JSON.stringify({
                success: false,
                message: `Error connecting to Phantom wallet: ${err.message}`,
                walletType: "phantom"
            });
        }
    };
    
    /**
     * Connect to Solflare wallet
     * @returns {Promise<Object>} Connection result
     */
    hiramWallet.connectSolflare = async function() {
        if (!isSolflareInstalled()) {
            return JSON.stringify({
                success: false,
                message: "Solflare wallet is not installed. Please install the Solflare browser extension.",
                walletType: "solflare"
            });
        }
        
        try {
            const provider = window.solflare;
            
            // Check if already connected
            if (connectedWallet && connectedWalletType === "solflare") {
                return JSON.stringify({
                    success: true,
                    publicKey: connectedWallet,
                    walletType: "solflare",
                    message: "Already connected to Solflare wallet."
                });
            }
            
            // Connect to wallet
            // In a real implementation, this would be:
            // const resp = await provider.connect();
            // const publicKey = resp.publicKey.toString();
            
            // For demo, we'll simulate a successful connection
            // with a mock Solana public key
            const mockPublicKey = "7ZnH5t9kGBwXUkDmfcMKpMD1gpLMXHBg5ui3NBgHWdUP";
            
            // Store connection info
            connectedWallet = mockPublicKey;
            connectedWalletType = "solflare";
            
            console.log("Connected to Solflare wallet:", mockPublicKey);
            
            return JSON.stringify({
                success: true,
                publicKey: mockPublicKey,
                walletType: "solflare"
            });
        } catch (err) {
            console.error("Error connecting to Solflare wallet:", err);
            return JSON.stringify({
                success: false,
                message: `Error connecting to Solflare wallet: ${err.message}`,
                walletType: "solflare"
            });
        }
    };
    
    /**
     * Disconnect wallet
     * @returns {Promise<Object>} Disconnection result
     */
    hiramWallet.disconnectWallet = async function() {
        try {
            // In a real implementation, this would disconnect from the provider
            // if (connectedWalletType === "phantom") {
            //     await window.solana.disconnect();
            // } else if (connectedWalletType === "solflare") {
            //     await window.solflare.disconnect();
            // }
            
            // Reset connection state
            const previousWallet = connectedWallet;
            const previousType = connectedWalletType;
            
            connectedWallet = null;
            connectedWalletType = null;
            
            console.log(`Disconnected from ${previousType} wallet:`, previousWallet);
            
            return JSON.stringify({
                success: true,
                message: `Disconnected from ${previousType} wallet.`
            });
        } catch (err) {
            console.error("Error disconnecting wallet:", err);
            return JSON.stringify({
                success: false,
                message: `Error disconnecting wallet: ${err.message}`
            });
        }
    };
    
    /**
     * Check if wallet is connected
     * @returns {boolean} True if wallet is connected, false otherwise
     */
    hiramWallet.isConnected = function() {
        return connectedWallet !== null;
    };
    
    /**
     * Get connected wallet type
     * @returns {string|null} Wallet type or null if not connected
     */
    hiramWallet.getWalletType = function() {
        return connectedWalletType;
    };
    
    /**
     * Get connected wallet address
     * @returns {string|null} Wallet address or null if not connected
     */
    hiramWallet.getWalletAddress = function() {
        return connectedWallet;
    };
    
    /**
     * Simulate a transaction
     * @param {Object} txData Transaction data
     * @returns {Promise<Object>} Transaction result
     */
    hiramWallet.simulateTransaction = async function(txData) {
        if (!connectedWallet) {
            return JSON.stringify({
                success: false,
                message: "No wallet connected. Please connect a wallet first."
            });
        }
        
        try {
            console.log("Simulating transaction:", txData);
            
            // In a real implementation, this would create and send a transaction
            // For demo, we'll simulate a successful transaction
            const mockTxId = "5wqG7yzaGfSYJhKbbKsfY2RBBjP6aQ5TzXfuEvMEjU8HzJnc7Wd8K2ftoKDcgCj4XzPBEgLSLdZmjpU1p3R9JLv";
            
            // Simulate network delay
            await new Promise(resolve => setTimeout(resolve, 500));
            
            return JSON.stringify({
                success: true,
                txId: mockTxId,
                message: "Transaction simulated successfully."
            });
        } catch (err) {
            console.error("Error simulating transaction:", err);
            return JSON.stringify({
                success: false,
                message: `Error simulating transaction: ${err.message}`
            });
        }
    };
    
    /**
     * Get token balances
     * @returns {Promise<Object>} Token balances
     */
    hiramWallet.getTokenBalances = async function() {
        if (!connectedWallet) {
            return JSON.stringify({
                success: false,
                message: "No wallet connected. Please connect a wallet first."
            });
        }
        
        try {
            console.log("Getting token balances for:", connectedWallet);
            
            // In a real implementation, this would query token balances
            // For demo, we'll return mock balances
            const mockBalances = {
                SOL: {
                    amount: 5.25,
                    usdValue: 787.56
                },
                USDC: {
                    amount: 250.75,
                    usdValue: 250.75
                },
                HIRAM: {
                    amount: 1000,
                    usdValue: 1250
                }
            };
            
            // Simulate network delay
            await new Promise(resolve => setTimeout(resolve, 300));
            
            return JSON.stringify({
                success: true,
                balances: mockBalances
            });
        } catch (err) {
            console.error("Error getting token balances:", err);
            return JSON.stringify({
                success: false,
                message: `Error getting token balances: ${err.message}`
            });
        }
    };
    
    // Log initialization
    console.log("HiramAbiff wallet connector initialized");
})();

// For testing
window.testWalletConnection = async function() {
    console.log("Testing wallet connection...");
    
    if (isPhantomInstalled()) {
        console.log("Phantom is installed");
        const result = await hiramWallet.connectPhantom();
        console.log("Phantom connection result:", result);
    } else {
        console.log("Phantom is not installed");
    }
    
    if (isSolflareInstalled()) {
        console.log("Solflare is installed");
        const result = await hiramWallet.connectSolflare();
        console.log("Solflare connection result:", result);
    } else {
        console.log("Solflare is not installed");
    }
}; 