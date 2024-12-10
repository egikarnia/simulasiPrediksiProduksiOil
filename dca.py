import numpy as np

def dca_exponential(qi, b, t):
    return qi * np.exp(-b * t)

def dca_harmonic(qi, b, t):
    return qi / (1 + b * t)

def dca_hyperbolic(qi, b, t, n):
    return qi / ((1 + b * t) ** n)
