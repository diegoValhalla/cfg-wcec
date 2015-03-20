import os

from pycparser import c_parser, c_ast

from cfg import CFG
from cfg2graphml import CFG2Graphml


if __name__ == '__main__':

    # get test
    testdir = os.path.dirname(__file__)
    name = os.path.join(testdir, 'test.c')
    text = ''
    with open(name, 'rU') as f:
        text = f.read()

    # run pycparser
    parser = c_parser.CParser()
    ast = parser.parse(text, filename=name)
    #ast.show(showcoord=True)

    # create CFG
    cfg = CFG(name, ast)
    #cfg.show()

    # create graphml
    cfg2graph = CFG2Graphml()
    cfg2graph.make_graphml(cfg, file_name='', yed_output=False)
