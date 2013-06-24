import pymatgen
import os
import shutil
import sys
import unittest
import time
import filecmp
from filecmp import dircmp

from pymatgen.io.vaspio import Poscar

class TestCreator(unittest.TestCase):
    def setUp(self):
        myclass = NEBToDbTaskDrone("")
        pass
        #maybe mgdb insert? use mymgdb = subprocess.Popen(["mgdb insert -c ..."], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def tearDown(self):
        #maybe create a different db.json file so the next test is a new database?
        pass
    
    def test_contour(self):
        #either run the query and get output
        #mymgdb.communicate()[0] ???
        #or  
        #test myclass.d['energy_contour'] etc. directly
        testcontour = myclass.d['energy_contour']
        self.assertEquals(testcontour, "-x-/-x-\-x-")
    
    def test_maxminmin(self):
        energy00=util2.get_energy("OSZICAR00")
        energy01=...
        energy02=...
        maxminmin = max([energy00,energy01,energy02]])-min([...)
        self.assertEquals(myclass.d['maxminmin'], maxminmin)
