from itertools import pairwise
from cadmium.data import *
import networkx as nx
from pygcode import GCodeLinearMove,GCodeStopSpindle,GCodeEndProgram
from typing import Iterable, Union
from more_itertools import first

# stand optimization identifies consecutive cuts with simple dependencies then produces a dfs path
def strand_bfs_cutting_path_finder(G : nx.DiGraph):
    H = nx.DiGraph()
    for u in G.nodes:
        H.add_node(u)
    for u,v in G.edges:
        if u == NoneCut():
            continue
        if u.stop == v.start and G.out_degree(u) == 1 and G.in_degree(v) == 1:
            H.add_edge(u,v)
    J = nx.DiGraph()
    for c in nx.weakly_connected_components(H):
        h = first( u for u in c if H.in_degree(u) == 0)
        t = first( u for u in c if H.out_degree(u) == 0)
        J.add_node(tuple(nx.shortest_path(H,h,t)))
    n2c = {node:component for component in J.nodes for node in component}.get
    for u in J.nodes:
        h,t = u[0],u[-1]
        for v in map(n2c,G.predecessors(h)):
            if u == v:
                continue
            J.add_edge(v,u)
        for v in map(n2c,G.successors(t)):
            if u == v:
                continue
            J.add_edge(u,v)
    for u in nx.bfs_tree(J,n2c(NoneCut())).nodes:
        yield from u

def safe_height_cutting_path_solver(safe_height : float,hop_feed : float=100):
    def f(path : Iterable[Cut]):
        for u,v in pairwise(path):
            u : Cut
            v : Cut
            jump = False
            first = False
            if isinstance(u,NoneCut):
                jump = True
                first = True
                yield GCodeFeedRate(hop_feed)
                yield GCodeLinearMove(Z=safe_height)
                yield GCodeLinearMove(X=v.start[0],Y=v.start[1],Z=safe_height)
            elif u.stop != v.start: # cuts are not continuous
                jump = True
                yield GCodeFeedRate(hop_feed)
                yield GCodeLinearMove(X=u.stop[0],Y=u.stop[1],Z=safe_height)
                yield GCodeLinearMove(X=v.start[0],Y=v.start[1],Z=safe_height)
            yield from v.gcode(include_start=jump,include_stop=True,include_feed=True,include_speed=True,include_spindle_start=first)
        yield GCodeFeedRate(hop_feed)
        yield GCodeLinearMove(Z=safe_height)
    return f

def dfs_job_path_finder(job : Job):
    for u in nx.bfs_tree(job.operations,NoneOperation()).nodes:
        yield u

def solve(
        job : Job,
        machine : Machine,
        cutting_path_finder=None,
        cutting_path_solver=None,
        probing_path_finder=None,
        probing_path_solver=None,
        job_path_finder=None,
):
    for u,v in pairwise(job_path_finder(job)):
        u : Operation
        v : Operation
        d : Setup = job.operations.edges[u,v]
        if u != NoneOperation():
            if u.tool != v.tool:
                yield GCodeStopSpindle()
                yield from machine.useTool(v.tool)
            if d != None:
                yield GCodeStopSpindle()
                yield from machine.park()
        if isinstance(v,CuttingOperation):
            if not cutting_path_finder:
                raise ValueError('Cutting operation finder not provided')
            if not cutting_path_solver:
                raise ValueError('Cutting operation solver not provided')
            yield from cutting_path_solver(cutting_path_finder(v.cuts))
        elif isinstance(v,ProbingOperation):
            if not probing_path_finder:
                raise ValueError('Probing operation finder not provided')
            if not probing_path_solver:
                raise ValueError('Probing operation solver not provided')
            yield from probing_path_solver(probing_path_finder(v.prob))
        else:
            raise ValueError(f'Operation type {type(v)} not supported')
    yield GCodeStopSpindle()
    yield from machine.park()
    yield GCodeEndProgram()


