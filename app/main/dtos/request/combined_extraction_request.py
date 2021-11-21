from dataclasses import dataclass

from .extraction_request_file import ExtractionRequestFile

''' 
Description: This file contains the structure of a request to extract both the simple and the architecture plan.
'''

@dataclass
class CombinedExtractionRequest:
    transaction_id: str
    simple_plan: ExtractionRequestFile
    architecture_plan: ExtractionRequestFile

    def __post_init__(self):
        '''
        Description: This method parses a plan dict to an object instance.
        Params: self: CombinedExtractionRequest
        '''

        if isinstance(self.simple_plan, dict):
            self.simple_plan = ExtractionRequestFile(**self.simple_plan)
        if isinstance(self.architecture_plan, dict):
            self.architecture_plan = ExtractionRequestFile(**self.architecture_plan)
        