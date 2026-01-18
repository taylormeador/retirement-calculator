from create_charts import create_failure_rate_comparison, create_percentile_chart


def generate_analysis_page(trajectories_array, title, withdrawal_rate, results_dict):
    """
    Generate complete HTML page with embedded charts.
    """

    # Read the template
    with open("return_models/static/analysis_template.html", "r") as f:
        html = f.read()

    # Generate chart HTML
    fig1 = create_percentile_chart(trajectories_array, title, withdrawal_rate)
    fig2 = create_failure_rate_comparison(results_dict)

    chart1_html = fig1.to_html(
        include_plotlyjs="cdn", div_id="chart1", config={"displayModeBar": False}
    )
    chart2_html = fig2.to_html(
        include_plotlyjs=False, div_id="chart2", config={"displayModeBar": False}
    )

    # Replace placeholders
    html = html.replace(
        '<div class="chart-placeholder" id="failure-rate-chart">',
        chart1_html + '<div style="display:none">',
    )
    html = html.replace("Chart: Line chart with 4 lines", "")
    html = html.replace("</div>", "</div>", 1)  # Close the hidden div

    # Save final HTML
    with open("return_models/static/final_analysis.html", "w") as f:
        f.write(html)
