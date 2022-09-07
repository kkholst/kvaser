#!/usr/bin/env python3

import numpy as np
import networkx as nx
import pandas as pd
from PIL import Image
from io import BytesIO
import pydot

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



class dag:
    r"""DAG model class
    """

    def __init__(self):
        r"""
        """
        self.G = nx.DiGraph()
        self.var = {}

    def regression(self, y, x=[]):
        self.G.add_node(y)
        self.distribution(y)
        for v in x:
            self.G.add_edge(v, y)

    def distribution(self, y, generator=normal()):
        r"""Set distribution of variable"""
        self.G.add_node(y)
        self.var[y] = generator

    def simulate(self, n=1, p={}):
        deg = dict(self.G.in_degree)
        vv = list(self.G.nodes)
        res = np.ndarray((n, len(vv)))

        p0 = {}
        for y in vv:
            par = self.G.predecessors(y)
            for x in par:
                pname = y + '~' + x
                p0[pname] =1
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
                        lp = np.repeat([0.0], n)
                        # print("Variable :" + v)
                        for x in par:
                            pname = v + '~' + x
                            posx = int(vv.index(x))
                            lp += p0[pname]*res[:,posx]
                        y = np.float64(self.var[v].simulate(lp=lp))
                        res[:,pos] = y
        df = pd.DataFrame(res)
        df.columns = vv
        return df

    def plot(self):
        pdot = nx.nx_pydot.to_pydot(self.G)
        Image.open(BytesIO(pdot.create_png())).show()

    def __str__(self):
        st = ''
        for v in self.G.nodes:
            parents = list(self.G.predecessors(v))
            st += v + ' ~ ' + ' + '.join(parents) + '\n'
        st += '\n'
        for k,v in self.var.items():
            st += str(k) + ': ' + str(v) + '\n'
        return st


# m = dag()
# m.regression('y', ['x','z'])
# m.regression('z', ['x'])
# m.distribution('y', normal(scale=2))
# m.distribution('z', poisson())
# m.distribution('x', bernoulli())
# print(m)
# r = m.simulate(5000)
# r

# import statsmodels.formula.api as smf
# import statsmodels.genmod.families as fam
# smf.glm('y ~ x+z', data=r, family=fam.Gaussian()).fit().summary()

# smf.glm('z ~ x', data=r, family=fam.Poisson()).fit().summary()

# smf.glm('x ~ 1', data=r, family=fam.Binomial()).fit().summary()
