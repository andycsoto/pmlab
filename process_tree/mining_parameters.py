# -*- coding: utf-8 -*-
"""
Created on Wed Jan 07 12:27:30 2015

@author: Victor
"""
import utils
import networkx as nx
import base_case_finders as bcf
import cut_finders as cf
import resources

class MiningParameters:
    base_case_finders = None
    cut_finders = None
    log_splitter = None
    fall_throughs = None
    noise_threshold = None

    def __init__(self, noise_threshold):
        self.noise_threshold = noise_threshold


class MiningParametersEKS(MiningParameters):

    def __init__(self, noise_threshold):
        super(MiningParametersEKS, self).__init__(noise_threshold)
        self.base_case_finders = [bcf.BaseCaseFinderIMiEmptyLog(), bcf.BaseCaseFinderIMiEmptyTrace(), bcf.BaseCaseFinderIMiSingleActivity()]
        self.cut_finders = [cf.CutFinderIM(), cf.CutFinderEKS()]


class MinerState:
    discarded_events = {}
    parameters = None

    def __init__(self, parameters):
        self.parameters = parameters
        self.discarded_events = {}