import os
import inspect
def noop():
    return
assets_root=os.path.dirname(inspect.getfile(noop))