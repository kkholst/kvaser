# -*- coding: utf-8 -*-
#
# Distribution classes
# Copyright (c) 2019-2023 Klaus K. Holst.  All rights reserved.

import numpy as np
import sklearn.linear_model as glm

def randgen(func):
    def wrapper(*args, **kwargs):
        if len(args)>0:
            kwargs.setdefault('rng', args[0].rng)
            if kwargs.get('rng') is None:
                kwargs['rng'] = args[0].rng
        res = func(*args, **kwargs)
        return res
        ## After the function is called...
    return wrapper

class Dist:
    r"""Probability distribution class.
    Super class, not to be called directly
    """
    name = 'Generic'

    @randgen
    def gen(self, rng=None, *args, **kwargs):
        return rng

    @staticmethod
    def invlink(x):
        return np.array(x)

    def __init__(self, seed=None, **kwargs):
        r"""Distribution class constructor

        Parameters
        ----------
        seed: int64
              Random seed (optional)
        **kwargs:
              Extra arguments passed to random generator

        Returns
        ----------
        Dist
           Dist object
        """
        self.kparam = kwargs
        self.rng = np.random.default_rng(seed)

    def simulate(self, lp=None, rng=None):
        r"""Simulation method

        Parameters
        ----------
        mean:

        Returns
        ----------


        """
        mpar = self.invlink(lp)
        # par = {}
        # par[self.meanpar] = mean
        # res = self.gen(**par, **self.kparam, size=len(mean), rng=rng)
        res = self.gen(param=mpar, **self.kparam, rng=rng)
        return res

    @staticmethod
    def estimate(y, X=None, **kwargs):
        r"""Estimation method
        """
        return None, None

    def __repr__(self):
        return self.name + ' distribution ' + \
            str(self.kparam)

    def __str__(self):
        return self.name + ' distribution ' + \
            str(self.kparam)


class normal(Dist):
    r"""Normal distribution class

    Constructor arguments:

    scale: float or array_like of floats
         Standard deviation
    """
    name = 'Normal'

    @randgen
    def gen(self, param, rng, **kwargs):
        res = rng.normal(loc=param, **kwargs)
        return res

    @staticmethod
    def estimate(y, X):
        fit = glm.LinearRegression(fit_intercept=False) \
                 .fit(X=X, y=y)
        return fit.coef_, X


class bernoulli(Dist):
    name = 'Binomial'
    @randgen
    def gen(self, param, rng, **kwargs):
        return self.rng.binomial(p=param, n=1, **kwargs)

    @staticmethod
    def invlink(x):
        return(1/(1+np.exp(-np.array(x))))

    @staticmethod
    def estimate(y, X):
        fit = glm.LogisticRegression(penalty='none', fit_intercept=False) \
                 .fit(X=X, y=y)
        return fit.coef_, X


class poisson(Dist):
    name = 'Poisson'
    meanpar = 'lam'
    @randgen
    def gen(self, param, rng, **kwargs):
        return rng.poisson(lam=param, **kwargs)

    @staticmethod
    def invlink(x):
        return(np.exp(np.array(x)))

    @staticmethod
    def estimate(y, X):
        fit = glm.PoissonRegressor(alpha=0, fit_intercept=False) \
                  .fit(X=X, y=y)
        return fit.coef_, X


class discrete(Dist):
    name = 'Discrete'

    def __init__(self, values=[0,1], p=[0.5,0.5], **kwargs):
        super().__init__()
        self.values = np.array(values)
        self.p = np.array(p)

    @randgen
    def gen(self, param, rng, **kwargs):
        return rng.choice(a=self.values, p=self.p, size=len(param))

    @staticmethod
    def estimate(y, X=None):
        return None, None
