__author__ = 'alcifuen'
import networkx as nx
import enum
import log

Operator = enum.Enum('operator', 'xor sequence parallel loop')


class Cut:

    partition = None

    def __init__(self, operator, partition):
        self.operator = operator
        self.partition = partition

    def is_valid(self):
        if self.operator is None or len(self.partition) <= 1:
            return False
        for part in self.partition:
            if len(part) == 0:
                return False
        return True

    def __str__(self):
        return str(self.operator) + + str(self.partition)


class CutFinder(object):
    def __init__(self):
        pass


class CutFinderEKS(CutFinder):

    def find_cut(self, input_log, log_info, miner_state):
        kSuccesor = UpToKSuccessor.fromLog(input_log) #ANDRES: IMPLEMENTAR UPTOKSUCCESSOR
        exhaustive = Exhaustive(input_log, log_info, kSuccesor, miner_state) #ANDRES: IMPLEMENTAR EXHAUSTIVE
        r = exhaustive.try_all()
        return r.cut


class CutFinderIMExclusiveChoice(CutFinder):

    def find_cut(self, input_log, log_info, miner_state):
        return self.find_cut_dfg(log_info.directly_follows_graph)

    def find_cut_dfg_ms(self, dfg, miner_state):
        return self.find_cut_dfg(dfg)

    def find_cut_dfg(self, dfg):
        connected_components = list(nx.connected_components(dfg.to_undirected()))
        #connected_components = list(nx.connected_components(dfg))
        return Cut(Operator.xor, connected_components)


class CutFinderIMSequence(CutFinder):
    scr2 = None

    def find_cut(self, input_log, log_info, miner_state):
        return self.find_cut_dfg(log_info.directly_follows_graph)

    def find_cut_dfg_ms(self, dfg, miner_state):
        return self.find_cut_dfg(dfg)

    def find_cut_dfg(self, dfg):
        condensed_graph_1 = nx.DiGraph()
        for scc in nx.strongly_connected_components(dfg):
            condensed_graph_1.add_node(tuple(scc))
        for edge in dfg.edges():
            sccu = None
            sccv = None
            u = edge[0]
            for scc in nx.strongly_connected_components(dfg):
                if u in scc:
                    sccu = tuple(scc)
            v = edge[1]
            for scc in nx.strongly_connected_components(dfg):
                if v in scc:
                    sccv = tuple(scc)
            if sccv != sccu:
                condensed_graph_1.add_edge(sccu, sccv)
        xor_graph = nx.DiGraph()
        xor_graph.add_nodes_from(condensed_graph_1)
        scr1 = CutFinderIMSequenceReachability(condensed_graph_1)
        for node in condensed_graph_1.nodes():
            reachable_from_to = scr1.get_reachable_from_to(node)
            not_reachable = set(condensed_graph_1.nodes()).difference(reachable_from_to)
            if node in not_reachable:
                not_reachable.remove(node)
            for node2 in not_reachable:
                xor_graph.add_edge(node, node2)
        condensed_graph_2 = nx.DiGraph()
        for n in nx.strongly_connected_components(xor_graph):
            for n1 in n:
                condensed_graph_2.add_node(tuple(n1))
        for edge in condensed_graph_1.edges():
            sccu = None
            sccv = None
            u = edge[0]
            for scc in condensed_graph_2.nodes():
                if u[0] in scc:
                    sccu = tuple(scc)
            v = edge[1]
            for scc in condensed_graph_2.nodes():
                if v[0] in set(scc):
                    sccv = tuple(scc)
            if sccv != sccu:
                condensed_graph_2.add_edge(tuple(sccu), tuple(sccv))
        self.scr2 = CutFinderIMSequenceReachability(condensed_graph_2)
        result = []
        result.extend(set(condensed_graph_2.nodes()))
        result.sort(self.compare)
        return Cut(Operator.sequence, result)

    def compare(self, x, y):
        if y in self.scr2.get_reachable_from(x):
            return 1
        else:
            return -1


