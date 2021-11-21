from dataclasses import dataclass, field

from app.main.dtos.response.architecture_plan_dto import ArchitecturePlanDto
from app.main.dtos.response.report_dto import ReportDto
from app.main.dtos.response.simple_plan_dto import SimplePlanDto

'''
Description: This class contains the api representation of combined plans.
'''

@dataclass
class CombinedPlanDto:
    simple_plan: SimplePlanDto
    architecture_plan: ArchitecturePlanDto
    report: ReportDto
