from cfg import CFG
from cfg2graphml import CFG2Graphml


if __name__ == '__main__':

    # create CFG
    cfg = CFG('../tests/c_files/test_call.c')
    cfg.make_cfg()
    #cfg.show()

    # create graphml
    cfg2graph = CFG2Graphml()
    cfg2graph.make_graphml(cfg, file_name='', yed_output=True)
