import unittest
from app.main.extraction.dxf_extraction_coordinator import DxfExtractionCoordinator
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.main.constants import AREA_INCORRECT_EG
from app.main.constants import AREA_INCORRECT_1OG
from app.main.constants import AREA_INCORRECT_2OG
from app.main.constants import ACCEPTABLE_AREA_DEVIATION

'''
Description: This test class is used to validate the calculated area per polygon using extracted room area annotations with a possible deviation of 5%
assert values = AREA_INCORRECT_{EG,1OG,2OG} specified in constants.py
'''

class TestArea(unittest.TestCase):

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

    
    def test_calculated_area_is_annotation_area_simple_plan_eg(self):
        
        area_differs = []

        for polygon in self.simple_plan_eg.polygons:
            try:
                room_number = polygon.room.room_number
                area_calculated = polygon.area
                area_annotation = polygon.room.room_area
                area_deviation = abs(
                    (float(area_annotation) - float(area_calculated)) / float(area_annotation))
                if area_deviation >= ACCEPTABLE_AREA_DEVIATION:
                    area_differs_data = {
                        "room_number":   room_number,
                        "area_calculated":   area_calculated,
                        "area_annotation":   area_annotation,
                        "area_deviation":   area_deviation
                    }
                    area_differs.append(area_differs_data)
            except (AttributeError, KeyError):
                continue
        count_area_differs = len(area_differs)
        self.assertEqual(count_area_differs, AREA_INCORRECT_EG,
                         "area calculation incorrect: there are {} polygons/rooms where area_calculated != area_annotation".format(count_area_differs))
        

    def test_calculated_area_is_annotation_area_simple_plan_1og(self):
        
        area_differs = []

        for polygon in self.simple_plan_1og.polygons:
            try:
                room_number = polygon.room.room_number
                area_calculated = polygon.area
                area_annotation = polygon.room.room_area
                area_deviation = abs(
                    (float(area_annotation) - float(area_calculated)) / float(area_annotation))
                if area_deviation >= ACCEPTABLE_AREA_DEVIATION:
                    area_differs_data = {
                        "room_number":   room_number,
                        "area_calculated":   area_calculated,
                        "area_annotation":   area_annotation,
                        "area_deviation":   area_deviation
                    }
                    area_differs.append(area_differs_data)
                    #print("\t room_number: {} | area_calculated: {} | area_annotation: {} | area_deviation: {}".format(
                    #    room_number, round(area_calculated, 2), area_annotation, round(area_deviation, 2)))
            except (AttributeError, KeyError):
                continue
        count_area_differs = len(area_differs)
        self.assertEqual(count_area_differs, AREA_INCORRECT_1OG,
                         "area calculation incorrect: there are {} polygons/rooms where area_calculated != area_annotation".format(count_area_differs))

    def test_calculated_area_is_annotation_area_simple_plan_2og(self):
        
        area_differs = []

        for polygon in self.simple_plan_2og.polygons:
            try:
                room_number = polygon.room.room_number
                area_calculated = polygon.area
                area_annotation = polygon.room.room_area
                area_deviation = abs(
                    (float(area_annotation) - float(area_calculated)) / float(area_annotation))
                if area_deviation >= ACCEPTABLE_AREA_DEVIATION:
                    area_differs_data = {
                        "room_number":   room_number,
                        "area_calculated":   area_calculated,
                        "area_annotation":   area_annotation,
                        "area_deviation":   area_deviation
                    }
                    area_differs.append(area_differs_data)
                    #print("\t room_number: {} | area_calculated: {} | area_annotation: {} | area_deviation: {}".format(
                    #    room_number, round(area_calculated, 2), area_annotation, round(area_deviation, 2)))
            except (AttributeError, KeyError):
                continue
        count_area_differs = len(area_differs)
        self.assertEqual(count_area_differs, AREA_INCORRECT_2OG,
                         "area calculation incorrect: there are {} polygons/rooms where area_calculated != area_annotation".format(count_area_differs))

if __name__ == '__main__':
    unittest.main()