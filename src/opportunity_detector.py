#!/usr/bin/env python
"""
Opportunity Detector for HiramAbiff

This module analyzes yield data from various sources and identifies the best
opportunities based on configurable criteria like APY, TVL, and risk factors.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime

from src.data_aggregator import data_aggregator

# Risk scoring constants
MIN_TVL_THRESHOLD = 100000  # $100K minimum TVL
HIGH_TVL_THRESHOLD = 10000000  # $10M considered high TVL (lower risk)
MIN_APY_THRESHOLD = 5.0  # 5% minimum APY to consider
SUSPICIOUS_APY_THRESHOLD = 100.0  # APYs over 100% flagged as potentially risky

class OpportunityDetector:
    """
    Analyzes and ranks yield farming opportunities based on various criteria.
    """
    
    def __init__(
        self,
        min_apy: float = MIN_APY_THRESHOLD,
        min_tvl: float = MIN_TVL_THRESHOLD,
        suspicious_apy: float = SUSPICIOUS_APY_THRESHOLD,
        chain: str = "solana"
    ):
        """
        Initialize the opportunity detector.
        
        Args:
            min_apy: Minimum APY to consider (percentage)
            min_tvl: Minimum TVL to consider (USD)
            suspicious_apy: APY threshold considered suspiciously high
            chain: Blockchain to focus on
        """
        self.min_apy = min_apy
        self.min_tvl = min_tvl
        self.suspicious_apy = suspicious_apy
        self.chain = chain
        
        # Cache for analyzed opportunities
        self.opportunities = []
        self.last_update = None
    
    def calculate_risk_score(self, opportunity: Dict[str, Any]) -> float:
        """
        Calculate a risk score for an opportunity (0-100, lower is better).
        
        This uses a simple heuristic combining TVL, APY, and protocol factors.
        
        Args:
            opportunity: The yield opportunity data
            
        Returns:
            float: Risk score (0-100)
        """
        base_score = 50  # Start in the middle
        
        # Get key metrics, with fallbacks for missing data
        apy = opportunity.get("apy", 0)
        tvl = opportunity.get("tvlUsd", 0)
        
        # TVL factors (higher TVL = lower risk)
        if tvl >= HIGH_TVL_THRESHOLD:
            base_score -= 20  # Significant reduction for high TVL
        elif tvl >= MIN_TVL_THRESHOLD * 5:
            base_score -= 10  # Moderate reduction for decent TVL
        elif tvl < MIN_TVL_THRESHOLD:
            base_score += 20  # Significant increase for low TVL
        
        # APY factors (extremely high APY may indicate higher risk)
        if apy > self.suspicious_apy:
            base_score += min(40, (apy - self.suspicious_apy) / 10)  # Increase risk for very high APY
        
        # Protocol-specific adjustments (could be expanded)
        protocol = opportunity.get("project", "").lower()
        if protocol in ["raydium", "orca", "marinade", "solend"]:
            base_score -= 10  # Established protocols considered lower risk
        
        # Normalize score between 0-100
        return max(0, min(100, base_score))
    
    def calculate_opportunity_score(self, opportunity: Dict[str, Any]) -> float:
        """
        Calculate an overall opportunity score (0-100, higher is better).
        
        This balances reward (APY) with risk factors.
        
        Args:
            opportunity: The yield opportunity data
            
        Returns:
            float: Opportunity score (0-100)
        """
        # Get key metrics
        apy = opportunity.get("apy", 0)
        risk_score = self.calculate_risk_score(opportunity)
        
        # Start with normalized APY (0-100 scale)
        # We cap at 100% APY to prevent unrealistic values from dominating
        apy_normalized = min(100, apy) 
        
        # Convert risk score (lower is better) to risk factor (higher is better)
        risk_factor = 100 - risk_score
        
        # Calculate weighted score (60% APY, 40% risk factor)
        # This formula can be adjusted based on risk preference
        score = (0.6 * apy_normalized) + (0.4 * risk_factor)
        
        return score
    
    def detect_opportunities(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Detect and rank yield farming opportunities.
        
        Args:
            force_refresh: Whether to force refresh data
            
        Returns:
            List[Dict[str, Any]]: Ranked list of opportunities
        """
        # Skip re-processing if we have recent results (within last hour)
        if not force_refresh and self.last_update and self.opportunities:
            time_since_update = (datetime.now() - self.last_update).total_seconds()
            if time_since_update < 3600:  # 1 hour cache
                print(f"Using cached opportunities ({len(self.opportunities)} items)")
                return self.opportunities
        
        # Fetch Solana yields
        yields = data_aggregator.fetch_solana_yields(force_refresh)
        
        if not yields:
            print("No yield data available")
            return []
        
        print(f"Analyzing {len(yields)} yield opportunities...")
        
        # Filter and enhance opportunities
        filtered_opportunities = []
        
        for opp in yields:
            # Apply basic filters
            apy = opp.get("apy", 0)
            tvl = opp.get("tvlUsd", 0)
            
            if apy >= self.min_apy and tvl >= self.min_tvl:
                # Calculate scores
                risk_score = self.calculate_risk_score(opp)
                opportunity_score = self.calculate_opportunity_score(opp)
                
                # Add scores to the opportunity data
                enhanced_opp = opp.copy()
                enhanced_opp["risk_score"] = risk_score
                enhanced_opp["opportunity_score"] = opportunity_score
                
                # Add a risk level label
                if risk_score < 25:
                    risk_level = "Low"
                elif risk_score < 50:
                    risk_level = "Medium"
                elif risk_score < 75:
                    risk_level = "High"
                else:
                    risk_level = "Very High"
                
                enhanced_opp["risk_level"] = risk_level
                
                # Calculate estimated returns
                # For a hypothetical $1000 investment over 1 year
                estimated_return = 1000 * (apy / 100)
                enhanced_opp["estimated_return_1k_1y"] = estimated_return
                
                filtered_opportunities.append(enhanced_opp)
        
        # Sort by opportunity score (descending)
        sorted_opportunities = sorted(
            filtered_opportunities,
            key=lambda x: x.get("opportunity_score", 0),
            reverse=True
        )
        
        # Update cache
        self.opportunities = sorted_opportunities
        self.last_update = datetime.now()
        
        print(f"Found {len(sorted_opportunities)} viable opportunities")
        return sorted_opportunities
    
    def get_top_opportunities(self, top_n: int = 10, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get the top N yield opportunities.
        
        Args:
            top_n: Number of top opportunities to return
            force_refresh: Whether to force refresh data
            
        Returns:
            List[Dict[str, Any]]: Top opportunities
        """
        opportunities = self.detect_opportunities(force_refresh)
        return opportunities[:top_n]
    
    def get_opportunities_by_risk_level(self, risk_level: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get opportunities filtered by risk level.
        
        Args:
            risk_level: Risk level to filter by ("Low", "Medium", "High", "Very High")
            force_refresh: Whether to force refresh data
            
        Returns:
            List[Dict[str, Any]]: Opportunities matching the risk level
        """
        opportunities = self.detect_opportunities(force_refresh)
        return [opp for opp in opportunities if opp.get("risk_level") == risk_level]
    
    def get_protocol_opportunities(self, protocol: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get opportunities for a specific protocol.
        
        Args:
            protocol: Protocol name (e.g., "raydium")
            force_refresh: Whether to force refresh data
            
        Returns:
            List[Dict[str, Any]]: Opportunities for the protocol
        """
        # First try to get protocol-specific data
        protocol_yields = data_aggregator.fetch_protocol_yields(protocol, force_refresh)
        
        if not protocol_yields:
            # Fallback to filtering all opportunities
            opportunities = self.detect_opportunities(force_refresh)
            protocol_opportunities = [
                opp for opp in opportunities 
                if opp.get("project", "").lower() == protocol.lower()
            ]
            return protocol_opportunities
        
        # Process protocol-specific yields
        enhanced_opportunities = []
        
        for opp in protocol_yields:
            apy = opp.get("apy", 0)
            tvl = opp.get("tvlUsd", 0)
            
            if apy >= self.min_apy and tvl >= self.min_tvl:
                # Calculate scores
                risk_score = self.calculate_risk_score(opp)
                opportunity_score = self.calculate_opportunity_score(opp)
                
                # Add scores to the opportunity data
                enhanced_opp = opp.copy()
                enhanced_opp["risk_score"] = risk_score
                enhanced_opp["opportunity_score"] = opportunity_score
                
                # Add a risk level label
                if risk_score < 25:
                    risk_level = "Low"
                elif risk_score < 50:
                    risk_level = "Medium"
                elif risk_score < 75:
                    risk_level = "High"
                else:
                    risk_level = "Very High"
                
                enhanced_opp["risk_level"] = risk_level
                
                # Calculate estimated returns
                estimated_return = 1000 * (apy / 100)
                enhanced_opp["estimated_return_1k_1y"] = estimated_return
                
                enhanced_opportunities.append(enhanced_opp)
        
        # Sort by opportunity score (descending)
        sorted_opportunities = sorted(
            enhanced_opportunities,
            key=lambda x: x.get("opportunity_score", 0),
            reverse=True
        )
        
        return sorted_opportunities

# Create a global instance
opportunity_detector = OpportunityDetector()

if __name__ == "__main__":
    # Simple test
    detector = OpportunityDetector(min_apy=5.0, min_tvl=100000)
    top_opportunities = detector.get_top_opportunities(top_n=5)
    
    print("\n=== TOP 5 OPPORTUNITIES ===")
    for i, opp in enumerate(top_opportunities, 1):
        print(f"{i}. {opp.get('project', 'Unknown')} - {opp.get('symbol', 'Unknown')}")
        print(f"   APY: {opp.get('apy', 0):.2f}% | TVL: ${opp.get('tvlUsd', 0):,.2f}")
        print(f"   Risk Level: {opp.get('risk_level', 'Unknown')} | Score: {opp.get('opportunity_score', 0):.2f}")
        print(f"   Est. Return on $1000: ${opp.get('estimated_return_1k_1y', 0):,.2f}")
        print()
    
    # Get low risk opportunities
    low_risk = detector.get_opportunities_by_risk_level("Low")
    print(f"\nFound {len(low_risk)} low-risk opportunities") 