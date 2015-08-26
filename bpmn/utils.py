import os.path
import collections
import simplejson as json
import pydot

_root_graphics = os.path.dirname(__file__)+'/graphics/'

#def load_duration
class BPMN_Element(object):
    def __init__(self, name=None):
        self.type = 'bpmn_element'
        self.inset = [] # set of elements connected to its input
        self.outset = [] # set of elements connected to its output
        self.internal_name = ''
        if name!=None:
            self.name = name
        
    #def internal_name(self):
    #    return self.type+'{0}'.format(type(self).static_counter)
    
    def print_debug(self):
        if hasattr(self,'name'):
            print 'name:', self.name
        print 'internal name:', self.internal_name
        print 'inset:', ' '.join([e.internal_name for e in self.inset])
        print 'outset:', ' '.join([e.internal_name for e in self.outset])


class Event(BPMN_Element):
    static_counter = 0
    allowed_subtypes = ['start','end']

    def __init__(self, subtype, name=None):
        super(Event, self).__init__(name)
        self.type = 'event'
        self.subtype = subtype
        self.internal_name = self.type+'{0}'.format(Event.static_counter)
        Event.static_counter += 1
        
    def print_debug(self):
        print self.subtype+' '+self.type
        super(Event,self).print_debug()
    
    def dot_node(self, use_graphics=False):
        style = 'filled'
        if self.subtype == 'end':
            style += ', bold'
            fillcolor = "0.0 0.2 1.0"
        else:
            fillcolor = "0.3 0.2 1.0"
        return pydot.Node('{0}'.format(self.internal_name), shape='circle', style=style,
                                label="",fillcolor=fillcolor)
        
class Activity(BPMN_Element):
    static_counter = 0
    def __init__(self, name):
        super(Activity,self).__init__(name)
        self.type = 'activity'
        self.subtype = 'task'
        self.internal_name = self.type+'{0}'.format(Activity.static_counter)
        Activity.static_counter += 1
    
    def print_debug(self):
        print self.subtype+' '+self.type
        super(Activity,self).print_debug()
    
    def dot_node(self, use_graphics=False):
        return pydot.Node('{0}'.format(self.internal_name), shape='box', style='rounded, filled',
                                label='"{0}"'.format(self.name), 
                                fillcolor="0.2 0.2 1.0")
class Gateway(BPMN_Element):
    static_counter = 0
    allowed_subtypes = ['exclusive','inclusive','parallel'] 
    #sequential execution is implicit when two activities are immediately
    #one after the other
    def __init__(self, subtype, name=None):
        super(Gateway,self).__init__()
        self.type = 'gateway'
        self.subtype = subtype
        self.internal_name = self.type+'{0}'.format(Gateway.static_counter)
        Gateway.static_counter += 1
    
    def print_debug(self):
        print self.subtype+' '+self.type
        super(Gateway,self).print_debug()
    
    def dot_node(self, use_graphics=True):
        if self.subtype == 'exclusive':
            sign = 'X'
            file = _root_graphics+'bpmn_exclusive.eps'
        elif self.subtype == 'inclusive':
            sign = 'O'
            file = _root_graphics+'bpmn_inclusive.eps'
        elif self.subtype == 'parallel':
            sign = '+'
            file = _root_graphics+'bpmn_parallel.eps'
        else:
            sign = 'unknown'
        if use_graphics:
            return pydot.Node('{0}'.format(self.internal_name), image=file, shape='diamond',
                            style='filled', label="", fillcolor="0.5 0.1 0.8", 
                            fixedsize="true", width="0.7", height="0.7", margin="0.0")
        return pydot.Node('{0}'.format(self.internal_name), shape='diamond', style='filled',
                                label='"{0}"'.format(sign), fillcolor="0.5 0.1 0.8")

