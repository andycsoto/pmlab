# -*- coding: utf-8 -*-
"""
Created on Wed Jan 07 12:27:30 2015

@author: Victor
"""
import utils
import networkx as nx
import base_case_finders as bcf
import cut_n_finders
import log_splitter as ls
import resources
import fall_through as ft


class MiningParameters(object):
    base_case_finders = None
    cut_finders = None
    log_splitter = None
    fall_throughs = None
    noise_threshold = None

    def __init__(self, noise_threshold):
        self.noise_threshold = noise_threshold


class MiningParametersIM(MiningParameters):

    def __init__(self, noise_threshold):
        super(MiningParametersIM, self).__init__(noise_threshold)
        self.base_case_finders = [bcf.BaseCaseFinderIM()]
        self.cut_finders = [cut_n_finders.CutFinderIM()]
        self.log_splitter = ls.LogSplitterIMi()
        self.fall_throughs = [ft.FallThroughTauLoop(), ft.FallThroughFlower()]


class MinerState:

    discarded_events = {}
    parameters = None

    def __init__(self, parameters):
        self.parameters = parameters
        self.discarded_events = {}