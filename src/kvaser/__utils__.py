# -*- coding: utf-8 -*-
#
# Copyright (c) 2019-2023 Klaus K. Holst.  All rights reserved.

import pandas as pd

def filesize(size, digits=2):
    r"""From bytes to kilo, mega, giga, tera
    """
    power = 1024.0
    Dic_powerN = {0: 'B', 1: 'kB', 2: 'MB', 3: 'GB', 4: 'TB'}
    if size < power:
        return size, Dic_powerN[0]
    n = 0
    while size > power:
        n  += 1
        size /= power
    size = round(size*(10**digits))/(10**digits)
    return size, Dic_powerN[n]

def desc(x):
    r"""Summary statistics for Pandas/NumPy type objecte

    Examples
    ----------
    >>> desc(np.random.random((10,3)))
                   0          1          2
    count  10.000000  10.000000  10.000000
    mean    0.461966   0.447567   0.350905
    std     0.214195   0.307504   0.284285
    min     0.052849   0.017704   0.002699
    25%     0.310563   0.228061   0.162021
    50%     0.486678   0.356398   0.326617
    75%     0.649301   0.694684   0.516374
    max     0.694157   0.982049   0.900196

    See Also
    ----------
    pandas.describe:
    describe

    Returns
    ----------
    pandas.core.frame.DataFrame
        DataFrame with summary statistics (mean, std.dev, quantiles)

    Parameters
    ----------
    x: numpy.array, pandas.DataFrame
        NumPy or Pandas DataFrame (or something that can be cast to a DataFrame)
    """

    try:
        x = pd.DataFrame(x)
    except Exception as ex:
        raise TypeError("Expecting Pandas compatible type") from ex
    return x.describe()