class BPMN:
    """ Class for a BPMN diagram. The idea is that first all elements are declared
    and then their connections."""
    def __init__(self):
        #self.inset = defaultdict(set)
        #self.outset = defaultdict(set)
        self.elements = []
        self.name_to_elem = {} #maps each given name to its element
        self.internalname_to_elem = {} #maps each internal name to its element
        self.name = "bpmn"
        self.filename = None # the filename if loaded or saved to disk 
        #create Start and End events
        self.start_event = Event('start')
        self.end_event = Event('end')
        self.add_element(self.start_event)
        self.add_element(self.end_event)
        self.edge_info = collections.defaultdict(dict) 
        #maps each edge (src,trg) to a dictionary in which edge info like edge
        #frequency) is stored
        self.node_info = collections.defaultdict(dict) 
        #maps each node to a dictionary in which node info (like activity 
        #durations) is stored
    
    def set_name( self, name ):
        """Set the name of the BPMN"""
        self.name = name
        
    def add_element(self, elem):
        """Add an activity to the BPMN"""
        self.elements.append( elem )
        if hasattr(elem,'name'):
            self.name_to_elem[elem.name] = elem
        self.internalname_to_elem[elem.internal_name] = elem
        #print self.name_to_elem
        return elem

    def get_activities(self):
        """Returns the list of activity elements in the BPMN"""
        return [elem for elem in self.elements if elem.type == 'activity']
    
    def get_events(self):
        """Returns the list of event elements in the BPMN"""
        return [elem for elem in self.elements if elem.type == 'event']
    
    def elem_with_name():
        """Returns the object with the given name. If not found, then
        it is searched using the internal name TODO"""
        pass
    
    def add_connection(self, source, target):
        """Connects source to target. Updates the data of both elements
        accordingly. If they are strings, the element is searched by name first.
        [source] and [target] can be iterables containing elements or element names 
        too."""
        ns = self.name_to_elem[source] if isinstance(source,str) else source
        nt = self.name_to_elem[target] if isinstance(target,str) else target
#        print ns, nt
        if not isinstance(ns, collections.Iterable):
            ns = [ns]
        if not isinstance(nt, collections.Iterable):
#            print  'nt not iterable! correcting'
            nt = [nt]
#            print nt
        for src in ns:
            ns = self.name_to_elem[src] if isinstance(src,str) else src
            for trg in nt:
                ntrg = self.name_to_elem[trg] if isinstance(trg,str) else trg
                if ntrg not in ns.outset:
                    ns.outset.append(ntrg)
                if ns not in ntrg.inset:
                    ntrg.inset.append(ns)
    
    def add_frequency_info(self, log, bind_freq, case_level=True):
        """ Adds frequency information to the edges of the BPMN based on the 
        number of cases going through each C-net binding.
        [log] log for which binding frequencies were computed.
        [bind_freq] 2-Tuple. Dictionary mapping each input/outupt binding to the
        set of unique cases IDs that make use of that binding. Allows computing 
        edge percentages so that most frequent paths can be spot. Code assumes
        'multiset' binding frequencies are given (for case_level=True, 'set'
        frequencies should also work, but code does not expect it).
        [case_level] If True considers only the set of cases going through each
        activity, regardless of the number of times it is executed in the case.
        In this case, exclusive gateways percentages do not necessarily add at
        most 100%, since exclusive branches can be visited in the same case if 
        there is a loop.
        If False, every decision is considered independently so exclusive 
        gateways add 100%."""
        #compute first the number of cases that corresponds to each set of
        #unique cases
        num_cases = log.get_uniq_cases().values()
        #now num_cases[i] contains the number of cases associated to unique case i
        if case_level:
            act_set_cases = collections.defaultdict(set)
            oblig_set_cases = collections.defaultdict(set)
            #act_cases[act][0] is the number of cases in which this activity produces 
            #   an obligation (act, _) 
            #act_cases[act][1] is the number of cases in which this activity consumes 
            #   an obligation (_, act)
            act_cases = collections.defaultdict(lambda : [0,0])
            oblig_cases = collections.defaultdict(int)
            for binding, occ_map in bind_freq[1].iteritems():
                case_set = set(occ_map.keys())
                act_set_cases[binding[0]] |= case_set
                for outact in binding[1]:
                    oblig_set_cases[(binding[0], outact)] |= case_set
            # to avoid problems with last activity (which does not appear in previous mapping
            for binding, occ_map in bind_freq[0].iteritems():
                case_set = set(occ_map.keys())
                act_set_cases[binding[0]] |= case_set
                
            for act, case_set in act_set_cases.iteritems():
                act_cases[act][0] = sum(num_cases[case] for case in case_set)
                act_cases[act][1] = act_cases[act][0] # not correct for S and E, but not a problem
            for obl, case_set in oblig_set_cases.iteritems():
                oblig_cases[obl] = sum(num_cases[case] for case in case_set)
        else:
            pr_bind_cases = {}
            for binding, case_set in bind_freq[1].iteritems():
                pr_bind_cases[binding] = sum(num_cases[case]*case_set[case] for case in case_set)
            #count, for each obligation (a,b), the fraction it represents over
            # (i) all obligations (a,_) and (ii) all obligations (_,b)
            oblig_cases = collections.defaultdict(int)
            act_cases = collections.defaultdict(lambda : [0,0])
            
            #we need to count only input or output bindings
            for binding, occ in pr_bind_cases.iteritems():
    #            if isinstance(binding[0], basestring):
                    #output binding
                for outact in binding[1]:
                    oblig_cases[(binding[0], outact)] += occ
                act_cases[binding[0]][0] += occ
            #print oblig_cases
            cn_bind_cases = {}
            for binding, case_set in bind_freq[0].iteritems():
                cn_bind_cases[binding] = sum(num_cases[case]*case_set[case] for case in case_set)
            for binding, occ in cn_bind_cases.iteritems():
                act_cases[binding[0]][1] += occ
        print 'act_cases:', act_cases
        #count the obligations for each activity act, 
        #[0] is (act,_) [1] is (_,act)
