from more_itertools import pairwise
from cadmium.data import Tool,LinearCut
from enum import Enum

import numpy as np

from otavite.util import passes

# positive offset is outside, negative offset is inside
def rectangular_contour(a,b,tool : Tool,step_down, offset = 0):
    assert 0 < abs(b[2]-a[2]) <= tool.max_cutting_depth
    assert abs(offset) <= tool.radius
    assert step_down > 0
    a,b = np.array(a),np.array(b)
    a,b = np.fmax(a,b),np.fmin(a,b)
    a = a + np.array([offset,offset,0])
    b = b - np.array([offset,offset,0])
    for pz,z in pairwise(passes(a[2],b[2],step_down)):
        yield LinearCut([a[0],a[1],pz],[a[0],a[1],z])
        yield LinearCut([a[0],a[1],z],[a[0],b[1],z])
        yield LinearCut([a[0],b[1],z],[b[0],b[1],z])
        yield LinearCut([b[0],b[1],z],[b[0],a[1],z])
        yield LinearCut([b[0],a[1],z],[a[0],a[1],z])