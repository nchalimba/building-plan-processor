import math
from os import stat

from app.main.constants import (EDGE_THRESHOLD, ENABLE_CLOSE_POLYGONS,
                                ENABLE_COMPLEX_PILLAR_KILL, ENABLE_EDGES_KILL,
                                ENABLE_POINT_ON_LINE_KILL,
                                ENABLE_SIMPLE_PILLAR_KILL)
from app.main.models.pillar import Pillar
from app.main.models.point import Point
from app.main.models.wall import Wall
from app.main.reporting.reporting_models import LogMessage
from ezdxf.entities import LWPolyline
from shapely import geometry

'''
Description: This class represents the logic for detecting and extracting walls from simple plans
Note: The concepts of this class can be found here "/jupiter_notebooks/poc_walls/poc_walls_final.ipynb"
'''

class WallsExtraction:
    @staticmethod
    def create_walls_from_polyline(polyline: LWPolyline, log_messages: LogMessage = None) -> tuple[list[Wall], float, list[Pillar], bool] :
        '''
        Description: This method coordinates and orchestrations the wall generation from a given polyline.
        Params: polyline: LWPolyline, log_messages: LogMessage
        Return: walls: list[Wall], ignored_edges_length: float, pillars: list[Pillar], polygon_closed: bool
        Exception: ---
        '''

        ignored_edges_length = 0.0
        pillars = None
        coordinates = polyline.get_points("XYSEB")
        filtered_coordinates, walls, ignored_edges_length, pillars, polygon_closed = WallsExtraction.generete_walls_new(coordinates)
        return walls, ignored_edges_length, pillars, polygon_closed
        
        


    @staticmethod
    def transform_coordinate_to_point(coordinate: tuple) -> Point:
        '''
        Description: This method transforms a coordinate tuple into a point object.
        Params: coordinate: tuple 
        Return: point: Point
        Exception: ---
        '''
        return Point(x_coordinate=coordinate[0], y_coordinate=coordinate[1], 
        s_width=coordinate[2], e_width=coordinate[3], b_value=coordinate[4])

    @staticmethod
    def create_pillar_wall(start_coordinate: tuple, end_coordinate: tuple) -> Wall:
        '''
        Description: This method creates a pillar with a wall object.
        Params: start_coordinate: tuple, end_coordinate: tuple
        Return: wall: Wall
        Exception: ---
        '''
        start_point = WallsExtraction.transform_coordinate_to_point(start_coordinate)
        end_point = WallsExtraction.transform_coordinate_to_point(end_coordinate)
        return Wall(start_point=start_point, end_point=end_point, is_pillar=True)

    def create_pillar(start_coordinate: tuple, end_coordinate: tuple) -> Pillar:
        '''
        Description: This method creates an pillar object with two given coordinates.
        Params: start_coordinate: tuple, end_coordinate: tuple
        Return: pillar: Pillar
        Exception: ---
        '''
        start_point = WallsExtraction.transform_coordinate_to_point(start_coordinate)
        end_point = WallsExtraction.transform_coordinate_to_point(end_coordinate)
        return Pillar(start_point=start_point, end_point=end_point)

    @staticmethod
    def is_simple_pillar(coordinates: list, index: int) -> bool:
        '''
        Description: This method detects if a polygon (coordinates: list) contains a simple pillar.
        Params: coordinates: list, index: int
        Return: result: bool
        Exception: ---
        '''
        if len(coordinates) - 1 < index + 2:
            return False
        
        point_1 = coordinates[index]
        point_2 = coordinates[index + 1]
        point_3 = coordinates[index + 2]

        condition_1 = point_1[4] != 0.0 and point_2[4] != 0.0
        condition_2 = point_3[0] == point_1[0] and point_3[1] == point_1[1]
        return condition_1 and condition_2

    @staticmethod
    def is_complex_pillar(coordinates: list, index: int) -> bool:
        '''
        Description: This method detects if a polygon (coordinates: list) contains a complex pillar.
        Params: coordinates: list, index: int
        Return: result: bool
        Exception: ---
        '''
        if len(coordinates) - 1 < index + 9:
            return False
        threshold = 0.05
        point_1 = WallsExtraction.transform_coordinate_to_point(coordinates[index])
        point_2 = WallsExtraction.transform_coordinate_to_point(coordinates[index + 1])
        point_8 = WallsExtraction.transform_coordinate_to_point(coordinates[index + 7])
        point_9 = WallsExtraction.transform_coordinate_to_point(coordinates[index + 8])
        point_10 = WallsExtraction.transform_coordinate_to_point(coordinates[index + 9])

        condition_1 = WallsExtraction.get_distance_of_points(point_1, point_10) < threshold

        condition_2 = WallsExtraction.get_distance_of_points(point_2, point_9) < threshold
        condition_3 = point_2.b_value != None and point_2.b_value != 0.0 and point_8.b_value != None and point_8.b_value != 0.0
        return condition_1 and condition_2 and condition_3

    @staticmethod
    def get_distance_of_points(point_1: Point, point_2: Point) -> float:
        '''
        Description: This method gets the distance between two coordinate points after creating an linestring from them.
        Params: point_1: Point, point_2: Point
        Return: line_string.length: float
        Exception: ---
        '''
        line_string = geometry.LineString([(point_1.x_coordinate, point_1.y_coordinate), (point_2.x_coordinate, point_2.y_coordinate)])
        return line_string.length

    @staticmethod
    def are_points_on_line(point_1: tuple, point_2: tuple, point_3: tuple) -> bool:
        '''
        Description: This method checks if 3 coordinate points are on one straight line.
        Params: point_1: tuple, point_2: tuple, point_3: tuple
        Return: result: bool
        Exception: ---
        '''
        ang = WallsExtraction.get_angle(point_1, point_2, point_3)
        ang = round(ang, 1)
        return (WallsExtraction.is_in_angle_corridor(180.0, ang) or 
        WallsExtraction.is_in_angle_corridor(-180.0, ang) or WallsExtraction.is_in_angle_corridor(0, ang))

    @staticmethod
    def is_in_angle_corridor(angle: float, angle_is: float) -> bool:
        '''
        Description: This method checks if a fixed angle and a calculated angle are in a defined corridor.
        Params: angle: float, angle_is: float
        Return: result: bool
        Exception: ---
        '''
        corridor = 2.0
        return angle_is > angle - corridor and angle_is < angle + corridor

    @staticmethod
    def get_angle(a_in: tuple, b_in: tuple, c_in: tuple) -> float:
        '''
        Description: This method get the angle form 3 given coordinates.
        Params: a_in: tuple, b_in: tuple, c_in: tuple
        Return: ang: float
        Exception: ---
        '''
        a = {}
        b = {}
        c = {}
        a[0] = round(a_in[0], 2)
        a[1] = round(a_in[1], 2)

        b[0] = round(b_in[0], 2)
        b[1] = round(b_in[1], 2)

        c[0] = round(c_in[0], 2)
        c[1] = round(c_in[1], 2)

        angle = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
        return angle

    @staticmethod
    def check_bulge_value(coordinate: tuple) -> bool:
        '''
        Description: This method checks if an coordinate tuple has a bugle value.
        Params: coordinate: tuple
        Return: result: bool
        Exception: ---
        '''
        return coordinate[4] != 0.0

    @staticmethod
    def generete_walls_new(coordinates: list[tuple]) -> tuple[list[tuple], list[Wall]]:
        
        '''
        Description: This method contains and orchestrates the logic for creating all walls from a plan.
        Params: coordinates: list[tuple]
        Return: filtered_coordinates: tuple, walls_filtered: list[Walls], 
        ignored_edges_length: float, pillars: list[Walls] , polygon_closed: bool
        Exception: ---
        '''
        
        walls = []
        pillars = []
        ignored_indexes = []
        filtered_coordinates = []

        polygon_closed = False
        if(ENABLE_CLOSE_POLYGONS):
            first_coordinates = coordinates[0]
            first_coordinates_x = first_coordinates[0]
            first_coordinates_y = first_coordinates[1]
            last_coordinates = coordinates[len(coordinates) - 1]
            last_coordinates_x = last_coordinates[0]
            last_coordinates_y = last_coordinates[1]
            if not (first_coordinates_x == last_coordinates_x) or not (first_coordinates_y == last_coordinates_y):
                coordinates.append(first_coordinates)
                polygon_closed = True
                 
        if(ENABLE_SIMPLE_PILLAR_KILL):
            ### 1. Durchgang ###
            for coordinate_index in range(len(coordinates)):
                if WallsExtraction.is_simple_pillar(coordinates, coordinate_index):
                    ignored_indexes.append(coordinate_index)
                    ignored_indexes.append(coordinate_index + 1)
                    ignored_indexes.append(coordinate_index + 2)
                    ignored_indexes.append(coordinate_index + 3)

                    #wall = WallsExtraction.create_pillar_wall(coordinates[coordinate_index], coordinates[coordinate_index + 2])
                    #walls.append(wall)
                    pillar = WallsExtraction.create_pillar(coordinates[coordinate_index], coordinates[coordinate_index + 2])
                    pillars.append(pillar)
        
            for coordinate_index in range(len(coordinates)):
                if coordinate_index not in ignored_indexes:
                    filtered_coordinates.append(coordinates[coordinate_index])
        

            coordinates =filtered_coordinates
            ignored_indexes = []

        if(ENABLE_COMPLEX_PILLAR_KILL):
            ### 2. Durchgang
            for coordinate_index in range(len(coordinates)):
                if WallsExtraction.is_complex_pillar(coordinates, coordinate_index):
                    for i in range(8):
                        ignored_indexes.append(coordinate_index + i + 1)
                    #wall = WallsExtraction.create_pillar_wall(coordinates[coordinate_index + 1], coordinates[coordinate_index + 8])
                    #walls.append(wall)
                    pillar = WallsExtraction.create_pillar(coordinates[coordinate_index + 1], coordinates[coordinate_index + 8])
                    pillars.append(pillar)

            filtered_coordinates = []
            for coordinate_index in range(len(coordinates)):
                if coordinate_index not in ignored_indexes:
                    filtered_coordinates.append(coordinates[coordinate_index])
            coordinates =filtered_coordinates 
            ignored_indexes = []
        
   
        ignored_edges_length = 0.0
        if(ENABLE_EDGES_KILL):
        ### 3. Druchgang ###
            for coordinate_index in range(len(coordinates)-1):
                point_1 = WallsExtraction.transform_coordinate_to_point(coordinates[coordinate_index])
                point_2 = WallsExtraction.transform_coordinate_to_point(coordinates[coordinate_index + 1])
                edge_length = WallsExtraction.get_distance_of_points(point_1, point_2)
                if edge_length < EDGE_THRESHOLD and edge_length > 0.00001:
                    ignored_edges_length = ignored_edges_length + edge_length
                    ignored_indexes.append(coordinate_index)

            filtered_coordinates = []
            for coordinate_index in range(len(coordinates)):
                if coordinate_index not in ignored_indexes:
                    filtered_coordinates.append(coordinates[coordinate_index])
            coordinates =filtered_coordinates  

        if ENABLE_POINT_ON_LINE_KILL:
            point_on_line_possible = False
            ### 4. Durchgang ###
            for coordinate_index in range(len(coordinates)-1):
                coordinate_1 = coordinates[coordinate_index]
                coordinate_2 = coordinates[coordinate_index]
                coordinate_3 = coordinates[coordinate_index + 1]
                if coordinate_index - 1 >= 0:
                    point_on_line_possible = True
                    coordinate_1 = coordinates[coordinate_index - 1]

                if point_on_line_possible and WallsExtraction.are_points_on_line(coordinate_1, coordinate_2, coordinate_3):    
                    ignored_indexes.append(coordinate_index)
            
            filtered_coordinates = []
            for coordinate_index in range(len(coordinates)):
                if coordinate_index not in ignored_indexes:
                    filtered_coordinates.append(coordinates[coordinate_index])
            coordinates =filtered_coordinates

                

        last_wall = Wall(None, None)
        point_on_line_possible = False
        ### 5. Durchgang ###
        for coordinate_index in range(len(coordinates)-1):
            
            if WallsExtraction.check_bulge_value(coordinates[coordinate_index]):
                #round wall
                start_point = WallsExtraction.transform_coordinate_to_point(coordinates[coordinate_index])
                end_point = WallsExtraction.transform_coordinate_to_point(coordinates[coordinate_index + 1])
                wall_length = WallsExtraction.get_distance_of_points(start_point, end_point)
                wall = Wall(start_point=start_point, end_point=end_point, has_curves=True, length=wall_length)
                walls.append(wall)
                last_wall = wall
            else:
                #normal wall
                start_point = WallsExtraction.transform_coordinate_to_point(coordinates[coordinate_index])
                end_point = WallsExtraction.transform_coordinate_to_point(coordinates[coordinate_index + 1])
                wall_length = WallsExtraction.get_distance_of_points(start_point, end_point)
                wall = Wall(start_point=start_point, end_point=end_point, length=wall_length)
                walls.append(wall)
                last_wall = wall

        walls_filtered = []
        for wall in walls:
            if not(wall.start_point.x_coordinate == wall.end_point.x_coordinate and 
            wall.start_point.y_coordinate == wall.end_point.y_coordinate):
                walls_filtered.append(wall)


        return filtered_coordinates, walls_filtered, ignored_edges_length, pillars, polygon_closed
