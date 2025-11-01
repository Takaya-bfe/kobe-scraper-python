import requests
from bs4 import BeautifulSoup
import json 
import os
from openai import OpenAI

def create_openai_prompt(title, body):
    # (以前サービスクラスにあったプロンプト作成ロジックをここに移動)
    return f"""
    以下の神戸新聞NEXTの記事を分析し、指定されたJSON形式でリスクスコアと要約を生成してください。

    # 記事
    タイトル: {title}
    本文: {body}

    # 指示
    1.  **リスクスコア**: 記事の内容が示す事故や事件の深刻度を評価してください。評価基準は、被害範囲、被害の程度、社会的影響、死傷者の有無や被害金額の大きさです。スコアは1（低リスク）から100（高リスク）の整数で評価してください。
    2.  **要約**: 記事の内容を200文字から250文字程度の日本語で要約してください。

    # 出力形式
    以下のキーを持つJSONオブジェクトのみで回答してください:
    {{
      "risk_score": <整数>,
      "summary": "<200から250文字程度の要約>"
    }}
    """
    
def analyze_with_openai(title, body):
    """ OpenAI APIを呼び出して分析を行う関数 """
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI APIキーが環境変数に設定されていません。")

        client = OpenAI(api_key=api_key)
        prompt = create_openai_prompt(title, body)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content
        result_json = json.loads(result_text) 
        
        return {
            "risk_score": result_json.get("risk_score"),
            "summary": result_json.get("summary", "要約の取得に失敗")
        }
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return {"risk_score": None, "summary": "AIによる分析に失敗しました。"}
    

def lambda_handler(event, context):

    url = event.get('url')
    
    if not url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'URL is required'})
        }
        
    # ブラウザからのアクセスになりすますためのヘッダー情報
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # もしページ取得に失敗したらエラーを発生させる
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title = soup.select_one("h1.caption").get_text(strip=True) # .strip=Trueで前後の空白を削除
        datetime_str = soup.select_one("time.meta-time").get_text(strip=True)
        body = soup.select_one("div.article-body.cXenseParse").get_text(strip=True)
                
        
        analysis_result = analyze_with_openai(title, body)
        
        # 成功した結果をJSON形式で返す
        return {
            'statusCode': 200,
            'body': json.dumps({
                'title': title,
                'datetime': datetime_str,
                'body': body,
                'risk_score': analysis_result["risk_score"],
                'summary': analysis_result["summary"]
            }, ensure_ascii=False) # 日本語が文字化けしないように設定
        }
        
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(error)})
        }
