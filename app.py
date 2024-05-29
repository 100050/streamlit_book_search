import streamlit as st
from openai import OpenAI

@st.cache_data
def func(prompt):
  st.markdown(f"질문: {prompt}")
  client = OpenAI(api_key=st.session_state.key)
  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": prompt}
    ]
  )
  st.markdown(response.choices[0].message.content)

st.session_state.key = st.text_input("key", type="password")
st.header("무엇이든 물어보세요.")
prompt = st.text_input("질문?")

if st.button("실행하기"):
  func(prompt)
