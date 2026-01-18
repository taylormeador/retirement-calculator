import numpy as np
from jinja2 import Environment, FileSystemLoader

import models
from monte_carlo import Simulation
from create_html.create_charts import (
    create_percentile_chart,
    create_failure_rate_comparison,
)


def main():
    n_samples = 10000
    return_models = {
        "Normal": models.normal_returns,
        "Fat-Tailed (t)": models.multivariate_t_returns,
        "Mean Reversion": models.ar1_returns,
        "Historical Bootstrap": models.bootstrap_returns,
    }
    withdrawal_rates = [0.03, 0.035, 0.04, 0.045, 0.05]

    # Run all simulations
    print("Running simulations...")
    all_results = {}
    for model_name, return_model in return_models.items():
        print(f"\n{model_name}:")
        all_results[model_name] = {}

        for withdrawal_rate in withdrawal_rates:
            print(f"  {withdrawal_rate*100:.1f}%...", end=" ")

            simulation = Simulation(return_model, withdrawal_rate)
            all_trajectories = []
            failures = 0

            for _ in range(n_samples):
                result = simulation.run()
                all_trajectories.append(result["portfolio_values"])
                if not result["success"]:
                    failures += 1

            trajectories_array = np.array(all_trajectories)
            failure_rate = (failures / n_samples) * 100

            all_results[model_name][withdrawal_rate] = {
                "trajectories": trajectories_array,
                "failure_rate": failure_rate,
            }

            print(f"{failure_rate:.1f}%")

    # Generate charts
    print("\nGenerating charts...")

    # Failure rate comparison
    failure_rate_data = {
        model: [all_results[model][wr]["failure_rate"] for wr in withdrawal_rates]
        for model in return_models.keys()
    }
    fig_comparison = create_failure_rate_comparison(failure_rate_data)
    fig_comparison.write_html(
        "return_models/static/charts/failure_rate_comparison.html"
    )
    print("  - Failure rate comparison")

    # Percentile charts at 4%
    percentile_charts = {}
    for model_name in return_models.keys():
        trajectories = all_results[model_name][0.04]["trajectories"]
        fig = create_percentile_chart(trajectories, model_name, 0.04)

        filename = f"{model_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}_4pct.html"
        fig.write_html(f"return_models/static/charts/{filename}")
        percentile_charts[model_name] = filename
        print(f"  - {model_name}")

    print("\nGenerating HTML page...")
    env = Environment(loader=FileSystemLoader("."))

    def number_format(value):
        return f"{value:,}"

    env.filters["number_format"] = number_format

    template = env.get_template("return_models/static/results_template.html")

    html = template.render(
        n_samples=n_samples,
        withdrawal_rates=withdrawal_rates,
        model_names=list(return_models.keys()),
        results=all_results,
        percentile_charts=percentile_charts,
    )

    with open("return_models/static/results.html", "w") as f:
        f.write(html)

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY - Failure Rates (%)")
    print("=" * 70)
    print(f"{'Model':<25} ", end="")
    for wr in withdrawal_rates:
        print(f"{wr*100:>6.1f}%", end=" ")
    print()
    print("-" * 70)
    for model_name in return_models.keys():
        print(f"{model_name:<25} ", end="")
        for wr in withdrawal_rates:
            fr = all_results[model_name][wr]["failure_rate"]
            print(f"{fr:>6.1f}%", end=" ")
        print()
    print("=" * 70)

    print("\n✓ Generated: return_models/static/results.html")
    print("  Open this file in your browser to see all results!\n")


if __name__ == "__main__":
    main()
