import streamlit as st
from openai import OpenAI
import urllib.request
from PIL import Image

st.session_state.key = st.text_input("key", value=st.session_state.get("key", ""), type="password")
st.session_state.client = OpenAI(api_key=st.session_state.key)
st.header("챗봇")

@st.cache_data
def func(prompt):
    client = OpenAI(api_key=st.session_state.key)
    response = client.images.generate(model="dall-e-3",prompt=prompt)
    image_url = response.data[0].url
    urllib.request.urlretrieve(image_url, 'img.png')
    img = Image.open("img.png")
    st.image(img, use_column_width=True)




if st.button("Clear") and "thread" in st.session_state:
    del st.session_state.messages
    st.session_state.client.beta.threads.delete(st.session_state.thread.id)
    del st.session_state.thread

if st.button("대화창 나가기") and "thread" in st.session_state and "assistant" in st.session_state:
    del st.session_state.messages
    st.session_state.client.beta.threads.delete(st.session_state.thread.id)
    st.session_state.client.beta.assistants.delete(st.session_state.assistant.id)
    del st.session_state.thread
    del st.session_state.assistant

if "messages" not in st.session_state:     
    st.session_state.messages = [] 

for msg in st.session_state.messages:     
    with st.chat_message(msg["role"]):         
        st.markdown(msg["content"])

if prompt := st.chat_input("What is up?"): 
    if "assistant" not in st.session_state:  
        st.session_state.assistant = st.session_state.client.beta.assistants.create(
            instructions="챗봇입니다",
            model="gpt-4o",
            tools=[
                {
                    "type":"function",
                    "function": {
                        "name":"func",
                        "description":"dall-e를 이용해 받은 프롬포트를 바탕으로 그림을 그린다.",
                        "parameters": {
                            "type":"object",
                            "properties": {
                                "prompt": {"type":"string", "description":"프롬포트"}
                            }
                        }
                    }
                },
                {"type": "code_interpreter"}
            ]
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

    run_check = st.session_state.client.beta.threads.runs.retrieve(
      thread_id=st.session_state.thread.id,
      run_id=run.id
    )
    if run_check.status == 'requires_action':
        tool_calls = run_check.required_action.submit_tool_outputs.tool_calls

        tool_outputs = []
        for tool in tool_calls:
            func_name = tool.function.name
            kwargs = json.loads(tool.function.arguments)
            output = func(**kwargs)
            tool_outputs.append(
                {
                    "tool_call_id":tool.id,
                    "output":str(output)
                }
            )
        run = st.session_state.client.beta.threads.runs.submit_tool_outputs(
            thread_id=st.session_state.thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
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