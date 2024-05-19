import streamlit as st
from streamlit.logger import get_logger
from st_pages import add_page_title

import boto3
from boto3.dynamodb.conditions import Key
import itertools
import json
import logging
import time

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

add_page_title()

lambda_client = boto3.client("lambda")
PROPOSE_STRATEGIES_NAME = "air-conditioner-strategy-ProposeStrategies-2t2LAjv0qfzw"

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("SensorDatabaseTable")


def invoke_propose_strategies(request: dict):
    event = {
        "pathParameters": {
            "floor_id": 0
        },
        "body": json.dumps(request)
    }
    outcome = lambda_client.invoke(
        FunctionName=PROPOSE_STRATEGIES_NAME,
        InvocationType='RequestResponse',
        Payload=json.dumps(event),
    )
    payload = json.loads(outcome['Payload'].read().decode('utf-8'))
    return json.loads(payload["body"])


profile = {
    "time": 14,
    "uv_index": 7,
    "number_of_people": 5,
    "space_size": 50,
    "ceiling_height": 2.5,
    "humidity": 60,
    "temperature": 30,
    "co2_concentration": 500,
    "stress_index": 40,
    "air_quality": 50,
    "building_material": 70,
    "month": 7,
    "target_temperature": 28,
    "target_time": 12,
    "pressure": 101325
}

if "conclusion" not in st.session_state:
    st.session_state.conclusion = None

if st.session_state.conclusion is None:
    st.info("Room layouts have not been set up yet!")
else:
    conclusion = st.session_state.conclusion
    with st.spinner("Thinking..."):
        strategy = invoke_propose_strategies(profile)
        time.sleep(2)  # Our efficiency is far too great
    percents = itertools.chain(
        strategy["optimized_percentages"].values(),
        itertools.repeat(0.0)  # avoid iterator end exception
    )

    for (room_id, room) in enumerate(conclusion["rooms"]):
        st.subheader(room["name"])

        columns = st.columns(3)
        for (column, unit) in zip(columns, room["aircons"]):
            number = int(100 * next(percents))
            column.metric(label=unit, value=f"{number} %")

        response = table.query(
            TableName="SensorDatabaseTable",
            KeyConditionExpression=Key("id").eq(str(room_id)),
        )
        items = response["Items"]
        if len(items) == 0:
            st.write("Sensor disconnected")
        else:
            temperature = items[0]["temperature"]
            humidity = items[0]["humidity"]
            st.write(f"Temperature {temperature:.1f}°C and humidity {humidity:.1f}%")

        st.divider()


# row1 = st.columns(2)
# row2 = st.columns(2)
#
# for (room, column) in zip(conclusion["rooms"], row1 + row2):
#     tile = column.container(border=True)
#     tile.subheader(room["name"])
#     for aircons in room["aircons"]:
#         markdown = ''.join(f'- {aircon}' for aircon in room["aircons"])
#         tile.markdown('- {aircon}')
