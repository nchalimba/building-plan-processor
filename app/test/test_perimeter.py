import unittest

from app.main.extraction.dxf_extraction_coordinator import DxfExtractionCoordinator
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.main.constants import PERIMETER_INCORRECT_EG, PERIMETER_INCORRECT_1OG, PERIMETER_INCORRECT_2OG
from app.main.constants import ACCEPTABLE_PERIMETER_DEVIATION
from app.test.test_data.perimeter_validation import expect_perimeter_eg, expect_perimeter_1og, expect_perimeter_2og


'''
Description: This test class is used to validate the perimeter per room with a possible deviation of 5% using test data in app.test.test_data.test_perimeter_validation
assert values = PERIMETER_INCORRECT_{EG,1OG,2OG} specified in constants.py
'''

class TestPerimeter(unittest.TestCase):

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


    
    def test_perimeter_is_correct_simple_plan_eg(self):

        perimeter_differs = []
        expect_perimeter = expect_perimeter_eg
        
        for polygon in self.simple_plan_eg.polygons:
            try:
                room_number = polygon.room.room_number
                perimeter_calculated = polygon.perimeter
                perimeter_expect = expect_perimeter.get(room_number)
                if perimeter_expect:
                    perimeter_deviation = abs((float(
                        perimeter_expect) - float(perimeter_calculated)) / float(perimeter_expect))
                    if perimeter_deviation >= ACCEPTABLE_PERIMETER_DEVIATION:
                        perimeter_differs_data = {
                            "room_number": room_number,
                            "perimeter_calculated": perimeter_calculated,
                            "perimeter_expect": perimeter_expect,
                            "perimeter_deviation": perimeter_deviation
                        }
                        perimeter_differs.append(perimeter_differs_data)
            except (AttributeError, KeyError):
                continue
        count_perimeter_differs = len(perimeter_differs)
        self.assertEqual(count_perimeter_differs, PERIMETER_INCORRECT_EG,
                         "perimeter calculation incorrect: there area {} polygons/rooms where perimeter_calculated != measured_perimeter".format(count_perimeter_differs))
        
    def test_perimeter_is_correct_simple_plan_1og(self):

        perimeter_differs = []
        expect_perimeter = expect_perimeter_1og
        
        for polygon in self.simple_plan_1og.polygons:
            try:
                room_number = polygon.room.room_number
                perimeter_calculated = polygon.perimeter
                perimeter_expect = expect_perimeter.get(room_number)
                if perimeter_expect:
                    perimeter_deviation = abs((float(
                        perimeter_expect) - float(perimeter_calculated)) / float(perimeter_expect))
                    if perimeter_deviation >= ACCEPTABLE_PERIMETER_DEVIATION:
                        perimeter_differs_data = {
                            "room_number": room_number,
                            "perimeter_calculated": perimeter_calculated,
                            "perimeter_expect": perimeter_expect,
                            "perimeter_deviation": perimeter_deviation
                        }
                        perimeter_differs.append(perimeter_differs_data)
            except (AttributeError, KeyError):
                continue
        count_perimeter_differs = len(perimeter_differs)
        self.assertEqual(count_perimeter_differs, PERIMETER_INCORRECT_1OG,
                         "perimeter calculation incorrect: there area {} polygons/rooms where perimeter_calculated != measured_perimeter".format(count_perimeter_differs))

    def test_perimeter_is_correct_simple_plan_2og(self):

        perimeter_differs = []
        expect_perimeter = expect_perimeter_2og
        
        for polygon in self.simple_plan_2og.polygons:
            try:
                room_number = polygon.room.room_number
                perimeter_calculated = polygon.perimeter
                perimeter_expect = expect_perimeter.get(room_number)
                if perimeter_expect:
                    perimeter_deviation = abs((float(
                        perimeter_expect) - float(perimeter_calculated)) / float(perimeter_expect))
                    if perimeter_deviation >= ACCEPTABLE_PERIMETER_DEVIATION:
                        perimeter_differs_data = {
                            "room_number": room_number,
                            "perimeter_calculated": perimeter_calculated,
                            "perimeter_expect": perimeter_expect,
                            "perimeter_deviation": perimeter_deviation
                        }
                        perimeter_differs.append(perimeter_differs_data)
            except (AttributeError, KeyError):
                continue
        count_perimeter_differs = len(perimeter_differs)
        self.assertEqual(count_perimeter_differs, PERIMETER_INCORRECT_2OG,
                         "perimeter calculation incorrect: there area {} polygons/rooms where perimeter_calculated != measured_perimeter".format(count_perimeter_differs))
        
if __name__ == '__main__':
    unittest.main()