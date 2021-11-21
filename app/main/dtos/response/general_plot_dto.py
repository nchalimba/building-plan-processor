from dataclasses import dataclass, field

@dataclass
class GeneralPlotDto:
    category: str
    title: str
    file_path: str