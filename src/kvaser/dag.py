# -*- coding: utf-8 -*-
#
# Simulation class
# Copyright (c) 2019-2022 Klaus K. Holst.  All rights reserved.

import kvaser as kv
import networkx as nx
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
import pydot

class dag:
    r"""DAG model class
    """

    def __init__(self):
        r"""
        """
        self.G = nx.DiGraph()
        self.dist = {}

    def regression(self, y, x=[]):
        self.G.add_node(y)
        if y not in self.dist.keys():
            self.distribution(y)
        for v in x:
            self.G.add_edge(v, y)
            if v not in self.dist.keys():
                self.distribution(v)

    def distribution(self, y, generator=kv.normal()):
        r"""Set distribution of variable"""
        self.G.add_node(y)
        self.dist[y] = generator

    def simulate(self, n=1, p={}):
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
                        for x in par:
                            pname = v + '~' + x
                            posx = int(vv.index(x))
                            lp += p0[pname]*res[:,posx]
                        y = np.float64(self.dist[v].simulate(lp=lp))
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
        for k,v in self.dist.items():
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
