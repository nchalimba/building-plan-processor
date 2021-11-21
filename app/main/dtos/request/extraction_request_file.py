from dataclasses import dataclass, field

''' 
Description: This file contains the structure of the file, which is passed in an api request.
'''

@dataclass
class ExtractionRequestFile:
    file_path: str
    file_name: str
    floor_height: float = field(default=None)
    orientation: float = field(default=None)
