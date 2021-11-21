from os import remove
import unittest
from numpy import poly
from app.main.extraction.dxf_extraction_coordinator import DxfExtractionCoordinator
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.test.test_data import orientation_validation

''' 
Description: This test class is used to validate the orientation using extracted sky directions
'''

class TestOrientation(unittest.TestCase):
    
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


    def test_orientation(self):
        ''' 
        Return: none
        Exception: none
        '''

        expect_orientation = orientation_validation.expect_orientation
        for polygon in self.simple_plan_eg.polygons:
            try:
                room_number = polygon.room.room_number
                room_orientation_validation = expect_orientation.get(room_number)
                if room_orientation_validation != None:
                    walls = polygon.walls
                    orientations_for_this_room = []
                    for wall in walls:
                        skydirection = None
                        skydirection = wall.sky_direction
                        if skydirection != None:
                            orientations_for_this_room.append(skydirection)
                    orientations_for_this_room = list(set(orientations_for_this_room))
                    for skydirection in orientations_for_this_room:
                        for key, value in expect_orientation.items():
                            if key == room_number:
                                if skydirection in value:
                                    expect_orientation[room_number].remove(skydirection)
                    for key, value in expect_orientation.items():
                        if len(value) == 0:
                            del expect_orientation[key]    
            except Exception: 
                pass 

        self.assertEqual(len(expect_orientation), 0,
                            "Rooms with orientation that were not extrected {} ".format(expect_orientation))

if __name__ == '__main__':
    unittest.main()