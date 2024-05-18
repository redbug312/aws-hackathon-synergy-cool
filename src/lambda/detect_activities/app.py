import base64
import boto3
import json
import logging
from decimal import Decimal
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource('dynamodb')
ACTIVITY_DATABASE_TABLE = os.environ.get('ACTIVITY_DATABASE_TABLE')
table = dynamodb.Table(ACTIVITY_DATABASE_TABLE)


class Room:
    def __init__(self, name: str, headcount: int):
        self.name = name
        self.headcount = headcount

    def to_dict(self):
        return {
            'name': self.name,
            'headcount': self.headcount,
        }


def bad_request(message: str):
    return {
        'statusCode': 400,
        'body': json.dumps({
            'error': message,
        }),
    }


def handle_api_event(event, context):
    logger.debug(f'RESTful API triggered event {event}')
    path_parameters = event.get('pathParameters', {})
    room_id = path_parameters.get('room_id', None)
    logger.info(f'API queries the room {room_id}')

    if room_id is None:
        return bad_request('missing path parameter room_id')

    response = Room('diner', 0).to_dict()
    logger.info(f'API replies the room data {response}')

    return {
        'statusCode': 200,
        'body': json.dumps(response),
    }


def handle_kinesis_event(event):
    logger.debug(f'Kinesis stream triggered event {event}')
    assert len(event['Records']) > 0

    record = event['Records'][-1]
    data = base64.b64decode(record['kinesis']['data']).decode('utf-8')
    payload = json.loads(data, parse_float=Decimal)
    logger.info(f'Kinesis pushed payload {payload}')

    key = {
        "id": str(payload["room_id"]),
    }
    attributes = {
        "headcount": {
            "Value": payload["headcount"],
            "Action": "PUT"
        },
        "timestamp": {
            "Value": payload["timestamp"],
            "Action": "PUT"
        }
    }
    table.update_item(Key=key, AttributeUpdates=attributes)

    return {
        'statusCode': 200,
        'body': 'records uploaded to database',
    }


def lambda_handler(event, context):
    if 'httpMethod' in event:
        return handle_api_event(event)
    elif 'Records' in event and 'kinesis' in event['Records'][0]:
        return handle_kinesis_event(event)
    else:
        return bad_request("unknown event source")
