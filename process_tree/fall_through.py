__author__ = 'alcifuen'
import utils


class FallThrough():
    def __init__(self):
        pass

    def fall_through(self, log, log_info, tree, miner_state):
        pass


class FallThroughTauLoop(FallThrough):
    def fall_through(self, log, log_info, process_tree, miner_state):
        if log_info.activities.size() > 1:
            sublog = []
            #try to find a tau loop
            number_of_times_tau_taken = 0
            for trace in log:
                number_of_times_tau_taken += self.filter_trace(sublog, trace, log.get_case_freq(trace), log_info.start_activities)
            if sublog.size() > log.size():
                loop = ""
                loop.setProcessTree(process_tree)
                process_tree.addNode(loop)
                body = utils.inductive_mine_node(sublog, process_tree, miner_state)
                loop.addChild(body)
                redo = "tau"
                redo.setProcessTree(process_tree)
                process_tree.addNode(redo)
                loop.addChild(redo)
                exitNode = "tau"
                exitNode.setProcessTree(process_tree)
                process_tree.addNode(exitNode)
                loop.addChild(exitNode)

                return loop
        return None

    def filter_trace(self, sublog, trace, cardinality, start_activities):
        first = True
        number_of_times_tau_taken = 0
        partial_trace = []
        for event in trace:
            if first is False and event not in start_activities:
                sublog.add(partial_trace, cardinality)
                partial_trace = []
                first = True
                number_of_times_tau_taken = number_of_times_tau_taken + cardinality
            partial_trace.add(event)
            first = False
        sublog.add(partial_trace, cardinality)
        return number_of_times_tau_taken


class FallThroughFlower(FallThrough):
    def fall_through(self, log, log_info, process_tree, miner_state):
        loop_node = ""
        loop_node.setProcessTree(process_tree)
        process_tree.addNode(loop_node)
        #body: tau
        body = "tau"
        body.setProcessTree(process_tree)
        process_tree.addNode(body)
        loop_node.addChild(body)
        #redo xor/activity
        if log_info.activities.size() == 1:
            xorNode = loop_node
        else:
            xorNode = ""
            xorNode.setProcessTree(process_tree)
            process_tree.addNode(xorNode)
            loop_node.addChild(xorNode)
        for activity in log_info.activities:
            child = activity.id
            child.setProcessTree(process_tree)
            process_tree.addNode(child)
            xorNode.addChild(child)
        tau2 = "tau"
        tau2.setProcessTree(process_tree)
        process_tree.addNode(tau2)
        loop_node.addChild(tau2)
        return loop_node