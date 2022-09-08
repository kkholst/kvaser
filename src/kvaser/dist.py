#!/usr/bin/env python3

import numpy as np

class Dist:
    r"""Probability distribution class.
    Super class, not to be called directly
    """

    rng = np.random.default_rng()
    name = 'Generic'
    meanpar = 'loc'

    def gen(self, size, **kwargs):
        return None

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

    def simulate(self, mean=None, lp=None):
        r"""Simulation method

        Parameters
        ----------
        mean:

        Returns
        ----------

        """
        if lp is not None:
            mean = self.invlink(lp)
        par = {}
        par[self.meanpar] = mean

        return self.gen(**par, **self.kparam, size=len(mean))

    def __repr__(self):
        return self.name + ' distribution ' + \
            str(self.kparam)

    def __str__(self):
        return self.name + ' distribution ' + \
            str(self.kparam)


class normal(Dist):
    r"""Normal distribution class
    constructor arguments:
    loc: float or array_like of floats
         Mean
    scale: float or array_like of floats
         Standard deviation
    """
    def gen(self, size, **kwargs):
        return self.rng.normal(size=size, **kwargs)
    name = 'Normal'
    meanpar = 'loc'


class bernoulli(Dist):
    name = 'Binomial'
    meanpar = 'p'

    def gen(self, size, **kwargs):
        return self.rng.binomial(size=size, n=1, **kwargs)

    @staticmethod
    def invlink(x):
        return(1/(1+np.exp(-np.array(x))))


class poisson(Dist):
    name = 'Poisson'
    meanpar = 'lam'
    def gen(self, size, **kwargs):
        return self.rng.poisson(size=size, **kwargs)

    @staticmethod
    def invlink(x):
        return(np.exp(np.array(x)))


class discrete(Dist):
    name = 'Discrete'

    def __init__(self, values=[0,1], p=[0.5,0.5], **kwargs):
        super().__init__()
        self.values = np.array(values)
        self.p = np.array(p)

    def gen(self, size, **kwargs):
        return self.rng.choice(a=self.values, p=self.p, size=size)



