def generate_final_html(all_results, withdrawal_rates):
    """Generate a standalone HTML file with all results and embedded charts."""

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retirement Analysis Results</title>
    <style>
        body {
            font-family: Georgia, serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 40px;
        }
        h3 {
            color: #34495e;
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px;
            text-align: center;
            border: 1px solid #ddd;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        td:first-child {
            text-align: left;
            font-weight: 500;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .chart-container {
            margin: 30px 0;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        iframe {
            border: none;
            width: 100%;
        }
        .intro {
            background-color: #e8f4f8;
            padding: 20px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>How Return Distribution Assumptions Affect Safe Withdrawal Rates</h1>
    
    <div class="intro">
        <p><strong>Analysis Overview:</strong> This analysis compares four different approaches to modeling investment returns 
        and their impact on safe withdrawal rates for retirement planning. All simulations use a 60/40 stock/bond allocation, 
        30-year time horizon, and real (inflation-adjusted) returns.</p>
    </div>
    
    <h2>Summary: Failure Rates by Model and Withdrawal Rate</h2>
    <table>
        <thead>
            <tr>
                <th>Model</th>
"""

    # Add withdrawal rate headers
    for wr in withdrawal_rates:
        html += f"                <th>{wr*100:.1f}%</th>\n"

    html += """            </tr>
        </thead>
        <tbody>
"""

    # Add data rows
    for model_name in [
        "Normal",
        "Fat-Tailed (t)",
        "Mean Reversion",
        "Historical Bootstrap",
    ]:
        html += f"            <tr>\n                <td>{model_name}</td>\n"
        for wr in withdrawal_rates:
            failure_rate = all_results[model_name][wr]["failure_rate"]
            html += f"                <td>{failure_rate:.1f}%</td>\n"
        html += "            </tr>\n"

    html += """        </tbody>
    </table>
    
    <h2>Failure Rate Comparison Across Models</h2>
    <div class="chart-container">
        <iframe src="charts/failure_rate_comparison.html" height="500"></iframe>
    </div>
    
    <h2>Portfolio Value Trajectories at 4% Withdrawal Rate</h2>
    <p>These charts show the range of possible outcomes (10th-90th percentile) for a $1M portfolio with a 4% withdrawal rate under each return model.</p>
    
    <div class="chart-container">
        <h3>Normal Distribution</h3>
        <iframe src="charts/normal_4pct.html" height="450"></iframe>
    </div>
    
    <div class="chart-container">
        <h3>Fat-Tailed Distribution (Student's t)</h3>
        <iframe src="charts/fat-tailed_t_4pct.html" height="450"></iframe>
    </div>
    
    <div class="chart-container">
        <h3>Mean Reversion (AR(1))</h3>
        <iframe src="charts/mean_reversion_4pct.html" height="450"></iframe>
    </div>
    
    <div class="chart-container">
        <h3>Historical Bootstrap</h3>
        <iframe src="charts/historical_bootstrap_4pct.html" height="450"></iframe>
    </div>
    
    <hr style="margin: 40px 0;">
    <p style="text-align: center; color: #7f8c8d; font-size: 0.9em;">
        Generated with Python • Monte Carlo simulation with 1,000 iterations per scenario
    </p>
    
</body>
</html>
"""

    with open("return_models/static/results.html", "w") as f:
        f.write(html)

    print("\n" + "=" * 70)
    print("Generated: return_models/static/results.html")
    print("Open this file in your browser to see all results!")
    print("=" * 70)
