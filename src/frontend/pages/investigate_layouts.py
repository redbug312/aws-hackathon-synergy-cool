import streamlit as st
from streamlit.logger import get_logger
from st_pages import add_page_title

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_aws import ChatBedrock

import json
import logging
import pandas as pd
from pydantic import BaseModel, Field

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

add_page_title()


class Room(BaseModel):
    name: str
    area: float = Field("room area in unit sqaured meters")
    aircons: list[str]


class Layout(BaseModel):
    rooms: list[Room]


SECRET_WORD = "Here is the output in the requested JSON format"
TEMPLATE = """
AI needs to help a zero-knowledge human to investigate their rooms informations:
the area and the AC units. The investigation should be step-by-step,
so just propose one proper question to user every time.

1. If the rooms are unknown, ask human about the rooms and how to name them.
2. If the rooms are known, ask human about the first room that the ACs are
   still unknown.
3. If human respond an AC not recognized, confirm with human. Skip those
   unrecognized AC units in the following dialogs.
4. If collected enough info, confirm with user and output the conclusion in
   JSON format. Attach the sentence "{secret_word}" (case-sensitive) before
   the JSON code and put the JSON code in code blocks. Always use metric system
   in the JSON code.

{format_instructions}

Recognized AC units:
{units}
Current conversation:
{history}
Here is the human's next reply:
{input}
AI:
"""


def extract_json_from_markdown(content):
    # Define the markers for the JSON code block
    start_marker = '```json'
    end_marker = '```'

    # Find the start and end positions of the JSON code block
    start_pos = content.find(start_marker)
    if start_pos == -1:
        logger.warn("No JSON code block found")
        return None

    end_pos = content.find(end_marker, start_pos + len(start_marker))
    if end_pos == -1:
        logger.warn("No ending backticks for JSON code block found")
        return None

    # Extract the JSON code block
    json_code = content[start_pos + len(start_marker):end_pos].strip()

    # Convert the JSON string to a Python dictionary
    try:
        json_data = json.loads(json_code)
        return json_data
    except json.JSONDecodeError as e:
        logger.warn(f"Error decoding JSON: {e}")
        return None


reset_button = st.button("Reset Chat", key="reset_button")
expander = st.expander("Evaluated Room Layouts")


if "chain" not in st.session_state:
    datasheet = pd.read_csv("data/hitachi-spec-en.csv")
    parser = PydanticOutputParser(pydantic_object=Layout)
    llm = ChatBedrock(
        model_id="anthropic.claude-v2:1",
        model_kwargs={"temperature": 0},
    )
    memory = ConversationBufferMemory()
    prompt = PromptTemplate(
        template=TEMPLATE,
        input_variables=["history", "input"],
        partial_variables={
            "units": str(datasheet.unit.unique().tolist()),
            "format_instructions": parser.get_format_instructions(),
            "secret_word": SECRET_WORD,
        }
    )
    conversation = ConversationChain(
        llm=llm, memory=memory, prompt=prompt, verbose=True
    )
    st.session_state.chain = conversation

if "messages" not in st.session_state or reset_button:
    conversation = st.session_state.chain
    conversation.memory.clear()
    messages = [{
        "role": "assistant",
        "content": "Please tell me about the room layouts and the installed AC."
    }]
    st.session_state.messages = messages

if "conclusion" not in st.session_state:
    st.session_state.conclusion = None


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if question := st.chat_input("write here"):
    with st.chat_message("user"):
        st.write(question)

    user_message = {"role": "user", "content": question}
    st.session_state.messages.append(user_message)

    with st.chat_message("assistant"):
        conversation = st.session_state.chain
        with st.spinner("Thinking..."):
            response = conversation.predict(input=question)
            logger.debug(f"Obtained response {response} from chatbot")
        st.write(response)
        if SECRET_WORD in response:
            st.session_state.conclusion = extract_json_from_markdown(response)

    ai_message = {"role": "assistant", "content": response}
    st.session_state.messages.append(ai_message)


expander.write(st.session_state.conclusion)
