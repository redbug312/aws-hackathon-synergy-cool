import streamlit as st
from streamlit.logger import get_logger
from st_pages import add_page_title

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_aws import ChatBedrock

import logging
import pandas as pd

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

add_page_title()


template = """
AI needs to help a zero-knowledge human to investigate their rooms informations:
the area and the AC units. The investigation should be step-by-step,
so just propose one proper question to user every time.

1. If the rooms are unknown, ask human about the rooms and how to name them.
2. If the rooms are known, ask human about the first room that the ACs are
   still unknown.
3. If human respond an AC not recognized, confirm with human. Skip those
   unrecognized AC units in the following dialogs.
4. If collected enough info, confirm with user and output the conclusion in
   JSON format. Attach the sentence "Here is the output in the requested JSON
   format:" before the JSON code and put the JSON code in code blocks. Always
   use metric system in the JSON code.

Recognized AC units:
{units}
Current conversation:
{history}
Here is the human's next reply:
{input}
AI:
"""


reset_button = st.button("Reset Chat", key="reset_button")


if "chain" not in st.session_state:
    datasheet = pd.read_csv("data/hitachi-spec-en.csv")
    units = str(datasheet.unit.unique().tolist())
    llm = ChatBedrock(
        model_id="anthropic.claude-v2:1",
        model_kwargs={"temperature": 0},
    )
    memory = ConversationBufferMemory()
    prompt = PromptTemplate.from_template(template).partial(units=units)
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

    ai_message = {"role": "assistant", "content": response}
    st.session_state.messages.append(ai_message)
