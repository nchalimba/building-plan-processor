from dataclasses import dataclass, field

'''
Description: This class contains the api representation of rooms.
'''

@dataclass
class RoomDto:
    room_area: float
    room_number: str
    room_type: str
    room_name: str = field(default=None)
