"""
We use Dask for a couple of reasons. One is to get automatic parallelization of data loading.
The other is to be able to cache things on disk and in memory. The helpers
in this file provide some function that allow you to compute something, serialize it to disk,
and then just load it from disk next time instead of re-computing it. This helps us save time
after doing computationaly intensive things (like joins, data parsing).
"""
import pickle
from os.path import exists
from functools import partial

from toolz import valmap

import dask
from dask.rewrite import RewriteRule, RuleSet
from dask.delayed import Delayed
from dask.context import _globals
from dask.diagnostics import ProgressBar

# let's have progress bars, they are fun!
ProgressBar().register()


# At compile time, this checks if the file exists
# if it does, it replaces the instruction with just
# reading that file
# if it doens't it computes the vlaue and saves it

def _persist_disk(reader, writer, value, filename):
    raise RuntimeError('Should have been re-written')

def _rhs(d):
    if exists(d['f']):
        return (read_file, d['r'], d['f'])
    return (write_file, d['v'], d['f'], d['w'])
rule = RewriteRule(
    (_persist_disk, 'r', 'w', 'v', 'f'),
    _rhs,
    ('v', 'f', 'r', 'w')
)

rs = RuleSet(rule)
    
def write_file(value, filename, writer):
    writer(value, filename)
    return value


def read_file(reader, filename):
    return reader(filename)

def optimize_file(dsk, keys):
    return valmap(rs.rewrite, dsk)

# we add this as a global re-writer for delayed objects
# so we don't have to use context manager all around
_globals['delayed_optimize'] = optimize_file

# call this with for arguments
# reader, writer, value, filename.
# If filename exists, it will just load that by calling writer on it.
# if it doesn't exist, it will compute the value and call writer(value, filename)
# Either way it will return the value.
persist_disk = dask.delayed(_persist_disk, pure=True)


def pickle_reader(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)

def pickle_writer(obj, filename):
    with open(filename, 'wb') as file:
        pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)
        
pickle_disk = partial(persist_disk, pickle_reader, pickle_writer)


