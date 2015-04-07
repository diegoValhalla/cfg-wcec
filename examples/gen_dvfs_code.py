import sys, os

filedir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(filedir, '..'))
sys.path.insert(0, os.path.join(filedir, '..', 'cfg', 'pycparser'))

from pycparser import parse_file

from cfg import cfg, cfg_cdvfs_generator


def gen_cfg(filename=None):
    if filename is None:
        curdir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(curdir, 'c_files', 'test.c')

    graph = cfg.CFG(filename)
    graph.make_cfg()

    # a new C file is generated at the same path of the given on, and it is
    # appending to its name "_dvfs" string
    cdvfs = cfg_cdvfs_generator.CFG_CDVFS()
    cdvfs.gen(graph)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        gen_cfg()
    else:
        gen_cfg(sys.argv[1])
