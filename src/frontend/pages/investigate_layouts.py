import streamlit as st
from streamlit.logger import get_logger
from st_pages import add_page_title

from langchain_aws import ChatBedrock

import logging

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

add_page_title()

if "chain" not in st.session_state:
    llm = ChatBedrock(
        model_id="anthropic.claude-v2:1",
        model_kwargs={"temperature": 0},
    )
    st.session_state.chain = llm

if "messages" not in st.session_state:
    messages = [{
        "role": "assistant",
        "content": "How may I help you?"
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
            response = conversation.invoke(question)
            logger.debug(f"Obtained response {response} from chatbot")
        st.write(response.content)

    ai_message = {"role": "assistant", "content": response.content}
    st.session_state.messages.append(ai_message)
