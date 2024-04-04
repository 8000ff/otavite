import numpy as np
from cadmium.data import Cut,ArcCut
from typing import Union
import networkx as nx
from itertools import product,chain
from functools import reduce

# Returns a generator that yields the various CNC passes between two values
def passes(start,stop,step):
    assert step != 0
    assert start != stop
    yield from np.arange(start,stop,np.abs(step)*np.sign(stop-start))
    yield stop

def depends_on(sub : nx.DiGraph, dep : nx.DiGraph):
    yield from product(
        ( k for k,v in dep.out_degree() if v == 0 ),
        ( k for k,v in sub.in_degree() if v == 0 )
    )

def pipeline(x,*steps):
    return list(reduce(lambda xs,step: chain(*map(step,xs)),steps,[x]))