from dataclasses import dataclass, field

from app.main.dtos.response.point_dto import PointDto

'''
Description: This class contains the api representation of lines.
'''

@dataclass
class LineDto:
    start_point: PointDto
    end_point: PointDto
