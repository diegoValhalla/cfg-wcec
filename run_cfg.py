from cfg import cfg, cfg2graphml


if __name__ == '__main__':

    # create CFG
    cfg = cfg.CFG('tests/c_files/test_call.c')
    cfg.make_cfg()
    #cfg.show()

    # create graphml
    cfg2graphml = cfg2graphml.CFG2Graphml()
    cfg2graphml.make_graphml(cfg, file_name='', yed_output=True)
