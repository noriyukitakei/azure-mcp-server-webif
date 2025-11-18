import asyncio
import os
import json
from fastmcp import Client
from openai import AzureOpenAI
from dotenv import load_dotenv
import streamlit as st

load_dotenv(verbose=True)

# 環境変数の読み込み
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
MAX_STEPS = int(os.getenv("MAX_STEPS"))

# Azure OpenAI クライアントの初期化
client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=ENDPOINT,
)

# MCP サーバーの起動設定
config = {
    "mcpServers": {
        "local_server": {
            # Local stdio server
            "transport": "stdio",
            "command": "docker",
            "args": ["run", "-i", "--rm", "--env-file", ".env", "mcr.microsoft.com/azure-sdk/azure-mcp:latest"],
        }
    }
}
# MCP サーバーのツールを使ってエージェントを実行する非同期関数
async def run_agent(user_input):
    async with Client(config) as mcp:
        # MCP サーバーのツール情報を取得
        tools = await mcp.list_tools()  # FastMCPサーバーのツール一覧
        print(f"🔧 MCP サーバーで利用可能なツール: {[t.name for t in tools]}")
    
        # MCPサーバーのスキーマを OpenAI Function Calling 用スキーマに変換
        functions = []
        for t in tools:
            functions.append({
                "name": t.name,
                "description": t.description,
                "parameters": t.inputSchema  # FastMCP が JSON Schema を提供している
            })
    
        # 最初のユーザー発話は一度だけ入れる
        context = []
        context.append({"role": "user", "content": user_input})
        for step in range(MAX_STEPS):
            print(f"\n=== 推論ステップ {step + 1} ===")
    
            # ユーザ入力とコンテキストをもとにチャット補完を実行
            response = client.chat.completions.create(
                model=DEPLOYMENT_NAME,  # Azure OpenAI では model=デプロイ名
                # すでに context にユーザー発話や前段の関数実行結果が入っているのでそのまま渡す
                messages=context,
                functions=functions,
                function_call="auto"
            )
    
            msg = response.choices[0].message
    
            # 実行すべき関数があるか確認
            if msg.function_call:
                func_name = msg.function_call.name
                args = json.loads(msg.function_call.arguments or "{}")
                print(f"関数呼び出し: {func_name}({args})")
    
                # MCPサーバーで関数を実行
                result = await mcp.call_tool(func_name, arguments=args)
                print(f"実行結果: {result}")
    
                # 関数実行結果の取得(構造化されたJSONがあればそちらを優先)
                result_content = result.structured_content or result.content[0].text

                # MCPサーバーからの結果をLLMに再入力
                context.append(msg)
                context.append({
                    "role": "function",
                    "name": func_name,
                    "content": result_content
                })
            else:
                # 最終回答
                print("\nAI の最終回答:")
                print(msg.content)
                return msg.content
    
    print("最大ステップに達しました。最終応答:")
    return msg.content


# ここからは画面を構築するためのコード
# チャット履歴を初期化する。
if "history" not in st.session_state:
    st.session_state["history"] = []

# チャット履歴を表示する。
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ユーザーが質問を入力したときの処理を記述する。
if prompt := st.chat_input("質問を入力してください"):

    # ユーザーが入力した質問を表示する。
    with st.chat_message("user"):
        st.write(prompt)

    # ユーザの質問をチャット履歴に追加する
    st.session_state.history.append({"role": "user", "content": prompt})

    # ユーザーの質問に対して回答を生成するためにrun_agent関数を呼び出す。
    response = asyncio.run(run_agent(prompt))

    # 回答を表示する。
    with st.chat_message("assistant"):
        st.write(response)

    # 回答をチャット履歴に追加する。
    st.session_state.history.append({"role": "assistant", "content": response})