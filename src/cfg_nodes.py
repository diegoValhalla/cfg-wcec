import sys

from pycparser import c_ast


class CFGNodeType():
    COMMON = "COMMON"
    IF = "IF"
    ELSE = "ELSE"
    ELSE_IF = "ELSE_IF"
    END_IF = "END_IF"
    FOR = "FOR"
    WHILE = "WHILE"
    DO_WHILE = "DO_WHILE"
    PSEUDO = "PSEUDO"
    CALL = "CALL"


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
        self._start_line = 0
        self._end_line = 0
        self._func_owner = None
        self._call_func_name = None
        self._ref_node = None
        self._loop_wcec = 0
        self._loop_iters = 0
        self._wcec = 0
        self._rwcec = 0
        self._children = []
        self._ast_elem_list = []

    def set_type(self, type):
        self._type = type

    def get_type(self):
        return self._type

    def get_start_line(self):
        if self._start_line == 0 and self._ast_elem_list != []:
            self._start_line = self._ast_elem_list[0].coord.line

        return self._start_line

    def get_end_line(self):
        if self._end_line == 0 and self._ast_elem_list != []:
            self._end_line = self._ast_elem_list[-1].coord.line

        return self._end_line

    def set_func_owner(self, name):
        self._func_owner = name

    def get_func_owner(self):
        return self._func_owner

    def set_call_func_name(self, name):
        """ Keep function name and node that are called
            by the current node.
        """
        self._call_func_name = name

    def get_call_func_name(self):
        return self._call_func_name

    def set_ref_node(self, node):
        """ Reference node should be used by CALL or
            PSEUDO nodes to know the function or loop
            it is pointing to. So, it could be a CFGNode
            or CFGEntryNode.
        """
        self._ref_node = node

    def get_ref_node(self):
        return self._ref_node

    def get_loop_wcec(self):
        if self._loop_iters == 0: return 0
        return self._wcec / self._loop_iters

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

        msg = ((lead + '- %s, %d\n')
                % (self.get_type().lower(), self.get_start_line()))
        buf.write(msg)

        if self._type == CFGNodeType.PSEUDO:
            self.get_ref_node().show(buf, indent, lead + '|') # write loop

        for child in self._children:
            if child.get_type() == CFGNodeType.WHILE:
                msg = ((lead + '| - %s, %d\n')
                        % (child.get_type().lower(), child.get_start_line()))
                buf.write(msg)
            else:
                child.show(buf, indent, lead + '|')
