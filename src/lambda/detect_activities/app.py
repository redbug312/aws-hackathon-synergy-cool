import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Room:
    def __init__(self, name: str, headcount: int):
        self.name = name
        self.headcount = headcount

    def to_dict(self):
        return {
            'name': self.name,
            'headcount': self.headcount,
        }


def lambda_handler(event, context):
    path_parameters = event.get('pathParameters', {})
    room_id = path_parameters.get('room_id', None)
    logger.info(f'API queries the room {room_id}')

    response = Room('diner', 0).to_dict()
    logger.info(f'API replies the room data {response}')

    return {
        'statusCode': 200,
        'body': json.dumps(response),
    }
