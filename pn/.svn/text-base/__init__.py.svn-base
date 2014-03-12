import tempfile
import subprocess
import os.path
from random import randint

from pyparsing import (ParserElement, Word, Optional, Literal, oneOf, LineEnd,
                        ZeroOrMore, OneOrMore, Suppress, Group, ParseException, 
                        alphas, nums, alphanums, pythonStyleComment)
import graph_tool.all as gt 
import xml.etree.ElementTree as xmltree
from .. ts import draw_astg

__all__ = ['pn_from_ts', 'pn_from_file', 'PetriNet']
rbminer = '/usr/local/bin/rbminer'

def pn_from_ts(ts, method='rbminer', k=1, agg=0 ):
    """Uses the [method] to generate a TS out of the log.
    [method] describes which conversion method/tool must be used.
        'rbminer': use the rbminer application 
        'stp': use SMT method
    [k] k-boundedness of the regions found.
    [agg] aggregation factor (lower bound on the upper bound of arcs that a
    place can have). In many cases (e.g. acyclic TSs) it is the upper bound.
    0 represents unbounded. This parameter is ignored by 'stp' and should be
    quite small if the number of activities in the TS is large (4 or less is 
    usually a good option).
    """
    if method == 'rbminer':
        if (ts.modified_since_last_write or 
            ts.last_write_format != 'sis'):
            tmpfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
            print "Saving TS to temporary file '{0}'".format( tmpfile.name )
            ts.save(tmpfile)
            tmpfile.close()
            ts_filename = tmpfile.name
        else:
            ts_filename = ts.filename
        params = [rbminer, '--k', '{0}'.format(k)]
    #        return params
        if agg > 0:
            params += ['--agg','{0}'.format(agg)]
#        else:
#            if conversion=='seq':
#                pass
#            elif conversion in ('mset','set','cfm'):
#                params.append('--'+conversion)
        params.append( ts_filename )
        rbminer_output = subprocess.check_output( params )
        tmpfile2 = tempfile.NamedTemporaryFile(mode='w', delete=False)
        print "Saving PN to temporary file '{0}'".format( tmpfile2.name )
        print >>tmpfile2, rbminer_output
        tmpfile2.close()
        pn = pn_from_sis(tmpfile2.name)
        return pn
    elif method == 'stp':
        import stp_min_region
        pn = stp_min_region.pn_from_ts(ts, k)
        return pn
    else:
        raise TypeError, "Invalid discovery method for the pn_from_ts function"


# definition of PN grammar
ParserElement.setDefaultWhitespaceChars(" \t")
id = Word(alphanums+"_\"':-")
#place = Literal("p") + Word(nums)
number = Word(nums).setParseAction(lambda tokens: int(tokens[0]))
newlines = Suppress(OneOrMore(LineEnd()))
modelName = ".model" + id("modelName") + newlines
signalNames = ZeroOrMore( Suppress(oneOf(".inputs .outputs .dummy")) + OneOrMore( id ) + newlines)("signals")
arc = id + ZeroOrMore(Group(id + Optional(Suppress("(")+number+Suppress(")"), default=1))) + newlines
graph = Literal(".graph") + Suppress(OneOrMore(LineEnd())) + OneOrMore(Group(arc))("arcs")
capacity_list = ZeroOrMore(Group(id+Suppress("=")+number))
capacity = ".capacity" + capacity_list("capacities") + newlines
marking_list = ZeroOrMore(Group(id+Optional(Suppress("=")+number,default=1)))
marking = ".marking"+Suppress("{") + marking_list("marking") + Suppress("}") + newlines
pn = Optional(newlines) + Optional(modelName) + signalNames + graph + Optional(capacity) + marking + ".end"
pn.ignore(pythonStyleComment)

