import importlib
import re
import sys

def reload(pkg):
    """Reload package modules

    Examples
    ----------
    >>> kvaser.reload('mypackage')

    See Also
    ----------
    importlib.reload

    Returns
    ----------
    None

    Parameters
    ----------
    pkg: string
       Regular expression for module name(s)
    """


    mod = list(filter(lambda x: re.match(pkg, x),
                      list(sys.modules.keys())))
    for m in mod:
        try:
            importlib.reload(sys.modules[m])
            print(m)
        except:
            None
