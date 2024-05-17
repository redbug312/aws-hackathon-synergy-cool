import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Room:
    def __init__(self, name: str):
        self.name = name

    def to_dict(self):
        return {
            'name': self.name,
        }


class Floor:
    def __init__(self, rooms: list[Room]):
        self.rooms = rooms

    def to_dict(self):
        return {
            'rooms': [room.to_dict() for room in self.rooms],
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

    room1 = Room('diner')
    room2 = Room('kitchen')
    response = Floor([room1, room2]).to_dict()
    logger.info(f'API replies the floor data {response}')

    return {
        'statusCode': 200,
        'body': json.dumps(response),
    }