#        for obl, occ in oblig_cases.iteritems():
#            act_cases[obl[0]][0] += occ
#            act_cases[obl[1]][1] += occ
        #print sorted(act_cases.items(), key=lambda x:x[1])
#            else:
#                #input binding
#                for inact in binding[0]:
#                    oblig_cases[(, binding[1])] += occ
        #now annotate each gateway (only the side in which there is more than 
        #one edge)
        activities = self.get_activities()
        for act in activities:
            print 'Checking', act.name
            #check output edges, this should cover everything
#            ei_gateways = (elem for elem in act.outset if elem.type == 'gateway'
#                            and elem.subtype in ('exclusive','inclusive'))
            for elem in act.outset:#ei_gateways:
                if elem.type == 'gateway':
#                    #add info only to exclusive/inclusive
#                    if elem.subtype in ('exclusive','inclusive'):
                        #find next activity
                    for e2 in elem.outset:
                        if e2.type == 'activity':
                            obl = (act.name, e2.name)
                            print '\twith {0}: {3} {1:.1%} (for source) {2:.1%} (for target)'.format(e2.name, 
                                                    1.0*oblig_cases[obl]/act_cases[act.name][0],
                                                    1.0*oblig_cases[obl]/act_cases[e2.name][1],
                                                    oblig_cases[obl])
                            einfo = self.edge_info[(act.internal_name, elem.internal_name)]
                            einfo['frequency'] = act_cases[act.name][0]
                            einfo = self.edge_info[(elem.internal_name, e2.internal_name)]
                            einfo['frequency'] = act_cases[e2.name][1]
                        else:
                            for e3 in e2.outset:
                                if e3.type == 'activity':
                                    obl = (act.name, e3.name)
                                    print '\twith {0}: {3} {1:.1%} {2:.1%}'.format(e3.name, 
                                                            1.0*oblig_cases[obl]/act_cases[act.name][0],
                                                            1.0*oblig_cases[obl]/act_cases[e3.name][1],
                                                            oblig_cases[obl])
                                    einfo = self.edge_info[(act.internal_name, 
                                                            elem.internal_name)]
                                    einfo['frequency'] = act_cases[act.name][0]
                                    einfo = self.edge_info[(elem.internal_name, 
                                                            e2.internal_name)]
                                    einfo['frequency'] = oblig_cases[obl]
                                    einfo = self.edge_info[(e2.internal_name, 
                                                            e3.internal_name)]
                                    einfo['frequency'] = act_cases[e3.name][1]
                elif elem.type == 'activity':
                    einfo = self.edge_info[(act.internal_name, elem.internal_name)]
                    einfo['frequency'] = act_cases[act.name][0]
                    
    def add_activity_info(self, actinfo):
        """Adds activity information for each activity.
        
        [actinfo] a dictionary that maps each activity to a dictionary 
        containing information of the activity. e.g. min/max/average durations.
        If it is a string, it is assumed that it is a filename containing the
        previous information in JSON format."""
        if isinstance(actinfo, basestring):
            with open(actinfo) as f:
                info = json.load(f)
        else:
            info = actinfo
        for act, d in info.iteritems():
            self.node_info[act].update(d)
            
    def translate_activity_names(self, dictionary):
        """Changes the names of the activities according to the mapping in
        [dictionary], which is a dictionary from strings to strings.
        Activity names not present in the dictionary, will remain unchanged."""
        activities = self.get_activities()
        for act in activities:
            act.name = dictionary.get(act.name, act.name)
            
    def print_debug(self):
        for e in self.elements:
            e.print_debug()
            
    def print_dot(self, filename, use_graphics=True):
        """Saves BPMN in dot format.
        [use_graphics] Use special ps images to generate the gateway symbols
            (the files must be reachable)."""
        try:
            max_cases = max(einfo['frequency'] for einfo in self.edge_info.itervalues() 
                        if 'frequency' in einfo)
        except Exception:
            pass #no frequency information
        try:
            avg_durations = [ninfo['avg_duration'] for ninfo in self.node_info.itervalues() 
                        if 'avg_duration' in ninfo]
            global_avg = sum(avg_durations)/len(avg_durations)
            print 'Activity average duration:', global_avg
        except Exception:
            pass #no frequency information
        g = pydot.Dot(graph_type='digraph', splines="ortho") #ranksep="4.0", 
        for e in self.elements:
            n = e.dot_node(use_graphics)
            if e.type == 'activity' and 'avg_duration' in self.node_info[e.name]:
                avg = self.node_info[e.name]['avg_duration']
                h = max(0.15+0.15*(global_avg-avg)/(1.0*global_avg),0)
                n.set_fillcolor('"{0} 0.9 1.0"'.format(h))
                n.set_label('"{0} ({1:.1f})"'.format(n.get_label()[1:-1],avg))
            g.add_node(n)
            for out in e.outset:
                einfo = self.edge_info[(e.internal_name, out.internal_name)]
                if 'frequency' in einfo:
                    edge = pydot.Edge(e.internal_name, out.internal_name, 
                                    penwidth=str(20.0*einfo['frequency']/max_cases))
                else:
                    edge = pydot.Edge(e.internal_name, out.internal_name)
                g.add_edge(edge)
        g.write(filename,format='raw')

