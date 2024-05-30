import streamlit as st
from openai import OpenAI
import urllib.request
from PIL import Image

st.session_state.key = st.text_input("key", value=st.session_state.get("key", ""), type="password")
st.session_state.client = OpenAI(api_key=st.session_state.key)
st.header("챗봇")

if st.button("Clear") and "thread" in st.session_state:
    del st.session_state.messages
    st.session_state.client.beta.threads.delete(st.session_state.thread.id)

if st.button("대화창 나가기") and "thread" in st.session_state and "assistant" in st.session_state:
    del st.session_state.messages
    st.session_state.client.beta.threads.delete(st.session_state.thread.id)
    st.session_state.client.beta.assistants.delete(st.session_state.assistant.id)

if "messages" not in st.session_state:     
    st.session_state.messages = [] 

for msg in st.session_state.messages:     
    with st.chat_message(msg["role"]):         
        st.markdown(msg["content"])

if prompt := st.chat_input("What is up?"): 
    if "assistant" not in st.session_state:  
        st.session_state.assistant = st.session_state.client.beta.assistants.create(
            instructions="챗봇입니다",
            model="gpt-4o"
        )

    # 사용자 메시지 보여주기 
    st.chat_message("user").markdown(prompt) 

    # 메모리에 사용자 메시지 저장 
    st.session_state.messages.append({"role": "user", "content": prompt}) 

    # 챗봇 대답
    if "thread" not in st.session_state: 
        st.session_state.thread = st.session_state.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    #"attachments": [{"file_id": message_file.id, "tools":[{"type":"file_search"}]]
                }
            ]
        )

    run = st.session_state.client.beta.threads.runs.create_and_poll( # 1초에 1회 호출 (분당 100회 제한)
        thread_id=st.session_state.thread.id,
        assistant_id=st.session_state.assistant.id
    )
    ## run_id to filter
    thread_messages = st.session_state.client.beta.threads.messages.list(st.session_state.thread.id, run_id=run.id)

    # Assistant API Thread의 마지막 Message 가져오는 기능 추가 필요     
    response = f"Echo: {thread_messages.data[0].content[0].text.value}" 

    # LLM 응답 보여주기     
    with st.chat_message("assistant"): 
        st.markdown(response)     
        # 메모리에 LLM 응답 저장     
        st.session_state.messages.append({"role": "assistant", "content": response})