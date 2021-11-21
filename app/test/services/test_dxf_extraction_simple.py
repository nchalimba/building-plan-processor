import unittest

from app.main.extraction.dxf_extraction_coordinator import DxfExtractionCoordinator
from app.main.services.dxf_extraction_simple import DxfExtractionSimple
from app.main.services.extraction_helper import ExtractionHelper
from app.main.models.simple_plan import Simple_Plan
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.main.constants import *

'''
Description: taken from prototype C and adapted
'''
class TestDxfExtractionSimple(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.dxf_file_path = 'app/main/media/Einfache_Plaene/'
        cls.dxf_file_name = 'R-Bau_D_EG.dxf'
        cls.orientation = 90

        dxf_extraction_coordinator = DxfExtractionCoordinator()
        cls.dxf_file = dxf_extraction_coordinator.read_dxf_file(cls.dxf_file_path, cls.dxf_file_name)

        extraction_helper = ExtractionHelper()
        cls.modelspace = extraction_helper.get_modelspace(cls.dxf_file)
    
        cls.dxf_extraction_simple = DxfExtractionSimple()

        cls.extraction_request_file = ExtractionRequestFile(
            file_path=cls.dxf_file_path, file_name=cls.dxf_file_name, floor_height=3.21, orientation=3.21
        )

    def test_entry_point_return_type_is_simple_plan(self):
        simple_plan = self.dxf_extraction_simple.entry_point(self.extraction_request_file, self.dxf_file)
        self.assertIsInstance(simple_plan[0], Simple_Plan)

    def test_get_all_polygons(self):
        polygons = self.dxf_extraction_simple.get_all_polygons(self.dxf_file, self.dxf_file_path + self.dxf_file_name)
        self.assertEqual(len(polygons), 4)

    def test_get_all_polygons_with_orientation(self):
        polygons = self.dxf_extraction_simple.get_all_polygons(self.dxf_file, self.dxf_file_path + self.dxf_file_name, self.orientation)
        extracted_functionalities = polygons[2]
        self.assertEqual(extracted_functionalities.orientation, True)

    def test_get_polygon_with_virtual_entities(self):
        room_polylines = self.modelspace.query("LWPolyline[layer=='RAUMPOLYGON']")
        room_polyline_sample = room_polylines[11]
        polygon_with_virtual_entities = self.dxf_extraction_simple.get_polygon_with_virtual_entities(room_polyline_sample, "id-test-123")
        self.assertNotEqual(len(polygon_with_virtual_entities), 0)
        self.assertEqual(list(polygon_with_virtual_entities.keys()), 
                         ['polygon', 'all_line_list', 'straight_line_list_with_length', 'arc_list_with_length', 'polygon_id'])

    def test_get_virtual_entities(self):
        room_polylines = self.modelspace.query("LWPolyline[layer=='RAUMPOLYGON']")
        virtual_entities_polygon = self.dxf_extraction_simple.get_virtual_entities(room_polylines[0])
        self.assertNotEqual(None, virtual_entities_polygon)
        self.assertEqual(list(virtual_entities_polygon.keys()),
                         ['all_line_list', 'straight_line_list_with_length', 'arc_list_with_length'])
    
    def test_get_virtual_entities_no_polyline_parameter(self):
        lines = self.modelspace.query("LINE[layer=='RAUMSTEMPEL']")
        virtual_entities_line = self.dxf_extraction_simple.get_virtual_entities(lines[0])
        self.assertEqual(None, virtual_entities_line)


if __name__ == '__main__':
    unittest.main()