import json
import traceback
from dataclasses import asdict
from http import HTTPStatus
from os import error

from app.main.constants import QUEUE
from app.main.dtos.request.combined_extraction_request import \
    CombinedExtractionRequest
from app.main.dtos.request.extraction_request import ExtractionRequest
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.main.dtos.response.api_response_architecture import \
    ApiResponseArchitecture
from app.main.dtos.response.api_response_combined import ApiResponseCombined
from app.main.dtos.response.api_response_simple import ApiResponseSimple
from app.main.dtos.response.error_response import ErrorResponse
from app.main.extraction.dxf_extraction_coordinator import \
    DxfExtractionCoordinator
from flask import Blueprint, request
from loguru import logger

''' 
Description: This file contains the controller logic of the extraction. It is split into the following endpoints: simple, architecture, combined.
'''

extraction_endpoints = Blueprint('extraction', __name__)
main_logger = logger.bind()
main_logger.disable("ezdxf")

@extraction_endpoints.route('/simple', methods=['POST'])
def extract_simple_plan() -> ApiResponseSimple:
    '''
    Description: This method handles requests to extract data from a simple plan.
    Params: request_body: dict
    Return: error_response: ErrorResponse, api_response: ApiResponseSimple
    '''

    try:
        request_body = ExtractionRequest(**json.loads(request.data))
    except Exception:
        response = ErrorResponse(HTTPStatus.BAD_REQUEST.value, 'Bad Request', request.url)
        main_logger.error(create_error_log_message(response))
        return asdict(response), response.status
    if not check_redis_connection():
        response = ErrorResponse(HTTPStatus.INTERNAL_SERVER_ERROR.value, 'Failed to connect to redis database', request.url)
        main_logger.error(create_error_log_message(response))
        return asdict(response), response.status

    if not validate_request(request_body.file):
        response = ErrorResponse(HTTPStatus.BAD_REQUEST.value, 'Bad Request', request.url)
        main_logger.error(create_error_log_message(response))
        return asdict(response), response.status
        
    dxf_extraction_coordinator = DxfExtractionCoordinator()
    try:
        extractionDTO = dxf_extraction_coordinator.coordinate_simple_dxf_extraction(
            request_body.file)
    except Exception as e:
        traceback.print_exc()
        response = ErrorResponse(HTTPStatus.INTERNAL_SERVER_ERROR.value, str(e),request.url, transaction_id=request_body.transaction_id)
        main_logger.error(create_error_log_message(response))
        return asdict(response), response.status
    api_response = ApiResponseSimple(
        HTTPStatus.OK.value, request_body.transaction_id, extractionDTO)
    api_response_dict = asdict(api_response)
    api_response_dict = filter_out_null_from_dict(api_response_dict)
    push_dto_to_redis_queue(api_response_dict)
    return api_response_dict, api_response.status

def push_dto_to_redis_queue(dto):
    '''
    Description: This method initializes a RedisCommand-instance and pushes a DTO into a given REDIS-Queue
    Params: self, coordinate: tuple
    Return: bool
    Exception: none 
    '''
    from app.main.redis.redis_commands import RedisCommands
    redis_commands = RedisCommands()
    redis_commands.push_to_queue(QUEUE, dto, push_to_end=True)


@extraction_endpoints.route('/architecture', methods=['POST'])
def extract_architecture_plan() -> ApiResponseArchitecture:
    '''
    Description: This method handles requests to extract data from an architecture plan.
    Params: request_body: dict
    Return: error_response: ErrorResponse, api_response: ApiResponseArchitecture
    '''

    try:
        request_body = ExtractionRequest(**json.loads(request.data))
    except Exception:
        response = ErrorResponse(HTTPStatus.BAD_REQUEST.value, 'Bad Request', request.url)
        main_logger.error(create_error_log_message(response))
        return asdict(response), response.status

    if not check_redis_connection():
        response = ErrorResponse(HTTPStatus.INTERNAL_SERVER_ERROR.value, 'Failed to connect to redis database', request.url)
        main_logger.error(create_error_log_message(response))
        return asdict(response), response.status

    if not validate_request(request_body.file):
        response = ErrorResponse(HTTPStatus.BAD_REQUEST.value, 'Bad Request', request.url)
        main_logger.error(create_error_log_message(response))
        return asdict(response), response.status
        
    dxf_extraction_coordinator = DxfExtractionCoordinator()
    try:
        extractionDTO = dxf_extraction_coordinator.coordinate_architecture_dxf_extraction(
            request_body.file)
    except Exception as e:
        traceback.print_exc()
        response = ErrorResponse(HTTPStatus.INTERNAL_SERVER_ERROR, str(e), request.url, transaction_id=request_body.transaction_id)
        main_logger.error(create_error_log_message(response))
        return asdict(response), response.status
    api_response = ApiResponseArchitecture(
        HTTPStatus.OK.value, request_body.transaction_id, extractionDTO)
    api_response_dict = asdict(api_response)
    api_response_dict = filter_out_null_from_dict(api_response_dict)
    push_dto_to_redis_queue(api_response_dict)
    return api_response_dict, api_response.status



