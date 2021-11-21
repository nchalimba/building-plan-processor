import unittest
from app.main.extraction.dxf_extraction_coordinator import DxfExtractionCoordinator
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.main.services.dxf_extraction_combined import DxfExtractionCombined
from app.main.constants import TEST_POLYGON_INDEX



class TestMatching(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        
        '''
        Description: This method sets up the unit test for the matching of architecture and simple plans. 
        Params: cls
        Return: none
        Exception: none 
        '''

        file_path_simple_plan = 'app/main/media/Einfache_Plaene_Compass/'
        file_name_simple_plan = 'R-Bau_D_EG.dxf'
        floor_height_simple_plan = 2.44
        orientation_simple_plan = 90
        
        file_path_architecture_plan = 'app/main/media/Architektenplaene/'
        file_name_architecture_plan = 'R-Bau_A_EG.dxf'
        floor_height_architecture_plan = 2.44
        orientation_architecture_plan = 90
        level = 0

        cls.simple_plan = ExtractionRequestFile(file_path=file_path_simple_plan, file_name=file_name_simple_plan,
                                    floor_height=floor_height_simple_plan, orientation=orientation_simple_plan)
        

        cls.architecture_plan = ExtractionRequestFile(file_path=file_path_architecture_plan, file_name=file_name_architecture_plan,
                                    floor_height=floor_height_architecture_plan, orientation=orientation_architecture_plan)

        dxf_extraction_coordinator = DxfExtractionCoordinator()
        
        cls.simple_dxf_file = dxf_extraction_coordinator.read_dxf_file(file_path_simple_plan, file_name_simple_plan)
        cls.architecture_dxf_file = dxf_extraction_coordinator.read_dxf_file(file_path_architecture_plan, file_name_architecture_plan)

        dxf_extraction_combined = DxfExtractionCombined()
        cls.simple_plan, cls.architecture_plan, cls.extracted_functionalities, cls.log_messages = dxf_extraction_combined.entry_point(cls.simple_plan, cls.simple_dxf_file,
                                                                                                    cls.architecture_plan, cls.architecture_dxf_file, level)
    
    def test_matching(self):

        '''
        Description: This method sets up the unit test for the matching of architecture and simple plans.
                     The result should consist of architecture plan elements in the simple plan polygons for the chosen test polygon (wall type, wall thickness, pillars, windows)
        Params: self
        Return: none
        Exception: none 
        '''
        
      
        i = TEST_POLYGON_INDEX
        polygons = self.simple_plan.polygons

        test_polygon = polygons[i]
        
        amount_walls = 0
        amount_pillars = 0
        amount_windows = 0
        for wall in test_polygon.walls:
            if wall.wall_type is not None and wall.wall_thickness is not None: 
                amount_walls = amount_walls + 1
                print('ARCHITECTURE_WALL_TYPE: {} / ARCHITECTURE_WALL_THICKNESS:{}'.format(wall.wall_type, wall.wall_thickness))
        for pillar in test_polygon.pillars:
            amount_pillars = amount_pillars + 1
            print('ARCHITECTURE_PILLARS: {}'.format(pillar.center_point))
        for window in test_polygon.windows:
            amount_windows = amount_windows + 1
            print('ARCHITECTURE_WINDOWS: {}'.format(window.center_point))
        
        self.assertEqual(amount_walls, 6, 
            "This room should have 6 matched walls. It has {}".format(amount_walls))

        self.assertEqual(amount_pillars, 2, 
            "This room should have 2 matched pillars. It has {}".format(amount_pillars))

        self.assertEqual(amount_windows, 6, 
            "This room should have 6 matched windows. it has {}".format(amount_windows))
            
if __name__ == '__main__':
    unittest.main()


