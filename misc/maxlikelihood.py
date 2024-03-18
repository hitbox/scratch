import math

# Likelihood function for a normal distribution
def likelihood(params, data):
    mu, sigma = params
    n = len(data)
    log_likelihood = (
        -n/2
        * math.log(2 * math.pi * sigma**2)
        - (1/(2 * sigma**2))
        * sum((x - mu)**2 for x in data)
    )
    # Return negative log-likelihood for minimization
    return -log_likelihood

# Maximum Likelihood Estimation function
def maximum_likelihood_estimation(data):
    # Initial guess for mean and standard deviation
    initial_guess = [sum(data) / len(data), 1.0]

    # Using grid search for simplicity (can be replaced with more sophisticated
    # methods)
    best_params = initial_guess
    best_likelihood = likelihood(initial_guess, data)

    # Define ranges for mean and standard deviation (sigma should not be zero)
    mu_range = [min(data), max(data)]
    sigma_range = [0.001, max(data) - min(data)]

    # Iterate over the ranges to find the parameters that maximize the
    # likelihood function
    a = int(mu_range[0] * 1000)
    b = int(mu_range[1] * 1000)
    for mu in range(a, b):
        a2 = int(sigma_range[0] * 1000)
        b2 = int(sigma_range[1] * 1000)
        for sigma in range(a2, b2):
            params = [mu / 1000, sigma / 1000]
            current_likelihood = likelihood(params, data)
            if current_likelihood > best_likelihood:
                best_likelihood = current_likelihood
                best_params = params

    return best_params

# Sample data (mean = 3.0, std deviation = ~0.43)
data = [2.5, 3.0, 2.7, 3.2, 2.8, 3.5, 3.0, 2.4, 3.8, 3.2]

# Perform Maximum Likelihood Estimation on the sample dataset
estimated_mean, estimated_std = maximum_likelihood_estimation(data)

print(f"Estimated Mean: {estimated_mean}")
print(f"Estimated Standard Deviation: {estimated_std}")

# 2023-12-13
# https://www.kdnuggets.com/building-predictive-models-logistic-regression-in-python
# https://chat.openai.com/c/6957a15a-ea99-450d-be8c-cc9d5db6ec0d
