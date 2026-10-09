"""13. Métodos Estadísticos Requeridos; 20.3. Criterio 5: Análisis Estadístico (15 pts)."""
import math
import unittest
from estadistica import *
class Estadistica(unittest.TestCase):
    def test_binomial(self):
        self.assertAlmostEqual(binomial(10,10),2/1024)
        self.assertEqual(binomial(5,10),1)
        self.assertAlmostEqual(binomial(58,100),.1332106192072138)
    def test_wilson(self):
        lo,hi=wilson(50,100)
        self.assertAlmostEqual(lo,.4038315303659956)
        self.assertAlmostEqual(hi,1-lo)
        self.assertIsNone(wilson(0,0))
    def test_bootstrap(self):
        self.assertEqual(bootstrap_media([3,3,3]),[3.,3.])
        self.assertEqual(bootstrap_media([1,2,5]),bootstrap_media([1,2,5]))
        self.assertIsNone(bootstrap_media([1]))
    def test_correlacion(self):
        self.assertAlmostEqual(correlacion([1,2,3],[3,2,1]),-1)
        self.assertAlmostEqual(correlacion([1,2,2,4],[4,2,2,1],'spearman'),-1)
        self.assertIsNone(correlacion([1,1,1],[2,3,4]))
    def test_chi(self):
        r=chi_cuadrado([[20,10],[10,20]],True)
        self.assertAlmostEqual(r['chi2'],20/3)
        self.assertAlmostEqual(r['p'],math.erfc(math.sqrt((20/3)/2)))
        self.assertFalse(chi_cuadrado([[1,0],[0,1]],True)['aplicable'])
        self.assertFalse(chi_cuadrado([[20,10],[10,20]])['aplicable'])
        self.assertAlmostEqual(chi_cuadrado([[20,10],[10,20],[15,15]],True)['p'],math.exp(-10/3))
    def test_holm(self):
        self.assertEqual(holm([.01,.04,.03]),[.03,.06,.06])
