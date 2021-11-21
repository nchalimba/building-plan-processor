from dataclasses import dataclass

'''
Description: This class contains the api response for the fetching of available (extractable) data.
'''

@dataclass
class ApiResponseAvailableFields:
    status: int
    data: dict
