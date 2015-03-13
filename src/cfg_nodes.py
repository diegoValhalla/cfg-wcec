import sys

from cfg_node_type import CFGNodeType


class CFGEntryNode(object):
    """ Class to store initial data from function
        definition. The first node is always the
        first one made of the compound statement
        from pycparser AST.
    """
    def __init__(self, name, first_node):
        self._func_name = name
        self._func_first_node = first_node

    def get_func_name(self):
        return self._func_name

    def get_func_first_node(self):
        return self._func_first_node

    def show(self, buf=sys.stdout, indent=2):
        lead = ' ' * indent
        buf.write((lead + 'entry point - %s\n') % self._func_name)
        if isinstance(self._func_first_node, CFGNode):
            self._func_first_node.show(buf=buf, lead=lead)


class CFGNode(object):
    """ The basic structure for the CFG, this class
        stores the main important data about what
        this node represents in the context of a CFG.

        It also keeps track from the main data which
        made it. In other words, elements from pycparser
        AST are hold here to always know what parts of
        code were wrapped in this node.
    """
    def __init__(self, type):
        self._type = type
        self._start_line = -1
        self._end_line = -1
        self._loop_iters = -1
        self._call_func_name = None
        self._reference_node = None
        self._wcec = 0
        self._rwcec = 0
        self._children = []
        self._ast_elem_list = []

    def set_type(self, type):
        self._type = type

    def get_type(self):
        return self._type

    def set_start_line(self, line):
        self._start_line = line

    def get_start_line(self):
        return self._start_line

    def set_end_line(self, line):
        self._end_line = line

    def get_end_line(self):
        return self._end_line

    def set_call_func(self, name, entry_node):
        """ Keep function name and node that are called
            by the current node.
        """
        self._call_func_name = name
        self.set_reference_node(entry_node)

    def get_call_func_name(self):
        return self._call_func_name

    def set_reference_node(self, node):
        """ Reference node should be used by CALL or
            PSEUDO nodes to know the function or loop
            it is pointing to. So, it could be a CFGNode
            or CFGEntryNode.
        """
        self._reference_node = node

    def get_reference_node(self):
        return self._reference_node

    def set_loop_iters(self, iters):
        self._loop_iters = iters

    def get_loop_iters(self):
        return self._loop_iters

    def add_wcec(self, wcec):
        """ It is the sum of each ast_elem WCEC that
            belongs to this node. However, if node calls
            a function, then its WCEC is equal to the
            function one, or if it is a pseudo-loop, its
            wcec is equal to loop WCEC times its iteration
            number.
        """
        self._wcec += wcec

    def get_wcec(self):
        return self._wcec

    def set_rwcec(self, rwcec):
        self._rwcec = rwcec

    def get_rwcec(self):
        return self._rwcec

    def add_child(self, child):
        """ Add a new child that current node points to.
        """
        self._children.append(child)

    def get_children(self):
        """ Return all children nodes.
        """
        return self._children

    def add_ast_elem(self, ast_elem):
        """ A node is composed by one or more AST elements
            get from pycparser AST.
        """
        self._ast_elem_list.append(ast_elem)

    def get_ast_elem_list(self):
        return self._ast_elem_list

    def show(self, buf=sys.stdout, indent=1, lead=''):
        lead += ' ' * indent
        buf.write((lead + '- %s, %d\n')
                % (self._type.lower(), self._start_line))

        for child in self._children:
            child.show(buf, indent, lead + '|')
