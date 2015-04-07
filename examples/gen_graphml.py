import sys, os

filedir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(filedir, '..'))
sys.path.insert(0, os.path.join(filedir, '..', 'cfg', 'pycparser'))

from pycparser import parse_file

from cfg import cfg, cfg2graphml


def gen_cfg(filename=None):
    if filename is None:
        curdir = os.path.dirname(__file__)
        filename = os.path.join(curdir, 'c_files', 'test.c')

    graph = cfg.CFG(filename)
    graph.make_cfg()
    graph.show()

    # set file_name as empty to write graphml in stdout
    # set yed_output as true to write graphical information
    cfg2graph = cfg2graphml.CFG2Graphml()
    cfg2graph.make_graphml(graph, file_name='', yed_output=True)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        gen_cfg()
    else:
        gen_cfg(sys.argv[1])
