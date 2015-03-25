import sys, os
import unittest

sys.path.insert(0, '..')

from cfg import cfg, cfg2graphml


# Test if statements
#
class TestIf(unittest.TestCase):
    def _find_file(self, name):
        """ Find a c file by name, taking into account the current dir can be
            in a couple of typical places
        """
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, 'c_files', name)
        return name

    def test_if(self):
        test_name = self.test_if.__name__

        c_test_file = self._find_file(test_name + '.c')
        result_ok = self._find_file(test_name + '.cfg')
        result_check = self._find_file(test_name + '_check.cfg')

        graph = cfg.CFG(c_test_file)
        graph.make_cfg()
        with open(result_check, 'w') as f:
            graph.show(buf=f)

        test_assert = False
        with open(result_check, 'rU') as check_file,\
                open(result_ok, 'rU') as ok_file:
            check = check_file.read()
            ok = ok_file.read()
            test_assert = (check == ok)

        self.assertTrue(test_assert)
        os.remove(result_check)

    def test_if_graphml(self):
        test_name = self.test_if.__name__

        c_test_file = self._find_file(test_name + '.c')
        result_ok = self._find_file(test_name + '.graphml')
        result_check = self._find_file(test_name + '_check.graphml')

        graph = cfg.CFG(c_test_file)
        graph.make_cfg()
        cfg2graph = cfg2graphml.CFG2Graphml()
        cfg2graph.make_graphml(graph, result_check, True)

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
