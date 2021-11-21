import unittest

from app.main.services.extraction_helper import ExtractionHelper
from app.main.extraction.dxf_extraction_coordinator import DxfExtractionCoordinator
from app.main.constants import NUDATA_LAYER_RAUMPOLYGON, TEST_POLYGON_INDEX_GENERATE_WALLS
from app.main.services.walls_extraction import WallsExtraction
from app.main.models.polygon import Polygon
from app.main.services.room_geometry import RoomGeometry




class TestRoomGeometry(unittest.TestCase):
   
    @classmethod
    def setUpClass(cls):

            '''
            Description: This method sets up the extraction of the room geometry from a given polygon.
                        Therefore, a modelspace and room polylines are created.
            Params: cls
            Return: none
            Exception: none 
            '''

            cls.dxf_file_path = 'app/main/media/Einfache_Plaene/'
            cls.dxf_file_name = 'R-Bau_D_EG.dxf'
            cls.floor_height = 5.5
            cls.orientation = 55.3
            cls.status = "OK"

            
            dxf_extraction_coordinator = DxfExtractionCoordinator()
            cls.dxf_file = dxf_extraction_coordinator.read_dxf_file(cls.dxf_file_path, cls.dxf_file_name)
            extraction_helper = ExtractionHelper()
            cls.modelspace = extraction_helper.get_modelspace(cls.dxf_file)
            
            
            layer = NUDATA_LAYER_RAUMPOLYGON
            cls.room_polylines = cls.modelspace.query('LWPolyline[layer=="{}"]'.format(layer))
    
    
    def test_room_geometry(self):

            '''
            Description: This method tests the extraction of the room geometry from a given polygon.
                        Therefore, a test polygon (i=9) is used to identify the room geometry and additionally the simple wall coordinates for orientation.
            Return: none
            Exception: none 
            '''

            i = TEST_POLYGON_INDEX_GENERATE_WALLS
            room_polyline = self.room_polylines[i]
            walls, ignored_edges_length, pillars, polygon_closed = WallsExtraction.create_walls_from_polyline(room_polyline)
            
            coordinates = room_polyline.get_points("XY")
            coordinates_seb = room_polyline.get_points('XYSEB')
            room_geometry = RoomGeometry()
            if len(coordinates) > 2:
                points = []
                for coordinate in coordinates_seb:
                    point = ExtractionHelper.get_point_from_seb_coordinate(coordinate)
                    points.append(point)
                    area, perimeter = ExtractionHelper.get_area_and_perimeter_from_polyline(room_polyline)
                    polygon_id = "1"
                    polygon = Polygon(polygon_id, area, perimeter, True)
                    polygon.walls = walls
                    polygon.pillars = pillars
                    polygon.points = points
                    polygon.ignored_edges_length = ignored_edges_length
                    polygon.geometry = room_geometry.get_room_geometry(polygon, coordinate, coordinates_seb)
                print(polygon.geometry)   

            counter = 0
            boolhandler = False
            for wall in walls:
                x_coordinate_start = wall.start_point.x_coordinate
                y_coordinate_start = wall.start_point.y_coordinate

                x_coordinate_end = wall.end_point.x_coordinate
                y_coordinate_end = wall.end_point.y_coordinate
                counter = counter + 1
                print("Wall: start_point: {}/{} | end_point: {}/{}".format(x_coordinate_start, y_coordinate_start, x_coordinate_end, y_coordinate_end))
            
            if(counter ==4):
                boolhandler = True

            self.assertEqual(len(walls), 4, 
            "data for validation: {} walls | Amount Corners {} | Room is squareshaped {} ".format(len(walls),counter,boolhandler)
            )

if __name__ == '__main__':
    unittest.main()
