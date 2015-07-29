# -*- coding: utf-8 -*-
"""
Created on Wed Jan 07 12:27:30 2015

@author: Victor
"""
from enum import Enum
from sets import Set

class MiningParameters:
    base_case_finders = None


class MiningParametersEKS(MiningParameters):

    def __init__(self):
        self.base_case_finders = [BaseCaseFinderIMiEmptyLog(), BaseCaseFinderIMiEmptyTrace(), BaseCaseFinderIMiSingleActivity()]


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
                new_node = inductive_mine_node(input_log, tree, miner_state)
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
                child = inductive_mine_node(input_log, tree, miner_state)
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

    
class Cut:
    
    Operator = Enum('Operator', 'xor sequence parallel loop')    
    
    def __init__(self, Operator = None, partition = None):
        self.Operator = Operator
        self.partition = partition
    def isValid(self):
        if self.Operator == None and self.partition.size() <= 1:
            return False
        for part in self.partition:
            if part.size() == 0:
                return False
        return True


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
        return find_cut_dfg(log_info.directly_follows_graph)

    @classmethod
    def find_cut_dfg(cls, dfg):
        pass #ANDRES: IMPLEMENTAR


class CutFinderIMSequence(CutFinder):

    def find_cut(self, input_log, log_info, miner_state):
        return find_cut_dfg(log_info.directly_follows_graph)

    @classmethod
    def find_cut_dfg(cls, dfg):
        pass #ANDRES: IMPLEMENTAR


class CutFinderIMParallelWithMinimumSelfDistance(CutFinder):

    def find_cut(self, input_log, log_info, miner_state):
        return ""
    #ANDRES: IMPLEMENTAR

class CutFinderIMLoop(CutFinder):
    pass
    #ANDRRES IMPLEMENTAR

class CutFinderIMParallel(CutFinder):
    pass
    #ANDRES IMPLEMENTEAR


class FallThroughTauLoop:
    def filterTrace(sublog, trace, cardinality, startActivities):
        first = True
        numberOfTimesTauTaken = 0
        partialTrace = IMTrace()
        for event in trace:
            if (first == False and startActivities.contains(event) == False):
                sublog.add(partialTrace, cardinality)
                partialTrace = IMTrace()
                first = True
                numberOfTimesTauTaken = numberOfTimesTauTaken + cardinality
            partialTrace.add(event)
            first = False
        sublog.add(partialTrace, cardinality)
        return numberOfTimesTauTaken
        
    def fallThrough(self, log, logInfo, processTree, minerState):
        if logInfo.activities.size() > 1:
            sublog = IMLog()
            
            #intento de encontrar un tau loop
            numberOfTimesTauTaken = 0
            for trace in log:
                numberOfTimesTauTaken = numberOfTimesTauTaken + self.filterTrace(sublog, trace, log.getCardinalityOf(trace), log.getStartActivities())
            
            if sublog.size() > log.size():
                loop = ""
                loop.setProcessTree(processTree)
                processTree.addNode(loop)
                
                body = mineNode(sublog, processTree, minerState)
                loop.addChild(body)
                
                redo = "tau"
                redo.setProcessTree(processTree)
                processTree.addNode(redo)
                loop.addChild(redo)
                
                exitNode = "tau"
                exitNode.setProcessTree(processTree)
                processTree.addNode(exitNode)
                loop.addChild(exitNode)
                
                return loop
        return None
        
class FallThroughFlower:
    def fallThrough(log, logInfo, processTree, minerState):
        loopNode = ""
        loopNode.setProcessTree(processTree)
        processTree.addNode(loopNode)
        
        #body: tau
        body = "tau"
        body.setProcessTree(processTree)
        processTree.addNode(body)
        loopNode.addChild(body)
        
        #redo xor/activity
        if logInfo.activities.size() == 1:
            xorNode = loopNode
        else:
            xorNode = ""
            xorNode.setProcessTree(processTree)
            processTree.addNode(xorNode)
            loopNode.addChild(xorNode)
            
        for activity in logInfo.activities:
            child = activity.id
            child.setProcessTree(processTree)
            processTree.addNode(child)
            xorNode.addChild(child)
        
        tau2 = "tau"
        tau2.setProcessTree(processTree)
        processTree.addNode(tau2)
        loopNode.addChild(tau2)
        
        return loopNode

class FallThrough(FallThroughTauLoop, FallThroughFlower):
    pass

