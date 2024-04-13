import asyncio
import nest_asyncio
import streamlit as st
from langchain import hub
from langchain.agents import AgentExecutor, Tool, create_xml_agent
from langchain.agents import create_xml_agent, AgentExecutor, Tool
from langchain.prompts.prompt import PromptTemplate
from langchain_community.chat_models import BedrockChat
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Web ページの内容を読み込む関数
async def web_page_reader(url: str) -> str:
    loader = WebBaseLoader(url)
    content = loader.load()[0].page_content
    return content

# 検索ツールと Web ページ読み込みツールの設定
search = DuckDuckGoSearchRun()
tools = [
    Tool(
        name="duckduckgo-search",
        func=search.arun,
        description="このツールはユーザから検索キーワードを受け取り、Web上の最新情報を検索します。",
    ),
    Tool(
        name="WebBaseLoader",
        func=web_page_reader,
        description="このツールはユーザからURLを渡された場合に内容をテキストを返却します。URLの文字列のみを受け付けます。",
    )
]

# チャットモデルの設定
chat = BedrockChat(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs={"max_tokens": 1500},
)

# エージェントの設定
agent = create_xml_agent(
    chat,
    tools,
    prompt=hub.pull("hwchase17/xml-agent-convo")
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# Streamlit アプリケーションの設定
st.title("Bedrock Agent チャット")
messages = [
    SystemMessage(content="あなたは質問に対して必ず日本語で回答します。")
]

# ユーザー入力の処理
if prompt := st.chat_input("何でも聞いてください。"):
    messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())

        # 非同期処理でエージェントを呼び出す
        result = asyncio.run(agent_executor.ainvoke(
            {"input": prompt},
        ))

        st.write(result["output"])