def pn_from_file(filename, format=None):
    """Loads a PN stored in the [format] format in file [filename]. If [format]
    is None, then the extension is used to infer the correct format.
    
    Valid values for [format]: None, 'sis', 'pnml'
    """
    if not format:
        name, ext = os.path.splitext(filename)
        if ext=='.g':
            return pn_from_sis(filename)
        elif ext=='.pnml':
            return pn_from_pnml(filename)
        raise ValueError, 'Format could not be deduced from filename extension'
    if format == 'sis':
        return pn_from_sis(filename)
    elif format == 'pnml':
        return pn_from_pnml(filename)
    raise ValueError, 'Invalid format'

def pn_from_sis(filename):
    """Loads a PN in SIS format."""
    net = PetriNet(filename=filename, format='sis')
    ast = pn.parseFile( filename )
    for t in ast.signals:
        net.add_transition( t )
    #net.name = ast.modelName
    net.set_name(ast.modelName)
    #net.signals.update( ast.signals )
#    tuplelist = [ (m[0],m[1]) for m in ast.capacities ]
#    net.capacities = dict( tuplelist )
#    net.initial_marking = dict( [ (m[0],m[1]) for m in ast.marking ] )
    #print ast.arcs
    transitions = set(net.get_transitions())
    for a in ast.arcs:
        #print a[0]
        if a[0] not in transitions:
            # it's a place
            p = net.add_place(a[0])
            for t in a[1:]:
                net.add_edge(p,t[0],t[1])
        else:
            for t in a[1:]:
                p = net.add_place(t[0])
                net.add_edge(a[0],p,t[1])
    for m in ast.marking:
        net.set_initial_marking(m[0],m[1])
    for m in ast.capacities:
        net.set_capacity(m[0],m[1])
    net.to_initial_marking()
    return net

def pn_from_pnml(filename):
    """Loads a PN in PNML format."""
    pn = PetriNet(filename=filename, format='pnml')
    tree = xmltree.parse(filename)
    root = tree.getroot()
    net = root.find('net')
    trans_map = {}
    for c in net:
        if c.tag == 'place':
            marking = c.find('initialMarking/text')
            p = pn.add_place(c.attrib['id'])
            if marking is not None:
                pn.set_initial_marking(p,int(marking.text))
        elif c.tag == 'transition':
            node = c.find('name/text')
            if node is not None:
                name = node.text
                trans_map[c.attrib['id']] = name
                pn.add_transition(name) #c.attrib['id']
        elif c.tag == 'arc':
            pn.add_edge(trans_map.get(c.attrib['source'],c.attrib['source']), 
                        trans_map.get(c.attrib['target'],c.attrib['target']))
    pn.to_initial_marking()
    return pn

class PetriNet:
    """ Class to represent a Petri Net."""
    def __init__(self, filename=None, format=None):
        """ Constructs an empty PN.
        [filename] file name if the PN was obtained from a file.
        [format] only meaningful if filename is not None, since it is the format
        of the original file. Valid values: 'sis', 'xml', 'gml', 'dot'.
        """
        self.filename = filename
        #contains the filename of the file containing the TS (if TS was loaded
        #from a file), or the filename were the TS has been written
        self.modified_since_last_write = False
        #indicates if TS has been modified since it was last written (or 
        #initially loaded)
        self.last_write_format = format
        
        self.g = gt.Graph()
        self.gp_name = self.g.new_graph_property("string")
        self.g.graph_properties["name"] = self.gp_name
        self.gp_transitions = self.g.new_graph_property("vector<string>")
        self.g.graph_properties["transitions"] = self.gp_transitions
