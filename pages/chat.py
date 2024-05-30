import streamlit as st
from openai import OpenAI
import urllib.request
from PIL import Image

st.session_state.key = st.text_input("key", value=st.session_state.get("key", ""), type="password")
st.header("그림 그리기")

if "messages" not in st.session_state:     
    st.session_state.messages = [] 
    
for msg in st.session_state.messages:     
    with st.chat_message(msg["role"]):         
        st.markdown(msg["content"])

if prompt := st.chat_input("What is up?"): 
    # 사용자 메시지 보여주기 
    st.chat_message("user").markdown(prompt) 
    # 메모리에 사용자 메시지 저장 
    st.session_state.messages.append({"role": "user", "content": prompt}) 
    # Assistant API Thread의 마지막 Message 가져오는 기능 추가 필요     
    response = f"Echo: {prompt}" 
    # LLM 응답 보여주기     
    with st.chat_message("assistant"): 
        st.markdown(response)     
        # 메모리에 LLM 응답 저장     
        st.session_state.messages.append({"role": "assistant", "content": response})

    func()