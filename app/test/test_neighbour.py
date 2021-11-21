import unittest

from app.main.extraction.dxf_extraction_coordinator import DxfExtractionCoordinator
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.main.constants import NEIGHBOUR_INCORRECT_EG
from app.main.constants import NEIGHBOUR_INCORRECT_1OG
from app.main.constants import NEIGHBOUR_INCORRECT_2OG
from app.test.test_data import neighbour_validation

class TestNeighbour(unittest.TestCase):

    '''
    Description: This test class is used to validate amount of neighbours per room using test data in app.test.test_data.neighbour_validation
    amount test data for eg: 59, 1og: 60, 2og: 60
    assert values = NEIGHBOUR_INCORRECT_{EG,1OG,2OG} specified in constants.py
    '''

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

    def test_neighbour_eg(self):
        
        room_with_neighbours = []
        expect_neighbour = neighbour_validation.expect_neighbour_eg

        for polygon in self.simple_plan_eg.polygons:
            try:
                room_number = polygon.room.room_number
                adjacent_polygons = len(polygon.adjacent_polygons)
                adjacent_neighbours_expect = expect_neighbour.get(room_number)
                if adjacent_neighbours_expect > 0:
                    room_with_neighbours.append(room_number)
                    if adjacent_polygons == adjacent_neighbours_expect:
                        del expect_neighbour[room_number]
            except Exception as e:
                pass
        self.assertEqual(len(expect_neighbour), NEIGHBOUR_INCORRECT_EG,
            "number of incorrect calculated neighbour rooms: {} ".format(len(expect_neighbour)))
    
    def test_neighbour_1og(self):

        room_with_neighbours = []
        expect_neighbour = neighbour_validation.expect_neighbour_1og

        for polygon in self.simple_plan_1og.polygons:
            try:
                room_number = polygon.room.room_number
                adjacent_polygons = len(polygon.adjacent_polygons)
                adjacent_neighbours_expect = expect_neighbour.get(room_number)
                if adjacent_neighbours_expect > 0:
                    room_with_neighbours.append(room_number)
                    if adjacent_polygons == adjacent_neighbours_expect:
                        del expect_neighbour[room_number]
            except Exception as e:
                pass
        self.assertEqual(len(expect_neighbour), NEIGHBOUR_INCORRECT_1OG,
            "number of incorrect calculated neighbour rooms: {} ".format(len(expect_neighbour)))

    def test_neighbour_2og(self):
    
        room_with_neighbours = []
        expect_neighbour = neighbour_validation.expect_neighbour_2og

        for polygon in self.simple_plan_2og.polygons:
            try:
                room_number = polygon.room.room_number
                adjacent_polygons = len(polygon.adjacent_polygons)
                adjacent_neighbours_expect = expect_neighbour.get(room_number)
                if adjacent_neighbours_expect > 0:
                    room_with_neighbours.append(room_number)
                    if adjacent_polygons == adjacent_neighbours_expect:
                        del expect_neighbour[room_number]
                    #else:
            except Exception as e:
                pass
        self.assertEqual(len(expect_neighbour), NEIGHBOUR_INCORRECT_2OG,
            "number of incorrect calculated neighbour rooms: {} ".format(len(expect_neighbour)))

if __name__ == '__main__':
    unittest.main()