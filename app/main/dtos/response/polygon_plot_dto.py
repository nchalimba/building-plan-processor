from dataclasses import dataclass, field


@dataclass
class PolygonPlotDto:
    polygon_id: str
    category: str
    title: str
    file_path: str