from app.main.models.wall import Wall
import unittest
from app.main.extraction.dxf_extraction_coordinator import DxfExtractionCoordinator
from app.main.services.extraction_helper import ExtractionHelper

from ezdxf.layouts.layout import Modelspace

from app.main.extraction.dxf_extraction_coordinator import DxfExtractionSimple
from app.main.services.validation_helper import ValidationHelper
from app.main.models.point import Point
from app.main.models.wall import Wall
from app.main.models.polygon import Polygon

from app.main.constants import *

from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import LineString
from ezdxf.entities.lwpolyline import LWPolyline, LWPolylinePoints


'''
Description: taken from prototype C and adapted
'''
class TestExtractionHelper(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        dxf_file_path = 'app/main/media/Einfache_Plaene/'
        dxf_file_name = 'R-Bau_D_EG.dxf'

        dxf_extraction_coordinator = DxfExtractionCoordinator()
        cls.dxf_file = dxf_extraction_coordinator.read_dxf_file(dxf_file_path, dxf_file_name)

        cls.modelspace = ExtractionHelper.get_modelspace(cls.dxf_file)
        dxf_extraction_simple = DxfExtractionSimple()
        cls.polygons, cls.polygons_with_virtual_entities, cls.extraced_functionalities, cls.counter_polygon_closed = dxf_extraction_simple.get_all_polygons(cls.dxf_file, dxf_file_path + dxf_file_name)

    def test_get_all_annotations(self):
        annotations = ExtractionHelper.get_all_annotations(self.modelspace, NUDATA_LAYER_RAUMSTEMPEL)
        self.assertEqual(len(annotations), 244)

    def test_get_all_annotations_unknown_layer(self):
        annotations = ExtractionHelper.get_all_annotations(self.modelspace, 'ROOOOM')
        self.assertEqual(len(annotations), 0)

    def test_get_all_annotations_no_modelspace(self):
        annotations = ExtractionHelper.get_all_annotations(None, NUDATA_LAYER_RAUMSTEMPEL)
        self.assertIsNone(annotations)

    def test_calculate_perimeter_with_arcs_success(self):
        boundary_line_list = ValidationHelper.get_line_objects_of_polygon(list(self.polygons_with_virtual_entities[0]
                                                                         ['polygon'].exterior.coords))
        arc_list_with_length = self.polygons_with_virtual_entities[0]['arc_list_with_length']
        substituted_boundary_lines_with_arcs = ValidationHelper.substitute_boundary_lines_with_arcs(
            boundary_line_list_polygon=boundary_line_list, virt_arc_list_with_length=arc_list_with_length)
        correct_result = ExtractionHelper.calculate_perimeter_with_arcs(
            substituted_boundary_lines_with_arcs=substituted_boundary_lines_with_arcs)
        self.assertNotEqual(None, correct_result)

    def test_calculate_perimeter_with_arcs_false_param_type_for_subst_boundary_lines_list(self):
        point = Point(0.0, 0.0)
        no_list_result = ExtractionHelper.calculate_perimeter_with_arcs(substituted_boundary_lines_with_arcs=point)
        self.assertEqual(None, no_list_result)

    def test_calculate_perimeter_with_arcs_false_param_invalid_subst_boundary_lines_list(self):
        boundary_line_list = ValidationHelper.get_line_objects_of_polygon(list(self.polygons_with_virtual_entities[0]
                                                                         ['polygon'].exterior.coords))
        arc_list_with_length = self.polygons_with_virtual_entities[0]['arc_list_with_length']
        substituted_boundary_lines_with_arcs = ValidationHelper.substitute_boundary_lines_with_arcs(
            boundary_line_list_polygon=boundary_line_list, virt_arc_list_with_length=arc_list_with_length)
        line_list_without_length = []
        for line_with_length in substituted_boundary_lines_with_arcs:
            line_list_without_length.append(line_with_length['line'])
        no_dict_in_list_result = ExtractionHelper.calculate_perimeter_with_arcs(
            substituted_boundary_lines_with_arcs=line_list_without_length)
        self.assertEqual(None, no_dict_in_list_result)

    def test_calculate_perimeter_with_arcs_false_param_keys_in_dict_of_list(self):
        boundary_line_list = ValidationHelper.get_line_objects_of_polygon(list(self.polygons_with_virtual_entities[0]
                                                                         ['polygon'].exterior.coords))
        arc_list_with_length = self.polygons_with_virtual_entities[0]['arc_list_with_length']
        substituted_boundary_lines_with_arcs = ValidationHelper.substitute_boundary_lines_with_arcs(
            boundary_line_list_polygon=boundary_line_list, virt_arc_list_with_length=arc_list_with_length)
        line_list_missing_keys = []
        for line_with_length in substituted_boundary_lines_with_arcs:
            line_list_missing_keys.append({'line': line_with_length['line']})
        missing_keys_result = ExtractionHelper.calculate_perimeter_with_arcs(
            substituted_boundary_lines_with_arcs=line_list_missing_keys)
        self.assertEqual(None, missing_keys_result)
        
    def test_get_lines_of_polygon_success(self):
        correct_polygon_points = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
        correct_result = ExtractionHelper.get_lines_of_polygon(polygon_points=correct_polygon_points)
        self.assertEqual(list, type(correct_result))
        for line in correct_result:
            self.assertEqual(dict, type(line))
            self.assertEqual(['coords', 'length'], list(line.keys()))

    def test_get_lines_of_polygon_false_param_polygon_with_two_points(self):
        polygon_points_for_line = [[0, 0], [1, 0]]
        incorrect_coords_length_result = ExtractionHelper.get_lines_of_polygon(polygon_points=polygon_points_for_line)
        self.assertEqual(None, incorrect_coords_length_result)

    def test_get_lines_of_polygon_empty_list_of_points(self):
        coord_list = []
        empty_list_result = ExtractionHelper.get_lines_of_polygon(polygon_points=coord_list)
        self.assertEqual(None, empty_list_result)

    def test_get_lines_of_polygon_false_param_type_for_points(self):
        point = Point(0.0, 0.0)
        point_as_parameter_result = ExtractionHelper.get_lines_of_polygon(polygon_points=point)
        self.assertEqual(None, point_as_parameter_result)

    def test_has_inner_points(self):
        room_coords = [[0.5, 0.5], [2,2]]
        polygon_coords = [[0,0], [0,1], [1,1], [1,0]]
        shapely_polygon = ShapelyPolygon(polygon_coords)
        self.assertTrue(ExtractionHelper.has_inner_points(room_coords, shapely_polygon))

    def test_has_inner_points_point_is_outside_polygon(self):
        room_coords = [[2, 2]]
        polygon_coords = [[0,0], [0,1], [1,1], [1,0]]
        shapely_polygon = ShapelyPolygon(polygon_coords)
        self.assertFalse(ExtractionHelper.has_inner_points(room_coords, shapely_polygon))

    def test_check_points_as_polygon_success(self):
        polygon_coords = [[0,0], [0,1], [1,1], [1,0]]
        shapely_polygon = ShapelyPolygon(polygon_coords)
        point_coords = [0.5, 0.5]
        shapely_point = ShapelyPoint(point_coords)
        self.assertTrue(ExtractionHelper.check_points_as_polygon(shapely_polygon, shapely_point))

    def test_check_points_as_polygon_point_is_outside_polygon(self):
        polygon_coords = [[0,0], [0,1], [1,1], [1,0]]
        shapely_polygon = ShapelyPolygon(polygon_coords)
        point_coords = [2, 2]
        shapely_point = ShapelyPoint(point_coords)
        self.assertFalse(ExtractionHelper.check_points_as_polygon(shapely_polygon, shapely_point))

    def test_check_point_success(self):
        polygon_coords = [[0,0], [0,10], [10,10], [10,0]]
        shapely_polygon = ShapelyPolygon(polygon_coords)

        point_coords = [5, 5]
        shapely_point = ShapelyPoint(point_coords)
        self.assertTrue(ExtractionHelper.check_point(shapely_polygon, shapely_point))

    def test_check_point_outside(self):
        polygon_coords = [[0,0], [0,1], [1,1], [1,0]]
        shapely_polygon = ShapelyPolygon(polygon_coords)

        point_coords = [2.0, 2.0]
        shapely_point = ShapelyPoint(point_coords)
        self.assertFalse(ExtractionHelper.check_point(shapely_polygon, shapely_point))

    def test_separate_inner_points(self):
        polygon_coords = [[0,0], [0,1], [1,1], [1,0]]
        shapely_polygon = ShapelyPolygon(polygon_coords)

        inner_point = [(0.5, 0.5)]
        outer_point = [(5.0, 5.0)]
        points = []
        points.extend((inner_point, outer_point))

        separate_points = ExtractionHelper.separate_inner_points(points, shapely_polygon)
        self.assertEqual(list(separate_points.keys()), 
                         ['outer_points', 'inner_points'])
        self.assertIn(str(inner_point), str(separate_points['inner_points']))
        self.assertIn(str(outer_point), str(separate_points['outer_points']))

    def test_separate_inner_points_point_on_polygon(self):
        polygon_coords = [[0,0], [0,1], [1,1], [1,0]]
        shapely_polygon = ShapelyPolygon(polygon_coords)
        point = [(0.0, 0.0)]
        separate_points = ExtractionHelper.separate_inner_points(point, shapely_polygon)
        self.assertEqual(list(separate_points.keys()), 
                         ['outer_points', 'inner_points'])
        self.assertIn(str(point), str(separate_points['outer_points']))

    def test_get_modelspace_success(self):
        modelspace = ExtractionHelper.get_modelspace(self.dxf_file)
        self.assertEqual(type(modelspace), Modelspace)

    def test_get_modelspace_false_param(self):
        with self.assertRaises(Exception) as context:
            ExtractionHelper.get_modelspace(self.polygons)
        self.assertTrue('modelspace not found' in str(context.exception))

    def test_get_modelspace_none_param(self):
        with self.assertRaises(Exception) as context:
            ExtractionHelper.get_modelspace(None)
        self.assertTrue('modelspace not found' in str(context.exception))

    def test_get_outline_polygon_success(self):
        self.assertIsInstance(ExtractionHelper.get_outline_polygon(self.modelspace), Polygon)

    def test_get_point_from_coordinate_success(self):
        coords = [1,1]
        self.assertIsInstance(ExtractionHelper.get_point_from_coordinate(coords), Point)

    def test_get_area_and_perimeter_from_polyline(self):
        polyline = self.modelspace.query("LWPolyline[layer=='RAUMPOLYGON']")[10]
        polygon = ShapelyPolygon(polyline.get_points("XY"))
        area, perimeter = ExtractionHelper.get_area_and_perimeter_from_polyline(polyline)
        self.assertEqual(28.328623800147803, area)
        self.assertEqual(23.17626523252456, perimeter)

    def test_calculate_perimeter_false_param_polygon_with_two_points(self):
        polygon_points_for_line = [[0, 0], [1, 0]]
        incorrect_perimeter = ExtractionHelper.calculate_perimeter(polygon_points=polygon_points_for_line)
        self.assertEqual(None, incorrect_perimeter)

    def test_calculate_perimeter_empty_list_of_points(self):
        coord_list = []
        empty_list_perimeter = ExtractionHelper.calculate_perimeter(polygon_points=coord_list)
        self.assertEqual(None, empty_list_perimeter)

    def test_calculate_perimeter_false_param_type_for_points(self):
        point = Point(0.0, 0.0)
        point_perimeter = ExtractionHelper.calculate_perimeter(polygon_points=point)
        self.assertEqual(None, point_perimeter)

    def test_calculate_perimeter_success(self):
        correct_polygon_points = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
        perimeter = ExtractionHelper.calculate_perimeter(polygon_points=correct_polygon_points)
        self.assertEqual(4.0, perimeter)
    
    def test_transform_polygon_to_shapely_polygon(self):
        start_point = Point(1, 0)
        middle_point = Point(1, 0)
        end_point = Point(1, 1)
        polygon = Polygon(id=0, area=1.0, perimeter=1.0, has_roomstamp=True, points=[])
        polygon.points.extend((start_point, middle_point, end_point))
        self.assertIsInstance(ExtractionHelper.transform_polygon_to_shapely_polygon(polygon), ShapelyPolygon)

    def test_transform_polygon_to_line_string(self):
        start_point = Point(0, 0)
        middle_point = Point(1, 0)
        end_point = Point(1, 1)
        polygon = Polygon(id=0, area=1.0, perimeter=1.0, has_roomstamp=True, points=[])
        polygon.points.extend((start_point, middle_point, end_point))
        self.assertIsInstance(ExtractionHelper.transform_polygon_to_line_string(polygon), LineString)
    
    def test_transform_wall_to_line_string(self):
        start_point = Point(0, 0)
        end_point = Point(1,1)
        wall_to_transform = Wall(start_point=start_point, end_point=end_point, sky_direction='north')
        self.assertIsInstance(ExtractionHelper.transform_wall_to_line_string(wall_to_transform), LineString)

if __name__ == '__main__':
    unittest.main()