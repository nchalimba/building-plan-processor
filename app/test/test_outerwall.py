import unittest

from app.main.extraction.dxf_extraction_coordinator import DxfExtractionCoordinator
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.main.constants import OUTERWALL_INCORRECT_EG
from app.main.constants import OUTERWALL_INCORRECT_1OG
from app.main.constants import OUTERWALL_INCORRECT_2OG

from app.test.test_data import outerwall_validation

'''
Description: This test class is used to validate amount of outerwalls per room using test data in app.test.test_data.outerwall_validation
assert values = OUTERWALL_INCORRECT_{EG,1OG,2OG} specified in constants.py
'''

class TestOuterwall(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        file_path = 'app/main/media/Einfache_Plaene_Compass/'
        file_name = 'R-Bau_D_EG.dxf'
        file_name_1og = 'R-Bau_D_1OG.dxf'
        file_name_2og = 'R-Bau_D_2OG.dxf'
        floor_height = 0.0
        orientation = 0.0

        dxf_extraction_coordinator = DxfExtractionCoordinator()
        cls.extraction_request_file = ExtractionRequestFile(
            file_path=file_path, file_name=file_name, floor_height=floor_height, orientation=orientation
        )
        cls.extraction_request_file_1og = ExtractionRequestFile(
            file_path=file_path, file_name=file_name_1og, floor_height=floor_height, orientation=orientation
        )

        cls.extraction_request_file_2og = ExtractionRequestFile(
            file_path=file_path, file_name=file_name_2og, floor_height=floor_height, orientation=orientation
        )

        cls.simple_plan_eg = dxf_extraction_coordinator.coordinate_simple_dxf_extraction(
            cls.extraction_request_file)

        cls.simple_plan_1og = dxf_extraction_coordinator.coordinate_simple_dxf_extraction(
            cls.extraction_request_file_1og)

        cls.simple_plan_2og = dxf_extraction_coordinator.coordinate_simple_dxf_extraction(
            cls.extraction_request_file_2og)
        
    def test_outerwall_eg(self):
        
        expect_outerwall = outerwall_validation.expect_outerwall_eg

        for polygon in self.simple_plan_eg.polygons:
            try:
                room_number = polygon.room.room_number
                walls = polygon.walls
                outerwalls_in_this_room = 0
                for wall in walls:
                    if wall.is_outer_wall == True:
                        outerwalls_in_this_room = outerwalls_in_this_room + 1
                outerwalls_validation = expect_outerwall.get(room_number)
                if outerwalls_validation > 0:
                    if outerwalls_validation == outerwalls_in_this_room:
                        del expect_outerwall[room_number]
            except Exception as e:
                pass
        self.assertEqual(len(expect_outerwall), OUTERWALL_INCORRECT_EG,
            "number of incorrect calculated outerwalls per room: {} ".format(len(expect_outerwall)))

    def test_outerwall_1og(self):

        expect_outerwall = outerwall_validation.expect_outerwall_1og

        for polygon in self.simple_plan_1og.polygons:
            try:
                room_number = polygon.room.room_number
                walls = polygon.walls

                outerwalls_in_this_room = 0

                for wall in walls:
                    if wall.is_outer_wall == True:
                        outerwalls_in_this_room = outerwalls_in_this_room + 1
                
                outerwalls_validation = expect_outerwall.get(room_number)
                if outerwalls_validation > 0:
                    if outerwalls_validation == outerwalls_in_this_room:
                        del expect_outerwall[room_number]

            except Exception as e:
                pass
        self.assertEqual(len(expect_outerwall), OUTERWALL_INCORRECT_1OG,
            "number of incorrect calculated outerwalls per room: {} ".format(len(expect_outerwall)))

    def test_outerwall_2og(self):

        expect_outerwall = outerwall_validation.expect_outerwall_2og

        for polygon in self.simple_plan_2og.polygons:
            try:
                room_number = polygon.room.room_number
                walls = polygon.walls

                outerwalls_in_this_room = 0

                for wall in walls:
                    if wall.is_outer_wall == True:
                        outerwalls_in_this_room = outerwalls_in_this_room + 1
                
                outerwalls_validation = expect_outerwall.get(room_number)
                if outerwalls_validation > 0:
                    if outerwalls_validation == outerwalls_in_this_room:
                        del expect_outerwall[room_number]

            except Exception as e:
                pass
        self.assertEqual(len(expect_outerwall), OUTERWALL_INCORRECT_2OG,
            "number of incorrect calculated outerwalls per room: {} ".format(len(expect_outerwall)))

if __name__ == '__main__':
    unittest.main()