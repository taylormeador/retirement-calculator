import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_percentile_chart(trajectories_array, title, withdrawal_rate):
    """
    Create a chart showing percentile bands of portfolio values over time.

    Parameters:
    -----------
    trajectories_array : np.ndarray, shape (n_simulations, n_years+1)
        Array of portfolio value trajectories
    title : str
        Chart title (e.g., "Normal Distribution")
    withdrawal_rate : float
        Withdrawal rate for subtitle (e.g., 0.04 for 4%)

    Returns:
    --------
    fig : plotly.graph_objects.Figure
    """
    # Calculate percentiles
    years = np.arange(len(trajectories_array[0]))
    p10 = np.percentile(trajectories_array, 10, axis=0)
    p25 = np.percentile(trajectories_array, 25, axis=0)
    p50 = np.percentile(trajectories_array, 50, axis=0)
    p75 = np.percentile(trajectories_array, 75, axis=0)
    p90 = np.percentile(trajectories_array, 90, axis=0)

    # Create figure
    fig = go.Figure()

    # Add 10th-90th percentile band (lightest)
    fig.add_trace(
        go.Scatter(
            x=years,
            y=p90,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=years,
            y=p10,
            mode="lines",
            line=dict(width=0),
            fillcolor="rgba(68, 138, 255, 0.2)",
            fill="tonexty",
            name="10th-90th percentile",
            hovertemplate="Year %{x}<br>10th-90th: $%{y:,.0f}<extra></extra>",
        )
    )

    # Add 25th-75th percentile band (medium)
    fig.add_trace(
        go.Scatter(
            x=years,
            y=p75,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=years,
            y=p25,
            mode="lines",
            line=dict(width=0),
            fillcolor="rgba(68, 138, 255, 0.3)",
            fill="tonexty",
            name="25th-75th percentile",
            hovertemplate="Year %{x}<br>25th-75th: $%{y:,.0f}<extra></extra>",
        )
    )

    # Add median line (darkest)
    fig.add_trace(
        go.Scatter(
            x=years,
            y=p50,
            mode="lines",
            line=dict(color="rgb(31, 119, 180)", width=2),
            name="Median (50th percentile)",
            hovertemplate="Year %{x}<br>Median: $%{y:,.0f}<extra></extra>",
        )
    )

    # Update layout
    fig.update_layout(
        title=dict(
            text=f"{title}<br><sub>{withdrawal_rate*100:.1f}% Withdrawal Rate</sub>",
            x=0.5,
            xanchor="center",
        ),
        xaxis_title="Year",
        yaxis_title="Portfolio Value ($)",
        hovermode="x unified",
        template="plotly_white",
        height=400,
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    # Format y-axis as currency
    fig.update_yaxes(tickformat="$,.0f")

    return fig


def create_failure_rate_comparison(results_dict):
    """
    Create a line chart comparing failure rates across models.

    Parameters:
    -----------
    results_dict : dict
        Format: {
            'Normal': [failure_rate_3%, failure_rate_3.5%, ...],
            'Fat-Tailed': [...],
            'Mean Reversion': [...],
            'Historical Bootstrap': [...]
        }

    Returns:
    --------
    fig : plotly.graph_objects.Figure
    """
    withdrawal_rates = [3.0, 3.5, 4.0, 4.5, 5.0]

    fig = go.Figure()

    # Colors for each model
    colors = {
        "Normal": "rgb(31, 119, 180)",
        "Fat-Tailed": "rgb(255, 127, 14)",
        "Mean Reversion": "rgb(44, 160, 44)",
        "Historical Bootstrap": "rgb(214, 39, 40)",
    }

    # Add a line for each model
    for model_name, failure_rates in results_dict.items():
        fig.add_trace(
            go.Scatter(
                x=withdrawal_rates,
                y=failure_rates,
                mode="lines+markers",
                name=model_name,
                line=dict(color=colors.get(model_name), width=2),
                marker=dict(size=8),
                hovertemplate="%{x}% withdrawal<br>Failure rate: %{y:.1f}%<extra></extra>",
            )
        )

    # Update layout
    fig.update_layout(
        title="Failure Rates by Withdrawal Rate and Model",
        xaxis_title="Withdrawal Rate (%)",
        yaxis_title="Failure Rate (%)",
        hovermode="x unified",
        template="plotly_white",
        height=450,
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    # Format axes
    fig.update_xaxes(ticksuffix="%")
    fig.update_yaxes(ticksuffix="%")

    return fig


# Example usage:
if __name__ == "__main__":
    # Generate some dummy data for testing
    np.random.seed(42)

    # Simulate 1000 portfolio trajectories over 30 years
    n_sims = 1000
    n_years = 31  # 0-30

    # Example: portfolio starts at $1M, declines over time with noise
    trajectories = []
    for _ in range(n_sims):
        path = [1_000_000]
        for year in range(30):
            # Simple random walk for demonstration
            change = np.random.normal(-30_000, 100_000)
            new_value = max(0, path[-1] + change)
            path.append(new_value)
        trajectories.append(path)

    trajectories_array = np.array(trajectories)

    # Create percentile chart
    fig1 = create_percentile_chart(
        trajectories_array, title="Normal Distribution", withdrawal_rate=0.04
    )

    # Save as HTML
    fig1.write_html("portfolio_trajectory_example.html")
    print("Saved: portfolio_trajectory_example.html")

    # Create failure rate comparison
    example_results = {
        "Normal": [2.0, 5.0, 8.0, 15.0, 25.0],
        "Fat-Tailed": [4.0, 8.0, 13.0, 22.0, 35.0],
        "Mean Reversion": [1.0, 3.0, 6.0, 12.0, 20.0],
        "Historical Bootstrap": [2.5, 6.0, 9.0, 16.0, 27.0],
    }

    fig2 = create_failure_rate_comparison(example_results)
    fig2.write_html("failure_rate_comparison_example.html")
    print("Saved: failure_rate_comparison_example.html")

    print("\nTo embed in your HTML:")
    print("1. Save chart with fig.write_html('chart.html')")
    print(
        "2. Embed in main HTML with <iframe src='chart.html' width='100%' height='450'></iframe>"
    )
    print("   OR")
    print(
        "3. Use fig.to_html(include_plotlyjs='cdn', div_id='chart-div') and paste directly"
    )
