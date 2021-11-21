from dataclasses import dataclass, field
from pathlib import PosixPath

from app.main.dtos.response.polygon_dto import PolygonDto

from .adjacent_polygon import Adjacent_Polygon
from .pillar import Pillar
from .point import Point
from .room import Room
from .wall import Wall
from .window import Window

'''
    Description: This class represents a polygon for one room within a DXF-file.
'''


@dataclass()
class Polygon:
    id: int
    area: float
    perimeter: float
    has_roomstamp: bool
    room: Room = field(default=None)
    points: list[Point] = field(default=None)
    jetty_area: float = field(default=None)
    has_jetty: bool = field(default=False)
    amount_corners: int = field(default=None)
    has_curves: bool = field(default=False)
    geometry: str = field(default=None)
    shape_type: str = field(default=None)
    adjacent_polygons: list[Adjacent_Polygon] = field(default=None)
    walls: list[Wall] = field(default=None)
    outer_wall_percentage: float = field(default=None)
    ignored_edges_length: float = field(default=0.0)
    pillars: list[Pillar] = field(default=None)
    windows: list[Window] = field(default=None)
    

    def convert_to_dto(self, floor_height: float = None) -> PolygonDto:
        '''
        Description: This method transforms a polygon to its dto representation.
        Params: self: Polygon, floor_height: float
        Return: polygon_dto: PolygonDto
        '''

        wall_dtos = None
        if self.walls:
            wall_dtos = []
            for wall in self.walls:
                wall_dtos.append(wall.convert_to_dto())
        room_dto = None
        if self.room:
            room_dto = self.room.convert_to_dto()
        adjacent_polygon_dtos = None
        if self.adjacent_polygons:
            adjacent_polygon_dtos = []
            for adjacent_polygon in self.adjacent_polygons:
                adjacent_polygon_dtos.append(adjacent_polygon.convert_to_dto())
        point_dtos = None
        if self.points:
            point_dtos = []
            for point in self.points:
                point_dtos.append(point.convert_to_dto())
        pillar_dtos = None
        if self.pillars:
            pillar_dtos = []
            for pillar in self.pillars:
                if pillar.center_point or pillar.start_point:
                    pillar_dtos.append(pillar.convert_to_dto())
        ignored_edges_percentage = self.ignored_edges_length / self.perimeter
        #calculating window length and facade length
        window_length = 0
        facade_length = 0
        if self.walls:
            for wall in self.walls:
                 if wall.window_length: 
                    window_length += wall.window_length
                 if wall.is_outer_wall and wall.length:
                     facade_length += wall.length        
        #calculating window area and facade area
        window_area = None
        facade_area = None
        if floor_height:
            window_area = window_length * floor_height
            facade_area = facade_length * floor_height


        return PolygonDto(self.id, self.area, self.perimeter, has_roomstamp=self.has_roomstamp,
                          points=point_dtos, room=room_dto, adjacent_polygons=adjacent_polygon_dtos, walls=wall_dtos,
                          jetty_area=self.jetty_area, has_jetty=self.has_jetty, amount_corners=self.amount_corners,
                          has_curves=self.has_curves, shape_type=self.shape_type, outer_wall_percentage=self.outer_wall_percentage,
                          ignored_edges_percentage=ignored_edges_percentage, pillars=pillar_dtos, geometry=self.geometry, 
                          window_length=window_length, window_area=window_area, facade_length=facade_length, facade_area=facade_area)
