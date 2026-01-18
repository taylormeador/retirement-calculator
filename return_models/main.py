import numpy as np
import os

import models
from monte_carlo import Simulation
from create_charts import create_percentile_chart, create_failure_rate_comparison


def main():
    n_samples = 10
    return_models = {
        "Normal": models.normal_returns,
        "Fat-Tailed (t)": models.multivariate_t_returns,
        "Mean Reversion": models.ar1_returns,
        "Historical Bootstrap": models.bootstrap_returns,
    }
    withdrawal_rates = [0.03, 0.035, 0.04, 0.045, 0.05]

    # Run all simulations
    all_results = {}
    for model_name, return_model in return_models.items():
        print(f"\nRunning {model_name}...")
        all_results[model_name] = {}

        for withdrawal_rate in withdrawal_rates:
            print(f"  {withdrawal_rate*100:.1f}% withdrawal rate...", end=" ")

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

            print(f"Failure rate: {failure_rate:.1f}%")

    # Generate charts
    print("\nGenerating charts...")

    # Create failure rate comparison chart
    failure_rate_data = {}
    for model_name in return_models.keys():
        failure_rates = [
            all_results[model_name][wr]["failure_rate"] for wr in withdrawal_rates
        ]
        failure_rate_data[model_name] = failure_rates

    fig_comparison = create_failure_rate_comparison(failure_rate_data)
    fig_comparison.write_html(
        "return_models/static/charts/failure_rate_comparison.html"
    )

    # Create percentile charts for each model at 4% withdrawal rate
    for model_name in return_models.keys():
        trajectories = all_results[model_name][0.04]["trajectories"]
        fig = create_percentile_chart(trajectories, model_name, 0.04)
        filename = f"return_models/static/charts/{model_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}_4pct.html"
        fig.write_html(filename)

    # Print summary table
    print("\n" + "=" * 70)
    print("SUMMARY TABLE - Failure Rates (%)")
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


if __name__ == "__main__":
    main()
