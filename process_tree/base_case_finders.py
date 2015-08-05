__author__ = 'alcifuen'
import utils


class BaseCaseFinder:

    def __init__(self):
        pass

    def find_base_cases(self, input_log, log_info, tree, miner_state):
        pass


class BaseCaseFinderIMiEmptyLog(BaseCaseFinder):

    def find_base_cases(self, input_log, log_info, tree, miner_state):
        if log_info.number_of_events == 0:
            node = "tau"
            node.set_process_tree(tree)
            tree.add_node(node)
            return node
        return None


class BaseCaseFinderIMiEmptyTrace(BaseCaseFinder):

    def find_base_cases(self, input_log, log_info, tree, miner_state):
        if log_info.number_of_empty_traces != 0:
            if log_info.number_of_empty_traces < (log_info.highest_trace_cardinality * miner_state.parameters.noise_threshold):
                new_node = utils.inductive_mine_node(input_log, tree, miner_state)
                return new_node
            else:
                new_node = ""
                new_node.set_process_tree(tree)
                tree.add_node(new_node)

                #adding tau
                tau = "tau"
                tau.set_process_tree(tree)
                tree.add_node(tau)
                new_node.addChild(tau)

                #Recursivo
                child = utils.inductive_mine_node(input_log, tree, miner_state)
                new_node.add_child(child)
                return new_node
        return None


class BaseCaseFinderIMiSingleActivity(BaseCaseFinder):

    def find_base_cases(self, input_log, log_info, tree, miner_state):
        if log_info.activities.size() == 1:
            p = input_log.size() / (log_info.numberOfEvents + input_log.size() * 1.0)
            if 0.5 - miner_state.parameters.noiseThreshold <= p <= 0.5 + miner_state.parameters.noiseThreshold:
                activity = log_info.activities.iterator().next()
                node = activity.id
                node.set_process_tree(tree)
                tree.add_node(node)
        return None