class CutFinderIMParallel(CutFinder):

    def find_cut_log_info_ms(self, log_info, miner_state):
        return self.find_cut(log_info.start_activities, log_info.end_activities, log_info.directly_follows_graph, None)

    def find_cut(self, start_activities, end_activities, dfg, minimum_self_distance_between):
        #noise filtering can have removed all start and end activities
        #if that is the case, return
        if len(start_activities) == 0 or len(end_activities) == 0:
            return None
        #construct the negated graph
        negated_graph = nx.DiGraph()
        #add the vertices
        negated_graph.add_nodes_from(dfg)
        #walk through the edges and negate them
        for e1 in dfg.nodes():
            for e2 in dfg.nodes():
                if e1 != e2:
                    found_edge = dfg.get_edge_data(e1, e2, default=False)
                    if found_edge is not False:
                        found_edge = True
                    found_rev_edge = dfg.get_edge_data(e2, e1, default=False)
                    if found_rev_edge is not False:
                        found_rev_edge = True
                    if not found_edge or not found_rev_edge:
                        negated_graph.add_edge(e1, e2)
        #If wanted, apply an extension to the IM algorithm to account for loops that
        #have the same directly-follows graph as a parallel operator would have.
        #Make sure that activities on the minimum-self-distance-path are not
        #separated by a parallel operator.
        if minimum_self_distance_between is not None:
            for activity in dfg.nodes():
                for activity2 in minimum_self_distance_between(activity):
                    negated_graph.add_edge(activity, activity2)
        #compute the connected components of the negated path
        connected_components = nx.strongly_connected_components(negated_graph) #DUDA
        #not all connected components are guaranteed to have start/end activities.
        ccs_with_start_end = []
        ccs_with_start = []
        ccs_with_end = []
        ccs_with_nothing = []
        for cc in connected_components:
            has_start = True
            if len(set(cc).intersection(set(start_activities))) == 0:
                has_start = False
            has_end = True
            if len(set(cc).intersection(set(end_activities))) == 0:
                has_end = False
            if has_start:
                if has_end:
                    ccs_with_start_end.append(cc)
                else:
                    ccs_with_start.append(cc)
            else:
                if has_end:
                    ccs_with_end.append(cc)
                else:
                    ccs_with_nothing.append(cc)
        #if there is no set with both start/end activities, there is no parallel cut.
        if len(ccs_with_start_end) == 0:
            return None
        #add full sets
        connected_components2 = set(ccs_with_start_end)
        #add combinations of end-only and start-only components
        start_counter = 0
        end_counter = 0
        while start_counter < len(ccs_with_start) and end_counter < len(ccs_with_end):
            set1 = set()
            for ccs in ccs_with_start[start_counter]:
                for cc in ccs:
                    set1.add(cc)
            for ccs in ccs_with_end[end_counter]:
                for cc in ccs:
                    set1.add(cc)
            connected_components2.add(set1)
            start_counter += 1
            end_counter += 1
        #the start-only components can be added to any set
        while start_counter < len(ccs_with_start):
            set2 = set(connected_components2[0])
            for ccs in ccs_with_start[start_counter]:
                for cc in ccs:
                    set2.add(cc)
            connected_components2[0] = set2
            start_counter += 1
        #the end-only components can be added to any set
        while end_counter < len(ccs_with_end):
            set3 = set(connected_components2[0])
            for ccs in ccs_with_end[end_counter]:
                for cc in ccs:
                    set3.add(cc)
            connected_components2[0] = set3
            end_counter += 1
        #the non-start-non-end components can be added to any set
        for ccs in ccs_with_nothing:
            set4 = set(connected_components2[0])
            for cc in ccs:
                set4.add(cc)
            connected_components2[0] = set4
        return Cut(Operator.parallel, connected_components2)


class CutFinderIMParallelWithMinimumSelfDistance(CutFinder):

    def find_cut(self, input_log, log_info, miner_state):
        return CutFinderIMParallel().find_cut(log_info.start_activities, log_info.end_activities, log_info.directly_follows_graph, log.LogInfo.get_min_self_distances_between_act)


