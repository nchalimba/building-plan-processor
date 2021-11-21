from dataclasses import asdict
from http import HTTPStatus

from app.main import constants
from app.main.dtos import available_fields
from app.main.dtos.response.api_response_available_fields import \
    ApiResponseAvailableFields
from app.main.dtos.response.error_response import ErrorResponse
from flask import Blueprint, request

''' 
Description: This file contains the controller logic of all informational endpoints.
'''

data_endpoints = Blueprint('data', __name__)


@data_endpoints.route('/available_fields', methods=['GET'])
def get_available_fields() -> ApiResponseAvailableFields:
    '''
    Description: This method handles requests to get the available data, that can be extracted.
    Params: plan_type: str
    Return: error_response: ErrorResponse, api_response: ApiResponseAvailableFields
    '''

    args = request.args
    if "plan_type" not in args:
        response = ErrorResponse(HTTPStatus.BAD_REQUEST.value, 'plan_type not specified', request.url)
        return asdict(response), response.status
    plan_type = args['plan_type']
    if plan_type not in constants.AVAILABLE_PLAN_TYPES:
        response = ErrorResponse(HTTPStatus.BAD_REQUEST.value, 'wrong plan_type specified', request.url)
        return asdict(response), asdict(response)['status']
    data = getattr(available_fields, plan_type.upper())
    if plan_type == "simple_plan" or plan_type == "combined_plan":
        if not constants.ENABLE_OUTER_WALLS:
            data["polygon"].remove("outer_wall_percentage")
            data["wall"].remove("is_outer_wall")
            data["wall"].remove("orientation")
            data["wall"].remove("sky_direction")


        if not constants.ENABLE_NEIGHBOURS:
            data["polygon"].remove("adjacent_polygons")
            data.pop("adjacent_polygon")

    if plan_type == "simple_plan":
        if not constants.ENABLE_NEW_GENERATE_WALLS or not constants.ENABLE_EDGES_KILL:
            data["polygon"].remove("ignored_edges_percentage")
        if not constants.ENABLE_NEW_GENERATE_WALLS or (not constants.ENABLE_SIMPLE_PILLAR_KILL and not constants.ENABLE_COMPLEX_PILLAR_KILL):
            data.pop("pillar")
    if plan_type == "combined_plan":
        if not constants.ENABLE_NEW_GENERATE_WALLS or not constants.ENABLE_EDGES_KILL:
            data["polygon"].remove("ignored_edges_percentage")
        if not constants.ENABLE_NEW_GENERATE_WALLS or (not constants.ENABLE_SIMPLE_PILLAR_KILL and not constants.ENABLE_COMPLEX_PILLAR_KILL):
            data["pillar"].remove("start_point")
            data["pillar"].remove("end_point")
    response = ApiResponseAvailableFields(HTTPStatus.OK.value, data)
    return asdict(response), response.status


