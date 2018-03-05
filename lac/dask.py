import pickle
from os.path import exists
from functools import partial

from toolz import valmap

import dask
from dask.rewrite import RewriteRule, RuleSet
from dask.delayed import Delayed
from dask.context import _globals
from dask.diagnostics import ProgressBar


ProgressBar().register()

def pickle_reader(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)

def pickle_writer(obj, filename):
    with open(filename, 'wb') as file:
        pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)
        

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

persist_disk = dask.delayed(_persist_disk, pure=True)
pickle_disk = partial(persist_disk, pickle_reader, pickle_writer)
_globals['delayed_optimize'] = optimize_file


