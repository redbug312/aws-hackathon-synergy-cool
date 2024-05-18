from enum import Enum
import json
import logging
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
# 添加 calculate_watt 所在目录到 sys.path
sys.path.append(os.path.join(current_dir, '..'))
from vincent_algorithm import vincent_algorithm_test
from calculate_watt import calculate_watt_test
from calculate_watt import save_to_json


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Mode(Enum):
    OFF = 0
    LOW = 1
    MID = 2
    HIGH = 3


class AirCon:
    def __init__(self, unit: str, mode: Mode):
        self.unit = unit
        self.mode = mode

    def to_dict(self):
        return {
            'unit': self.unit,
            'mode': str(self.mode),
        }


class Strategy:
    def __init__(self, aircons: list[AirCon]):
        self.aircons = aircons

    def to_dict(self):
        return {
            'aircons': [aircon.to_dict() for aircon in self.aircons],
        }


def bad_request(message: str):
    return {
        'statusCode': 400,
        'body': json.dumps({
            'error': message,
        }),
    }


def lambda_handler(event, context):
    path_parameters = event.get('pathParameters', {})
    floor_id = path_parameters.get('floor_id', None)
    logger.info(f'API queries the floor {floor_id}')
    query_parameters = event.get('queryStringParameters', {})
    param1 = query_parameters.get('param1', None)
    param2 = query_parameters.get('param2', None)
    logger.info(f'Query parameters: param1={param1}, param2={param2}')

    if param1 is None or param2 is None:
        return bad_request('missing query parameters param1 or param2')


    save_to_json(param1, "input.json")
    save_to_json(param2, "aircondition_array_data")

    calculate_watt_test()
    vincent_algorithm_test() ##


    if floor_id is None:
        return bad_request('missing path parameter floor_id')

    with open('output.json', 'r') as f:
        output_data = json.load(f)
        
    return {
        'statusCode': 200,
        'body': output_data,
    }