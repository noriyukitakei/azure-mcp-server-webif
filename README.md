# AzureMCPServerとStreamlitでAzureを対話的に操作するWebアプリ

## 概要

このリポジトリは、AzureMCPServerとStreamlitを使用して、Azureリソースを対話的に操作するWebアプリケーションを提供します。ユーザーはこのアプリケーションを通じて、Azureの各種サービスを簡単に管理および操作できます。

## 起動方法

### [ステップ1] リポジトリのクローン

まず、GitHubリポジトリをクローンします。ターミナルを開き、以下のコマンドを実行してください。

```bash
git clone https://github.com/noriyukitakei/azure-mcp-server-webif.git
cd azure-mcp-server-webif
```

### [ステップ2] 環境変数の設定

次に、必要な環境変数を設定します。`.env.example`ファイルをコピーして`.env`ファイルを作成し、必要な値を設定してください。

```bash
cp .env.example .env
``` 

`.env`ファイル内で設定する主な環境変数は以下の通りです。

- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI ServiceのエンドポイントURL
- `AZURE_OPENAI_API_KEY`: Azure OpenAI ServiceのAPIキー
- `AZURE_OPENAI_API_VERSION`: 使用するAPIバージョン (例: 2024-06-01)
- `AZURE_OPENAI_CHAT_DEPLOYMENT`: 使用するチャットモデルのデプロイメント名 (例: gpt-4)`
- `MAX_STEPS`: AIエージェントが実行する最大ステップ数 (例: 5)
- `AZURE_TENANT_ID`: AzureテナントID
- `AZURE_SUBSCRIPTION_ID`: AzureサブスクリプションID
- `AZURE_CLIENT_ID`: AzureクライアントID
- `AZURE_CLIENT_SECRET`: Azureクライアントシークレット

`AZURE_OPENAI_ENDPOINT`、`AZURE_OPENAI_API_KEY`、`AZURE_OPENAI_CHAT_DEPLOYMENT`は、Azure OpenAI Serviceに接続するための情報となります。これはLLMにFunction Callingを実行させるために必要です。

`AZURE_TENANT_ID`、`AZURE_SUBSCRIPTION_ID`、`AZURE_CLIENT_ID`、`AZURE_CLIENT_SECRET`は、Azure MCP ServerがAzureリソースにアクセスするための情報となります。これらの値はAzureポータルでアプリケーション登録を行い、サービスプリンシパルを作成することで取得できます。そして、そのサービスプリンシパルに対して必要なAzureリソースへのアクセス権限を付与してください。例えば、ストレージアカウントの情報を取得する場合は、「ストレージ アカウント閲覧者」ロールを付与します。

`MAX_STEPS`は、AIエージェントが実行する最大ステップ数を指定します。これにより、無限ループを防止できます。もしこれを設定しないと、AIエージェントが過剰に多くのステップを実行し、Azure OpenAI Serviceにすごいい数のリクエストを送ってしまう可能性があります。結果、コストが高額になる恐れがあるため、適切な値を設定してください。

### [ステップ3] 依存関係のインストール

次に、必要なPythonパッケージをインストールします。以下のコマンドを実行してください。

```bash
pip install -r requirements.txt
```

### [ステップ4] アプリケーションの起動

本アプリケーションでは、MCPサーバーの起動にDockerを使用しますので、Dockerがインストールされていることを確認してください。

Dockerがインストールされていることを確認したら、アプリケーションを起動します。以下のコマンドを実行してください。

```bash
$ streamlit run agent.py
```

これで、Streamlitアプリケーションが起動し、ブラウザでアクセスできるようになります。デフォルトでは、`http://localhost:8501`でアプリケーションが利用可能です。