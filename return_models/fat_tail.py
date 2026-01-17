import numpy as np
from scipy import stats


def multivariate_t_returns():
    """
    Generate samples from multivariate Student's t distribution.
    """
    mean = [0.07, 0.02]  # stocks, bonds
    cov = [
        [0.04, -0.002],  # 20% std for stocks, -0.2 correlation
        [-0.002, 0.0036],  # 6% std for bonds
    ]
    df = 5
    n_assets = 2
    n_samples = 30

    # Generate samples from multivariate normal
    normal_samples = np.random.multivariate_normal(
        mean=np.zeros(n_assets),
        cov=cov,
        size=n_samples,
    )

    # Generate chi-squared samples for scaling
    chi2_samples = np.random.chisquare(df=df, size=n_samples)

    # Scale the normal samples by sqrt(df / chi2) to get t-distribution
    # This gives us standard multivariate t
    scaling = np.sqrt(df / chi2_samples)
    t_samples = normal_samples * scaling[:, np.newaxis]

    # Add the mean
    t_samples = t_samples + mean

    return t_samples
