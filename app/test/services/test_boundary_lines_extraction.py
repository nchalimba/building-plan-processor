import unittest
from app.main.services.boundary_lines_extraction import BoundaryLinesExtraction
from app.main.extraction.dxf_extraction_coordinator import DxfExtractionCoordinator
from app.main.services.dxf_extraction_simple import DxfExtractionSimple
from app.main.services.extraction_helper import ExtractionHelper
from app.main.services.room_extraction import RoomExtraction

from app.main.constants import *
from app.test.test_data import room_113

'''
Description: taken from prototype C and adapted
'''
class TestBoundaryLinesExtraction(unittest.TestCase):

    def setUp(self):
        self.lines = room_113.test_lines["all_lines"]
        self.line = room_113.test_lines["all_lines"][0]
        self.list_to_filter = [1, 2, 1, 3, 4, 5, 5]
        self.room_name = "TestRoom"
        self.arcs = room_113.test_lines["arc_lines"]

    def test_recreate_missing_lines(self):
        result = BoundaryLinesExtraction.recreate_missing_lines(self.lines, self.room_name)
        self.assertTrue('coords' in result[0].keys())
        self.assertTrue('length' in result[0].keys())

    def test_substitute_boundary_lines_with_arcs(self):
        lines_to_substitute = BoundaryLinesExtraction.recreate_missing_lines(
            BoundaryLinesExtraction.cut_duplicated_lines_by_length_and_point_distance(self.lines, self.room_name), self.room_name)
        result = BoundaryLinesExtraction.substitute_boundary_lines_with_arcs(lines_to_substitute, self.arcs)
        self.assertTrue('coords' in result[0].keys())
        self.assertTrue('length' in result[0].keys())

    def test_get_boundary_lines(self):
        result = BoundaryLinesExtraction.get_boundary_lines(self.lines, self.arcs, self.room_name)
        self.assertTrue('coords' in result[0].keys())
        self.assertTrue('length' in result[0].keys())

    def test_check_start_end_points(self):
        result = BoundaryLinesExtraction.check_start_end_points(self.lines[0], self.lines)
        self.assertTrue(bool, type(result))

    def test_cut_duplicated_lines_by_length_and_point_distance(self):
        result = BoundaryLinesExtraction.cut_duplicated_lines_by_length_and_point_distance(self.lines, self.room_name)
        self.assertTrue('coords' in result[0].keys())
        self.assertTrue('length' in result[0].keys())


if __name__ == '__main__':
    unittest.main()
