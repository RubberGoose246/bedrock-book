# Pyhton外部モジュールのインポート
import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# タイトル
st.title("つくよみちゃんチャット")

# ChatOpenAIを生成
chat = ChatOpenAI(
    openai_api_key=st.secrets["OPENAI_API_KEY"],
    model_name=st.secrets["MODEL_TSUKUYOMICHAN"],
    streaming=True,
)

# セッションにメッセージを定義
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="あなたはつくよみちゃんです"),
    ]

# メッセージを画面表示
for message in st.session_state.messages:
    if message.type != "system":
        with st.chat_message(message.type):
            st.markdown(message.content)

# チャット入力欄を定義
if prompt := st.chat_input("何でも聞いてください。"):
    # ユーザーの入力をメッセージに追加
    st.session_state.messages.append(HumanMessage(content=prompt))

    # ユーザーの入力を画面表示
    with st.chat_message("user"):
        st.markdown(prompt)

    # モデルの呼び出しと結果の画面表示
    with st.chat_message("assistant"):
        response = st.write_stream(chat.stream(st.session_state.messages))
        
    # モデル呼び出し結果をメッセージに追加
    st.session_state.messages.append(AIMessage(content=response))
