import streamlit as st
from openai import OpenAI
import urllib.request
from PIL import Image

@st.cache_data
def func(prompt):
    client = OpenAI(api_key=st.session_state.key)
    response = client.images.generate(model="dall-e-3",prompt=prompt)
    image_url = response.data[0].url
    urllib.request.urlretrieve(image_url, 'img.png')
    img = Image.open("img.png")
    st.image(img, use_column_width=True)

st.session_state.key = st.text_input("key", key="key", type="password")
st.header("그림 그리기")
prompt = st.text_input("프롬포트")

if st.button("그리기"):
    func(prompt)
