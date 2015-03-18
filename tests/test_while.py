import sys, os
import unittest

sys.path.insert(0, '..')

from pycparser import parse_file, c_ast

from src.cfg import CFG
from src.cfg2graphml import CFG2Graphml

# Test if statements
#
class TestWhile(unittest.TestCase):
    def _find_file(self, name):
        """ Find a c file by name, taking into account the current dir can be
            in a couple of typical places
        """
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, 'c_files', name)
        return name

    def test_while(self):
        test_name = self.test_while.__name__

        c_test_file = self._find_file(test_name + '.c')
        result_ok = self._find_file(test_name + '.cfg')
        result_check = self._find_file(test_name + '.cfg.check')

        ast = parse_file(c_test_file, use_cpp=True)
        cfg = CFG(ast)

        with open(result_check, 'w') as f:
            cfg.show(buf=f)

        test_assert = False
        with open(result_check, 'r+') as check_file,\
                open(result_ok, 'rU') as ok_file:
            check = check_file.read()
            ok = ok_file.read()
            test_assert = (check == ok)

        self.assertTrue(test_assert)
        os.remove(result_check)

    def test_while_graphml(self):
        test_name = self.test_while.__name__

        c_test_file = self._find_file(test_name + '.c')
        result_ok = self._find_file(test_name + '.graphml')
        result_check = self._find_file(test_name + '.graphml.check')

        ast = parse_file(c_test_file, use_cpp=True)
        cfg = CFG(ast)

        cfg2graph = CFG2Graphml()
        cfg2graph.make_graphml(cfg, result_check, True)

        test_assert = False
        with open(result_check, 'r+') as check_file,\
                open(result_ok, 'rU') as ok_file:
            check = check_file.read()
            ok = ok_file.read()
            test_assert = (check == ok)

        self.assertTrue(test_assert)
        os.remove(result_check)

if __name__ == '__main__':
    unittest.main()