class LogSplitterIMi:
    def findOptimalSplit(trace, sigma, startPosition, ignore):
        positionLeastCost = 0
        leastCost = 0
        cost = 0
        position = 0
        
        it = iter(trace)
        for i in it:
            if position < startPosition:
                position += 1
                positionLeastCost += 1
                it.next()
        for i in it:
            event = it.next()
            if ignore.__contains__(event):
                pass
            elif sigma.__contains__(event):
                cost -= 1
            else:
                cost += 1
            position += 1
            
            if cost < leastCost:
                leastCost = cost
                positionLeastCost = position
        return positionLeastCost
            
    
    def splitXor(result, trace, partition, cardinality, mapSigma2sublog, mapActivity2sigma, noise):
        if trace.size() == 0:
            for sublog in result:
                sublog.add(trace, cardinality)
            return None
        eventCounter = {}
        for sigma in partition:
            eventCounter[sigma] = 0
        maxCounter = 0
        maxSigma = set()
        for event in trace:
            sigma = mapActivity2sigma.get(event)
            newCounter = eventCounter.get(sigma) + 1
            if newCounter > maxCounter:
                maxCounter = newCounter
                maxSigma = sigma
            eventCounter[sigma] = newCounter
        
        newTrace = IMTrace()
        for event in trace:
            if maxSigma.__contains__(event):
                newTrace.add(event)
            else:
                noise.add(event, cardinality)
        sublog = mapSigma2sublog.get(maxSigma)
        sublog.add(newTrace, cardinality)
        mapSigma2sublog[maxSigma] = sublog
    
    def splitSequence(self, result, trace, partition, cardinality, mapSigma2sublog, mapActivity2sigma, noise):
        atPosition = 0
        lastPosition = 0
        ignore = set()
        
        i = 0
        for sigma in partition:
            if i < partition.size() - 1:
                atPosition = self.findOptimalSplit(trace, sigma, atPosition, ignore)
            else:
                atPosition = trace.size()
            ignore = ignore | sigma
            newTrace = IMTrace()
            for event in trace[lastPosition:atPosition]:
                if sigma.__contains__(event):
                    newTrace.add(event)
                else:
                    noise.add(event)
            sublog = mapSigma2sublog.get(sigma)
            sublog.add(newTrace, cardinality)
            lastPosition = atPosition
            i += 1
                
    
    def splitParallel(result, trace, partition, cardinality, mapSigma2sublog, mapActivity2sigma, noise):
        mapSigma2subtrace = {}  #Map<Set<XEventClass>, IMTrace>
        
        for sigma in partition:
            subtrace = IMTrace()
            mapSigma2subtrace[sigma] = subtrace
        
        for event in trace:
            sigma = mapSigma2subtrace.get(event)
            mapSigma2subtrace.get(sigma).add(event)
        
        for sigma in partition:
            mapSigma2sublog.get(sigma).add(mapSigma2subtrace.get(sigma), cardinality)
        
    
    def splitLoop(result, trace, partition, cardinality, mapSigma2sublog, mapActivity2sigma, noise):
        partialTrace = IMTrace()
        lastSigma = set(iter(partition).next())
        
        for event in trace:
            if lastSigma.__contains__(event) == False:
                mapSigma2sublog.get(lastSigma).add(partialTrace, cardinality)
                partialTrace = ImTrace()
                lastSigma = mapActivity2sigma.get(event)
            partialTrace.add(event)
        mapSigma2sublog.get(lastSigma).add(partialTrace, cardinality)
        
        if lastSigma != iter(partition).next():
            mapSigma2sublog.get(lastSigma).add(IMTrace(), cardinality)
    
    def split(self, log, logInfo, cut, minerState):
        result = []     #List<IMLog>
        noise = {}      #MultiSet<XEventClass>
        
        mapSigma2sublog = {}    #Map<Set<XEventClass>, IMLog>
        mapActivity2sigma = {}  #Map<XEventClass, Set<XEventClass>>
        
        for sigma in cut.partition():
            sublog = IMLog()
            result.append(sublog)
            mapSigma2sublog[sigma] = sublog
            
            for activity in sigma:
                mapActivity2sigma[activity] = sigma
        
        for trace in log:
            if cut.operator() == Cut.Operator.xor:
                self.splitXor(result, trace, cut.partition(), log.cardinality(), mapSigma2sublog, mapActivity2sigma, noise)
            elif cut.operator() == Cut.Operator.sequence:
                self.splitSequence(result, trace, cut.partition(), log.cardinality(), mapSigma2sublog, mapActivity2sigma, noise)
            elif cut.operator() == Cut.Operator.parallel:
                self.splitParallel(result, trace, cut.partition(), log.cardinality(), mapSigma2sublog, mapActivity2sigma, noise)
            elif cut.operator() == Cut.Operator.loop:
                self.splitLoop(result, trace, cut.partition(), log.cardinality(), mapSigma2sublog, mapActivity2sigma, noise)
                
        return LogSplitter.LogSplitResult(result, noise)
        

class LogSplitter(LogSplitterIMi):
    class LogSplitResult:
        def __init__(self, sublogs, noise):
            self.sublogs = sublogs
            self.noise = noise
        
p = MiningParametersEKS()
print p.name
print p.keys