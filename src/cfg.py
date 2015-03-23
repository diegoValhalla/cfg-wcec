import sys

from pycparser import parse_file

from cfg_ast_visitor import CFGAstVisitor
from cfg_wcec import CFGWCEC


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

    def __init__(self, filename):
        self._filename = filename
        self._ast = None
        self._entry_nodes = []

    def get_entry_nodes(self):
        return self._entry_nodes

    def get_ast(self):
        return self._ast

    def make_cfg(self):
        # run pycparser
        self._ast = parse_file(self._filename, use_cpp=True,
                                cpp_path='gcc',
                                cpp_args=['-E'])
        # explore AST and make CFG
        ast_visitor = CFGAstVisitor()
        self._entry_nodes = ast_visitor.make_cfg_from_ast(self._ast)
        self._compute_wcec()

    def _compute_wcec(self):
        cfg_wcec = CFGWCEC(self._filename, self)
        cfg_wcec.compute_cfg_wcec()

    def show(self, buf=sys.stdout):
        for entry_point in self.get_entry_nodes():
            entry_point.show(buf=buf)
