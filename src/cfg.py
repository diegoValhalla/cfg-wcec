import sys, os

from pycparser import c_parser, c_ast

from cfg_ast_visitor import CFGAstVisitor


class CFG(object):
    """ CFG is made of a list of entry nodes that represents
        all functions defined in the source code. Each entry
        node has the function name and its start node. Given
        the start node, everyone can be achieved.

        All visit functions must always return an CFGNode.
        However, when a function definitions is being visited,
        an CFGEntryNode should be returned.

        PS1: It is helpful to look to pycparser/_c_ast.cfg at
        the same time, because of nodes structures.

        PS2: This code was strictly based on pycparser/c_ast.py.
        This class is not a subclass of c_ast.NodeVisitor,
        because generic_visit() should have some changes.
    """

    def __init__(self, ast):
        self._entry_nodes = []
        self._make_cfg(ast)

    def get_entry_nodes(self):
        return self._entry_nodes

    def _make_cfg(self, ast):
        ast_visitor = CFGAstVisitor()
        self._entry_nodes = ast_visitor.make_cfg_from_ast(ast)

    def show(self, buf=sys.stdout):
        for entry_point in self.get_entry_nodes():
            entry_point.show(buf=buf)


#############################

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
    ast.show(showcoord=True)

    # create CFG
    cfg = CFG(ast)
    cfg.show()
