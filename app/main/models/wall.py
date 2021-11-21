from dataclasses import dataclass, field

from app.main.dtos.response.wall_dto import WallDto
from app.main.models.line import Line
from app.main.models.window import Window

from .line import Line
from .point import Point

'''
    Description: This class represents a wall in a polygon or architecture plan.
'''


@dataclass()
class Wall:
    start_point: Point
    sky_direction: str = field(default=None)
    end_point: Point = field(default=None)
    length: float = field(default=None)
    orientation: float = field(default=None)
    is_outer_wall: bool = field(default=False)
    is_pillar: bool = field(default=False)
    wall_thickness: float = field(default=None)
    window_length: float = field(default=None)
    wall_type: str = field(default=None)
    has_curves: bool = field(default=None)
    wall_id: str = field(default=None)
    windows: list[Window] = field(default=None)
     
    def convert_to_dto(self) -> WallDto:
        '''
        Description: This method transforms a simple plan to its dto representation.
        Params: self: Wall
        Return: wall_dto: WallDto
        '''

        start_point = self.start_point.convert_to_dto()
        end_point = self.end_point.convert_to_dto()
        window_dtos = None
        if self.windows:
            window_dtos = []
            for window in self.windows:
                window_dtos.append(window.convert_to_dict())
        return WallDto(start_point, end_point, length=self.length, is_outer_wall=self.is_outer_wall, is_pillar=self.is_pillar,
                       orientation=self.orientation, wall_thickness=self.wall_thickness, window_length=self.window_length, wall_type=self.wall_type
                       , sky_direction=self.sky_direction, wall_id=self.wall_id, windows=window_dtos)
