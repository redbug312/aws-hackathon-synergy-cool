import streamlit as st
from streamlit.logger import get_logger
from st_pages import add_page_title

import asyncio
import boto3
import json
import logging
import random
import time

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

kinesis_client = boto3.client('kinesis')
DEFAULT_ARN = "air-conditioner-strategy-SensorKinesisStream-NpM7rD086C1n"

add_page_title()


keep_running = st.checkbox("Enable")
stream_arn = st.text_input("Kinesis Stream ARN", DEFAULT_ARN)
temperature_range = st.slider("Temperature", -20.0, 60.0, (10.0, 30.0))
humidity_range = st.slider("Relative Humidity", 0.0, 100.0, (50.0, 70.0))

st.session_state.keep_running = keep_running
st.session_state.stream_arn = stream_arn
st.session_state.temperature_range = temperature_range
st.session_state.humidity_range = humidity_range


async def heartbeat():
    while st.session_state.keep_running:
        data = {
            "temperature": random.uniform(*st.session_state.temperature_range),
            "humidity": random.uniform(*st.session_state.humidity_range),
        }
        response = kinesis_client.put_record(
            StreamName=st.session_state.stream_arn,
            Data=json.dumps(data),
            PartitionKey='partition_key',
        )
        logger.debug(f"Pushed data {data} to kinesis with response {response}")
        time.sleep(1)

if st.session_state.keep_running:
    st.info("Keep uploading data to kinesis stream every second.", icon='🤖')
    # THE CODE IS STUCK HERE
    asyncio.run(heartbeat())
