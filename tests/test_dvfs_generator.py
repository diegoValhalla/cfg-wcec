import sys, os
import unittest

sys.path.insert(0, '..')

from cfg import cfg, cfg2graphml, cfg_cdvfs_generator


# Test if statements
#
class TestDVFSGen(unittest.TestCase):
    def _find_file(self, name):
        """ Find a c file by name, taking into account the current dir can be
            in a couple of typical places
        """
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, 'c_files', name)
        return name

    def test_dvfs_generator(self):
        test_name = self.test_dvfs_generator.__name__

        c_test_file = self._find_file(test_name + '.c')
        result_ok = self._find_file(test_name + '_ok_dvfs.c')
        result_check = self._find_file(test_name + '_check.c')

        graph = cfg.CFG(c_test_file)
        graph.make_cfg()

        cdvfs = cfg_cdvfs_generator.CFG_CDVFS()
        cdvfs.gen(graph, result_check)

        test_assert = False
        # '_dvfs' string is always appending to new file name
        result_check = self._find_file(test_name + '_check_dvfs.c')
        with open(result_check, 'rU') as check_file,\
                open(result_ok, 'rU') as ok_file:
            check = check_file.read()
            ok = ok_file.read()
            test_assert = (check == ok)

        self.assertTrue(test_assert)
        os.remove(result_check)


if __name__ == '__main__':
    unittest.main()
