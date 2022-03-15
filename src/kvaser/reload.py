import importlib
import re

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
       Module name
    """


    mod = list(filter(lambda x: re.match("^"+pkg, x),
                      list(sys.modules.keys())))
    for m in mod:
        try:
            importlib.reload(sys.modules[m])
            print(m)
        except:
            None
