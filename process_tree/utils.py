import log
import process_tree


def process_tree_from_file(input_file):
    #log = pmlab.log.log_from_file('/Users/alcifuen/Dropbox/TESIS/Logs_Mauro/Lfull.xes')
    input_log = log.log_from_file(input_file)
    process_tree_from_log(input_log)


def process_tree_from_log(input_log, method='inductive_miner'):
    if method is 'inductive_miner':
        inductive_mine_process_tree(input_log)


def inductive_mine_process_tree(input_log):
    tree = process_tree.ProcessTree.process_tree_no_params()
    miner_state = MinerState()
    root = inductive_mine_node(input_log, tree, miner_state)
    #root.setProcessTree(tree);
	#tree.setRoot(root);
    #//reduce if necessary
	#	if (parameters.isReduce()) {
	#		ReduceTree.reduceTree(tree);
	#		debug("after reduction " + tree.getRoot(), minerState);
	#	}
	return tree


def inductive_mine_node(input_log, tree, miner_state):
    log_info = log.create_logInfo(input_log)
    base_case = find_base_cases(log, log_info, tree, miner_state)
    if base_case is not None:
        return base_case
    cut = find_cut(input_log, log_info, miner_state)
    if cut is not None and cut.is_valid():
        split_result = split_log(input_log, log_info, cut)
        new_node = new_node(cut.get_operator())
        add_node(tree, new_node)
        #recurse
        if cut.get_operator() != Operator.loop:
            for sub_log in split_result.sub_logs:
                child = inductive_mine_node(sub_log, tree)
                new_node.add_child(child)
        else:
            #it = split_result.sub_logs.iterator()
            it = split_result.sub_logs
            #first_sub_log = it.next()
            first_sub_log = it.next()
            first_child = inductive_mine_node(first_sub_log, tree)
            new_node.add_child(first_child)
            if split_result.sub_logs.size > 2:
                redoXor = Xor("")
                add_node(tree, redoXor)
                new_node.add_child(redoXor)
            else:
                redoXor = new_node
            while it.hasNext():
                sub_log = it.next()
                child = inductive_mine_node(sub_log, tree)
                redoXor.add_child(child)
            tau = AbstractTask.Automatic("tau")
            add_node(tree, tau)
            new_node.add_child(tau)
        return new_node
    else:
        return find_fall_through(input_log, log_info, tree)


def find_base_cases(input_log, log_info, tree, miner_state):
    n = None
    it = iter(miner_state.parameters.base_case_finders)
    while True:
        next_bcf = next(it, None)
        if next_bcf is not None:
            n = next_bcf.find_base_cases(input_log, log_info, tree, miner_state)
        else:
            break
    return n


def find_cut(input_log, log_info, miner_state):
    c = None
    it = iter(miner_state.parameters.cut_finders)
    while True:
        next_cf = next(it, None)
        if next_cf is not None and (c is None or not c.is_valid()):
            c = next_cf.find_cut(input_log, log_info, miner_state)
        else:
            break
    return c