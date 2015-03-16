from pycparser import c_parser, c_ast

from cfg_nodes import CFGNodeType
from cfg_nodes import CFGEntryNode
from cfg_nodes import CFGNode


class CFGAstVisitor(object):
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

    def __init__(self):
        self._entry_nodes = []
        self._init_vars()

    def _init_vars(self):
        self._current_func_name = None
        self._current_node = None
        self._init_entry_node = False
        self._create_new_node = False
        self._is_first_node = True

    def _add_entry_node(self, entry_node):
        self._entry_nodes.append(entry_node)

    def _get_entry_nodes(self):
        return self._entry_nodes

    def make_cfg_from_ast(self, ast):
        if isinstance(ast, c_ast.FileAST):
            self.visit(ast)
            self._clean_graph()

        return self._get_entry_nodes()

    ####### AST visit algorithm #######

    def visit(self, n):
        """ Visit a node.
        """
        method = 'visit_' + n.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(n)

    def visit_FileAST(self, n):
        """ Visit only function definitions
        """
        for ext in n.ext:
            if isinstance(ext, c_ast.FuncDef):
                self._init_vars()
                self.visit(ext)

    def visit_FuncDef(self, n):
        """ Start visiting function declaration and its statements
        """
        self._init_entry_node = True
        self.visit(n.decl)
        self.visit(n.body)
        #print '%s %s' % (self.visit_FuncDef.__name__, self._current_func_name)

    def visit_Decl(self, n):
        """ Get function name
        """
        if self._init_entry_node:
            self._current_func_name = n.name
            self._init_entry_node = False

    def visit_Compound(self, n):
        """ A new block was found and must be created a node for it
        """
        self._create_new_node = True
        for stmt in n.block_items:
            self.visit(stmt)

    def visit_If(self, n):
        if n.cond is None: return

        cond_node = CFGNode(CFGNodeType.IF)
        cond_node.set_start_line(n.coord.line)
        self._add_new_node(cond_node)
        self._current_node = cond_node
        self._create_new_node = False
        self.visit(n.cond) # a function call can be presented in condition

        # then
        self._current_node = cond_node
        self._create_new_node = True
        iftrue_last_node = None
        if n.iftrue is not None:
            self.visit(n.iftrue)
            iftrue_last_node = self._current_node

        # else
        self._current_node = cond_node
        self._create_new_node = True
        iffalse_last_node = None
        if n.iffalse is not None:
            self.visit(n.iffalse)
            iffalse_last_node = self._current_node

        # add end node
        end_node = CFGNode(CFGNodeType.END_IF)
        self._add_child_case_if(cond_node, iftrue_last_node,
                iffalse_last_node, end_node)

        self._current_node = end_node
        self._create_new_node = True

    def visit_FuncCall(self, n):
        call_node = CFGNode(CFGNodeType.CALL)
        call_node.set_start_line(n.coord.line)
        call_node.set_call_func_name(n.name)
        self._add_new_node(call_node)
        self._current_node = call_node
        self._create_new_node = True

    def visit_While(self, n):
        if n.cond is None: return

        pseudo = CFGNode(CFGNodeType.PSEUDO)
        pseudo.set_start_line(n.coord.line)
        self._add_new_node(pseudo)

        # while-cond
        cond = CFGNode(CFGNodeType.WHILE)
        cond.set_start_line(n.coord.line)
        self._current_node = cond
        self._create_new_node = False
        self.visit(n.cond) # a function call can be presented in condition

        # while-stmt
        self._current_node = cond
        self._create_new_node = True
        if n.stmt is not None: self.visit(n.stmt)

        # get all stmt nodes without child and point them to while-cond
        self._make_loop_cycle(cond, cond)

        # pseudo:   reference -> while-cond
        #           child -> other CFG nodes
        pseudo.set_reference_node(cond)
        self._current_node = pseudo
        self._create_new_node = True

    def generic_visit(self, n):
        """ Called if no explicit visitor function exists for a
            node. Implements preorder visiting of the node.
        """
        self._add_ast_elem(n)
        for c_name, c in n.children():
            self.visit(c)

    def _add_ast_elem(self, ast_elem):
        if self._create_new_node:
            new_node = CFGNode(CFGNodeType.COMMON)
            new_node.set_start_line(ast_elem.coord.line)
            self._add_new_node(new_node)
            self._current_node = new_node
            self._create_new_node = False

        # an AST element should be added
        # only when there is a valid node
        if isinstance(self._current_node, CFGNode):
            self._current_node.add_ast_elem(ast_elem)

    def _add_new_node(self, new):
        # there is a previous node being updated
        if isinstance(self._current_node, CFGNode):
            self._current_node.add_child(new)

        if self._is_first_node:
            entry_node = CFGEntryNode(self._current_func_name, new)
            self._add_entry_node(entry_node)
            self._is_first_node = False

    def _add_child_case_if(self, cond_node, iftrue_last_node,
            iffalse_last_node, end_node):

        children = cond_node.get_children()

        # if-then or if-then-else stmt:
        #    last then node -> end if node
        if isinstance(iftrue_last_node, CFGNode):
            iftrue_last_node.add_child(end_node)

        # if-then stmt:
        #   if cond -> end if node
        if len(children) == 1:
            cond_node.add_child(end_node)

        # if-then-else stmt:
        #   last else node -> end if node
        elif len(children) == 2:
            if isinstance(iffalse_last_node, CFGNode):
                iffalse_last_node.add_child(end_node)

                # else-if node: get else child and
                # check if the first node is an if
                else_node = cond_node.get_children()[1]
                if else_node.get_type() == CFGNodeType.IF:
                    else_node.set_type(CFGNodeType.ELSE_IF)

    def _make_loop_cycle(self, cond, child):
        if child.get_children() == []:
            child.add_child(cond)
        else:
            for c in child.get_children():
                self._make_loop_cycle(cond, c)
    def _clean_graph(self):
        for entry_node in self._entry_nodes:
            self._clean_node(entry_node.get_func_first_node())

    def _clean_node(self, node):
        while True:
            rp_node = None
            rp_id = -1
            for n_id, n in enumerate(node.get_children()):
                if n.get_type() == CFGNodeType.END_IF:
                    rp_node = n
                    rp_id = n_id
                    break

            if rp_node == None: break

            # end node points to only one child,
            # so replace it
            node.get_children()[rp_id] = rp_node.get_children()[0]

        for child in node.get_children():
            self._clean_node(child)
