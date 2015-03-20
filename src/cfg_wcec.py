import sys, os, re

sys.path.insert(0, '..')

from subprocess import Popen, PIPE

from cfg_nodes import CFGNodeType, CFGEntryNode, CFGNode


class CFGWCEC(object):

    def compute_cfg_wcec(self, cfile=None, cfg=None):
        """ Compute CFG WCEC for all nodes.
        """
        if cfg is None: return

        # make asm instruction-cycle table
        instr_cycle_table = self._make_instr_cycle_table()

        # make C line-asmInstruction table
        cline_instr_table = self._asm_instr_from_clines(cfile)

        # set nodes WCEC
        for entry in cfg.get_entry_nodes():
            self._node_wcec(entry.get_func_first_node(), {},
                    instr_cycle_table, cline_instr_table)

    def _node_wcec(self, n, visited, instr_cycle_table, cline_instr_table):
        """ Explore all function graph to set WCEC of each node. All
            instructions in the range of [start line, end line] of a node,
            their cost in cycles to be executed should be add as a part of node
            WCEC.

            Note I: The first node of each function is the only one that
            includes instructions of lines less than start line, i.e. node
            start line is 4, but the first instruction is reported in 2. This
            is done since assembler code allocates some important information
            at begining of a function.

            Note II: All END nodes are the ones which take the latest
            instructions line. In assembler code, every time a function is end,
            some memory are desallocated, so assembler code information is
            added to the last node.

            n:
                CFGNode to be visited

            visited:
                Dictionary which keeps all nodes that were already visited

            instr_cycle_table:
                Dictionary keeping the cost in cycles to execute each assembly
                instruction, i.e. {instr1: cost_cycle1, instr2: cost_cycle2, ...}

            cline_instr_table:
                Dictionary keeping the list of assembly instructions that map
                to each C line, i.e. {cline1: [asm_instr1, asm_instr2, ...], ...}
        """
        if not isinstance(n, CFGNode): return

        visited[n] = True
        if n.get_type() == CFGNodeType.PSEUDO:
            self._node_wcec(n.get_ref_node(), visited, instr_cycle_table,
                    cline_instr_table)
        else:
            clines = sorted(cline_instr_table.keys())
            wcec = 0
            for cline in clines:
                if (cline > n.get_end_line() and
                        n.get_type() != CFGNodeType.END):
                    break

                for instr in cline_instr_table[cline]:
                    wcec += instr_cycle_table[instr]
                del cline_instr_table[cline]

                # END node should include only the function last line in
                # assembly code
                if n.get_type() == CFGNodeType.END:
                    break
            n.set_wcec(wcec)

        for child in n.get_children():
            if child not in visited:
                self._node_wcec(child, visited, instr_cycle_table,
                        cline_instr_table)


    def _get_file_path(self, name):
        """ Find a c file by name, taking into account the current dir can be
            in a couple of typical places

            name:
                C file name to add the whole path.
        """
        curdir = os.path.dirname(__file__)
        name = os.path.join(curdir, name)
        return name

    def _make_instr_cycle_table(self, asm_cycle_file='_asm_cycle.txt'):
        """ Make a dictionary based on _asm_cycle.txt where each asm
            instruction has its own cost cycle.

            asm_cycle_file:
                CPU datasheet table where each line tells assembly instruction
                and the cost cycle to execute it. Default value is a table from
                armv4t architecture.

            return:
                Dictionary: {instr1: cost_cycle1, instr2: cost_cycle2, ...}
        """
        asm_cycle_table = {}
        file_path = self._get_file_path(asm_cycle_file)
        with open(file_path, 'rU') as f:
            lines = f.readlines()
            for line in lines:
                elems = line.split()
                instr = str(elems[0]).lower()
                cycles = int(elems[1])
                asm_cycle_table[instr] = cycles

        return asm_cycle_table

    def _gen_asm_file(self, cfile):
        """ Runs gcc of armv4t architecture to get assembler code with debug
            information in standard output.

            cfile:
                C file name.

            return:
                List where each element is a line from assembler code.
        """
        cpp_path = '../tools/toolschain/4.4.3/bin/arm-none-linux-gnueabi-gcc'
        cpp_args = ['-march=armv4t', '-g', '-S', '-o', '/dev/stdout']
        path_list = [cpp_path] + cpp_args + [cfile]
        text = []

        try:
            # Note the use of universal_newlines to treat all newlines
            # as \n for Python's purpose
            #
            pipe = Popen(   path_list,
                            stdout=PIPE,
                            universal_newlines=True)
            text = pipe.communicate()[0]
            text = text.split('\n') # make each line a list member
        except OSError as e:
            raise RuntimeError("Unable to produce assembler code.\n" +
                    ('Original error: %s' % e))

        return text

    def _asm_instr_from_clines(self, cfile):
        """ Parse assembler code from a C file.

            Searches for two patterns: '.loc' and '<spaces> instruction'. The
            first tells which line of C code the following assembler
            instructions are related. The latter is simply the map assembler
            instructions from C code.

            cfile:
                C file name.

            return:
                Dictionary: {cline1: [asm_instr1, asm_instr2, ...], ...}
        """
        # generate .s file
        asm_lines = self._gen_asm_file(cfile)
        if asm_lines == []: return

        # regular expressions for instructions and locs
        pattern_loc = r'^\s*\.loc\b\s+\d+\s+(\d+)\s+'
        pattern_instr = r'^\s+(\w+)[^\.]*(\.\w+)?.*'

        # states of the automaton
        INIT = 0
        NEW_LOC = 1
        ADD_INSTR = 2

        # initial settings
        state = INIT;
        curline = 0
        cline = 0
        data = None
        cline_table = {}

        for line in asm_lines:
            res = re.search(pattern_loc, line)
            if res: # found loc
                cline = int(res.group(1))
                state = NEW_LOC
            else:
                res = re.search(pattern_instr, line)
                if res: # found assembly instruction
                    data = res.group(1)
                    state = ADD_INSTR
                else: continue

            # each loc is made of a list of instrs
            if state == NEW_LOC:
                if cline not in cline_table:
                    cline_table[cline] = []
                curline = cline

            elif state == ADD_INSTR:
                cline_table[curline].append(data)

        return cline_table
