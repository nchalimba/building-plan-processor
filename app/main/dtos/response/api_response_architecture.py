from dataclasses import dataclass

from app.main.dtos.response.architecture_plan_dto import ArchitecturePlanDto

'''
Description: This class contains the api response for an architecture plan extraction.
'''


@dataclass
class ApiResponseArchitecture:
    status: int
    transaction_id: str
    data: ArchitecturePlanDto
