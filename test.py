from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys 


def scrape_nhk_news(url):
    """ Seleniumを使って、指定されたNHKニュースのURLから情報をスクレイピングする関数 """

    # --- Seleniumのセットアップ ---
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')


    driver = uc.Chrome(options=options, use_subprocess=True)
    
    html = "" 
    # Seleniumでページを開く
    driver.get(url)
    
    # 本文のCSSセレクタを指定
    BODY_SELECTOR = 'div.esl7kn2s._1i1d7sh0' 

    # 最大15秒間、本文の要素が現れるまで待機
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, BODY_SELECTOR))
    )
    
    # 待機が完了した後、HTMLを取得
    html = driver.page_source

    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(">>> デバッグ用に debug_page.html を保存")
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # CSSセレクタを使って情報を抽出
    title = soup.select_one('h1._1j6dito2').get_text(strip=True) 
    time_tag = soup.select_one('article time')
    datetime_str = time_tag['datetime'] 
    body_element = soup.select_one(BODY_SELECTOR)
    body = body_element.get_text(strip=True) 
    
    
    print(f"タイトル: {title}")
    print(f"日時: {datetime_str}")
    print(f"本文 (最初の100文字): {body[:100]}...")
    print(f"本文の文字数: {len(body)}")


if __name__ == '__main__':
    target_url = sys.argv[1]
    scrape_nhk_news(target_url)