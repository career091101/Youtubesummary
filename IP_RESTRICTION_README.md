# YouTube IP制限回避機能 - README

## 概要

このプロジェクトには、YouTube Transcript APIを使用する際のIP制限を回避するための包括的な機能が実装されています。

## 実装された機能

### 1. レート制限の強化
- リクエスト間隔を5秒に設定
- 動画処理数を最大50本に制限

### 2. 指数バックオフリトライ
- 最大3回までの自動リトライ
- 指数バックオフ（1秒、2秒、4秒...）
- 429エラーの明示的な処理

### 3. 字幕キャッシング
- ファイルベースのキャッシュシステム
- 7日間の有効期限
- 自動クリーンアップ機能

### 4. プロキシサポート（オプション）
- HTTP/HTTPSプロキシの設定が可能
- クラウド環境での使用に最適

## 使用方法

### 基本的な使用

通常の使用では、追加の設定は不要です。デフォルトでキャッシングとリトライロジックが有効になります。

```bash
./.venv/bin/python3 -m src.main
```

### プロキシを使用する場合

1. `.env`ファイルにプロキシ設定を追加：

```bash
# Optional: Proxy settings for avoiding IP restrictions
PROXY_HTTP=http://proxy.example.com:8080
PROXY_HTTPS=https://proxy.example.com:8080
```

2. 通常通りアプリケーションを実行

## 推奨されるプロキシサービス

クラウド環境（GitHub Actions等）で使用する場合、以下のプロキシサービスが推奨されます：

- **WebShare** (https://www.webshare.io/)
  - youtube-transcript-apiの作者が推奨
  - レジデンシャルプロキシ対応
  - 無料プランあり

- **Bright Data** (https://brightdata.com/)
  - 大規模な用途に適している
  - 高い信頼性

## トラブルシューティング

### 429 Too Many Requests エラーが継続する場合

1. **待機時間を増やす**
   ```bash
   # .envファイルで設定を変更（現在は実装されていません）
   # または、config.pyを直接編集
   RETRY_DELAY = 10  # 10秒に増加
   ```

2. **プロキシを使用する**
   - 上記のプロキシサービスを利用

3. **実行頻度を減らす**
   - GitHub Actionsのスケジュールを調整

### キャッシュの確認

```bash
# キャッシュファイルの確認
cat .cache/transcripts.json

# キャッシュディレクトリの確認
ls -la .cache/
```

## ベストプラクティス

### ✅ 推奨
- キャッシュを有効にする（デフォルト）
- 適切な遅延を設定（5秒以上）
- 動画数を制限（50本以下）
- クラウド環境ではプロキシを使用

### ❌ 避けるべき
- Cookieに依存する（アカウントBANのリスク）
- 短い遅延時間（2秒未満）
- 大量の動画を一度に処理（100本以上）
- キャッシュを無効化

## GitHub Actions環境での使用

### GitHub Secretsの設定

1. リポジトリの Settings → Secrets and variables → Actions
2. 以下のシークレットを追加：
   - `PROXY_HTTP`: HTTPプロキシURL
   - `PROXY_HTTPS`: HTTPSプロキシURL

### ワークフローファイルの設定

```yaml
env:
  PROXY_HTTP: ${{ secrets.PROXY_HTTP }}
  PROXY_HTTPS: ${{ secrets.PROXY_HTTPS }}
```

## 技術詳細

詳細な実装内容については、以下のドキュメントを参照してください：

- [実装計画](file:///Users/y-sato/.gemini/antigravity/brain/fee4d9ca-9599-42d5-b077-1a0f7d15ffc3/implementation_plan.md)
- [ウォークスルー](file:///Users/y-sato/.gemini/antigravity/brain/fee4d9ca-9599-42d5-b077-1a0f7d15ffc3/walkthrough.md)

## ライセンス

このプロジェクトのライセンスに従います。
