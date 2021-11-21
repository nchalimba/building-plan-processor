from datetime import datetime

import ezdxf
from app.main.constants import FIRST_LEVEL_FILE_NAME, SECOND_LEVEL_FILE_NAME
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.main.dtos.response.architecture_plan_dto import ArchitecturePlanDto
from app.main.dtos.response.combined_plan_dto import CombinedPlanDto
from app.main.dtos.response.simple_plan_dto import SimplePlanDto
from app.main.models.architecture_plan import Architecture_Plan
from app.main.models.simple_plan import Simple_Plan
from app.main.reporting.reporting_models import LogMessage
from app.main.reporting.reporting_service import ReportingService
from app.main.services.dxf_extraction_architecture import \
    DxfExtractionArchitecture
from app.main.services.dxf_extraction_combined import DxfExtractionCombined
from app.main.services.dxf_extraction_simple import DxfExtractionSimple
from app.main.services.validation_helper import ValidationHelper
from ezdxf.document import Drawing
from loguru import logger

main_logger = logger.bind()

class DxfExtractionCoordinator:

    def coordinate_simple_dxf_extraction(self, extraction_request_file: ExtractionRequestFile) -> SimplePlanDto:
        '''
        Description: This method reads an simple plan, coordinates the extraction of its data and creates the ExtractionReport.
        Params: extraction_request_file: ExtractionRequestFile
        Return: simple_plan_dto: SimplePlanDto
        Exception: Exception
        '''
        
        erf = extraction_request_file
        main_logger.info('start simple plan extraction')
        try:
            main_logger.info('ExtractionRequestFile: {} | FilePath: {} | FloorHeight: {} | Orientation: {}'
                             .format(erf.file_name, erf.file_path, erf.floor_height, erf.orientation))
            dxf_file = self.read_dxf_file(
                erf.file_path, erf.file_name)
        except RuntimeError as re:
            main_logger.critical(re)
            raise re
        except Exception as e:
            main_logger.critical(e)
            raise e

        dxf_extraction_simple = DxfExtractionSimple()
        simple_plan, extracted_functionalities, log_messages = dxf_extraction_simple.entry_point(
            extraction_request_file, dxf_file)  

        reporting_service = ReportingService()
        report_dto = reporting_service.create_report(
            simple_plan, extracted_functionalities, log_messages)
        simple_plan_dto = self.map_simple_plan_to_extractionDTO(simple_plan, erf.floor_height)
        simple_plan_dto.report = report_dto
        return simple_plan_dto

    def coordinate_architecture_dxf_extraction(self, extraction_request_file: ExtractionRequestFile) -> ArchitecturePlanDto:
        '''
        Description: This method reads an architecture plan and coordinates the extraction of its data.
        Params: extraction_request_file: ExtractionRequestFile
        Return: architecture_plan_dto: ArchitecturePlanDto
        Exception: Exception
        '''

        try:
            dxf_file = self.read_dxf_file(extraction_request_file.file_path, extraction_request_file.file_name)
        except Exception as e:
            main_logger.critical(e)
            raise e
        dxf_extraction_architecture = DxfExtractionArchitecture()
        level = self.get_level_by_filename(extraction_request_file.file_name)
        architecture_plan, extracted_functionalities, log_messages, linestrings_list_total = dxf_extraction_architecture.entry_point(extraction_request_file, dxf_file, level)
        
        return architecture_plan.convert_to_dto()

    def coordinate_combined_dxf_extraction(self, simple_plan_file: ExtractionRequestFile, architecture_plan_file: ExtractionRequestFile) -> CombinedPlanDto:
        '''
        Description: This method reads both architecture and simple plan, validates them and coordinates the extraction and the matching of their data.
        Params: simple_plan: ExtractionRequestFile, architecture_plan: ExtractionRequestFile
        Return: combined_plan_dto: CombinedPlanDto
        Exception: Exception
        '''

        start_combined_plan_extraction_time = datetime.now()
        try:
            simple_dxf_file = self.read_dxf_file(
                simple_plan_file.file_path, simple_plan_file.file_name)
        except Exception as e:
            main_logger.critical(e)
            raise e
        try:
            architecture_dxf_file = self.read_dxf_file(
                architecture_plan_file.file_path, architecture_plan_file.file_name)
        except Exception as e:
            main_logger.critical(e)
            raise e
        if not ValidationHelper.check_scaling(simple_plan_file, architecture_plan_file):
            main_logger.error("Plans not correctly scaled. Aborting extraction")
            raise Exception("Plans not correctly scaled. Aborting extraction")
        dxf_extraction_combined = DxfExtractionCombined()
        level = self.get_level_by_filename(architecture_plan_file.file_name)
        simple_plan, architecture_plan, extracted_functionalities, log_messages = dxf_extraction_combined.entry_point(simple_plan_file, simple_dxf_file, architecture_plan_file, architecture_dxf_file, level)
        
        end_simple_plan_extraction_time = datetime.now()-start_combined_plan_extraction_time
        message = ('runtime: %s seconds' % (end_simple_plan_extraction_time.seconds))
        log_messages.append(LogMessage("CombinedPlanExtraction","Performance", message))

        reporting_service = ReportingService()
        report_dto = reporting_service.create_report(
            simple_plan, extracted_functionalities, log_messages, architecture_plan)

        simple_plan_dto = self.map_simple_plan_to_extractionDTO(simple_plan, simple_plan_file.floor_height)
        architecture_plan_dto = architecture_plan.convert_to_dto()
        return CombinedPlanDto(simple_plan_dto, architecture_plan_dto, report_dto)

    def get_level_by_filename(self, filename: str) -> int:
        '''
        Description: This method gets the level of the building by filename.
        Params: filename: str
        Return: level: int
        '''
        if(filename == FIRST_LEVEL_FILE_NAME):
            main_logger.info("Detected level: 1")
            return 1
        if(filename == SECOND_LEVEL_FILE_NAME):
            main_logger.info("Detected level: 2")
            return 2
        main_logger.info("Detected level: 0")
        return 0

    def map_simple_plan_to_extractionDTO(self, simple_plan: Simple_Plan, floor_height: float = None) -> SimplePlanDto:
        '''
        Description: This method maps a simple plan to its dto representation.
        Params: simple_plan: Simple_Plan, floor_height: float
        Return: simple_plan_dto: SimplePlanDto
        '''
        simple_plan_dto = simple_plan.convert_to_dto(floor_height)
        return simple_plan_dto


    def read_dxf_file(self, dxf_file_path: str, dxf_file_name: str) -> Drawing:
        '''
        Description: This method reads a dxf file.
        Params: dxf_file_path: str, dxf_file_name: str
        Return: dxf_file: Drawing
        Exception: Exception
        '''

        try:
            dxf_file = ezdxf.readfile(dxf_file_path + dxf_file_name)
            main_logger.success("dxf_file: {} {} read successfully".format(
                dxf_file_path, dxf_file_name))
        except IOError:
            raise RuntimeError(f'not a dxf file or generic I/O error.')
        except ezdxf.DXFStructureError:
            raise RuntimeError(f'Invalid or corrupted dxf file.')
        return dxf_file

if __name__ == '__main__':
    dxf_extraction_coordinator = DxfExtractionCoordinator()