#        self.gp_initial_marking = self.g.new_graph_property("vector<string>")
#        self.g.graph_properties["initial_state"] = self.gp_initial_state
        #each place and transition has a name
        self.vp_elem_name = self.g.new_vertex_property("string")
        self.g.vertex_properties["name"] = self.vp_elem_name
        self.vp_elem_type = self.g.new_vertex_property("string")
        self.g.vertex_properties["type"] = self.vp_elem_type 
        #either place or transition
        self.vp_place_initial_marking = self.g.new_vertex_property("int")
        self.g.vertex_properties["initial_marking"] = self.vp_place_initial_marking
        #current marking is not stored when saving
        self.vp_current_marking = self.g.new_vertex_property("int")
        self.vp_place_capacity = self.g.new_vertex_property("int")
        self.g.vertex_properties["capacity"] = self.vp_place_capacity
        
        self.ep_edge_weight = self.g.new_edge_property("int")
        self.g.edge_properties["weight"] = self.ep_edge_weight
        self.name_to_elem = {} # reverse map: name->elem
        #places = set()
#        self.place_postset = {} #dictionaries (one per place): for each event, store the weight of the arc 
#        self.trans_postset = {}
#        self.trans_preset = {}
##        self.places = self.place_postset.viewkeys() # only works in 2.7
#        self.name = ""
#        self.signals = set()
#        self.capacities = {}
#        self.initial_marking = {}
#        self.current_marking = {}

    def mark_as_modified(self, modified=True):
        """Marks the PN as modified (so that operations on this PN that 
        require a file are not forwarded the corresponding file (if any)), 
        instead they will create a new suitable file.
        """
        self.modified_since_last_write = modified
    
    def set_name(self, name):
        self.gp_name[self.g] = name
        
    def get_name(self):
        return self.gp_name[self.g]
    
#    def set_signals(self, signals):
#        self.gp_signals[self.g] = signals
#        
#    def get_signals(self):
#        return self.gp_signals[self.g]
    def get_elem(self, elem):
        """Returns a vertex object representing the element. If [elem] is an 
        element name, then the corresponding element object (a vertex 
        representing either a place or a transition) is returned. If it is 
        already an object, the same object is returned."""
        return self.name_to_elem[elem] if isinstance(elem,str) else elem

    def add_transition(self, transition_name):
        """Adds the given transition to the graph, if not previously added. The 
        transition (either existent or new) is returned."""
        if transition_name in self.name_to_elem:
            return self.name_to_elem[transition_name]
        t = self.g.add_vertex()
        self.vp_elem_name[t] = transition_name
        self.vp_elem_type[t] = 'transition'
        self.name_to_elem[transition_name] = t
        self.mark_as_modified()
        return t
    
    def add_place(self, place_name):
        """Adds the given place to the graph, if not previously added. The 
        place (either existent or new) is returned."""
        if place_name in self.name_to_elem:
            return self.name_to_elem[place_name]
        p = self.g.add_vertex()
        self.vp_elem_name[p] = place_name
        self.vp_elem_type[p] = 'place'
        self.name_to_elem[place_name] = p
        self.mark_as_modified()
        return p

    def add_edge(self, source, target, weight=1):
        """Adds a weighted edge between source and target elements. 
        The edge is returned.
        """
        s = self.get_elem(source)
        t = self.get_elem(target)
        e = self.g.add_edge(s, t)
        self.ep_edge_weight[e] = weight
        self.mark_as_modified()
        return e

    def set_initial_marking(self, place, tokens):
        p = self.get_elem(place)
        self.vp_place_initial_marking[p] = tokens
    
    def to_initial_marking(self):
        """Copy initial marking to current marking"""
        for p in self.get_places(names=False):
            self.vp_current_marking[p] = self.vp_place_initial_marking[p]
