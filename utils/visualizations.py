"""
Visualization functions for Aviator probability calculator
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
from typing import List, Dict

def create_probability_chart(house_edge: float) -> go.Figure:
    """
    Create probability distribution chart.
    """
    # Generate multiplier range
    multipliers = np.linspace(1, 100, 200)
    
    # Calculate probabilities
    crash_probs = []
    for mult in multipliers:
        crash_prob = 1 - (mult ** (-(1 - (house_edge/100)/np.log(2))))
        crash_probs.append(crash_prob)
    
    success_probs = 1 - np.array(crash_probs)
    
    # Create figure
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Success Probability", "Crash Probability",
                       "Probability Density", "Cumulative Distribution"),
        vertical_spacing=0.15,
        horizontal_spacing=0.15
    )
    
    # Success probability
    fig.add_trace(
        go.Scatter(
            x=multipliers,
            y=success_probs,
            mode='lines',
            name='Success',
            line=dict(color='#38a169', width=3),
            hovertemplate='<b>%{x:.2f}×</b><br>Success: %{y:.1%}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Crash probability
    fig.add_trace(
        go.Scatter(
            x=multipliers,
            y=crash_probs,
            mode='lines',
            name='Crash',
            line=dict(color='#e53e3e', width=3),
            hovertemplate='<b>%{x:.2f}×</b><br>Crash: %{y:.1%}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Add reference lines
    for threshold in [0.5, 0.25, 0.1, 0.01]:
        # Find where success probability equals threshold
        idx = np.abs(success_probs - threshold).argmin()
        x_val = multipliers[idx]
        
        fig.add_vline(
            x=x_val,
            line_dash="dash",
            line_color="gray",
            opacity=0.5,
            row=1, col=1
        )
        
        fig.add_annotation(
            x=x_val,
            y=threshold,
            text=f"{x_val:.1f}×",
            showarrow=False,
            yshift=10,
            row=1, col=1
        )
    
    # Probability density (derivative of CDF)
    pdf = np.gradient(crash_probs, multipliers)
    fig.add_trace(
        go.Scatter(
            x=multipliers,
            y=pdf,
            mode='lines',
            name='Density',
            line=dict(color='#667eea', width=2),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)',
            hovertemplate='<b>%{x:.2f}×</b><br>Density: %{y:.4f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Cumulative distribution
    fig.add_trace(
        go.Scatter(
            x=multipliers,
            y=crash_probs,
            mode='lines',
            name='CDF',
            line=dict(color='#764ba2', width=3),
            hovertemplate='<b>%{x:.2f}×</b><br>CDF: %{y:.1%}<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=700,
        showlegend=False,
        template="plotly_white",
        title_text=f"Probability Analysis (House Edge: {house_edge}%)",
        title_x=0.5
    )
    
    # Update axes
    fig.update_xaxes(title_text="Multiplier (×)", row=1, col=1)
    fig.update_xaxes(title_text="Multiplier (×)", row=1, col=2)
    fig.update_xaxes(title_text="Multiplier (×)", row=2, col=1)
    fig.update_xaxes(title_text="Multiplier (×)", row=2, col=2)
    
    fig.update_yaxes(title_text="Probability", row=1, col=1, tickformat=".0%")
    fig.update_yaxes(title_text="Probability", row=1, col=2, tickformat=".0%")
    fig.update_yaxes(title_text="Density", row=2, col=1)
    fig.update_yaxes(title_text="Cumulative Probability", row=2, col=2, tickformat=".0%")
    
    return fig

def create_simulation_chart(results_df: pd.DataFrame) -> go.Figure:
    """
    Create visualization for simulation results.
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Final Balance Distribution", "Profit/Loss Histogram",
                       "Win Rate Distribution", "ROI Distribution"),
        specs=[[{"type": "box"}, {"type": "histogram"}],
               [{"type": "histogram"}, {"type": "histogram"}]]
    )
    
    # Final balance box plot
    fig.add_trace(
        go.Box(
            y=results_df['final_balance'],
            name='Balance',
            boxpoints='outliers',
            marker_color='#38a169',
            line_color='#2f855a'
        ),
        row=1, col=1
    )
    
    # Profit/Loss histogram
    fig.add_trace(
        go.Histogram(
            x=results_df['net_profit'],
            name='Profit/Loss',
            nbinsx=50,
            marker_color='#667eea',
            opacity=0.7,
            hovertemplate='<b>%{x:.0f}</b><br>Count: %{y}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Add vertical line at 0
    fig.add_vline(
        x=0,
        line_dash="dash",
        line_color="red",
        opacity=0.7,
        row=1, col=2
    )
    
    # Win rate distribution
    fig.add_trace(
        go.Histogram(
            x=results_df['win_rate'] * 100,
            name='Win Rate',
            nbinsx=30,
            marker_color='#ed8936',
            opacity=0.7,
            hovertemplate='<b>%{x:.1f}%</b><br>Count: %{y}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Add theoretical win rate line
    theoretical_rate = 1 - (0.5 ** (1 - ((results_df['win_rate'].mean()/100)/np.log(2))))
    fig.add_vline(
        x=theoretical_rate * 100,
        line_dash="dash",
        line_color="green",
        opacity=0.7,
        row=2, col=1
    )
    
    # ROI distribution
    fig.add_trace(
        go.Histogram(
            x=results_df['roi'],
            name='ROI',
            nbinsx=50,
            marker_color='#9f7aea',
            opacity=0.7,
            hovertemplate='<b>%{x:.1f}%</b><br>Count: %{y}<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Add vertical line at 0%
    fig.add_vline(
        x=0,
        line_dash="dash",
        line_color="red",
        opacity=0.7,
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=700,
        showlegend=False,
        template="plotly_white",
        title_text="Simulation Results Analysis",
        title_x=0.5
    )
    
    # Update axes
    fig.update_xaxes(title_text="Final Balance ($)", row=1, col=1)
    fig.update_xaxes(title_text="Net Profit/Loss ($)", row=1, col=2)
    fig.update_xaxes(title_text="Win Rate (%)", row=2, col=1)
    fig.update_xaxes(title_text="ROI (%)", row=2, col=2)
    
    return fig

def create_histogram_chart(results_df: pd.DataFrame) -> go.Figure:
    """
    Create histogram chart for simulation outcomes.
    """
    # Calculate outcome categories
    results_df['outcome'] = pd.cut(
        results_df['net_profit'],
        bins=[-float('inf'), -1000, -500, -100, 0, 100, 500, 1000, float('inf')],
        labels=['<-$1000', '-$1000 to -$500', '-$500 to -$100', 
                '-$100 to $0', '$0 to $100', '$100 to $500', 
                '$500 to $1000', '>$1000']
    )
    
    outcome_counts = results_df['outcome'].value_counts().sort_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=outcome_counts.index,
        y=outcome_counts.values,
        marker_color=['#e53e3e', '#dd6b20', '#d69e2e', '#ecc94b',
                     '#9ae6b4', '#68d391', '#38a169', '#2f855a'],
        hovertemplate='<b>%{x}</b><br>Count: %{y}<br>Percentage: %{customdata:.1f}%<extra></extra>',
        customdata=(outcome_counts.values / outcome_counts.sum() * 100)
    ))
    
    fig.update_layout(
        title="Outcome Distribution",
        xaxis_title="Profit/Loss Range",
        yaxis_title="Number of Simulations",
        template="plotly_white",
        height=500,
        showlegend=False
    )
    
    # Add percentage labels
    fig.update_traces(texttemplate='%{customdata:.1f}%', textposition='outside')
    
    return fig

def create_strategy_comparison_chart(strategy_results: List[Dict]) -> go.Figure:
    """
    Create comparison chart for different betting strategies.
    """
    df = pd.DataFrame(strategy_results)
    
    fig = go.Figure()
    
    # Add bars for each metric
    metrics = ['Avg Final Balance', 'Win Rate', 'Max Drawdown']
    colors = ['#667eea', '#38a169', '#e53e3e']
    
    for i, metric in enumerate(metrics):
        fig.add_trace(go.Bar(
            name=metric,
            x=df['Strategy'],
            y=df[metric],
            marker_color=colors[i],
            opacity=0.8,
            hovertemplate='<b>%{x}</b><br>' + metric + ': %{y:.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Strategy Comparison",
        xaxis_title="Strategy",
        yaxis_title="Value",
        template="plotly_white",
        barmode='group',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig