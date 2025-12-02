"""
Core mathematical calculations for Aviator probability analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from scipy import stats

def calculate_crash_probability(house_edge: float, multiplier: float) -> float:
    """
    Calculate probability of crash before reaching target multiplier.
    
    Formula: P(crash < x) = 1 - x^(-k)
    where k = 1 - (house_edge/100) / ln(2)
    
    Args:
        house_edge: House edge percentage (e.g., 1.0 for 1%)
        multiplier: Target multiplier
    
    Returns:
        Probability of crashing before reaching multiplier
    """
    # Ensure house_edge is between 0.1 and 10
    house_edge = max(0.1, min(house_edge, 10.0))
    
    # Calculate k parameter based on house edge
    house_edge_decimal = house_edge / 100
    k = 1 - (house_edge_decimal / np.log(2))
    
    # Calculate crash probability
    if multiplier <= 1:
        return 0.0
    return 1 - (multiplier ** (-k))

def simulate_round(
    bet_amount: float,
    target_multiplier: float,
    house_edge: float,
    current_bankroll: float
) -> Tuple[float, bool]:
    """
    Simulate a single round of the game.
    
    Returns:
        Tuple of (new_bankroll, won)
    """
    if current_bankroll < bet_amount:
        return current_bankroll, False
    
    crash_prob = calculate_crash_probability(house_edge, target_multiplier)
    
    # Generate random outcome
    if np.random.random() > crash_prob:
        # Win
        win_amount = bet_amount * (target_multiplier - 1)
        return current_bankroll + win_amount, True
    else:
        # Lose
        return current_bankroll - bet_amount, False

def simulate_rounds(
    num_simulations: int,
    num_rounds: int,
    bet_amount: float,
    target_multiplier: float,
    house_edge: float,
    initial_bankroll: float,
    strategy: str = "Fixed Cash-out"
) -> pd.DataFrame:
    """
    Run Monte Carlo simulation for multiple rounds.
    
    Returns:
        DataFrame with simulation results
    """
    results = []
    
    for sim in range(num_simulations):
        bankroll = initial_bankroll
        max_bankroll = initial_bankroll
        min_bankroll = initial_bankroll
        wins = 0
        
        for round_num in range(num_rounds):
            # Adjust bet based on strategy
            current_bet = adjust_bet_for_strategy(
                strategy, bet_amount, bankroll, wins, round_num
            )
            
            # Simulate round
            bankroll, won = simulate_round(
                current_bet, target_multiplier, house_edge, bankroll
            )
            
            if won:
                wins += 1
            
            # Track max/min bankroll for drawdown calculation
            max_bankroll = max(max_bankroll, bankroll)
            min_bankroll = min(min_bankroll, bankroll)
        
        # Calculate statistics for this simulation
        results.append({
            'simulation': sim + 1,
            'final_balance': bankroll,
            'total_wins': wins,
            'total_losses': num_rounds - wins,
            'win_rate': wins / num_rounds,
            'net_profit': bankroll - initial_bankroll,
            'max_drawdown': min_bankroll - max_bankroll,
            'roi': ((bankroll - initial_bankroll) / initial_bankroll) * 100
        })
    
    return pd.DataFrame(results)

def adjust_bet_for_strategy(
    strategy: str,
    base_bet: float,
    bankroll: float,
    wins: int,
    round_num: int
) -> float:
    """
    Adjust bet amount based on chosen strategy.
    
    Args:
        strategy: Betting strategy name
        base_bet: Base bet amount
        bankroll: Current bankroll
        wins: Number of wins so far
        round_num: Current round number
    
    Returns:
        Adjusted bet amount
    """
    if bankroll <= 0:
        return 0
    
    if strategy == "Fixed Cash-out":
        return min(base_bet, bankroll)
    
    elif strategy == "Martingale":
        # Double after loss
        if round_num == 0:
            return min(base_bet, bankroll)
        
        # This is simplified - in reality you'd track last outcome
        return min(base_bet * (2 ** wins), bankroll)
    
    elif strategy == "Fibonacci":
        # Fibonacci sequence betting
        fib_sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        idx = min(wins % 10, len(fib_sequence) - 1)
        return min(base_bet * fib_sequence[idx], bankroll)
    
    elif strategy == "D'Alembert":
        # Increase by base bet after loss, decrease after win
        adjustment = (wins - (round_num - wins)) * base_bet
        return min(max(base_bet + adjustment, base_bet * 0.1), bankroll)
    
    return min(base_bet, bankroll)

def calculate_expected_value(
    bet_amount: float,
    multiplier: float,
    success_prob: float
) -> float:
    """
    Calculate expected value of a bet.
    
    Args:
        bet_amount: Amount wagered
        multiplier: Target multiplier
        success_prob: Probability of success
    
    Returns:
        Expected value
    """
    win_amount = bet_amount * (multiplier - 1)
    loss_amount = -bet_amount
    
    return (success_prob * win_amount) + ((1 - success_prob) * loss_amount)

def kelly_criterion(success_prob: float, win_multiplier: float) -> float:
    """
    Calculate Kelly Criterion optimal bet fraction.
    
    Formula: f* = (p * b - q) / b
    where:
        f* = fraction of bankroll to bet
        p = probability of winning
        b = odds received on win (multiplier - 1)
        q = probability of losing (1 - p)
    
    Returns:
        Optimal fraction of bankroll to bet (0 to 1)
    """
    b = win_multiplier
    p = success_prob
    q = 1 - p
    
    if b <= 0 or p <= 0:
        return 0.0
    
    kelly = (p * b - q) / b
    return max(0.0, min(kelly, 1.0))  # Cap between 0 and 1

def risk_of_ruin_simulation(
    initial_bankroll: float,
    bet_amount: float,
    target_multiplier: float,
    house_edge: float,
    num_rounds: int,
    num_simulations: int = 1000
) -> float:
    """
    Calculate risk of ruin using Monte Carlo simulation.
    
    Returns:
        Percentage chance of losing entire bankroll
    """
    ruins = 0
    
    for _ in range(num_simulations):
        bankroll = initial_bankroll
        crashed = False
        
        for _ in range(num_rounds):
            if bankroll <= 0:
                crashed = True
                break
            
            crash_prob = calculate_crash_probability(house_edge, target_multiplier)
            
            if np.random.random() > crash_prob:
                bankroll += bet_amount * (target_multiplier - 1)
            else:
                bankroll -= bet_amount
        
        if bankroll <= 0:
            ruins += 1
    
    return (ruins / num_simulations) * 100

def calculate_probability_table(
    house_edge: float,
    multipliers: List[float]
) -> pd.DataFrame:
    """
    Create a probability table for various multipliers.
    
    Returns:
        DataFrame with probabilities
    """
    data = []
    
    for mult in multipliers:
        crash_prob = calculate_crash_probability(house_edge, mult)
        success_prob = 1 - crash_prob
        
        data.append({
            'Multiplier': mult,
            'Crash Probability': f"{crash_prob*100:.3f}%",
            'Success Probability': f"{success_prob*100:.3f}%",
            'Odds': f"1 in {int(1/success_prob):,}",
            'Decimal Odds': f"{1/success_prob:.2f}"
        })
    
    return pd.DataFrame(data)