# kobe-scraper-python

神戸新聞の記事をスクレイピングし、OpenAI API で **リスクスコア** と **要約** を生成する AWS Lambda 関数です。
Web アプリ [kobe-news-scraper](https://github.com/Takaya-bfe/kobe-news-scraper) から呼び出されます。

## リポジトリ構成

このアプリは 2 つのリポジトリで構成されています。

| リポジトリ | 役割 | 言語 |
|---|---|---|
| [**kobe-news-scraper**](https://github.com/Takaya-bfe/kobe-news-scraper) | Web アプリ本体。URL の入力画面、Lambda の呼び出し、結果の保存と一覧表示 | Ruby / Rails |
| **kobe-scraper-python**（このリポジトリ） | Lambda 関数。記事のスクレイピングと OpenAI によるリスクスコア・要約の生成 | Python |

## 処理の流れ

1. Rails アプリから記事の URL を受け取る（`{"url": "..."}`）
2. `requests` で記事ページを取得し、`BeautifulSoup` でタイトル・日時・本文を抽出
3. OpenAI API（gpt-3.5-turbo）で、リスクスコア（1〜100）と 200〜250 文字の要約を生成
4. 結果を JSON で返す

```json
{
  "statusCode": 200,
  "body": "{\"title\": \"...\", \"datetime\": \"...\", \"body\": \"...\", \"risk_score\": 42, \"summary\": \"...\"}"
}
```

## 使用技術

- Python 3.12
- requests / BeautifulSoup4（スクレイピング）
- OpenAI API（スコアリング・要約）
- AWS Lambda（`kobeNewsScraperFunction`, ap-northeast-3）
- AWS CodeBuild（ビルド・デプロイ）

## ファイル構成

```
.
├── buildspec.yml              # CodeBuild のビルド・デプロイ手順
└── lambda_package/
    ├── scraper.py             # Lambda ハンドラ（lambda_handler）
    └── requirements.txt       # 依存ライブラリ
```

## デプロイ

CodeBuild が `buildspec.yml` に従って、依存ライブラリと `scraper.py` を zip にまとめ、`aws lambda update-function-code` で Lambda に反映します。

## 環境変数

| 名前 | 説明 |
|---|---|
| `OPENAI_API_KEY` | OpenAI の API キー。Lambda の環境変数に設定し、リポジトリには含めない |
