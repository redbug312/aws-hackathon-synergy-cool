import streamlit as st
from st_pages import add_page_title
from langchain_aws import ChatBedrock
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

add_page_title()

template = """
Human: The following is a friendly conversation between a human and an AI. The
AI is talkative and provides lots of specific details from its context. If the
AI does not know the answer to a question, it truthfully says it does not know.

Current conversation:
<conversation_history>
{history}
</conversation_history>

Here is the human's next reply:
<human_reply>
{input}
</human_reply>

AI:
"""

if "chain" not in st.session_state:
    llm = ChatBedrock(
        model_id="anthropic.claude-v2:1",
        model_kwargs={"temperature": 0},
    )
    memory = ConversationBufferMemory(k=5)
    prompt = PromptTemplate.from_template(template)
    conversation = ConversationChain(
        llm=llm, memory=memory, prompt=prompt, verbose=True
    )
    st.session_state.chain = conversation

if "messages" not in st.session_state:
    messages = [{
        "role": "assistant",
        "content": "How may I help you?"
    }]
    st.session_state.messages = messages

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# User-provided prompt
if question := st.chat_input("write here"):
    with st.chat_message("user"):
        st.write(question)

    user_message = {"role": "user", "content": question}
    st.session_state.messages.append(user_message)

    with st.chat_message("assistant"):
        conversation = st.session_state.chain
        with st.spinner("Thinking..."):
            response = conversation.predict(input=question)
        st.write(response)

    ai_message = {"role": "assistant", "content": response}
    st.session_state.messages.append(ai_message)
