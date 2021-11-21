import unittest
from app.main.services.orientation_extraction import OrientationExtraction
from manage import app

'''
Description: Unittest for orientation.
'''


class OrientationTest(unittest.TestCase):
    '''
    Description: This test class is used to test the extraction of compass needles in 3 plans.

    '''

    @classmethod
    def setUp(cls):
        cls.dxf_path = "app/main/media/Einfache_Plaene_Compass/R-Bau_D_EG.dxf"
        cls.dxf_path_firstOG = "app/main/media/Einfache_Plaene_Compass/R-Bau_D_1OG.dxf"
        cls.dxf_path_secondOG = "app/main/media/Einfache_Plaene_Compass/R-Bau_D_2OG.dxf"

    def test_get_north_orientation_ground_floor(self):
        coordinate_system = OrientationExtraction.get_north_orientation(self.dxf_path)
        self.assertEqual(tuple, type(coordinate_system))
        self.assertEqual(3, len(coordinate_system))

    def test_get_north_orientation_first_floor(self):
        coordinate_system = OrientationExtraction.get_north_orientation(
            self.dxf_path_firstOG)
        self.assertEqual(tuple, type(coordinate_system))
        self.assertEqual(3, len(coordinate_system))

    def test_get_north_orientation_second_floor(self):
        coordinate_system = OrientationExtraction.get_north_orientation(
            self.dxf_path_secondOG)
        self.assertEqual(tuple, type(coordinate_system))
        self.assertEqual(3, len(coordinate_system))


if __name__ == '__main__':
    unittest.main()