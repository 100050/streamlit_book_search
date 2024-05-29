import streamlit as st
from openai import OpenAI

@st.cache_data
def func():
  st.markdown(f"질문: {st.session_state.prompt}")
  client = OpenAI(api_key=st.session_state.key)
  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": st.session_state.prompt}
    ]
  )
  st.markdown(response.choices[0].message.content)

st.session_state.key = st.text_input("key", value=st.session_state.get("key", ""), type="password")
st.header("무엇이든 물어보세요.")
st.session_state.prompt = st.text_input("질문?", value=st.session_state.get("prompt", ""))

if st.button("실행하기"):
  func()
