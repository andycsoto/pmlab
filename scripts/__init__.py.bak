"""High level scripts Module """
import os.path
from collections import defaultdict
import pmlab.cnet
import pmlab.bpmn
import pmlab.log.filters
import os
#import projectors
#import filters
#import clustering
#import tempfile
#import subprocess
#import pmlab.ts

def draw_bpmn(bp):
	bp.print_dot(bp.name+'.dot')
	os.system('dot -Tps '+ bp.name+'.dot > '+bp.name+'.ps')
	os.system('ps2pdf ' + bp.name+'.ps')
	os.system('pdfcrop '+bp.name +'.pdf')
	os.system('evince '+ bp.name+'-crop.pdf')

def bpmn_discovery(log,log_percentage=None,minimal_case_length=None,add_frequency=None):
	if (minimal_case_length):
		log = pmlab.log.filters.filter_log(log,pmlab.log.filters.CaseLengthFilter(above=minimal_case_length))
	if (log_percentage):
		log = pmlab.log.filters.filter_log(log,pmlab.log.filters.FrequencyFilter(log,log_min_freq=log_percentage))
	clog = pmlab.cnet.condition_log_for_cnet(log)
	skeleton = pmlab.cnet.flexible_heuristic_miner(clog)
	cn,bf = pmlab.cnet.cnet_from_log(clog,skeleton=skeleton)
	bp = pmlab.bpmn.bpmn_from_cnet(cn)
	if (add_frequency):
		bp.add_frequency_info(clog,bf)
	return bp
		
def parallel_cnet_discovery(view,log):
	cases = map(lambda t: list(t),log.get_uniq_cases())
	scat_cases = []
	for l in cases:
		s = reduce(lambda x,y: x+' '+y,l)
		scat_cases.append(s)
	view.scatter('sublog',scat_cases)
	view.execute('l = pmlab.log.log_from_iterable(sublog)')
	view.execute('cl = pmlab.cnet.condition_log_for_cnet(l)')
	view.execute('sk = pmlab.cnet.flexible_heuristic_miner(cl)')
	view.execute('c,b = pmlab.cnet.cnet_from_log(cl, skeleton=sk)')
	cn = reduce(lambda x,y: x+y, view.gather('c'))
	return cn
	
	
	
