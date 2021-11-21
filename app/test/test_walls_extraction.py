import unittest

from app.main.extraction.dxf_extraction_coordinator import DxfExtractionCoordinator
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.test.test_data import walls_extraction_validation
from app.main.constants import WALL_INCORRECT_EG, WALL_INCORRECT_1OG, WALL_INCORRECT_2OG

'''
Description: This test class is used to validate amount of walls per room using test data in app.test.test_data.generate_walls_validation
assert values = WALL_INCORRECT_{EG,1OG,2OG} specified in constants.py
'''

class TestWallsExtraction(unittest.TestCase):

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
        
        
    def test_walls_extraction_eg(self):
       
        expect_walls_eg_initial = walls_extraction_validation.expect_walls_eg_initial
        expect_walls_eg_validation = walls_extraction_validation.expect_walls_eg_validation
        
        validation_data = len(expect_walls_eg_validation)

        for polygon in self.simple_plan_eg.polygons:
            try:
                room_number = polygon.room.room_number
                walls = polygon.walls
                wall_counter = 0
                for wall in walls:
                    if not wall.is_pillar:
                        wall_counter += 1

                wall_counter_validation = expect_walls_eg_initial.get(room_number)
                wall_counter_should = expect_walls_eg_validation.get(room_number)

                if wall_counter_validation >0 and wall_counter_should > 0:
                    if wall_counter == wall_counter_should:
                        del expect_walls_eg_validation[room_number]
                   
            except Exception as e:
                pass

        self.assertEqual(len(expect_walls_eg_validation), WALL_INCORRECT_EG,
            "data for validation: {} rooms | generate_walls ok: {}  | not ok: {} ".format(validation_data, validation_data - len(expect_walls_eg_validation), len(expect_walls_eg_validation)))

    def test_walls_extraction_1og(self):

        expect_walls_1og_initial = walls_extraction_validation.expect_walls_1og_initial
        expect_walls_1og_validation = walls_extraction_validation.expect_walls_1og_validation
        
        validation_data = len(expect_walls_1og_validation)

        for polygon in self.simple_plan_1og.polygons:
            try:
                room_number = polygon.room.room_number
                walls = polygon.walls
                wall_counter = 0
                for wall in walls:
                    if not wall.is_pillar:
                        wall_counter += 1

                wall_counter_validation = expect_walls_1og_initial.get(room_number)
                wall_counter_should = expect_walls_1og_validation.get(room_number)

                if wall_counter_validation >0 and wall_counter_should > 0:
                    if wall_counter == wall_counter_should:
                        del expect_walls_1og_validation[room_number]
                   
            except Exception as e:
                pass

        self.assertEqual(len(expect_walls_1og_validation), WALL_INCORRECT_1OG,
            "data for validation: {} rooms | generate_walls ok: {}  | not ok: {} ".format(validation_data, validation_data - len(expect_walls_1og_validation), len(expect_walls_1og_validation)))

    def test_walls_extraction_2og(self):

        expect_walls_2og_initial = walls_extraction_validation.expect_walls_2og_initial
        expect_walls_2og_validation = walls_extraction_validation.expect_walls_2og_validation
        
        validation_data = len(expect_walls_2og_validation)

        for polygon in self.simple_plan_2og.polygons:
            try:
                room_number = polygon.room.room_number
                walls = polygon.walls
                wall_counter = 0
                for wall in walls:
                    if not wall.is_pillar:
                        wall_counter += 1

                wall_counter_validation = expect_walls_2og_initial.get(room_number)
                wall_counter_should = expect_walls_2og_validation.get(room_number)

                if wall_counter_validation >0 and wall_counter_should > 0:
                    if wall_counter == wall_counter_should:
                        del expect_walls_2og_validation[room_number]
                   
            except Exception as e:
                pass

        self.assertEqual(len(expect_walls_2og_validation), WALL_INCORRECT_2OG,
            "data for validation: {} rooms | generate_walls ok: {}  | not ok: {} ".format(validation_data, validation_data - len(expect_walls_2og_validation), len(expect_walls_2og_validation)))


if __name__ == '__main__':
    unittest.main()