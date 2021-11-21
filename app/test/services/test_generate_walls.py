import unittest
from ezdxf.document import Drawing
from app.main.constants import NUDATA_LAYER_RAUMPOLYGON, TEST_POLYGON_INDEX_GENERATE_WALLS
from app.main.services.walls_extraction import WallsExtraction
from app.main.services.extraction_helper import ExtractionHelper
from shapely.geometry.polygon import Polygon as Shapely_Polygon
from app.main.extraction.dxf_extraction_coordinator import DxfExtractionCoordinator



class TestGenerateWalls(unittest.TestCase):

    
    @classmethod
    def setUpClass(cls):

        '''
        Description: This method sets up the unit test to check if the creation of simple walls works. 
        Params: cls
        Return: none
        Exception: none 
        '''
        
        cls.dxf_file_path = 'app/main/media/Einfache_Plaene/'
        cls.dxf_file_name = 'R-Bau_D_EG.dxf'

        dxf_extraction_coordinator = DxfExtractionCoordinator()
        cls.dxf_file = dxf_extraction_coordinator.read_dxf_file(cls.dxf_file_path, cls.dxf_file_name)

        extraction_helper = ExtractionHelper()
        cls.modelspace = extraction_helper.get_modelspace(cls.dxf_file)

        layer = NUDATA_LAYER_RAUMPOLYGON
        cls.room_polylines = cls.modelspace.query('LWPolyline[layer=="{}"]'.format(layer))
    
    
    def test_generate_walls(self):

        '''
        Description: This method runs the unit test for generate walls.
                    The creation of walls for the chosen test polygon (i=30), which has visibly 4 walls in the simple plan ('R-Bau_D_EG.dxf') works correctly

        Params: self
        Return: none
        Exception: none 
        '''
        
        i = TEST_POLYGON_INDEX_GENERATE_WALLS
        room_polyline = self.room_polylines[i]
        walls, ignored_edges_length, pillars, polygon_closed = WallsExtraction.create_walls_from_polyline(room_polyline)
        self.assertEqual(len(walls), 4)
        

        for wall in walls:
            x_coordinate_start = wall.start_point.x_coordinate
            y_coordinate_start = wall.start_point.y_coordinate

            x_coordinate_end = wall.end_point.x_coordinate
            y_coordinate_end = wall.end_point.y_coordinate
            print("Wall: start_point: {}/{} | end_point: {}/{}".format(x_coordinate_start, y_coordinate_start, x_coordinate_end, y_coordinate_end))
        

if __name__ == '__main__':
    unittest.main()
