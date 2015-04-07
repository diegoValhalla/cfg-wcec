import sys, os

thisdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,  os.path.join(thisdir, 'pycparser'))

from pycparser import parse_file

from . import cfg_ast_visitor, cfg_wcec


class CFG(object):
    """ CFG is made of a list of entry nodes that represents all functions
        defined in the source code. Each entry node has the function name and
        its start node. Given the start node, everyone can be achieved.
        Moreover, this classs also keeps its AST.

        Args:
            filename (string): C file name

        Attributes:
            filename (string): C file name
            ast (pycparser/c_ast): Abstract Syntax Tree
            entry_nodes (CFGEntryNode): list of all functions presented in AST
    """

    def __init__(self, filename):
        """ Initialize attributes

            Args:
                filename (string): C file name
        """
        self._filename = filename
        self._ast = None
        self._entry_nodes = []

    def get_entry_nodes(self):
        """ Returns:
                list of all functions parsed by the AST
        """
        return self._entry_nodes

    def get_cfilename(self):
        """ Returns:
                C file name
        """
        return self._filename

    def get_ast(self):
        """ Returns:
                Abstract syntax tree as pycparser/c_ast object
        """
        return self._ast

    def make_cfg(self):
        """ Parser the source code using pycparser to generate the AST, then
            explore the AST to generate the CFG. After that, WCEC and RWCEC are
            computed.

            Returns:
                list of all functions parsed by the AST
        """
        # run pycparser
        self._ast = parse_file(self._filename, use_cpp=True,
                                cpp_path='gcc',
                                cpp_args=['-E'])
        # explore AST and make CFG
        ast_visitor = cfg_ast_visitor.CFGAstVisitor()
        self._entry_nodes = ast_visitor.make_cfg_from_ast(self._ast)
        self._compute_wcec_rwcec()
        return self._entry_nodes

    def _compute_wcec_rwcec(self):
        """ Compute WCEC and RWCEC of the given CFG.
        """
        wcec = cfg_wcec.CFGWCEC(self._filename, self)
        wcec.compute_cfg_wcec()

    def show(self, buf=sys.stdout):
        """ Display in standard output if no parameter is given all CFG's
            nodes, each one children and their start line,

            Args:
                buf (file): file object to write CFG. If no file is provided,
                    then writes in standard output.
        """
        for entry_point in self.get_entry_nodes():
            entry_point.show(buf=buf)
