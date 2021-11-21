from dataclasses import dataclass, field

from app.main.dtos.response.plots_dto import PlotsDto


@dataclass
class ReportDto:
    report_path: str
    plots: PlotsDto