from itertools import product
from more_itertools import pairwise
from cadmium.data import CuttingTool,LinearCut,ArcCut
from .util import passes

def helical_boring(
        bore_center,
        bore_diameter,
        bore_depth,
        tool : CuttingTool,
        step_down,
):
    assert step_down > 0
    assert 0 < bore_depth < tool.max_cutting_depth
    assert bore_diameter/2 < tool.end_diameter < bore_diameter

    remaining_depth = bore_depth%step_down
    turns = bore_depth//step_down

    offset = tool.end_diameter/2 - bore_diameter/2
    start = (bore_center[0]-offset,bore_center[1],bore_center[2])
    mid = (start[0],start[1],start[2]-bore_depth+remaining_depth)
    bottom = (start[0],start[1],start[2]-bore_depth)

    yield ArcCut(start,mid,(offset,0,0),turns=turns)
    yield ArcCut(mid,bottom,(offset,0,0),turns=1)
    yield ArcCut(bottom,bottom,(offset,0,0),turns=1)
    yield LinearCut(bottom,bore_center)

def helical_over_boring(
        bore_center,
        bore_diameter,
        bore_depth,
        tool : CuttingTool,
        step_down,
        step_over,
):
    assert step_down > 0
    assert 0 < bore_depth < tool.max_cutting_depth
    assert tool.end_diameter < bore_diameter

    bore_radius = bore_diameter/2

    remaining_depth = bore_depth%step_down
    turns = int(bore_depth//step_down)

    step = tool.end_diameter * step_over

    for i,(u,v) in enumerate(pairwise(passes(step,bore_radius-tool.end_diameter/2,step))):
        offset = v
        if i%2:
            # start from top
            start = (bore_center[0]-offset,bore_center[1],bore_center[2])
            mid = (start[0],start[1],start[2]-bore_depth+remaining_depth)
            bottom = (start[0],start[1],start[2]-bore_depth)
            ub = (bore_center[0]-u,start[1],start[2])

            yield LinearCut(ub,start)
            yield ArcCut(start,mid,(offset,0,0),turns=turns)
            yield ArcCut(mid,bottom,(offset,0,0),turns=1)
            yield ArcCut(bottom,bottom,(offset,0,0),turns=1)
        else:
            # start from bottom
            start = (bore_center[0]-offset,bore_center[1],bore_center[2]-bore_depth)
            mid = (start[0],start[1],start[2]+bore_depth-remaining_depth)
            bottom = (start[0],start[1],start[2]+bore_depth)
            ub = (bore_center[0]-u,start[1],start[2])

            yield LinearCut(ub,start)
            yield ArcCut(start,mid,(offset,0,0),turns=turns)
            yield ArcCut(mid,bottom,(offset,0,0),turns=1)
            yield ArcCut(bottom,bottom,(offset,0,0),turns=1)
            # vb = (bore_center[0]-v,bottom[1],bottom[2])
            # yield LinearCut(bottom,vb)