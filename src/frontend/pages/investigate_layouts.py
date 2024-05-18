import streamlit as st
from st_pages import add_page_title
from langchain_aws import ChatBedrock

add_page_title()

llm = ChatBedrock(
    model_id="anthropic.claude-v2:1",
    model_kwargs={"temperature": 0},
)

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{
        "role": "assistant",
        "content": "How may I help you?"
    }]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Function for generating LLM response
def generate_response(prompt_input):
    return llm.invoke(prompt_input)


# User-provided prompt
if prompt := st.chat_input("write here"):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_response(prompt)
                st.write(response.content)
        message = {
            "role": "assistant",
            "content": response.content
        }
        st.session_state.messages.append(message)
