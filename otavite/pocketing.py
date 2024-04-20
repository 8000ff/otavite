from itertools import product
from more_itertools import pairwise
from cadmium.data import Tool,LinearCut
from .util import passes
from enum import Enum

import numpy as np

def rectangular_pocket_AB(
    a,
    b,
    tool : Tool,
    step_down,
    step_over
):
    assert step_down > 0
    assert 0 <= step_over < 1
    assert 0 < abs(b[2]-a[2]) <= tool.max_cutting_depth
    step = tool.end_diameter * step_over
    a,b = np.array(a),np.array(b)
    a,b = np.fmax(a,b),np.fmin(a,b)
    ab,ba = b-a,a-b
    focus_offset = np.fmax([0,0],[ba[0]-ba[1],ba[1]-ba[0]])/2
    focus = a[:2] + ab[:2]/2 - focus_offset, a[:2] + ab[:2]/2 + focus_offset
    # dirty patch
    last = None
    for pz,z in pairwise(passes(a[2],b[2],step_down)):
        yield LinearCut([*focus[0],pz],[*focus[0],z])
        yield LinearCut([*focus[0],z],[*focus[1],z])
        for pxy, xy in pairwise(passes(0,min(ba[:2])/2-tool.radius,step)):
            pcorner = focus[1] + np.array([pxy,pxy])
            corner = focus[1] + np.array([xy,xy])
            ocorner = focus[0] - np.array([xy,xy])
            yield LinearCut([*pcorner,z],[*corner,z])
            yield from ( LinearCut(i,j) for i,j in pairwise([
                [corner[0],corner[1],z],
                [corner[0],ocorner[1],z],
                [ocorner[0],ocorner[1],z],
                [ocorner[0],corner[1],z],
                [corner[0],corner[1],z]
            ]))
            last = (corner[0],corner[1],z)
        if z == b[2]:
            yield LinearCut(last,(*(a[:2]+ab[:2]/2),a[2]))
        else:
            yield LinearCut(last,(*focus[0],z))