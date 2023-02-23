# -*- coding: utf-8 -*-
#
# Simulation class
# Copyright (c) 2019-2023 Klaus K. Holst.  All rights reserved.

import kvaser as kv
import networkx as nx
import numpy as np
import pandas as pd
from PIL import Image # Python Imaging library
from io import BytesIO
import patsy


class dag:
    r"""DAG model class

    Examples
    -----------

    >>> m = dag()
    >>> m.regression('y', ['x','z'])
    >>> m.regression('z', ['x'])
    >>> m.distribution('y', normal(scale=2))
    >>> m.distribution('z', poisson())
    >>> m.distribution('x', bernoulli())
    >>> print(m)
        y ~ x + z
        x ~ v
        z ~ x + w
        w ~ 1
        v ~ 1

        y: Normal distribution {'scale': 2}
        x: Binomial distribution {}
        z: Poisson distribution {}
        w: Discrete distribution {}
        v: Generic distribution {}

    >>> r = m.simulate(5000)
    >>> r
                      y    x    z    w    v
        0      7.482054  1.0  8.0  1.0  1.0
        1      1.324973  1.0  0.0 -1.0  1.0
        2      5.071795  1.0  4.0  1.0  1.0
        3     -2.643319  1.0  0.0 -1.0  1.0
        4      8.206240  1.0  4.0  1.0  1.0
        ...         ...  ...  ...  ...  ...
        4995   4.020084  1.0  3.0  0.0  2.0
        4996   0.277728  1.0  1.0 -1.0  2.0
        4997  12.546145  1.0  8.0  1.0  2.0
        4998   4.043192  1.0  0.0 -1.0  2.0
        4999   4.402478  1.0  1.0 -1.0  2.0

    >>> # import statsmodels.formula.api as smf
    >>> # import statsmodels.genmod.families as fam
    >>> # smf.glm('y ~ x+z', data=r, family=fam.Gaussian()).fit().summary()
    >>> # smf.glm('z ~ x', data=r, family=fam.Poisson()).fit().summary()
    >>> # smf.glm('x ~ 1', data=r, family=fam.Binomial()).fit().summary()
    """

    def __init__(self):
        r"""
        Constructor
        """
        self.G = nx.DiGraph()
        self._distribution = {}
        self._functionalform = {}

    def regression(self, y, x=[], f=None):
        r"""Add regression association between response 'y' and list of covariates 'x'

        Parameters
        ----------
        y: str
           response variable name
        x: list of str
           covariate names
        """
        self.G.add_node(y)
        self._functionalform[y] = f
        if y not in self._distribution.keys():
            self.distribution(y)
        for v in x:
            self.G.add_edge(v, y)
            if v not in self._distribution.keys():
                self.distribution(v)
                self._functionalform[v] = f
        return self

    def distribution(self, y, generator=kv.normal()):
        r"""Set distribution of variable

        Parameters
        ----------
        y: str
           variable name
        generator: Dist inherited class
           random generator (see details below)

        Notes
        ----------
        Available generators:
          - kv.normal(scale=...)
          - kv.bernoulli()
          - kv.poisson()
          - kv.discrete(values=..., p=...)

        New generators can easily be constructed.

        >>> class mydist(kv.Dist):
        >>> @kv.randgen
        >>> def gen(self, param, **kwargs):
                return np.repeat([1,2], len(param)/2)

        'param' is a parameter array derived from the regression design -
        typically the mean parameter.

        Here a generator for a Gamma distribution:

        >>> class mydist2(kv.Dist):
        >>>    invlink = np.exp
        >>>    @kv.randgen
        >>>    def gen(self, param, rng, **kwargs):
        >>>        return rng.gamma(scale=param, shape=param, **kwargs)

        """
        self.G.add_node(y)
        self._distribution[y] = generator
        return self

    def simulate(self, n=1, p={}, file=None, rng=None):
        r"""Simulate from model

        Parameters
        ----------
        n: int
           number of samples to simulate
        p: dict
           (optional) Dictionary of parameters (see below)
        file: str
           (optional) file name to store data in CSV format
        rng: numpy.random._generator.Generator
           (optional) Random number generator

        Notes
        ----------
        Parameters are default 0 for all intercepts and 1 for all other regression coefficients.
        This can be changed for a subset of the parameters via the argument 'p'.
        'p' must be a dictionary where the keys are the names of the parameters where intercept parameters
        are simply the name of the variable, e.g., 'y', and the regression coefficients are named as
        'y~x' (response y and covariate x). For examples

        >>> m = kv.dag()
        >>> m.regression('y', ['x','z'])
        >>> m.distribution('y', kv.poisson())
        >>> p = {'y': -1, 'y~x': 2}
        >>> m.simulate(10, p=p)

        which draws 10 simulations from the model

        .. math:: y|x,z \sim \operatorname{pois}\left\{\exp(-1 + 2x + z)\right\}

        """
        deg = dict(self.G.in_degree)
        vv = list(self.G.nodes)
        n = int(n)
        res = np.ndarray((n, len(vv)))

        p0 = {}
        for y in vv:
            p0[y] = 0.0
            if y in p.keys():
                p0[y] = p[y]
            par = self.G.predecessors(y)
            for x in par:
                pname = y + '~' + x
                p0[pname] = 1
                if pname in p.keys():
                    p0[pname] = p[pname]

        while any(x>=0 for x in deg.values()):
            for v, d in deg.items():
                if d>=0:
                    par = list(self.G.predecessors(v))
                    subdict = dict((k, deg[k]) for k in par if k in deg)
                    if all(x<0 for x in subdict.values()):
                        deg[v] = -1
                        pos = vv.index(v)
                        lp = np.repeat([float(p0[v])], n)
                        if len(par)>0:
                            f = self._functionalform[v]
                            if f is None:
                                for x in par:
                                    pname = v + '~' + x
                                    posx = int(vv.index(x))
                                    lp += p0[pname]*res[:,posx]
                            else:
                                idx = np.array([vv.index(x) for x in par], dtype="int64")
                                lp = np.array(f(res[:,idx])).flatten()
                        print(lp)
                        y = np.float64(self._distribution[v].simulate(lp=lp, rng=rng))
                        res[:,pos] = y
        df = pd.DataFrame(res)
        df.columns = vv
        if file is not None:
            df.to_csv(file)
            return None
        return df

    def summary(self):
        r"""Summary method"""
        res = {}
        for v in self.G.nodes:
            parents = list(self.G.predecessors(v))
            if len(parents)==0:
                parents = "1"
            formula = v + ' ~ ' + ' + '.join(parents)
            dist = self._distribution[v]
            res[v] = (formula, dist)
        return res

    def design(self, data):
        r"""Extract model design matrix

        Parameters
        ----------
        data: pandas.DataFrame
              DataFrame with all variables in the model (as returned by the simulate method)

        Returns
        ----------
        Dict
           Dictonary which for each variable name contains a tuple
           y, X of response and design matrix values

        """
        res = {}
        mod = self.summary()
        for v in mod.keys():
            f = mod[v][0]
            y, X = patsy.dmatrices(f, data=data)
            res[v] = (y, X)
        return res

    def estimate(self, data):
        r"""Estimate model parameters

        Parameters
        ----------
        data: pandas.DataFrame
              DataFrame with all variables in the model (as returned by the simulate method)

        Returns
        ----------
        Dict
           Dictonary which for each variable name contains a dictonary with elements
           'coef' (regression coefficients) and 'ic' (influence curve).

        Examples
        ----------

        >>> m = kv.dag().regression('y', 'x').distribution('y', poisson())
        >>> d = m.simulate(1000)
        >>> m.estimate(d)['y']
            {'coef': array([-0.01545999,  0.96640726]), 'ic': ...}

        """
        res = {}
        mod = self.summary()
        for v in mod.keys():
            dist = mod[v][1]
            f = mod[v][0]
            y, X = patsy.dmatrices(f, data=data)
            coef, influ = dist.estimate(y=y.ravel(), X=X)
            res[v] = {'coef': coef, 'ic': influ}
        return res

    def plot(self):
        r"""Plot DAG model
        """
        pdot = nx.nx_pydot.to_pydot(self.G)
        Image.open(BytesIO(pdot.create_png())).show()

    def __str__(self):
        st = 'DAG model class'
        nvar = len(self.G.nodes)
        if nvar>0: st += '\n'
        for f in self.summary().values():
            st += '\n' + f[0]
        if nvar>0: st += '\n'
        for k,v in self._distribution.items():
            st += '\n' + str(k) + ': ' + str(v)
        return st


