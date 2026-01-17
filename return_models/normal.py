import numpy as np


def normal_returns():
    """
    Generate 30 year multivariate normal returns for stocks and bonds.
    """
    mean = [0.10, 0.05]  # stocks, bonds
    cov = [
        [0.04, -0.002],  # 20% std for stocks, -0.2 correlation
        [-0.002, 0.0036],  # 6% std for bonds
    ]
    return np.random.multivariate_normal(mean, cov, size=30)


result = normal_returns()
breakpoint()
