from dataclasses import dataclass, field
from datetime import datetime

from app.main.constants import TIME_STAMP_FORMAT

''' 
Description: This file contains the structure of the api response if an error occured.
'''

@dataclass
class ErrorResponse:
    status: int
    message: str
    path: str
    transaction_id: str = field(default=None)
    timestamp: str = field(init=False)

    def __post_init__(self):
        '''
        Description: This method injects the timestamp of an initialized instance.
        Params: self: ErrorResponse
        '''
        self.timestamp = datetime.now().strftime(TIME_STAMP_FORMAT)
