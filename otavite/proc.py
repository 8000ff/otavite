from functools import reduce
from typing import Iterable, Union
from cadmium.data import *
import networkx as nx
from more_itertools import flatten, pairwise
from itertools import chain, product
from dataclasses import replace
from otavite.util import pipeline

def map_graph(graph : nx.DiGraph, *steps):
    m = { u:pipeline(u,*steps) for u in graph.nodes}
    g = nx.DiGraph()
    for u in graph.nodes:
        g.add_edges_from(pairwise(m[u]))
    for u,v in nx.transitive_closure_dag(graph).edges:
        g.add_edges_from(product(m[u][-1::1],m[v][0:1]))
    return nx.transitive_reduction(g)

def cutting_operation_preprocessor(operation : CuttingOperation,*steps):
    return replace(operation,cuts=map_graph(operation.cuts,*steps))

def probing_operation_preprocessor(operation : ProbingOperation,*steps):
    return replace(operation,probes=map_graph(operation.probes,*steps))

def job_preprocessor(job : Job,*steps):
    return replace(job,operations=map_graph(job.operations,*steps))

def decompose_full_helix(cut : Cut):
    if isinstance(cut,ArcCut) and cut.turns > 1:
        assert cut.start[2] != cut.stop[2]
        assert cut.start[:2] == cut.stop[:2]
        assert cut.offset[2] == 0
        step_down = (cut.stop[2] - cut.start[2]) / cut.turns
        for turn in range(cut.turns):
            start = (*cut.start[:2],cut.start[2] + step_down*turn)
            stop = (*cut.stop[:2],cut.start[2] + step_down*(turn+1))
            yield replace(cut,start=start,stop=stop,turns=1)
    else:
        yield cut

def set_feed(feed : float):
    def f(move : Move):
        if isinstance(move,Union[ArcCut,LinearCut,LinearProbe]):
            yield replace(move,feed=feed)
        else:
            yield move
    return f

def set_speed(speed : float):
    def f(cut : Cut):
        if isinstance(cut,NoneCut):
            yield cut
        else:
            yield replace(cut,speed=speed)
    return f

def trim_zero_length_cut(cut : Cut):
    if isinstance(cut,LinearCut) and cut.start == cut.stop:
        pass
    # TODO implement ArcCut case
    else:
        yield cut

def remove_redundant_feed(gcode : Iterable[GCode]):
    last_feed = None
    for command in gcode:
        if isinstance(command,GCodeFeedRate):
            if last_feed != command.word.value:
                last_feed = command.word.value
                yield command
        else:
            yield command