from dataclasses import dataclass

from app.main.dtos.response.simple_plan_dto import SimplePlanDto

'''
Description: This class contains the api response for a simple plan extraction.
'''

@dataclass
class ApiResponseSimple:
    status: int
    transaction_id: str
    data: SimplePlanDto
