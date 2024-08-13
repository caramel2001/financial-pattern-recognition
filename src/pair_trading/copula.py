"""
The purpose of this file is to contain classes for various types of Archimedian and Elliptical Copulae
"""

from itertools import compress
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sympy
from numpy import ndarray
from pandas import DataFrame
from scipy.interpolate import interp1d
from scipy.stats import kendalltau
from statsmodels.distributions.empirical_distribution import ECDF
from scipy.optimize import minimize_scalar

plt.style.use("seaborn-v0_8")
plt.rcParams.update({"font.family": "Times New Roman"})
plt.rcParams.update(
    {"axes.grid": True, "axes.linewidth": 0.5, "axes.edgecolor": "black"}
)


class ClaytonCopula:
    def __init__(self, alpha: float = None, isOrdinal: bool = False):
        """
        This class implements the Clayton Copula

        Parameters
        ----------
        ndims : number of dimensions in our dataset to model
        alpha : parameter for our copula
        isOrdinal : is our data already converted into ranked data/cdf
        """
        self.alpha = alpha
        self.pdf_func = None

    def convert_to_ecdf(self, vector: DataFrame):
        """
        This function converts our numeric RVs into their respective empirical cdfs

        Parameters
        ----------
        vector : dataframe

        Returns
        -------
        dataframe of ranked vectors
        """

        ndims = vector.shape[1]

        ecdf = np.empty(shape=(vector.shape[0], vector.shape[1]))

        for idx in range(ndims):
            ecdf[:, idx] = ECDF(vector.iloc[:, idx])(vector.iloc[:, idx])

        ecdf = np.where(ecdf == 1, 0.9999, ecdf)
        ecdf = np.where(ecdf == 0, 0.0001, ecdf)

        ecdf = pd.DataFrame(ecdf, index=vector.index)
        ecdf.columns = vector.columns

        self.inverted_ecdf = []

        for idx in range(ndims):
            self.inverted_ecdf.append(interp1d(ecdf.iloc[:, idx], vector.iloc[:, idx]))

        return ecdf

    def cdf(self, vector: DataFrame, alpha: float):
        """
        This function gets the cdf value correspoding to a set of row vectors and alpha

        Parameters
        ----------
        vector : dataset
        alpha : copula parameter

        Returns
        -------
        CDF value of copula  in (0, 1)
        """

        if isinstance(vector, DataFrame):
            vector = vector.values

        elif not isinstance(vector, ndarray) and not isinstance(vector, list):
            raise TypeError

        if isinstance(vector, list):
            return self.phi_inverse(
                np.sum([self.phi(t=x, alpha=alpha) for x in vector]), alpha=alpha
            )

        else:

            return self.phi_inverse(
                np.sum([self.phi(t=x, alpha=alpha) for x in vector], axis=1),
                alpha=alpha,
            )

    def phi(self, t: Union[DataFrame, float], alpha: float):
        """
        Generator Function

        Parameters
        ----------
        t : input parameter
        alpha : copula paramter

        Returns
        -------

        """
        return (1 / alpha) * (t ** (-alpha) - 1)

    def phi_inverse(self, t: Union[DataFrame, float], alpha: float):
        """Inverse of Generator Function

        Parameters
        ----------
        t : input parameter
        alpha : copula paramter

        Returns
        -------

        """

        # return np.sign(alpha * t + 1) * (np.abs(alpha * t + 1)) ** (-1 / alpha)
        return (alpha * t + 1) ** (-1 / alpha)

    def pdf(self, vector: DataFrame, alpha: float):
        """
        This function provides the pdf at a given row vector and alpha level

        Parameters
        ----------
        vector : dataset
        alpha : copula parameter

        Returns
        -------
        pdf value
        """

        vector = self.convert_to_ecdf(vector)

        vector_symbols = [
            (sympy.symbols(f"vector_{idx}"), vector[i]) for idx, i in enumerate(vector)
        ]

        def fprime(vector_symbols):
            return sympy.diff(self.cdf(vector_symbols, alpha), *vector_symbols)

        if not self.pdf_func:
            self.pdf_func = sympy.lambdify(
                [x[0] for x in vector_symbols], fprime([x[0] for x in vector_symbols])
            )

        return self.pdf_func(*[x[1] for x in vector_symbols])

    def marginal_cdf(self, mask, vector, alpha=None, method=None):
        """Provides the marginal CDF or more of the random variables conditional on the others."""

        if method == "sympy":

            vector = self.convert_to_ecdf(vector)

            vector_symbols = [
                (sympy.symbols(f"vector_{idx}"), vector[i])
                for idx, i in enumerate(vector)
            ]

            # @cache
            def fprime(vector_symbols):
                return sympy.diff(
                    self.cdf(vector_symbols, alpha),
                    *list(compress(vector_symbols, mask)),
                )

            marginal_cdf_func = sympy.lambdify(
                [x[0] for x in vector_symbols], fprime([x[0] for x in vector_symbols])
            )

            return marginal_cdf_func(*[x[1] for x in vector_symbols])

        else:

            vector = self.convert_to_ecdf(vector)

            assert sum(mask) == 1 and vector.shape[1] == 2

            if not alpha and self.alpha:
                alpha = self.alpha
            else:
                raise ValueError

            u = vector.iloc[:, 0]
            v = vector.iloc[:, 1]

            term_1 = (u ** (-alpha) + v ** (-alpha) - 1) ** (-(1 / alpha) - 1)

            if mask[0]:
                return (v ** (-alpha - 1)) * term_1

            else:
                return (u ** (-alpha - 1)) * term_1

    def fit(self, vector, method="kendall"):
        """Fit a mxn dataset based on neg log likelihood to get optimal value of alpha"""

        if method == "mle":

            raise NotImplementedError
            #
            # if not self.isOrdinal:
            #     vector = self.convert_to_ecdf(vector)
            #
            # def neg_log_likelihood(alpha, vector):
            #     return -np.sum(np.log(self.pdf(vector, alpha)))
            #
            # result = minimize_scalar(
            #         neg_log_likelihood,
            #         args = (vector),
            #         bounds = (-1, 2 ** 32),
            #         method = "bounded",
            #         options = {"disp": True},
            #         )
            #
            # self.alpha = result["x"]

        elif method == "kendall":

            assert vector.shape[1] == 2

            k = kendalltau(vector.iloc[:, 0], vector.iloc[:, 1]).statistic

            self.alpha = 2 * k / (1 - k)

        self.vector = vector

    def plot_2d(self):
        """Plot of copula in 2D conditional on other random variables"""

        self.vector = self.convert_to_ecdf(self.vector)

        fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(14, 4))

        X = self.vector.iloc[:, 0]
        Y = self.vector.iloc[:, 1]

        ax[0].hist(X, density=True, bins=30)
        ax[0].set(title="CDF of X")

        ax[1].hist(Y, density=True, bins=30)
        ax[1].set(title="CDF of Y")

        ax[2].scatter(X, Y, alpha=0.25)
        ax[2].set(title="Scatterplot of CDF(X,Y)")

    def plot_3d(self):

        # create a grid
        x = np.linspace(start=0.001, stop=0.999, num=100)
        y = np.linspace(start=0.001, stop=0.999, num=100)
        x, y = np.meshgrid(x, y)

        assert self.vector.shape[1] == 2

        pairs = np.array([[i, j] for i, j in zip(x.flatten(), y.flatten())])

        z = self.cdf(vector=pairs, alpha=self.alpha).reshape([100, 100])

        fig = plt.figure(figsize=(18, 6))
        ax0 = fig.add_subplot(121, projection="3d")

        ax0.plot_surface(x, y, z, cmap="coolwarm", rstride=10, cstride=10, linewidth=1)
        ax0.invert_xaxis()
        ax0.set(title="3D surface copula representation")