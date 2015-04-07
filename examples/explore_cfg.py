import sys, os

filedir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(filedir, '..'))
sys.path.insert(0, os.path.join(filedir, '..', 'cfg', 'pycparser'))

from pycparser import parse_file

from cfg import cfg, cfg_nodes


def cfg_init_visit(cfg):
    # visit each function graph
    for entry in cfg.get_entry_nodes():
        print('function name %s' % entry.get_func_name())
        cfg_visit(entry.get_func_first_node(), {})

def cfg_visit(node, visited):
    if not isinstance(node, cfg_nodes.CFGNode):
        return

    # set current node as visited
    visited[node] = True

    # visit loop
    if node.get_type() == cfg_nodes.CFGNodeType.PSEUDO:
        print('  node line %d child line %d'
                % (node.get_start_line(), child.get_start_line()))
        cfg_visit(child, visited)

    # visit node's children
    for child in node.get_children():
        if child not in visited:
            print('  node line %d child line %d'
                    % (node.get_start_line(), child.get_start_line()))
            cfg_visit(child, visited)

def gen_cfg(filename=None):
    if filename is None:
        curdir = os.path.dirname(__file__)
        filename = os.path.join(curdir, 'c_files', 'test.c')

    graph = cfg.CFG(filename)
    graph.make_cfg()

    cfg_init_visit(graph)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        gen_cfg()
    else:
        gen_cfg(sys.argv[1])
