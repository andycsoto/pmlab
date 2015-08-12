__author__ = 'alcifuen'

import mining


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

    def split(self, log, log_info, cut, miner_state):
        result = []     #List<IMLog>
        noise = {}      #MultiSet<XEventClass>
        map_sigma_2_sublog = {}    #Map<Set<XEventClass>, IMLog>
        map_activity_2_sigma = {}  #Map<XEventClass, Set<XEventClass>>
        for sigma in cut.partition():
            sublog = log.Log()
            result.append(sublog)
            map_sigma_2_sublog[sigma] = sublog
            for activity in sigma:
                map_activity_2_sigma[activity] = sigma
        for trace in log:
            if cut.operator() == mining.Cut.Operator.xor:
                self.splitXor(result, trace, cut.partition(), log.get_case_freq(trace), map_sigma_2_sublog, map_activity_2_sigma, noise)
            elif cut.operator() == mining.Cut.Operator.sequence:
                self.splitSequence(result, trace, cut.partition(), log.get_case_freq(trace), map_sigma_2_sublog, map_activity_2_sigma, noise)
            elif cut.operator() == mining.Cut.Operator.parallel:
                self.splitParallel(result, trace, cut.partition(), log.get_case_freq(trace), map_sigma_2_sublog, map_activity_2_sigma, noise)
            elif cut.operator() == mining.Cut.Operator.loop:
                self.splitLoop(result, trace, cut.partition(), log.get_case_freq(trace), map_sigma_2_sublog, map_activity_2_sigma, noise)
        return LogSplitter.LogSplitResult(result, noise)

    def split_Xor(self, result, trace, partition, cardinality, map_sigma_2_sublog, map_activity_2_sigma, noise):
        if trace.size() == 0:
            for sublog in result:
                sublog.add(trace, cardinality)
            return
        event_counter = {}
        for sigma in partition:
            event_counter[sigma] = 0
        max_counter = 0
        max_sigma = set()
        for event in trace:
            sigma = map_activity_2_sigma.get(event)
            new_counter = event_counter.get(sigma) + 1
            if new_counter > max_counter:
                max_counter = new_counter
                max_sigma = sigma
            event_counter[sigma] = new_counter
        new_trace = []
        for event in trace:
            if event in max_sigma:
                new_trace.add(event)
            else:
                noise.add(event, cardinality)
        sublog = map_sigma_2_sublog.get(max_sigma)
        sublog.add(new_trace, cardinality)
        map_sigma_2_sublog[max_sigma] = sublog

    def split_sequence(self, result, trace, partition, cardinality, map_sigma_2_sublog, map_activity_2_sigma, noise):
        at_position = 0
        last_position = 0
        ignore = set()
        i = 0
        for sigma in partition:
            if i < partition.size() - 1:
                at_position = self.find_optimal_split(trace, sigma, at_position, ignore)
            else:
                at_position = trace.size()
            ignore = ignore | sigma
            new_trace = []
            for event in trace[last_position:at_position]:
                if event in sigma:
                    new_trace.add(event)
                else:
                    noise.add(event)
            sublog = map_sigma_2_sublog.get(sigma)
            sublog.add(new_trace, cardinality)
            last_position = at_position
            i += 1

    def find_optimal_split(self, trace, sigma, start_position, ignore):
        position_least_cost = 0
        least_cost = 0
        cost = 0
        position = 0
        it = iter(trace)
        while True:
            next_trace = next(it, None)
            if next_trace is not None and position < start_position:
                position += 1
                position_least_cost += 1
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
            sigma = map_sigma_2_subtrace.get(event)
            map_sigma_2_subtrace.get(sigma).add(event)
        for sigma in partition:
            map_sigma_2_sublog.get(sigma).add(map_sigma_2_subtrace.get(sigma), cardinality)

    def split_loop(self, result, trace, partition, cardinality, map_sigma_2_sublog, map_activity_2_sigma, noise):
        partial_trace = []
        last_sigma = set(iter(partition).next())
        for event in trace:
            if event in last_sigma is False:
                map_sigma_2_sublog.get(last_sigma).add(partial_trace, cardinality)
                partial_trace = []
                lastSigma = map_activity_2_sigma.get(event)
            partial_trace.add(event)
        map_sigma_2_sublog.get(lastSigma).add(partial_trace, cardinality)
        if lastSigma != iter(partition).next():
            map_sigma_2_sublog.get(lastSigma).add([], cardinality)