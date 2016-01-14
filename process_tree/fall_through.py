__author__ = 'alcifuen'
import utils
import block
import task
import log

class FallThrough():
    def __init__(self):
        pass

    def fall_through(self, log, log_info, tree, miner_state):
        pass


class FallThroughTauLoop(FallThrough):
    def fall_through(self, input_log, log_info, process_tree, miner_state):
        if len(log_info.activities.keys()) > 1:
            sublog = log.Log()
            #try to find a tau loop
            number_of_times_tau_taken = 0
            for trace in input_log.cases:
                number_of_times_tau_taken += self.filter_trace(sublog, trace, input_log.get_case_freq(trace), log_info.start_activities)
            if len(sublog.cases) > len(input_log.cases):
                loop = block.LoopXOR(None, "")
                utils.add_node(process_tree, loop)

                body = utils.inductive_mine_node(sublog, process_tree, miner_state)
                loop.add_child(body)

                redo = task.Automatic("tau")
                utils.add_node(process_tree, redo)
                loop.add_child(redo)

                exit_node = task.Automatic("tau")
                utils.add_node(process_tree, exit_node)
                loop.add_child(exit_node)

                return loop
        return None

    def filter_trace(self, sublog, trace, cardinality, start_activities):
        first = True
        number_of_times_tau_taken = 0
        partial_trace = []
        for event in trace:
            if first is False and event not in start_activities:
                for i in range(0, cardinality):
                    sublog.cases.append(partial_trace)
                partial_trace = []
                first = True
                number_of_times_tau_taken = number_of_times_tau_taken + cardinality
            partial_trace.append(event)
            first = False
        for i in range(0, cardinality):
            sublog.cases.append(partial_trace)
        return number_of_times_tau_taken


class FallThroughFlower(FallThrough):
    def fall_through(self, log, log_info, tree, miner_state):
        loop_node = block.LoopXOR(None,"")
        utils.add_node(tree, loop_node)

        body = task.Automatic("tau")
        utils.add_node(tree, body)
        loop_node.add_child(body)

        xor_node = None
        if len(log_info.activities.keys()) == 1:
            xor_node = loop_node
        else:
            xor_node = block.XOR(None,"")
            utils.add_node(tree, xor_node)
            loop_node.add_child(xor_node)

        for activity in log_info.activities:
            child = task.Task(name=str(activity))
            utils.add_node(tree, child)
            xor_node.add_child(child)

        tau2 = task.Automatic("tau")
        utils.add_node(tree, tau2)
        loop_node.add_child(tau2)

        return loop_node