import streamlit as st
from streamlit.logger import get_logger
from st_pages import add_page_title

import boto3
import json
import logging
import random
import time

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

kinesis_client = boto3.client('kinesis')
DEFAULT_ARN = "air-conditioner-strategy-ActivityKinesisStream-o2Vb8ujOT4Nl"

add_page_title()


enabled = st.checkbox("Enable")
if enabled:
    st.info("Upload data to kinesis when taking photos.", icon="🤖")

stream_arn = st.text_input("Kinesis Stream ARN", DEFAULT_ARN)
picture = st.camera_input("Infrared Sensor")
headcount = 0

if picture:
    headcount = random.randint(0, 2)
    logger.info(f"Infrared sensor detects {headcount} people")
    if enabled:
        data = {
            "room_id": 0,
            "headcount": headcount,
            "timestamp": int(time.time()),
        }
        response = kinesis_client.put_record(
            StreamName=stream_arn,
            Data=json.dumps(data),
            PartitionKey='partition_key',
        )
        logger.debug(f"Pushed data {data} to kinesis with response {response}")

headcount = st.number_input("Number of People", value=headcount, min_value=0)