#        print "current marking:", self.current_marking
        
    def enabled_transitions(self, names=True):
        """Computes the set of enabled transitions in the current marking.
        If [names] then the set contains the transition names, otherwise
        it contains the objects."""
        set_enabled = []
        for t in self.get_transitions(names=False):
            enabled = True
            for e in t.in_edges():
                p = e.source()
                enabled = enabled and (self.vp_current_marking[p] >= self.ep_edge_weight[e])
                if not enabled:
                    break
            if enabled:
                if names:
                    set_enabled.append( self.vp_elem_name[t] )
                else:
                    set_enabled.append( t )
        return set_enabled
    
    def fire_transition(self, t):
        """Modifies the current marking to reflect the firing of t. 
        Precondition: t must be enabled"""
        t = self.get_elem(t)
        for e in t.in_edges():
            p = e.source()
            self.vp_current_marking[p] -= self.ep_edge_weight[e]
        for e in t.out_edges():
            p = e.target()
            self.vp_current_marking[p] += self.ep_edge_weight[e]
        #print "current marking:", self.current_marking

    def simulate(self, length, names=True):
        """Return a list of transitions of at most the given [length] obtained 
        by simulation of the PN from the current marking."""
#        enabled_transitions = self.enabled_transitions()
#        print "enabled transitions: ", enabled_transitions
        seq = []
        for i in range(length):
            enabled_transitions = self.enabled_transitions(names=False)
            #print "enabled transitions: ", enabled_transitions
            if len(enabled_transitions) == 0:
                break 
            selected = randint(0,len(enabled_transitions)-1)
            t = enabled_transitions[selected]
            if names:
                seq.append(self.vp_elem_name[t])
            else:
                seq.append(t)
            self.fire_transition(t)
            #print enabled_transitions[selected], 
        #print
        return seq
    
    def set_capacity(self, place, tokens):
        """Sets the capacity of [place] to [tokens]"""
        p = self.get_elem(place)
        self.vp_place_capacity[p] = tokens
    
    def get_transitions(self, names=True):
        """Returns the set of transitions of this PN. If [names], then
        the transition names are returned, rather than the objects"""
        if names:
            return [self.vp_elem_name[v] for v in self.g.vertices() 
                if self.vp_elem_type[v] == 'transition']
        else:
            return [v for v in self.g.vertices() 
                if self.vp_elem_type[v] == 'transition']
    
    def get_transitions_without_places(self, names=True):
        """Returns the set of unconnected transitions of this PN. If [names], 
        then the transition names are returned, rather than the objects"""
        if names:
            return [self.vp_elem_name[v] for v in self.g.vertices() 
                if self.vp_elem_type[v] == 'transition' and 
                v.in_degree() == 0 and v.out_degree()== 0]
        else:
            return [v for v in self.g.vertices() 
                if self.vp_elem_type[v] == 'transition' and 
                v.in_degree() == 0 and v.out_degree()== 0]
    
    def get_transitions_with_places(self, names=True):
        """Returns the set of connected transitions (i.e. transitions with 
        places) of this PN. If [names], then the transition names are returned,
        rather than the objects"""
        if names:
            return [self.vp_elem_name[v] for v in self.g.vertices() 
                if self.vp_elem_type[v] == 'transition' and 
                (v.in_degree() != 0 or v.out_degree()!= 0)]
        else:
            return [v for v in self.g.vertices() 
                if self.vp_elem_type[v] == 'transition' and 
                (v.in_degree() != 0 or v.out_degree()!= 0)]
    
    def get_places(self, names=True):
        """Returns the set of places of this PN. If [names], then
        the places names are returned, rather than the objects"""
        if names:
            return [self.vp_elem_name[v] for v in self.g.vertices() 
                if self.vp_elem_type[v] == 'place']
        else:
            return [v for v in self.g.vertices() 
                if self.vp_elem_type[v] == 'place']
    
    def draw(self, filename, engine='cairo'):
        """Draws the TS. The filename extension determines the format.
        [engine] Rendering engine used to draw the TS. Valid values:
            cairo, graphviz, astg (for draw_astg)
        If [use_graphviz] is False, then Cairo is used to draw the graf. In such
        a case, if [filename] is None, then the interactive window is used"""
        if engine == 'graphviz':
            pass
        elif engine=='cairo': #use cairo
            pos = gt.sfdp_layout(self.g)
            names = self.vp_elem_name.copy()
            shapes = self.vp_elem_type.copy()
            color = self.g.new_vertex_property("vector<double>")
            for v in self.g.vertices():
                if self.vp_elem_type[v] == 'place':
                    if self.vp_place_initial_marking[v] > 0:
                        names[v] = str(self.vp_place_initial_marking[v])
                    else:
                        names[v] = ''
                if shapes[v] == 'place':
                    shapes[v] = 'circle'
                else:
                    shapes[v] = 'square'
                if self.vp_elem_type[v] == 'place':
                    color[v] = [0.7,0.2,0.2,0.9]
                else:
                    color[v] = [0.2,0.2,0.7,0.9]
            vprops = {'text':names, 'shape':shapes, 'fill_color':color}
