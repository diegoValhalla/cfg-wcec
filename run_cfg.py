import sys

from cfg import cfg, cfg2graphml

def run_cfg(filename):
    # create CFG
    graph = cfg.CFG(filename)
    graph.make_cfg()
    #cfg.show()

    # create graphml
    graphml = cfg2graphml.CFG2Graphml()
    graphml.make_graphml(graph, file_name='', yed_output=True)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('Too few arguments')
    else:
        run_cfg(sys.argv[1])
