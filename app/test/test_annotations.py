import unittest

from app.main.extraction.dxf_extraction_coordinator import DxfExtractionCoordinator
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.main.constants import ANNOTATION_NOT_MATCHED_EG, ANNOTATION_NOT_MATCHED_1OG, ANNOTATION_NOT_MATCHED_2OG
from app.test.test_data import annotations_validation

'''
Description: This test class is used to test annotations matching

validate the matching between room annotations and rooms using test data in app.test.test_data.annotations_validation
assert values = ANNOTATION_NOT_MATCHED_{EG,1OG,2OG} specified in constants.py
'''
class TestAnnotations(unittest.TestCase):

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

    
    def test_all_annotations_matched_simple_plan_eg(self):

        expect_annotations = annotations_validation.expect_annotations_eg
        
        for polygon in self.simple_plan_eg.polygons:
            try:
                room_number = polygon.room.room_number
                if room_number in expect_annotations:
                    expect_annotations.remove(room_number)
            except (AttributeError, KeyError):
                continue
        self.assertEqual(len(expect_annotations), ANNOTATION_NOT_MATCHED_EG,
                         "The following rooms were not matched: {} ".format(expect_annotations))
    
    def test_all_annotations_matched_simple_plan_1og(self):

        expect_annotations = annotations_validation.expect_annotations_1og
        
        for polygon in self.simple_plan_1og.polygons:
            try:
                room_number = polygon.room.room_number
                if room_number in expect_annotations:
                    expect_annotations.remove(room_number)
            except (AttributeError, KeyError):
                continue
        self.assertEqual(len(expect_annotations), ANNOTATION_NOT_MATCHED_1OG,
                         "The following rooms were not matched: {} ".format(expect_annotations))
        
    def test_all_annotations_matched_simple_plan_2og(self):
        
        expect_annotations = annotations_validation.expect_annotations_2og
        
        for polygon in self.simple_plan_2og.polygons:
            try:
                room_number = polygon.room.room_number
                if room_number in expect_annotations:
                    expect_annotations.remove(room_number)
            except (AttributeError, KeyError):
                continue
        self.assertEqual(len(expect_annotations), ANNOTATION_NOT_MATCHED_2OG,
                         "The following rooms were not matched: {} ".format(expect_annotations))

if __name__ == '__main__':
    unittest.main()