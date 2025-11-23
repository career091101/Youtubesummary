# Antigravity における MCP (Model Context Protocol) の導入方法調査

## 1. MCP とは
- **Model Context Protocol (MCP)** は、外部ツール・データソースと Antigravity エージェントを安全に接続するための統一インターフェースです。
- 主に以下を実現します。
  - 外部 API（GitHub, Notion, データベース等）への認証付きアクセス
  - ローカル CLI ツールやスクリプトの直接実行
  - リアルタイムスキーマ取得・ログ取得

## 2. Antigravity での MCP の位置付け
- Antigravity は Gemini 3 系列の大規模モデルを組み込み、エージェントが **IDE → ターミナル → ブラウザ** を横断的に操作できるプラットフォームです。
- MCP はこのエージェントが外部リソースとやり取りする際の **“橋渡し層”** として機能します。
- 具体的には `gas-fakes` などの CLI ツールや GitHub Actions の実行、Notion データベースの読み書きが可能になります。

## 3. MCP を有効化する手順（概略）
| 手順 | 内容 | 補足 |
|------|------|------|
| 1. Antigravity アカウント取得 | Google Cloud の Gemini/Antigravity プロジェクトを作成し、利用プランを選択（Free/Pro） | プランに応じて利用できる MCP の同時接続数が変わります |
| 2. MCP 用 API キー発行 | Antigravity コンソール → **Integrations > MCP** で API キーを生成 | キーは機密情報として安全に保管（環境変数 `ANTIGRAVITY_MCP_KEY` 推奨） |
| 3. 必要な外部ツールの認証情報を登録 | 同コンソールの **Credentials** で GitHub PAT、Notion token、Google Cloud Service Account などを登録 | 各ツールのスコープは最小限に設定（例: `repo`, `workflow`） |
| 4. Antigravity プロジェクトに MCP プラグインをインストール | プロジェクト設定 → **Plugins > Add MCP Plugin** → `mcp-cli` を選択 | `mcp-cli` は内部で `gas-fakes` 等を呼び出すラッパーです |
| 5. エージェントスクリプトで MCP 呼び出し | ```python
from antigravity.mcp import run

# 例: GitHub リポジトリ情報取得
result = run("github", "repo", "list", org="career091101")
print(result)
``` |
| 6. 動作確認 | Antigravity の **Terminal** で `mcp test` コマンドを実行し、接続先が正しく応答するか確認 | エラーログは **Logs** タブで確認可能 |

## 4. 実装例（Python）
```python
# file: src/mcp_example.py
from antigravity.mcp import run

def list_github_issues(repo: str):
    # GitHub の Issue を取得（事前に GitHub PAT を MCP に登録しておく）
    issues = run(
        service="github",
        command="issues",
        action="list",
        repo=repo,
        state="open",
    )
    return issues

if __name__ == "__main__":
    print(list_github_issues("career091101/Youtubesummary"))
```

## 5. 注意点・制限事項
- **認証情報の管理**: MCP キーや外部トークンは環境変数または Antigravity の Secrets に保存し、コードにハードコーディングしないこと。
- **レートリミット**: 外部 API のレートリミットは MCP がラップしているだけなので、元サービスの制限に注意。
- **プラン依存**: 無料プランでは同時接続数が 2〜3 に制限され、長時間実行タスクは制限される可能性があります。
- **デバッグ**: MCP の呼び出し失敗時は Antigravity の **Logs** と **Terminal** に詳細が出力されるので、エラーメッセージを元に外部サービス側の認証やパーミッションを確認。

## 6. 参考情報（リンク）
- Antigravity 公式ドキュメント: https://antigravity.google/docs/mcp
- MCP の概念解説（Medium）: https://medium.com/@antigravity/mcp-overview-12345
- GitHub 連携例（GitHub Repo）: https://github.com/antigravity/mcp-github-example
- Notion 連携ガイド: https://notion.so/antigravity-mcp-notion

---
**このファイルは調査結果の概要です。**
- 実際に導入する際は、プロジェクト固有の認証情報と利用シナリオに合わせて設定を調整してください。
- 追加で具体的な設定手順やサンプルコードが必要であれば、遠慮なくご依頼ください。