@extraction_endpoints.route('/combined', methods=['POST'])
def extract_combined_plan() -> ApiResponseCombined:
    '''
    Description: This method handles requests to extract data from an architecture plan and a simple plan as well as matching the objects of both plans
    Params: request_body: dict
    Return: error_response: ErrorResponse, api_response: ApiResponseCombined
    '''

    try:
        request_body = CombinedExtractionRequest(**json.loads(request.data))
    except Exception:
        response = ErrorResponse(HTTPStatus.BAD_REQUEST.value, 'Bad Request', request.url)
        main_logger.error(create_error_log_message(response))
        return asdict(response), response.status
    if not check_redis_connection():
        response = ErrorResponse(HTTPStatus.INTERNAL_SERVER_ERROR.value, 'Failed to connect to redis database', request.url)
        main_logger.error(create_error_log_message(response))
        return asdict(response), response.status
    
    if not validate_request(request_body.simple_plan) or not validate_request(request_body.architecture_plan):
        response = ErrorResponse(HTTPStatus.BAD_REQUEST.value, 'Bad Request', request.url)
        main_logger.error(create_error_log_message(response))
        return asdict(response), response.status

    dxf_extraction_coordinator = DxfExtractionCoordinator()
    try:
        extractionDTO = dxf_extraction_coordinator.coordinate_combined_dxf_extraction(
            request_body.simple_plan, request_body.architecture_plan)
    except Exception as e:
        traceback.print_exc()
        response = ErrorResponse(HTTPStatus.INTERNAL_SERVER_ERROR.value, str(e), request.url, transaction_id=request_body.transaction_id)
        main_logger.error(create_error_log_message(response))
        return asdict(response), response.status
    api_response = ApiResponseCombined(
        HTTPStatus.OK.value, request_body.transaction_id, extractionDTO)
    api_response_dict = asdict(api_response)
    api_response_dict = filter_out_null_from_dict(api_response_dict)
    push_dto_to_redis_queue(api_response_dict)
    return api_response_dict, api_response.status


def filter_out_null_from_dict(data: dict) -> dict:
    '''
    Description: This method filters out all None values recursively from a dict to remove noise in the api response.
    Params: data: dict
    Return: data: dict
    '''

    if isinstance(data, dict):
        return {
            key: value
            for key, value in ((key, filter_out_null_from_dict(value)) for key, value in data.items())
            if value
        }
    if isinstance(data, list):
        return [value for value in map(filter_out_null_from_dict, data) if value]
    return data

def check_redis_connection() -> bool:
    '''
    Description: This method pings the redis database to check if it is currently running.
    Return: is_connected: bool
    '''

    from app.main.redis.redis_commands import RedisCommands
    try:
        redis_commands = RedisCommands()
        redis_commands.ping_redis()
        return True
    except:
        return False

def create_error_log_message(error_response: ErrorResponse) -> str:
    '''
    Description: This method formats an error response into a log message.
    Params: error_response: ErrorResponse
    Return: log_message: str
    '''

    if error_response.transaction_id:
        return "HTTP Error - status: {}, message: {}, path: {}, transaction_id: {}".format(str(error_response.status), error_response.message, error_response.path, error_response.transaction_id)
    return "HTTP Error - status: {}, message: {}, path: {}".format(str(error_response.status), error_response.message, error_response.path)
def validate_request(request_file: ExtractionRequestFile) -> bool:
    '''
    Description: This method validates the types of the request attributes.
    Params: request_file: ExtractionRequestFile
    Return: is_valid: bool
    '''
    return (isinstance(request_file.floor_height, float) or not request_file.floor_height) and (
        isinstance(request_file.orientation, float) or not request_file.orientation)
