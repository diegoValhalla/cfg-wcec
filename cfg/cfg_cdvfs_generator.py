import sys, os, shutil

sys.path.insert(0, '..')

from cfg import CFG
from cfg_nodes import CFGNodeType, CFGEntryNode, CFGNode


class CFG_CDVFS(object):
    """ This class gets the CFG from a C-DVFS-unaware code and generates a
        C-DVFS-aware code.

        First, it addes a header file (cfg/cfg_wcec.h) which have all functions
        to compute and set the new frequency. Five global variables to keep
        track at what type of edge we are following, RWCEC of current and next
        node, loop maximum number of iterations and loop iterations in runtime,
        are also added at this part.

        Then, the CFG is explored. Every time a type-B (if statements) or
        type-L (while statements) edge is found, those five variables are set
        properly and the new frequency is computed. type-B edges only need to
        set the three first variables whereas type-L needs to set all the
        five ones.

        When a type-B edge is found, all new information, including call to
        change frequency, is added in the begining of the node. Although,
        type-L edge must set the five variables before loop begins, then the
        call to change frequency must be added in next node right after loop
        execution.

        Note-I: the header file (cfg/cfg_wcec.h) is copy to the same directory
        as the given C file to it runs properly.

        Note-II: nested loops are not supported in code generation, because the
        node right after a nested loop could be a condition one from parent
        loop. So, we can not add DVFS information in this case. Another
        approach should be by getting the line of each bracket '}' as the last
        line.

        Attributes:
            _dvfscode (string): template string to add DVFG information code
    """
    def __init__(self):
        self._dvfscode = '\n{sp}/*** auto generate DVFS code ***/\n{code}\n'

    def gen(self, graph=None, dvfsfilename=''):
        """ Generates DVFS-aware code by first getting C code lines as a list
            then inserting in each position where a type-B or type-L edge is
            the DVFS information

            Args:
                graph (cfg.CFG): CFG of the given C file
                dvfsfilename (string): filename of the DVFS-aware code. If no
                    name is given, write it at standard output.

            Raises:
                RuntimeError: if cfg is not valid or C file does not have any
                    lines
        """
        if not isinstance(graph, CFG):
            raise RuntimeError('cfg is not valid')

        clines = self._get_file_lines(graph.get_cfilename())
        if clines == []:
            raise RuntimeError('no lines in {0}'.format(graph.get_cfilename()))

        self._insert_dvfs_info(graph, clines) # explore CFG graph
        self._write_new_code(dvfsfilename, clines) # write to a file
        self._copy_new_header(dvfsfilename)

    def _get_file_lines(self, filename):
        """ Read C code and create a list from its lines by enumerating all
            them according to the line number they belong to

            Returns:
                List of tuples (clines, text) from C code
        """
        lines_list = []
        with open(filename, 'rU') as f:
            lines = f.readlines()
            for k, l in enumerate(lines):
                lines_list.append((k + 1, l))
        return lines_list

    def _insert_header(self, clines):
        """ Insert cfg_wcec.h and define some variables important to control
            program flow

            Args:
                clines (list): list of tuples (clines, text) from C code
        """
        spaces = ''
        autocode = spaces + '#include "cfg_wcec.h"\n'
        autocode += spaces + '__cfg_edge_type __cfg_type;\n'
        autocode += spaces + 'float __cfg_rwcec_bi;\n'
        autocode += spaces + 'float __cfg_rwcec_bj;\n'
        autocode += spaces + 'int __cfg_loop_max_iter;\n'
        newline = (-1, self._dvfscode.format(sp='', code=autocode))
        clines.insert(0, newline)

    def _insert_dvfs_info(self, graph, clines):
        """ Explore all functions in the C code

            Args:
                graph (cfg.CFG): CFG of the given C file
                clines (list): list of tuples (clines, text) from C code
        """
        self._insert_header(clines)
        for entry in graph.get_entry_nodes():
            if isinstance(entry, CFGEntryNode):
                n = entry.get_func_first_node()
                self._insert_dvfs_info_visit(clines, n, {})

    def _insert_dvfs_info_visit(self, clines, n, visited):
        """ Looking for all type-B and type-L edges in all functions

            Args:
                clines (list): list of tuples (clines, text) from C code
                n (CFGNode): current node being visited
                visited (dic): keep track of all visited node
        """
        if not isinstance(n, CFGNode): return

        visited[n] = True

        # explore loop if current node is PSEUDO
        if n.get_type() == CFGNodeType.PSEUDO:
            self._insert_dvfs_info_visit(clines, n.get_refnode(), visited)

        # explore node children that were not visited yet
        for child in n.get_children():
            if child not in visited:
                if n.get_type() == CFGNodeType.IF:
                    self._check_typeB_edge(clines, n, child)
                elif n.get_type() == CFGNodeType.PSEUDO:
                    self._check_typeL_edge(clines, n, child)
                self._insert_dvfs_info_visit(clines, child, visited)

    def _check_typeB_edge(self, clines, n, child):
        """ Check if current child has a RWCEC less than the greatest RWCEC of
            a successor of current node. If it is, so this is a type-B edge.

            Args:
                clines (list): list of tuples (clines, text) from C code
                n (CFGNode): current node being visited
                child (CFGNode): child of n
        """
        succbi = n.get_rwcec() - n.get_wcec()
        bj = child.get_rwcec()
        bjline = child.get_start_line()
        if bj < succbi:
            self._insert_typeB_info(clines, bjline, succbi, bj)

    def _check_typeL_edge(self, clines, n, child):
        """ Get loop information from current node and child and add DVFS code

            Args:
                clines (list): list of tuples (clines, text) from C code
                n (CFGNode): current node being visited
                child (CFGNode): child of n
        """
        if n.get_loop_iters() != 0:
            loop_wcec_once = n.get_refnode_rwcec() / n.get_loop_iters()
        else:
            loop_wcec_once = n.get_refnode_rwcec()
        loop_cond_line = n.get_start_line()
        loop_max_iter = n.get_loop_iters()
        loop_after_line = child.get_start_line()
        loop_after_rwcec = child.get_rwcec()
        self._insert_typeL_info(clines, loop_cond_line, loop_wcec_once,
                loop_max_iter, loop_after_line, loop_after_rwcec)

    def _insert_typeB_info(self, clines, bjline, rwcec_bi, rwcec_bj):
        """ Gather all information from a type-B edge and add DVFS code to C
            lines list.

            Note: since DVFS information is not a real part of the C code yet,
            it does not have a line, so -1 is used instead.

            Args:
                clines (list): list of tuples (clines, text) from C code
                bjline (int): start line of bj
                rwcec_bi (int): RWCEC of bi
                rwcec_bj (int): RWCEC of bj
        """
        index, spaces = self._get_line_index_spaces(clines, bjline)
        autocode = spaces + '__cfg_type = __CFG_TYPE_B;\n'
        autocode += spaces + '__cfg_rwcec_bi = ' + str(rwcec_bi) + ';\n'
        autocode += spaces + '__cfg_rwcec_bj = ' + str(rwcec_bj) + ';\n'
        autocode += spaces + '__cfg_change_freq(&__cfg_type, '
        autocode += '__cfg_rwcec_bi, __cfg_rwcec_bj, 0, 0);\n'
        newline = (-1, self._dvfscode.format(sp=spaces, code=autocode))
        clines.insert(index, newline)

    def _insert_typeL_info(self, clines, loop_cond_line, loop_wcec_once,
            loop_max_iter, loop_after_line, loop_after_rwcec):
        """ Gather all information from a type-L edge and add DVFS code to C
            lines list.

            Type-L edges have three parts to be added: first, it is before loop
            starts and all variables are define; second is inside the loop
            where a counter is add to count how many iterations the loop did at
            runtime; third, inserts information in the node right after loop.
            This last information is the call to change processor frequency if
            it is possible.

            Note-I: all loops must have its own iteration counter, so it is
            unique. This is done by add to the variable name loop start line
            since it is different of each loop.

            Note-II: nested loops are not supported in code generation, because
            the node right after a nested loop could be a condition one from
            parent loop. So, we can not add DVFS information in this case.
            Another approach should be by getting the line of each bracket '}'
            as the last line.

            Args:
                clines (list): list of tuples (clines, text) from C code
                bjline (int): start line of bj
                rwcec_bi (int): RWCEC of bi
                rwcec_bj (int): RWCEC of bj
        """
        # before loop starts
        index, spaces = self._get_line_index_spaces(clines, loop_cond_line)
        autocode = spaces + '__cfg_type = __CFG_TYPE_L;\n'
        autocode += spaces + '__cfg_rwcec_bi = ' + str(loop_wcec_once) + ';\n'
        autocode += spaces + '__cfg_rwcec_bj = ' + str(loop_after_rwcec) + ';\n'
        autocode += spaces + '__cfg_loop_max_iter = ' +str(loop_max_iter)+';\n'
        autocode += spaces + 'int __cfg_loop{0}_iter = 0;\n'
        autocode = autocode.format(loop_cond_line)
        newline = (-1, self._dvfscode.format(sp=spaces, code=autocode))
        clines.insert(index - 1, newline)

        # inside loop
        index, spaces = self._get_line_index_spaces(clines, loop_cond_line + 1)
        autocode = spaces + '__cfg_loop{0}_iter++;\n'
        autocode = autocode.format(loop_cond_line)
        newline = (-1, self._dvfscode.format(sp=spaces, code=autocode))
        clines.insert(index, newline)

        # after loop
        index, spaces = self._get_line_index_spaces(clines, loop_after_line)
        autocode = spaces + '__cfg_change_freq(&__cfg_type, __cfg_rwcec_bi, '
        autocode += '__cfg_rwcec_bj, __cfg_loop_max_iter, '
        autocode += '__cfg_loop{0}_iter);\n'
        autocode = autocode.format(loop_cond_line)
        newline = (-1, self._dvfscode.format(sp=spaces, code=autocode))
        clines.insert(index, newline)

    def _get_line_index_spaces(self, clines, line):
        """ Find the index of a line in the clines. It also get the number of
            spaces to indent a block according to the given line.

            Args:
                clines (list): list of tuples (clines, text) from C code
                line (int): line from C code
        """
        index = -1
        indentation = ''
        for l, text in clines:
            index += 1
            if l == line:
                indentation = ' ' * (len(text) - len(text.lstrip()))
                break
        return index, indentation

    def _write_new_code(self, filename='', clines=[]):
        """ Write the new code into the given file and append '_dvfs' string to
            it. However, if no name is given, write it at standard output.

            Args:
                filename (string): new C file name
                clines (list): list of tuples (clines, text) from C code
        """
        if filename != '':
            filename = os.path.splitext(filename)[0]
            filename = filename + '_dvfs.c'
        try:
            with open(filename, 'w') as f:
                for line, text in clines:
                    f.write(text)
        except IOError:
            for line, text in clines:
                sys.stdout.write(text)

    def _copy_new_header(self, filename):
        """ Copy cfg_wcec.h to C file directory.

            Args:
                filename (string): C file name
        """
        cheader_dir = os.path.dirname(__file__)
        cheader = os.path.join(cheader_dir, 'cfg_wcec.h')
        filedir = os.path.dirname(os.path.abspath(filename))
        shutil.copy(cheader, filedir)
