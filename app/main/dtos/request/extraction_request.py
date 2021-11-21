from dataclasses import dataclass

from .extraction_request_file import ExtractionRequestFile

''' 
Description: This file contains the structure of a simple extraction request (both for simple and architecture plan).
'''

@dataclass
class ExtractionRequest:
    transaction_id: str
    file: ExtractionRequestFile

    def __post_init__(self):
        '''
        Description: This method parses a file dict into an object instance.
        Params: self: ExtractionRequest
        '''

        if isinstance(self.file, dict):
            self.file = ExtractionRequestFile(**self.file)

