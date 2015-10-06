import log
import process_tree
import mining_parameters as mp
import cut_n_finders
import control_flow as cf
import task
import log_splitter as ls
import block


def process_tree_from_file(input_file, mining_parameters):
    #log = pmlab.log.log_from_file('/Users/alcifuen/Dropbox/TESIS/Logs_Mauro/running-example-just-two-cases.xes')
    input_log = log.log_from_file(input_file)
    process_tree_from_log(input_log, mining_parameters)


def process_tree_from_log(input_log, mining_parameters=mp.MiningParametersEKS(0.2), method='inductive_miner'):
    if method is 'inductive_miner':
        inductive_mine_process_tree(input_log, mining_parameters)


def inductive_mine_process_tree(input_log, mining_parameters):
    tree = process_tree.ProcessTree()
    miner_state = mp.MinerState(mining_parameters)
    root = inductive_mine_node(input_log, tree, miner_state)
    root.tree = tree
    tree.root = root
    return tree


#root.setProcessTree(tree);
#tree.setRoot(root);
#//reduce if necessary
#	if (parameters.isReduce()) {
#		ReduceTree.reduceTree(tree);
#		debug("after reduction " + tree.getRoot(), minerState);
#	}
#return tree


def new_node(operator):
    if operator == cut_n_finders.Operator.xor:
        return block.XOR()
    elif operator == cut_n_finders.Operator.sequence:
        return block.SEQ()
    elif operator == cut_n_finders.Operator.parallel:
        return block.AND()
    elif operator == cut_n_finders.Operator.loop:
        return block.LoopXOR()
    return None


def add_node(tree, node):
    node.tree = tree
    tree.add_node(node)


def inductive_mine_node(input_log, tree, miner_state):
    log_info = log.create_logInfo(input_log)
    base_case = find_base_cases(input_log, log_info, tree, miner_state)
    if base_case is not None:
        return base_case
    cut = find_cut(input_log, log_info, miner_state)
    if cut is not None and cut.is_valid():
        split_result = split_log(input_log, log_info, cut, miner_state)
        new_n = new_node(cut.operator)
        add_node(tree, new_n)
        #recurse
        if cut.operator != cut_n_finders.Operator.loop:
            for sub_log in split_result.sublogs:
                child = inductive_mine_node(sub_log, tree, miner_state)
                new_n.add_child(child)
        else:
            it = iter(split_result.sublogs)
            first_sub_log = it.next()
            first_child = inductive_mine_node(first_sub_log, tree, miner_state)
            new_n.add_child(first_child)
            if len(split_result.sublogs) > 2:
                redoXor = cut_n_finders.Xor("")
                add_node(tree, redoXor)
                new_n.add_child(redoXor)
            else:
                redoXor = new_n
            while True:
                sub_log = next(it, None)
                if sub_log is not None:
                    child = inductive_mine_node(sub_log, tree, miner_state)
                    redoXor.add_child(child)
                else:
                    break
            tau = task.Automatic("tau")
            add_node(tree, tau)
            new_n.add_child(tau)
        return new_n
    else:
        return find_fall_through(input_log, log_info, tree, miner_state)


def find_base_cases(input_log, log_info, tree, miner_state):
    print("Finding Base Cases")
    n = None
    for bcf in miner_state.parameters.base_case_finders:
        n = bcf.find_base_cases(input_log, log_info, tree, miner_state)
    return n


def find_cut(input_log, log_info, miner_state):
    print("Finding Cut")
    c = None
    for case_finder in miner_state.parameters.cut_finders:
        if c is None or not c.is_valid():
            c = case_finder.find_cut(input_log, log_info, miner_state)
        else:
            break
        print("Returning Cut: "+str(c.operator))
        return c


def split_log(input_log, log_info, cut, miner_state):
    result = miner_state.parameters.log_splitter.split(input_log, log_info, cut, miner_state)
    miner_state.discarded_events.update(result.discarded_events)
    return result


def find_fall_through(input_log, log_info, tree, miner_state):
    n = None
    for ft in miner_state.parameters.fall_throughs:
        n = ft.fall_through(input_log, log_info, cut_n_finders, miner_state)
    return n