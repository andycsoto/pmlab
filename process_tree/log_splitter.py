__author__ = 'alcifuen'

from cut_n_finders import Cut
from cut_n_finders import Operator
import log


class LogSplitter():

    def __init__(self):
        pass

    class LogSplitResult:
        def __init__(self, sublogs, noise):
            self.sublogs = sublogs
            self.discarded_events = noise

    def split(self, log, log_info, cut, miner_state):
        pass


class LogSplitterIMi(LogSplitter):

    def split(self, input_log, log_info, cut, miner_state):
        result = []     #List<IMLog>
        noise = {}      #MultiSet<XEventClass>
        map_sigma_2_sublog = {}    #Map<Set<XEventClass>, IMLog>
        map_activity_2_sigma = {}  #Map<XEventClass, Set<XEventClass>>
        for sigma in cut.partition:
            sublog = log.Log()
            result.append(sublog)
            map_sigma_2_sublog[sigma] = sublog
            for activity in sigma:
                map_activity_2_sigma[activity] = sigma
        for trace in input_log.get_uniq_cases():
            if cut.operator == Operator.xor:
                self.split_xor(result, trace, cut.partition, input_log.get_case_freq(list(trace)), map_sigma_2_sublog, map_activity_2_sigma, noise)
            elif cut.operator == Operator.sequence:
                self.split_sequence(result, trace, cut.partition, input_log.get_case_freq(list(trace)), map_sigma_2_sublog, map_activity_2_sigma, noise)
            elif cut.operator == Operator.parallel:
                self.split_parallel(result, trace, cut.partition, input_log.get_case_freq(list(trace)), map_sigma_2_sublog, map_activity_2_sigma, noise)
            elif cut.operator == Operator.loop:
                self.split_loop(result, trace, cut.partition, input_log.get_case_freq(list(trace)), map_sigma_2_sublog, map_activity_2_sigma, noise)
        return LogSplitter.LogSplitResult(result, noise)

    def split_xor(self, result, trace, partition, cardinality, map_sigma_2_sublog, map_activity_2_sigma, noise):
        if len(trace) == 0:
            for sublog in result:
                sublog.add(trace, cardinality)
            return
        event_counter = {}
        for sigma in partition:
            event_counter[sigma] = 0
        max_counter = 0
        max_sigma = set()
        for event in trace:
            sigma = map_activity_2_sigma[event]
            new_counter = event_counter[sigma] + 1
            if new_counter > max_counter:
                max_counter = new_counter
                max_sigma = sigma
            event_counter[sigma] = new_counter
        new_trace = []
        for event in trace:
            if event in max_sigma:
                new_trace.append(event)
            else:
                noise.add(event, cardinality)
        sublog = map_sigma_2_sublog.get(max_sigma)
        for x in range(0, cardinality):
            sublog.cases.append(new_trace)
        map_sigma_2_sublog[max_sigma] = sublog

    def split_sequence(self, result, trace, partition, cardinality, map_sigma_2_sublog, map_activity_2_sigma, noise):
        at_position = 0
        last_position = 0
        ignore = set()
        i = 0
        for sigma in partition:
            if i < len(partition) - 1:
                at_position = self.find_optimal_split(trace, sigma, at_position, ignore)
            else:
                at_position = len(trace)
            ignore.update(sigma)
            new_trace = []
            for event in trace[last_position:at_position]:
                if event in sigma:
                    new_trace.append(event)
                else:
                    noise[event] = cardinality
            sublog = map_sigma_2_sublog.get(sigma)
            for x in range(0, cardinality):
                sublog.cases.append(new_trace)
            last_position = at_position
            i += 1

    def find_optimal_split(self, trace, sigma, start_position, ignore):
        position_least_cost = 0
        least_cost = 0
        cost = 0
        position = 0
        it = iter(trace)
        next_trace = ""
        while True:
            if next_trace is not None and position < start_position:
                position += 1
                position_least_cost += 1
                next_trace = next(it, None)
            else:
                break
        while True:
            event = next(it, None)
            if event is not None:
                if event in ignore:
                    pass
                elif event in sigma:
                    cost -= 1
                else:
                    cost += 1
                position += 1
                if cost < least_cost:
                    least_cost = cost
                    position_least_cost = position
            else:
                break
        return position_least_cost

    def split_parallel(self, result, trace, partition, cardinality, map_sigma_2_sublog, map_activity_2_sigma, noise):
        map_sigma_2_subtrace = {}  #Map<Set<XEventClass>, IMTrace>
        for sigma in partition:
            subtrace = []
            map_sigma_2_subtrace[sigma] = subtrace
        for event in trace:
            sigma = map_activity_2_sigma[event]
            map_sigma_2_subtrace[sigma].append(event)
        for sigma in partition:
            for x in range(0, cardinality):
                map_sigma_2_sublog[sigma].cases.append(map_sigma_2_subtrace[sigma])

    def split_loop(self, result, trace, partition, cardinality, map_sigma_2_sublog, map_activity_2_sigma, noise):
        partial_trace = []
        last_sigma = iter(partition).next()
        for event in trace:
            if event not in last_sigma:
                for x in range(0, cardinality):
                    map_sigma_2_sublog[last_sigma].cases.append(partial_trace)
                partial_trace = []
                last_sigma = map_activity_2_sigma[event]
            partial_trace.append(event)
        for x in range(0, cardinality):
            map_sigma_2_sublog[last_sigma].cases.append(partial_trace)
        if last_sigma != iter(partition).next():
            for x in range(0, cardinality):
                map_sigma_2_sublog[last_sigma].cases.append([])
