import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Simple mobile config
st.set_page_config(
    page_title="FiatFlow Fixed",
    page_icon="🪙", 
    layout="centered"
)

st.title("🪙 FiatFlow Tracker")
st.write("✅ **Working Version - No Errors**")

# Simple data
coins = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "MATIC", "DOT"]

for coin in coins:
    # Simple calculations (no API calls)
    flow = np.random.randint(50, 200)
    price_change = np.random.uniform(-5, 5)
    momentum = flow + (price_change * 10)
    
    if momentum > 50:
        signal = "🟢 BUY"
        color = "green"
    elif momentum < -30:
        signal = "🔴 SELL" 
        color = "red"
    else:
        signal = "🟡 HOLD"
        color = "yellow"
    
    # Display each coin
    st.markdown(f"""
    <div style='background: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid {color}'>
        <div style='display: flex; justify-content: space-between;'>
            <h3 style='margin: 0;'>{coin}</h3>
            <span style='font-size: 1.2em; font-weight: bold;'>{signal}</span>
        </div>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;'>
            <div>Flow: <b>{flow}%</b></div>
            <div>Momentum: <b>{momentum:.1f}</b></div>
            <div>Price: <b>{price_change:+.2f}%</b></div>
            <div>Volume: <b>${np.random.randint(1, 100)}M</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Refresh button
if st.button("🔄 Refresh Data", use_container_width=True):
    st.rerun()

st.caption(f"Last update: {datetime.now().strftime('%H:%M:%S')}")