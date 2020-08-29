import numpy as np
import kvaser.__kvaser_c__ as kvaserc


def expit(x):
    """Sigmoid function (Inverse Logit)

    Parameters
    ----------
    x: numpy.array

    Returns
    -------
    numpy.array
        matrix with elementwise inverse logit

    """

    val = np.array(x)
    return kvaserc.expit(val)
