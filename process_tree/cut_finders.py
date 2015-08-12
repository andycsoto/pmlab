__author__ = 'alcifuen'

import networkx as nx
import mining


class CutFinder:

    def __init__(self):
        pass


class CutFinderIM(CutFinder):

    cutFinders = [CutFinderIMExclusiveChoice(), CutFinderIMSequence(), CutFinderIMParallelWithMinimumSelfDistance(), CutFinderIMLoop(), CutFinderIMParallel()]

    def find_cut(self, input_log, log_info, miner_state):
        c = None
        it = iter(miner_state.parameters.cut_finders)
        while True:
            next_cf = next(it, None)
            if next_cf is not None and (c is None or not c.is_valid()):
                c = next_cf.find_cut(input_log, log_info, miner_state)
            else:
                break
        return c


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
        connected_components = nx.strongly_connected_components(dfg) #BUG de sander?
        return mining.Cut(Operator.xor, connected_components)


class CutFinderIMSequence(CutFinder):

    def find_cut(self, input_log, log_info, miner_state):
        return self.find_cut_dfg(log_info.directly_follows_graph)

    def find_cut_dfg_ms(self, dfg, miner_state):
        return self.find_cut_dfg(dfg)

    def find_cut_dfg(self, dfg):
        sccs = nx.strongly_connected_components(dfg)
        condensed_graph_1 = nx.DiGraph()
        condensed_graph_1.add_nodes_from(sccs)
        for edge in dfg.edges:
            u = edge[0]
            for scc in sccs:
                if u in scc:
                    sccu = scc
            v = edge[1]
            for scc in sccs:
                if v in scc:
                    sccv = scc
            if sccv != sccu:
                condensed_graph_1.add_edge(sccu, sccv)
        xor_graph = nx.DiGraph()
        xor_graph.add_nodes_from(condensed_graph_1)
        scr1 = CutFinderIMSequenceReachability(condensed_graph_1)
        for node in condensed_graph_1.nodes:
            reachable_from_to = scr1.get_reachable_from_to(node)
            not_reachable = difference(condensed_graph_1.nodes, reachable_from_to) #implementar difference
            not_reachable.remove(node) #revisar si remove hace lo mismo que en prom
            for node2 in not_reachable:
                xor_graph.add_edge(node, node2)
        xor_condensed_nodes = nx.strongly_connected_components(xor_graph) #BUG3 Sander?
        condensed_graph_2 = nx.DiGraph()
        condensed_graph_2.add_nodes_from(xor_condensed_nodes)
        for edge in condensed_graph_1.edges:
            u = edge[0]
            for scc in condensed_graph_2.nodes:
                if u.iterator.next() in scc:
                    sccu = scc
            v = edge[1]
            for scc in condensed_graph_2.nodes:
                if v.iterator.next() in scc:
                    sccu = scc
            if sccv != sccu:
                condensed_graph_2.add_edge(sccu, sccv)
        scr2 = CutFinderIMSequenceReachability(condensed_graph_2)
        result = []
        result.addAll(condensed_graph_2.nodes) #implementar addAll
        sort(result, Comparator) #implementar comparador
        return mining.Cut(Operator.sequence, result)


class CutFinderIMParallel(CutFinder):

    def find_cut_log_info_ms(self, log_info, miner_state):
        return self.find_cut(log_info.start_activities, log_info.end_activities, log_info.directly_follows_graph, None, None)

    def find_cut(self, start_activities, end_activities, dfg, minimum_self_distance_between, *args):
        #noise filtering can have removed all start and end activities
        #if that is the case, return
        if len(start_activities) == 0 or len(end_activities) == 0:
            return None
        #construct the negated graph
        negated_graph = nx.Digraph()
        #add the vertices
        negated_graph.add_nodes_from(dfg)
        #walk through the edges and negate them
        for e1 in dfg.nodes:
            for e2 in dfg.nodes:
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
        if minimum_self_distance_between(*args) is not None:
            for activity in dfg.nodes:
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
        return mining.Cut(Operator.parallel, connected_components2)


class CutFinderIMParallelWithMinimumSelfDistance(CutFinder):

    def find_cut(self, input_log, log_info, miner_state, activity):
        return CutFinderIMParallel.find_cut(log_info.start_activities, log_info.end_activities, log_info.directly_follows_graph, log_info.get_min_self_distances_between_act, activity)


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
        for node in dfg.nodes:
            if node not in connected_components.keys():
                label_connected_components(graph, node, connected_components, ccs)
                ccs += 1
        #find the start activities of each component
        sub_start_activities = {}
        cc = 0
        while cc < ccs:
            sub_start_activities[cc] = {}
        for node in graph.nodes:
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
        for node in graph.nodes:
            cc = connected_components[node]
            for edge in graph.out_edges(node):
                if cc != connected_components[edge[1]]:
                    #this is an end activity
                    end = set(sub_end_activities[cc])
                    end.add(node)
                    sub_end_activities[cc] = end
        #initialize the candidates
        candidates = []
        candidates[0] = False
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
        #exclude all candidates that have no connection from all end activites
        cc = 0
        while cc < ccs:
            start = sub_start_activities[cc]
            for node1 in start:
                for node2 in set(end_activities):
                    found_edge = graph.get_edge_data(node2, node1, default=False)
                    if not found_edge:
                        candidates[cc] = False
        #make the lists of sets of nodes
        result = []
        for i in range(0, ccs):
            result.append(set())
        #divide the activities
        for node in graph.nodes:
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
        return mining.Cut(Operator.loop, result2)


class CutFinderIMSequenceReachability:

    def __init__(self, graph):
        self.reachable_to = {}
        self.reachable_from = {}
        self.condensed_graph = graph

    def get_reachable_from_to(self, node):
        pass


    def get_reachable_from(self, node):
        return self.find_reachable_from(node)

    def find_reachable_to(self, from_node):
        pass

    def find_reachable_from(self, to_node):
        pass