#            if 'frequency' in self.g.vertex_properties:
#                vp_width = self.g.new_vertex_property("float")
#                all_traces = self.vp_state_frequency[self.get_state(self.get_initial_state())]
#                #use numpy array access 
##                vp_widht.a = int(max(100.0*self.vp_state_frequency.a/all_traces)
#                for v in self.g.vertices():
#                    vp_width[v] = int(100.0*self.vp_state_frequency[v]/all_traces)
#                vprops['size'] = vp_width
            gt.graph_draw(self.g, pos=pos, vprops=vprops, output=filename)
        elif engine=='astg':
            if filename.endswith('.ps'):
                format = '-Tps'
            elif filename.endswith('.gif'):
                format = '-Tgif'
            elif filename.endswith('.dot'):
                format = '-Tdot'
            else:
                raise TypeError, 'Unsupported output for draw_astg'
            #check if file can be forwarded as input_filename 
            if self.filename and not self.modified_since_last_write:
                input_filename = self.filename
            else:
            # or create tmp file with save
                tmpfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
                print "Saving TS to temporary file '{0}'".format( tmpfile.name )
                self.save(tmpfile)
                tmpfile.close()
                input_filename = tmpfile.name
            params = [draw_astg, '-sg', '-nonames', '-noinfo', format, input_filename]
            output = subprocess.check_output( params )
            with open(filename,'w+b') as f:
                f.write(output)
        else:
            raise ValueError, "Unknown graphical engine"

    def save(self, filename):
        """Save PN in SIS format to [filename].
        
        [filename]: file or filename in which the PN has to be written"""
        own_fid = False
        if isinstance(filename, basestring): #a filename
            file = open(filename,'w')
            self.filename = filename
            own_fid = True
        else:
            file = filename
            self.filename = file.name
        if not self.gp_name[self.g]:
            self.gp_name[self.g] = "pn"
        print >> file, ".model",self.gp_name[self.g]
        print >> file, ".outputs",
        for t in self.get_transitions():
            print >> file, t, 
        print >> file
        print >> file, ".graph"
        used_transitions = set()
        for e in self.g.edges():
            print >> file, self.vp_elem_name[e.source()], self.vp_elem_name[e.target()],
            if self.ep_edge_weight[e] > 1:
                print >> file, "(%d)" % self.ep_edge_weight[e]
            else:
                print >> file
            t = (self.vp_elem_name[e.target()] if 
                    self.vp_elem_type[e.target()] == 'transition' else
                    self.vp_elem_name[e.source()])
            used_transitions.add(t)
        all_transitions = set( self.get_transitions() )
        for t in all_transitions - used_transitions:
            print >> file, t
        marking = []
        for p in self.get_places(names=False):
            tokens = self.vp_place_initial_marking[p]
            if tokens == 1:
                marking.append(self.vp_elem_name[p])
            elif tokens > 1:
                marking.append("{0}={1}".format(self.vp_elem_name[p], tokens))
        if marking:
            print >> file, ".marking {",' '.join(marking),"}"
        print >> file, ".end"
        self.last_write_format = 'sis'
        self.mark_as_modified(False)
        if own_fid:
            file.close()