class CutFinderIMLoop(CutFinder):

    def find_cut(self, input_log, log_info, miner_state):
        return self.find_cut_start_act_end_act_dfg(log_info.start_activities, log_info.end_activities, log_info.directly_follows_graph)

    def find_cut_start_act_end_act_dfg(self, start_activities, end_activities, graph):
        connected_components = {}
        #initialize the start and end activities as a connected component
        for start_activity in set(start_activities):
            connected_components[start_activity] = 0
        for end_activity in set(end_activities):
            connected_components[end_activity] = 0
        #find the other connected components
        ccs = 1
        for node in graph.nodes():
            if node not in connected_components.keys():
                self.label_connected_components(graph, node, connected_components, ccs)
                ccs += 1
        #find the start activities of each component
        sub_start_activities = {}
        cc = 0
        while cc < ccs:
            sub_start_activities[cc] = {}
            cc += 1
        for node in graph.nodes():
            cc = connected_components[node]
            for edge in graph.in_edges(node):
                if cc != connected_components[edge[0]]:
                    #this is a start activity
                    start = set(sub_start_activities[cc])
                    start.add(node)
                    sub_start_activities[cc] = start
        #find the end activities of each component
        sub_end_activities = {}
        cc = 0
        while cc < ccs:
            sub_end_activities[cc] = {}
            cc += 1
        for node in graph.nodes():
            cc = connected_components[node]
            for edge in graph.out_edges(node):
                if cc != connected_components[edge[1]]:
                    #this is an end activity
                    end = set(sub_end_activities[cc])
                    end.add(node)
                    sub_end_activities[cc] = end
        #initialize the candidates
        candidates = []
        candidates.append(False)
        for i in range(1, ccs):
            candidates[i] = True
        #exclude all candidates that are reachable from the start activities
        #(that are not an end activity)
        for start_activity in set(start_activities):
            if start_activity not in end_activities:
                for edge in graph.out_edges(start_activity):
                    candidates[connected_components[edge[1]]] = False
        #exclude all candidates that can reach an end activity
        #(which is not a start activity)
        for start_activity in set(end_activities):
            if end_activity not in start_activities:
                for edge in graph.in_edges(end_activity):
                    candidates[connected_components[edge[0]]] = False
        #exclude all candidates that have no connection from all start activities
        cc = 0
        while cc < ccs:
            end = sub_end_activities[cc]
            for node1 in end:
                for node2 in set(start_activities):
                    found_edge = graph.get_edge_data(node1, node2, default=False)
                    if not found_edge:
                        candidates[cc] = False
            cc += 1
        #exclude all candidates that have no connection from all end activites
        cc = 0
        while cc < ccs:
            start = sub_start_activities[cc]
            for node1 in start:
                for node2 in set(end_activities):
                    found_edge = graph.get_edge_data(node2, node1, default=False)
                    if not found_edge:
                        candidates[cc] = False
            cc += 1
        #make the lists of sets of nodes
        result = []
        for i in range(0, ccs):
            result.append(set())
        #divide the activities
        for node in graph.nodes():
            if candidates[connected_components[node]]:
                index = connected_components[node]
            else:
                index = 0
            s = result[index]
            s.add(node)
            result[index] = s
        #filter the empty sets
        result2 = []
        for s in result:
            if len(s) > 0:
                result2.add(s)
        return Cut(Operator.loop, result2)

    def label_connected_components(self, graph, node, connected_components, connected_component):
        if node not in connected_components.keys:
            connected_components[node] = connected_component
            for edge in graph.edges:
                self.label_connected_components(graph, edge[0], connected_components, connected_component)
                self.label_connected_components(graph, edge[1], connected_components, connected_component)


class CutFinderIMSequenceReachability:

    def __init__(self, graph):
        self.reachable_to = {}
        self.reachable_from = {}
        self.condensed_graph = graph

    def get_reachable_from_to(self, node):
        r = self.find_reachable_to(node)
        r.update(self.find_reachable_from(node))
        return r

    def get_reachable_from(self, node):
        return self.find_reachable_from(node)

    def find_reachable_to(self, from_node):
        if from_node not in self.reachable_to:
            reached = set()
            for edge in self.condensed_graph.out_edges(from_node):
                target = edge[1]
                reached.add(target)
                reached.update(self.find_reachable_to(target))
            self.reachable_to[from_node] = reached
        return self.reachable_to[from_node]

    def find_reachable_from(self, to_node):
        if to_node not in self.reachable_from:
            reached = set()
            for edge in self.condensed_graph.in_edges(to_node):
                target = edge[0]
                reached.add(target)
                reached.update(self.find_reachable_from(target))
            self.reachable_from[to_node] = reached
        return self.reachable_from[to_node]


class CutFinderIM(CutFinder):

    cut_finders = [CutFinderIMExclusiveChoice(), CutFinderIMSequence(), CutFinderIMParallelWithMinimumSelfDistance(), CutFinderIMLoop(), CutFinderIMParallel()]

    def find_cut(self, input_log, log_info, miner_state):
        c = None
        for cf in self.cut_finders:
            if c is None or not c.is_valid():
                c = cf.find_cut(input_log, log_info, miner_state)
            else:
                break
        return c