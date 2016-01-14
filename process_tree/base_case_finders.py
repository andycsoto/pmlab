__author__ = 'alcifuen'
import utils
import task


class BaseCaseFinder:

    def __init__(self):
        pass

    def find_base_cases(self, input_log, log_info, tree, miner_state):
        pass


class BaseCaseFinderIM(BaseCaseFinder):

    def find_base_cases(self, input_log, log_info, tree, miner_state):
        if len(log_info.activities.keys()) == 1 and log_info.number_of_epsilon_traces == 0 and log_info.number_of_events == len(input_log.cases):
            activity = iter(log_info.activities).next()
            node = task.Task(name=str(activity))
            node.tree = tree
            tree.add_node(node)
            return node
        elif len(log_info.activities.keys()) == 0:
            node = task.Automatic("tau")
            node.tree = tree
            tree.add_node(node)
            return node
        return None


class BaseCaseFinderIMiEmptyLog(BaseCaseFinder):

    def find_base_cases(self, input_log, log_info, tree, miner_state):
        if log_info.number_of_events == 0:
            node = task.Automatic("tau")
            node.tree = tree
            tree.add_node(node)
            return node
        return None


class BaseCaseFinderIMiEmptyTrace(BaseCaseFinder):

    def find_base_cases(self, input_log, log_info, tree, miner_state):
        if log_info.number_of_epsilon_traces != 0:
            if log_info.number_of_epsilon_traces < (log_info.highest_trace_cardinality * miner_state.parameters.noise_threshold):
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
        if len(log_info.activities) == 1:
            p = len(input_log.cases) / (log_info.number_of_events + len(input_log.cases) * 1.0)
            if 0.5 - miner_state.parameters.noise_threshold <= p <= 0.5 + miner_state.parameters.noise_threshold:
                activity = iter(log_info.activities).next()
                node = task.Task(name=str(activity))
                node.tree = tree
                tree.add_node(node)
                return node
        return None
