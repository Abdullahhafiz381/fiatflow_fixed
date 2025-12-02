"""
🎰 Aviator Probability Calculator - Streamlit App
Educational tool for analyzing crash game probabilities
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from utils.calculator import (
    calculate_crash_probability,
    simulate_rounds,
    calculate_expected_value,
    kelly_criterion,
    risk_of_ruin_simulation
)
from utils.visualizations import (
    create_probability_chart,
    create_simulation_chart,
    create_histogram_chart
)

# Page configuration
st.set_page_config(
    page_title="Aviator Probability Calculator",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .warning-box {
        background-color: #fff5f5;
        border-left: 4px solid #fc8181;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .result-card {
        background: linear-gradient(135deg, #f6f8ff, #ffffff);
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    .positive {
        color: #38a169;
        font-weight: bold;
    }
    
    .negative {
        color: #e53e3e;
        font-weight: bold;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">✈️ Aviator Probability Calculator</h1>', unsafe_allow_html=True)
st.markdown("**Educational tool for analyzing crash game mathematics**")

# Warning Box
with st.container():
    st.markdown("""
    <div class="warning-box">
        ⚠️ **IMPORTANT EDUCATIONAL DISCLAIMER**  
        This tool is for **educational purposes only** to understand probability theory.  
        Gambling carries significant risks of financial loss and addiction.  
        No strategy can overcome the house edge in the long run.
    </div>
    """, unsafe_allow_html=True)

# Sidebar for inputs
with st.sidebar:
    st.header("⚙️ Simulation Parameters")
    
    # Game parameters
    house_edge = st.slider(
        "House Edge (%)",
        min_value=0.1,
        max_value=10.0,
        value=1.0,
        step=0.1,
        help="Casino's mathematical advantage"
    )
    
    target_multiplier = st.slider(
        "Target Multiplier (×)",
        min_value=1.1,
        max_value=100.0,
        value=2.0,
        step=0.1,
        help="Where you plan to cash out"
    )
    
    bet_amount = st.number_input(
        "Bet Amount ($)",
        min_value=1,
        max_value=10000,
        value=10,
        step=1
    )
    
    initial_bankroll = st.number_input(
        "Initial Bankroll ($)",
        min_value=10,
        max_value=100000,
        value=1000,
        step=100,
        help="Starting capital for simulations"
    )
    
    num_rounds = st.select_slider(
        "Number of Rounds to Simulate",
        options=[10, 50, 100, 500, 1000, 5000, 10000],
        value=1000
    )
    
    num_simulations = st.select_slider(
        "Number of Simulations",
        options=[1, 10, 100, 500, 1000],
        value=100,
        help="More simulations = more accurate results"
    )
    
    # Strategy selector
    strategy = st.selectbox(
        "Betting Strategy",
        ["Fixed Cash-out", "Martingale", "Fibonacci", "D'Alembert"],
        help="Different betting progression systems"
    )
    
    # Advanced settings
    with st.expander("Advanced Settings"):
        kelly_fraction = st.slider(
            "Kelly Fraction (%)",
            min_value=0,
            max_value=100,
            value=25,
            step=5,
            help="Percentage of Kelly Criterion to use"
        )
        
        show_advanced_stats = st.checkbox("Show Advanced Statistics")
        show_code = st.checkbox("Show Mathematical Formulas")
    
    st.divider()
    
    # Run simulation button
    run_simulation = st.button(
        "🚀 Run Simulation",
        type="primary",
        use_container_width=True
    )

# Main content area
if run_simulation:
    # Calculate probabilities
    crash_prob = calculate_crash_probability(house_edge, target_multiplier)
    success_prob = 1 - crash_prob
    
    # Calculate expected value
    ev = calculate_expected_value(
        bet_amount=bet_amount,
        multiplier=target_multiplier,
        success_prob=success_prob
    )
    
    # Run Monte Carlo simulation
    results = simulate_rounds(
        num_simulations=num_simulations,
        num_rounds=num_rounds,
        bet_amount=bet_amount,
        target_multiplier=target_multiplier,
        house_edge=house_edge,
        initial_bankroll=initial_bankroll,
        strategy=strategy
    )
    
    # Calculate Kelly Criterion
    kelly = kelly_criterion(
        success_prob=success_prob,
        win_multiplier=target_multiplier - 1
    )
    kelly_bet = max(0, kelly_fraction / 100 * kelly * initial_bankroll)
    
    # Risk of ruin calculation
    risk_of_ruin = risk_of_ruin_simulation(
        initial_bankroll=initial_bankroll,
        bet_amount=bet_amount,
        target_multiplier=target_multiplier,
        house_edge=house_edge,
        num_rounds=num_rounds,
        num_simulations=1000
    )
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Success Probability",
            f"{success_prob*100:.2f}%",
            f"1 in {int(1/success_prob):,}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Expected Value",
            f"${ev:.2f}",
            "per round"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "House Edge",
            f"{house_edge}%",
            f"RTP: {100 - house_edge}%"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Risk of Ruin",
            f"{risk_of_ruin:.1f}%",
            f"after {num_rounds} rounds"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Probability distribution chart
    st.subheader("📊 Probability Distribution")
    
    fig1 = create_probability_chart(house_edge)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Simulation results
    st.subheader("📈 Simulation Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.write("**Final Balance Distribution**")
        
        fig2 = create_simulation_chart(results)
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.write("**Round-by-Round Performance**")
        
        fig3 = create_histogram_chart(results)
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed statistics
    with st.expander("📋 Detailed Statistics"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Simulation Summary**")
            summary_stats = {
                "Total Simulations": num_simulations,
                "Total Rounds": num_simulations * num_rounds,
                "Ended with Profit": f"{(results['final_balance'] > initial_bankroll).mean()*100:.1f}%",
                "Ended with Loss": f"{(results['final_balance'] < initial_bankroll).mean()*100:.1f}%",
                "Maximum Drawdown": f"${results['max_drawdown'].min():.2f}",
                "Best Run": f"${results['final_balance'].max():.2f}",
                "Worst Run": f"${results['final_balance'].min():.2f}"
            }
            
            for key, value in summary_stats.items():
                st.write(f"• {key}: {value}")
        
        with col2:
            st.write("**Probability Table**")
            multipliers = [1.5, 2, 3, 5, 10, 20, 50, 100]
            prob_data = []
            
            for mult in multipliers:
                prob = 1 - calculate_crash_probability(house_edge, mult)
                prob_data.append({
                    "Multiplier": f"{mult}×",
                    "Probability": f"{prob*100:.3f}%",
                    "1 in": f"{int(1/prob):,}",
                    "Payout": f"${bet_amount * mult - bet_amount:.2f}"
                })
            
            st.table(pd.DataFrame(prob_data))
    
    # Strategy comparison
    if strategy != "Fixed Cash-out":
        st.subheader("🔄 Strategy Analysis")
        
        strategies = ["Fixed Cash-out", "Martingale", "Fibonacci", "D'Alembert"]
        strategy_results = []
        
        for strat in strategies:
            strat_res = simulate_rounds(
                num_simulations=100,
                num_rounds=num_rounds,
                bet_amount=bet_amount,
                target_multiplier=target_multiplier,
                house_edge=house_edge,
                initial_bankroll=initial_bankroll,
                strategy=strat
            )
            
            strategy_results.append({
                "Strategy": strat,
                "Avg Final Balance": strat_res['final_balance'].mean(),
                "Win Rate": (strat_res['final_balance'] > initial_bankroll).mean() * 100,
                "Max Drawdown": strat_res['max_drawdown'].min()
            })
        
        strategy_df = pd.DataFrame(strategy_results)
        st.dataframe(strategy_df, use_container_width=True)
    
    # Kelly Criterion information
    if show_advanced_stats:
        st.subheader("🎯 Kelly Criterion Analysis")
        
        st.write(f"""
        **Kelly Criterion Calculation:**
        - Optimal bet fraction: {kelly*100:.2f}% of bankroll
        - Using {kelly_fraction}% of Kelly: {kelly_fraction/100 * kelly * 100:.2f}%
        - Suggested bet size: ${kelly_bet:.2f}
        
        *The Kelly Criterion maximizes long-term growth but assumes perfect knowledge of probabilities.*
        """)
    
    # Mathematical formulas
    if show_code:
        st.subheader("🧮 Mathematical Formulas")
        
        st.code("""
        # Core Probability Formula
        def crash_probability(house_edge, multiplier):
            # Convert house edge to k parameter
            k = 1 - (house_edge / 100) / np.log(2)
            return 1 - multiplier ** (-k)
        
        # Expected Value
        def expected_value(bet, multiplier, success_prob):
            win_amount = bet * multiplier - bet
            loss_amount = -bet
            return (success_prob * win_amount) + ((1 - success_prob) * loss_amount)
        
        # Kelly Criterion
        def kelly_criterion(win_prob, odds):
            # odds = multiplier - 1
            return (win_prob * odds - (1 - win_prob)) / odds
        """, language="python")
    
    # Download results
    st.download_button(
        label="📥 Download Simulation Data",
        data=results.to_csv(index=False).encode('utf-8'),
        file_name=f"aviator_simulation_{num_rounds}_rounds.csv",
        mime="text/csv"
    )

else:
    # Welcome/instruction screen
    st.markdown("""
    ## 📚 Welcome to the Aviator Probability Calculator
    
    This educational tool helps you understand the mathematics behind crash-style gambling games.
    
    ### 🔍 **What You Can Analyze:**
    
    1. **Probability Distribution** - See how likely different multipliers are
    2. **Expected Value** - Calculate the mathematical average outcome
    3. **Risk Analysis** - Understand your risk of losing your bankroll
    4. **Strategy Testing** - Compare different betting systems
    5. **Monte Carlo Simulation** - See thousands of possible outcomes
    
    ### 🧮 **Key Mathematical Concepts:**
    
    - **House Edge**: The casino's built-in mathematical advantage (typically 1-5%)
    - **Return to Player (RTP)**: 100% - House Edge
    - **Independence**: Each round is completely random and independent
    - **Expected Value**: The average outcome over infinite trials
    
    ### ⚠️ **Educational Warning:**
    
    This calculator demonstrates why:
    - No betting system can overcome the house edge in the long run
    - All strategies have negative expected value
    - Gambling is mathematically designed for the house to win
    
    ### 🚀 **Getting Started:**
    
    1. Adjust parameters in the sidebar
    2. Click **"Run Simulation"**
    3. Analyze the results
    4. Learn about probability theory!
    
    *Note: No real money is involved. This is purely for educational purposes.*
    """)
    
    # Quick example chart
    st.subheader("📉 Example: Probability Curve (1% House Edge)")
    
    # Create example chart
    multipliers = np.linspace(1, 20, 100)
    probs = 1 - calculate_crash_probability(1.0, multipliers)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=multipliers,
        y=probs,
        mode='lines',
        name='Probability',
        line=dict(color='#667eea', width=3)
    ))
    
    fig.update_layout(
        title="Probability of Reaching Different Multipliers",
        xaxis_title="Multiplier (×)",
        yaxis_title="Probability",
        hovermode="x unified",
        template="plotly_white",
        height=400
    )
    
    fig.add_hline(y=0.5, line_dash="dash", line_color="gray",
                  annotation_text="50% chance",
                  annotation_position="bottom right")
    
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 0.9rem;">
    <p>📚 <strong>Educational Tool Only</strong> • No Real Money Involved • Made for Learning Probability Theory</p>
    <p>⚠️ If you or someone you know has a gambling problem, seek help at: 
    <a href="https://www.ncpgambling.org/help-treatment/help-by-state/" target="_blank">National Problem Gambling Helpline</a></p>
</div>
""", unsafe_allow_html=True)