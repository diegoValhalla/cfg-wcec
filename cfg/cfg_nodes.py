import sys, os

thisdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,  os.path.join(thisdir, 'pycparser'))

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
    """ Class to store initial data from function definition. The first node
        is always the first one made of the compound statement from pycparser
        AST.

        Attributes:
            func_name (string): function name
            func_first_node (CFGNode): first node of the current function
    """
    def __init__(self, name, first_node):
        self._func_name = name
        self._func_first_node = first_node

    def get_func_name(self):
        """ Returns:
                Current function name (string)
        """
        return self._func_name

    def get_func_first_node(self):
        """ Returns:
                First node of the current function (CFGNode)
        """
        return self._func_first_node

    def show(self, buf=sys.stdout, indent=2):
        """ Display current function and all its nodes.

            Args:
                buf (file): file object to write CFG. If no file is provided,
                    then writes in standard output.
                indent (int): indentation to apply in each tree level
        """
        lead = ' ' * indent
        buf.write((lead + 'entry point - %s\n') % self._func_name)
        if isinstance(self._func_first_node, CFGNode):
            self._func_first_node.show(buf=buf, lead=lead)


class CFGNode(object):
    """ The basic structure for the CFG, this class stores the main important
        data about what this node represents in the context of a CFG. It also
        keeps track from the main data which made it. In other words, elements
        from pycparser AST are hold here to always know what parts of code were
        wrapped in this node.

        Attributes:
            type (CFGNodeType): node type
            start_line (int): node first line in C code
            last_line (int): node last line in C code
            func_owner (string): function name current node belongs to
            call_func_name (string): function name that is being called
            refnode (CFGNode): reference node for PSEUDO or CALL nodes
            loop_wcec (int): loop WCEC
            loop_iters (int): number of iterations in a loop
            wcec (int): WCEC value
            rwcec (int): RWCEC value
            children (int): all children of the current node
            ast_elem_list (list): list of pycparser/c_ast elements
    """
    def __init__(self, type):
        self._type = type
        self._start_line = 0
        self._last_line = 0
        self._func_owner = None
        self._call_func_name = None
        self._refnode = None
        self._loop_iters = 0
        self._wcec = 0
        self._rwcec = 0
        self._children = []
        self._ast_elem_list = []

    def set_type(self, type):
        """ Set current node type

            Args:
                type (CFGNodeType): node type
        """
        self._type = type

    def get_type(self):
        """ Returns:
                CFGNodeType
        """
        return self._type

    def get_start_line(self):
        """ Return node first line related to the first pycparser/c_ast element
            added.

            Returns:
                Start line (int)
        """
        if self._start_line == 0 and self._ast_elem_list != []:
            self._start_line = self._ast_elem_list[0].coord.line

        return self._start_line

    def get_last_line(self):
        """ Return node last line related to the last pycparser/c_ast element
            added.

            Returns:
                Last line (int)
        """
        if self._last_line == 0 and self._ast_elem_list != []:
            self._last_line = self._ast_elem_list[-1].coord.line

        return self._last_line

    def set_func_owner(self, name):
        """ Set the function name current node belongs to.

            Args:
                name (string): function name
        """
        self._func_owner = name

    def get_func_owner(self):
        """ Returns:
                Return function name that this node belongs to (string)
        """
        return self._func_owner

    def set_call_func_name(self, name):
        """ Keep function name and node that are called by the current node.

            Args:
                name (string): the function name that is being called
        """
        self._call_func_name = name

    def get_call_func_name(self):
        """ Return function name that is being called.

            Returns:
                string
        """
        return self._call_func_name

    def set_refnode(self, node):
        """ Set reference node for PSEUDO or CALL nodes

            Args:
                node (CFGNode): node that is being referenced to
        """
        self._refnode = node

    def get_refnode(self):
        """ Reference node should be used by CALL or PSEUDO nodes to know the
            function or loop it is pointing to. So, it could be a CFGNode or
            CFGEntryNode.

            Returns:
                CFGNode if this node is PSEUDO or CFGEntryNode if it is CALL
        """
        return self._refnode

    def get_refnode_rwcec(self):
        """ RWCEC of referenced node is applied in only two cases: when current
            current node is a PSEUDO one or it is of type CALL. If it is
            PSEUDO, its RWCEC is equal to loop RWCEC. However, if it is a CALL,
            then its RWCEC is equal to the cycles to call (jump to) the function
            plus the function RWCEC.

            Returns:
                RWCEC of the reference node (int)
        """
        if (self._type == CFGNodeType.PSEUDO
                and isinstance(self._refnode, CFGNode)):
            return self._refnode.get_rwcec()

        elif (self._type == CFGNodeType.CALL
                and isinstance(self._refnode, CFGEntryNode)
                and isinstance(self._refnode.get_func_first_node(), CFGNode)):
            return self._refnode.get_func_first_node().get_rwcec()

        return 0

    def set_loop_iters(self, iters):
        """ Set loop iterations number

            Args:
                iters (int): the value of loop iterations
        """
        self._loop_iters = iters

    def get_loop_iters(self):
        """ Returns:
                The maximum number of loop iterations (int)
        """
        if not isinstance(self._refnode, CFGNode):
            return self._loop_iters

        return self._refnode.get_loop_iters()

    def set_wcec(self, wcec):
        """ Set WCEC

            Args:
                wcec (int): the value of WCEC
        """
        self._wcec = wcec

    def get_wcec(self):
        """ WCEC is the sum of all cycles to executed the statements of this
            node. However, if it is of type PSEUDO, its wcec is equal to loop
            condition node, since PSEUDO nodes are kind of 'fake nodes'.

            Returns:
                The value of WCEC
        """
        if (self._type == CFGNodeType.PSEUDO and
                isinstance(self._refnode, CFGNode)):
            return self._refnode.get_wcec()

        elif (self._type == CFGNodeType.CALL
                and isinstance(self._refnode, CFGEntryNode)
                and isinstance(self._refnode.get_func_first_node(), CFGNode)):
            return self._wcec + self.get_refnode_rwcec()

        return self._wcec

    def set_rwcec(self, rwcec):
        """ Set RWCEC

            Args:
                rwcec (int): the value of RWCEC
        """
        self._rwcec = rwcec

    def get_rwcec(self):
        """ RWCEC means the remaining cycles to be executed until the WCEC of
            the worst case execution path of the CFG is completely consumed.

            Returns:
                RWCEC (int)
        """
        return self._rwcec

    def add_child(self, child):
        """ Add a new child that current node points to.

            Args:
                child (CFGNode): a new node to be added
        """
        self._children.append(child)

    def get_children(self):
        """ Return all children nodes.

            Returns:
                List of CFGNodes
        """
        return self._children

    def add_ast_elem(self, ast_elem):
        """ A node is composed by one or more AST elements get from pycparser
            AST. Add a new ast_elem to the list.

            Args:
                ast_elem (pycparser/c_ast/element): pycparser/c_ast element class
        """
        self._ast_elem_list.append(ast_elem)

    def get_ast_elem_list(self):
        """ Return all AST elements that compose this node.

            Returns:
                List of pycparser/c_ast elements
        """
        return self._ast_elem_list

    def show(self, buf=sys.stdout, indent=1, lead=''):
        """ Display current node line and its children.

            Args:
                buf (file): file object to write CFG. If no file is provided,
                    then writes in standard output.
                indent (int): indentation to apply in each tree level
                lead (string): the number of spaces that precedes current node
        """
        lead += ' ' * indent

        msg = ((lead + '- %s, %d\n')
                % (self.get_type().lower(), self.get_start_line()))
        buf.write(msg)

        if self._type == CFGNodeType.PSEUDO:
            self.get_refnode().show(buf, indent, lead + '|') # write loop

        for child in self._children:
            if child.get_type() == CFGNodeType.WHILE:
                msg = ((lead + '| - %s, %d\n')
                        % (child.get_type().lower(), child.get_start_line()))
                buf.write(msg)
            else:
                child.show(buf, indent, lead + '|')
