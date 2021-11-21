from app.main.models.polygon import Polygon
from loguru import logger
main_logger = logger.bind()
from app.main.constants import COORDINATE_THRESHOLD_BULGE_VALUE_MIN
from app.main.constants import COORDINATE_THRESHOLD_BULGE_VALUE_MAX


class RoomGeometry():
    
    def check_bulge_value(self, coordinate: tuple):
        '''
        Description: This method checks if a buldge value exists for a given coordinate tuple in order to identify round walls
        Params: coordinate: tuple
        Return: bool
        Exception: none 
        '''

        if coordinate[4] >= COORDINATE_THRESHOLD_BULGE_VALUE_MIN and coordinate[4] <= COORDINATE_THRESHOLD_BULGE_VALUE_MAX and coordinate[4] != 0.0:
            return True 
        return False

    

    def get_polygon_corners(self, polygon: Polygon) -> int:
        '''
        Description: This method determines corners in polygons. Used for room geometry.
        Params: polygon: Polygon
        Return: corner_counter: int
        '''
        
        wall_list = polygon.walls 
        corner_counter = 0
            
        start_points = []
        end_points = []
            
        for wall in wall_list: 
            start_points.append(wall.start_point) 
            end_points.append(wall.end_point)
                
        for i in range(len(start_points)): 
            for m in range(len(end_points)): 
                if start_points[i] == end_points[m]:
                    corner_counter = corner_counter + 1
        polygon.amount_corners = corner_counter
        return polygon.amount_corners


 
    def get_room_geometry(self, polygon: Polygon, coordinate: tuple, coordinates_seb):
        
        '''
        Description: This method identifies the geometry for a given polygon regarding its possible buldge value and amount of corners.
        Params: polygon: Polygon, coordinate: tuple, coordinates_seb
        Return: polygon.geometry
        Exception: none 
        '''  
        
        for coordinate in coordinates_seb:

            if self.check_bulge_value(coordinate) == True:
                polygon.geometry = "Raum hat einen runden Wandanteil"
                return polygon.geometry
        if self.get_polygon_corners(polygon) == 4:
            polygon.geometry = "Raum ist viereckig"
        elif self.get_polygon_corners(polygon) == 5:
            polygon.geometry = "Raum ist fünfeckig"
        elif self.get_polygon_corners(polygon) == 6:
            polygon.geometry = "Raum ist sechseckig"
        elif self.get_polygon_corners(polygon) == 8:
            polygon.geometry = "Raum ist achteckig"
        else:
            polygon.geometry = "Sonstige Raumform"
        return polygon.geometry
