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
    END = "END"


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
        self._refnode = None
        self._loop_wcec = 0
        self._loop_iters = 0
        self._wcec = 0
        self._rwcec = 0
        self._children = []
        self._ast_elem_list = []

    def set_type(self, type):
        self._type = type

    def get_type(self):
        """ return:
                CFGNodeType
        """
        return self._type

    def get_start_line(self):
        """ Return node first line related to the first pycparser/c_ast element
            added.

            return:
                int
        """
        if self._start_line == 0 and self._ast_elem_list != []:
            self._start_line = self._ast_elem_list[0].coord.line

        return self._start_line

    def get_end_line(self):
        """ Return node last line related to the last pycparser/c_ast element
            added.

            return:
                int
        """
        if self._end_line == 0 and self._ast_elem_list != []:
            self._end_line = self._ast_elem_list[-1].coord.line

        return self._end_line

    def set_func_owner(self, name):
        self._func_owner = name

    def get_func_owner(self):
        """ Return function name that this node belongs to.

            return:
                string
        """
        return self._func_owner

    def set_call_func_name(self, name):
        """ Keep function name and node that are called
            by the current node.
        """
        self._call_func_name = name

    def get_call_func_name(self):
        """ Return function name that is being called.

            return:
                string
        """
        return self._call_func_name

    def set_ref_node(self, node):
        self._refnode = node

    def get_ref_node(self):
        """ Reference node should be used by CALL or PSEUDO nodes to know the
            function or loop it is pointing to. So, it could be a CFGNode or
            CFGEntryNode.

            return:
                CFGNode if this node is PSEUDO or CFGEntryNode if it is CALL
        """
        return self._refnode

    def get_loop_wcec(self):
        """ Only PSEUDO nodes can have a value different of zero since
            reference node is the while-condition itself.

            return:
                WCEC of the loop
        """
        if (self._type != CFGNodeType.PSEUDO or
                not isinstance(self._refnode, CFGNode) or
                self._refnode.get_loop_iters() == 0):
            return 0

        return self.get_wcec() / self._refnode.get_loop_iters()

    def set_loop_iters(self, iters):
        self._loop_iters = iters

    def get_loop_iters(self):
        """ return:
                The maximum number of loop iterations
        """
        if not isinstance(self._refnode, CFGNode):
            return self._loop_iters

        return self._refnode.get_loop_iters()

    def set_wcec(self, wcec):
        self._wcec = wcec

    def get_wcec(self):
        """ WCEC is the sum of all cycles to executed the statements of this
            node. However, if this node if of type CALL, then its WCEC is equal
            to cycles to call plus the function RWCEC, or if it is of type
            PSEUDO, its wcec is equal to loop RWCEC times its iterations.

            return:
                int
        """
        if (self._type == CFGNodeType.PSEUDO and
                isinstance(self._refnode, CFGNode)):
            return (self._refnode.get_rwcec() *
                    self._refnode.get_loop_iters())
        elif (self._type == CFGNodeType.CALL and
                isinstance(self._refnode, CFGEntryNode) and
                isinstance(self._refnode.get_func_first_node(), CFGNode)):
            return (self._wcec +
                self._refnode.get_func_first_node().get_rwcec())

        return self._wcec

    def set_rwcec(self, rwcec):
        self._rwcec = rwcec

    def get_rwcec(self):
        """ RWCEC means the remaining cycles to be executed until the WCEC of
            the worst case execution path of the CFG is completely consumed.

            return:
                int
        """
        return self._rwcec

    def add_child(self, child):
        """ Add a new child that current node points to.

            child:
                CFGNode
        """
        self._children.append(child)

    def get_children(self):
        """ Return all children nodes.

            return:
                List of CFGNodes
        """
        return self._children

    def add_ast_elem(self, ast_elem):
        """ A node is composed by one or more AST elements get from pycparser
            AST.

            ast_elem:
                pycparser/c_ast element class
        """
        self._ast_elem_list.append(ast_elem)

    def get_ast_elem_list(self):
        """ Return all AST elements that compose this node.

            return:
                List of pycparser/c_ast elements
        """
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
