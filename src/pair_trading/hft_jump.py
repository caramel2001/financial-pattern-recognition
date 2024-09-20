# Pairs trading with a mean-reverting jump-diffusion model on high-frequency data
# https://www.econstor.eu/bitstream/10419/157807/1/885569830.pdf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def overnight_intraday_jumps_analysis(data, threshold=0.01):
    # For each sub-period, determine the spreads of all possible pair combinations. The absolute first differences of each spread are splitted into the subsets overnight variations and intraday variations.s. For the overnight and intraday variations, we consider the highest 1−q variations for q ∈ {0.90, 0.95, 0.97, 0.99, 0.999}. 
    # Now, the jump threshold cq (cq ∈ R+) is calculated based on the q-quantile of the whole data base of overnight and intraday variations together. We estimate the jump intensity λ by the following: 

    # λ overnight(intraday) = number of overnight (intraday) variations greater than cq/total number of overnight (intraday) variations 

    pass

# Function to estimate parameters using MLE for the JDM
def log_likelihood(params, spread):
    theta, mu, sigma, lambd = params
    n = len(spread)
    dt = 1/390  # assuming 390 minutes in a trading day
    likelihood = 0
    
    for t in range(1, n):
        dXt = spread[t] - spread[t-1]
        dNt = np.random.poisson(lambd * dt)
        lnJ = np.random.normal(mu, sigma)
        mean_reversion_term = theta * (mu - spread[t-1]) * dt
        diffusive_term = sigma * np.sqrt(dt) * np.random.normal(0, 1)
        jump_term = lnJ * dNt
        
        Xt = spread[t-1] + mean_reversion_term + diffusive_term + jump_term
        
        likelihood += -0.5 * np.log(2 * np.pi * sigma**2 * dt) - 0.5 * ((dXt - Xt)**2 / (sigma**2 * dt))
    
    return -likelihood

def ou_process(spread):
    """
    Use OU process to calibrate the parameters of the OU process for the spread.
    The OU process is a stochastic process that captures the effect of mean-reversion, 
    modeling the spread {Xt}t≥0 by the following stochastic differential equation:
    
    dXt = θ(µ − Xt)dt + σdWt, X0 = x,

    where:
    - θ (float): The mean-reversion speed. Higher values indicate faster reversion to the mean level µ.
    - µ (float): The equilibrium level to which the process reverts.
    - σ (float): The volatility of the process, representing the intensity of the random fluctuations.
    - X0 (float): The initial value of the process at time t=0.
    - dt (float): The time increment for each step in the simulation.
    - num_steps (int): The number of time steps to simulate.

    The mean reversion speed θ measures the degree of reversion to the equilibrium level µ, i.e., the higherthe value θ is, the faster the process Xt tends back to its mean level
    """

    