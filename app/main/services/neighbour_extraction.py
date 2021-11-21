from app.main.constants import DISTANCE_TO_NEIGHBOURS
from app.main.models.adjacent_polygon import Adjacent_Polygon
from app.main.models.polygon import Polygon
from app.main.services.extraction_helper import ExtractionHelper


class NeighbourExtraction():
    def get_neighbours(self, polygons: list, this_polygon: Polygon) -> list[Adjacent_Polygon]:
        '''
        Description: This method checks the scaling of the plans and if they can be matched.
        Params: polygons: list, this_polygon: Polygon
        Return: potential_neighbors: list[Adjacent_Polygon]
        Exception: ---
        '''
        potential_neighbors = []
        for other_polygon in polygons:
            if other_polygon == this_polygon:
                continue
            else:
                shapely_polygon = ExtractionHelper.transform_polygon_to_shapely_polygon(
                    this_polygon)
                shapely_polygon_other = ExtractionHelper.transform_polygon_to_shapely_polygon(
                    other_polygon)

                if shapely_polygon.distance(shapely_polygon_other) < DISTANCE_TO_NEIGHBOURS:
                    adjacent_polygon = Adjacent_Polygon(other_polygon.id)
                    potential_neighbors.append(adjacent_polygon)
        return potential_neighbors
    pass
