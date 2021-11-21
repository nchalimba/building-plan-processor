from dataclasses import dataclass, field

from app.main.dtos.response.adjacent_polygon_dto import AdjacentPolygonDto

''' 
    Description: This class represents the roompolygons next to each other(adjacent rooms).
'''


@dataclass()
class Adjacent_Polygon:
    adjacent_polygon_id: int
    shared_wall_length: float = field(default=None)
    polygon_id: int = field(default=None)

    def convert_to_dto(self) -> AdjacentPolygonDto:
        '''
        Description: This method transforms an adjacent polygon to its dto representation.
        Params: self: Adjacent_Polygon
        Return: adjacent_polygon_dto: AdjacentPolygonDto
        '''
        
        return AdjacentPolygonDto(self.adjacent_polygon_id, shared_wall_length=self.shared_wall_length)
