from dataclasses import dataclass

from app.main.dtos.response.combined_plan_dto import CombinedPlanDto

'''
Description: This class contains the api response for a combined plan extraction and matching.
'''

@dataclass
class ApiResponseCombined:
    status: int
    transaction_id: str
    data: CombinedPlanDto
