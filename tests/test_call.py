import sys, os
import unittest

sys.path.insert(0, '..')

from pycparser import parse_file, c_ast

from src.cfg import CFG

# Test if statements
#
class TestCall(unittest.TestCase):
    def _find_file(self, name):
        """ Find a c file by name, taking into account the current dir can be
            in a couple of typical places
        """
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, 'c_files', name)
        return name

    def test_call(self):
        test_name = self.test_call.__name__

        c_test_file = self._find_file(test_name + '.c')
        result_check = self._find_file(test_name + '.out.check')
        result_ok = self._find_file(test_name + '.out.ok')

        ast = parse_file(c_test_file, use_cpp=True)
        cfg = CFG(ast)

        with open(result_check, 'w') as f:
            cfg.show(buf=f)

        test_assert = False
        with open(result_check, 'rU') as check_file,\
                open(result_ok, 'rU') as ok_file:
            check = check_file.read()
            ok = ok_file.read()
            test_assert = (check == ok)

        self.assertTrue(test_assert)
        os.remove(result_check)

if __name__ == '__main__':
    unittest.main()