def bpmn_from_cnet(net):
    """Converts a Cnet to a BPMN diagram."""
    b = BPMN()
    for act in net.activities:
        b.add_element(Activity(act))
    start_act = net.starting_activities()
    if len(start_act) == 1:
        b.add_connection(b.start_event, start_act[0])
    else:
        #TODO: create a parallel
        pass
    #each activity has a single pre and post element that can be eiter a gw or another activity
    #depending on the structure of its bindings
    elem_out = {}
    elem_in = {}
    for act in net.activities:
        #creation of gateways
        ##outsets
        if len(net.outset[act]) == 1:
            for oset in net.outset[act]:
                #print 'oset:', oset, 'len:', len(oset)
                if len(oset) == 1:
                    elem_out[act] = act
                else:
                    elem_out[act] = b.add_element( Gateway('parallel') )
                    b.add_connection(act, elem_out[act])
        elif len(net.outset[act]) > 1:
            outsets = list(net.outset[act])
            pairwise_disjoint = True
            for i, oset1 in enumerate(outsets):
                for oset2 in outsets[i+1:]:
                    if len(oset1 & oset2) > 0:
                        pairwise_disjoint = False
                        break
            if pairwise_disjoint:
                #print act, 'has pairwise disjoint outsets'
                elem_out[act] = b.add_element( Gateway('exclusive') )
                b.add_connection(act, elem_out[act])
            else:
#                common = outsets[0].intersection(outsets[1:])
#                if len(common) == 0:
                elem_out[act] = b.add_element( Gateway('inclusive') )
                b.add_connection(act, elem_out[act])
#                else:
#                    print "Common outset elements for '{0}':".format(act), commmon
        ##insets
        if len(net.inset[act]) == 1:
            for iset in net.inset[act]:
                #print 'oset:', oset, 'len:', len(oset)
                if len(iset) == 1:
                    elem_in[act] = act
                else:
                    elem_in[act] = b.add_element( Gateway('parallel') )
                    b.add_connection( elem_in[act], act)
        elif len(net.inset[act]) > 1:
            insets = list(net.inset[act])
            pairwise_disjoint = True
            for i, iset1 in enumerate(insets):
                for iset2 in insets[i+1:]:
                    if len(iset1 & iset2) > 0:
                        pairwise_disjoint = False
                        break
            if pairwise_disjoint:
                #print act, 'has pairwise disjoint outsets'
                elem_in[act] = b.add_element( Gateway('exclusive') )
                b.add_connection(elem_in[act], act)
            else:
#                common = insets[0].intersection(insets[1:])
#                if len(common) == 0:
                elem_in[act] = b.add_element( Gateway('inclusive') )
                b.add_connection(elem_in[act], act)
#                else:
#                    print "Common inset elements for '{0}':".format(act), commmon
                
    for act in net.activities:
        for oset in net.outset[act]:
            for opp in oset:
                b.add_connection(elem_out[act], elem_in[opp])
                            
    end_act = net.final_activities()
    if len(end_act) == 1:
        b.add_connection(end_act[0], b.end_event )
    else:
        #TODO: create a parallel
        pass
    return b
