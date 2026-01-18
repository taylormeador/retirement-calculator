import numpy as np

import models
from monte_carlo import Simulation
from embed_charts import generate_analysis_page


def main():
    n_samples = 10
    return_models = {
        "Normal": models.normal_returns,
        "Fat-Tailed (t)": models.multivariate_t_returns,
        "Mean Reversion": models.ar1_returns,
        "Historical Bootstrap": models.bootstrap_returns,
    }
    withdrawal_rates = [0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06]
    for title, return_model in return_models.items():
        for withdrawal_rate in withdrawal_rates:
            simulation = Simulation(return_model, withdrawal_rate)
            all_trajectories = []
            failures = 0
            for _ in range(n_samples):
                result = simulation.run()
                all_trajectories.append(result["portfolio_values"])
                if not result["success"]:
                    failures += 1

            # Calculate stats
            trajectories_array = np.array(all_trajectories)
            p10 = np.percentile(trajectories_array, 10, axis=0)
            p25 = np.percentile(trajectories_array, 25, axis=0)
            p50 = np.percentile(trajectories_array, 50, axis=0)
            p75 = np.percentile(trajectories_array, 75, axis=0)
            p90 = np.percentile(trajectories_array, 90, axis=0)

            failure_rate = failures / n_samples * 100
            print(f"Failure rate: {failure_rate}%")

            generate_analysis_page(trajectories_array, title, withdrawal_rate, {})


if __name__ == "__main__":
    main()
