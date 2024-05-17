from enum import Enum
import json
import logging

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
            'mode': self.mode,
        }


class Strategy:
    def __init__(self, aircons: list[AirCon]):
        self.aircons = aircons

    def to_dict(self):
        return {
            'aircons': self.aircons,
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

    if floor_id is None:
        return bad_request('missing path parameter floor_id')

    aircon1 = AirCon('RAS-22NJP', Mode.HIGH)
    aircon2 = AirCon('RAC-22JP', Mode.OFF)
    response = Strategy([aircon1, aircon2]).to_dict()
    logger.info(f'API replies the strategy data {response}')

    return {
        'statusCode': 200,
        'body': json.dumps(response),
    }
