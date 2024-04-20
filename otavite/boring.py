from itertools import product
from more_itertools import pairwise
from cadmium.data import CuttingTool,LinearCut,ArcCut
from .util import passes


def onion_boring(
        bore_center,
        bore_diameter,
        bore_depth,
        tool : CuttingTool,
        step_down,
        step_over,
):
    assert step_down > 0
    assert 0 <= step_over < 1
    assert 0 < bore_depth < tool.max_cutting_depth

    for pz,z in pairwise(passes(bore_center[2],bore_center[2]-bore_depth,step_down)):
        pz_center = (bore_center[0],bore_center[1],pz)
        z_center = (bore_center[0],bore_center[1],z)
        yield LinearCut(pz_center,z_center)
        for pr,r in pairwise(passes(0,bore_diameter/2-tool.end_diameter/2,tool.end_diameter*(1-step_over))):
            pr_start = (bore_center[0]-pr,bore_center[1],z)
            r_start = (bore_center[0]-r,bore_center[1],z)
            yield LinearCut(pr_start,r_start)
            yield ArcCut(r_start,r_start,(r,0,0))

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