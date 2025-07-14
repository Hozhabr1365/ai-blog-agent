import os
import requests
from bs4 import BeautifulSoup
import base64
import datetime

# تنظیمات وردپرس
WORDPRESS_URL = "https://hozhigraphicdesign.ir/wp-json/wp/v2/posts"
WORDPRESS_USER = "appwrite blog writer"
WORDPRESS_PASSWORD = "bXyA p98N XrKE q1WV GXjk 9SLq"  # Application Password

# تنظیمات ترجمه (استفاده از سرویس رایگان)
TRANSLATE_API_URL = "https://api.mymemory.translated.net/get"

def translate_text(text, source='en', target='fa'):
    """ترجمه متن با استفاده از API رایگان"""
    try:
        params = {'q': text, 'langpair': f'{source}|{target}'}
        response = requests.get(TRANSLATE_API_URL, params=params)
        return response.json()['responseData']['translatedText']
    except:
        return text  # در صورت خطا متن اصلی برگردانده می‌شود

def fetch_ai_news():
    """جمع‌آوری اخبار هوش مصنوعی"""
    sources = [
        "https://techcrunch.com/category/artificial-intelligence/",
        "https://venturebeat.com/category/ai/"
    ]
    
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
    
    for url in sources:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if "techcrunch" in url:
                items = soup.select('article.post-block')[:2]
                for item in items:
                    title = item.select_one('h2 a').text.strip()
                    link = item.select_one('h2 a')['href']
                    articles.append({"title": title, "link": link})
            else:
                items = soup.select('article.ArticleListing')[:2]
                for item in items:
                    title = item.select_one('h2 a').text.strip()
                    link = item.select_one('h2 a')['href']
                    articles.append({"title": title, "link": link})
                    
        except Exception as e:
            print(f"خطا در دریافت اخبار: {str(e)}")
    
    return articles[:2]  # حداکثر دو مقاله

def create_wordpress_post(title, content):
    """ایجاد پست در وردپرس"""
    # احراز هویت
    credential = f"{WORDPRESS_USER}:{WORDPRESS_PASSWORD}"
    token = base64.b64encode(credential.encode()).decode()
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'title': title,
        'content': content,
        'status': 'draft',  # پیش‌نویس
        'categories': [1]  # ID دسته‌بندی بلاگ
    }
    
    try:
        response = requests.post(WORDPRESS_URL, headers=headers, json=payload, timeout=15)
        if response.status_code == 201:
            print(f"پست ایجاد شد: {title}")
            return True
        else:
            print(f"خطا در ایجاد پست: {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        print(f"خطای ارتباط: {str(e)}")
        return False

def main():
    print("شروع جمع‌آوری اخبار...")
    articles = fetch_ai_news()
    
    for article in articles:
        print(f"پردازش: {article['title']}")
        
        # ترجمه عنوان
        persian_title = translate_text(article['title'])
        print(f"عنوان فارسی: {persian_title}")
        
        # دریافت و ترجمه محتوا
        article_response = requests.get(article['link'], headers={'User-Agent': 'Mozilla/5.0'})
        article_soup = BeautifulSoup(article_response.text, 'html.parser')
        
        # استخراج محتوا
        content_paragraphs = []
        if "techcrunch" in article['link']:
            content_div = article_soup.select_one('div.article-content')
            if content_div:
                content_paragraphs = content_div.find_all('p')[:5]  # 5 پاراگراف اول
        else:
            content_paragraphs = article_soup.find_all('p')[:5]
        
        english_content = " ".join(p.text.strip() for p in content_paragraphs)
        persian_content = translate_text(english_content[:1500])  # محدودیت طول
        
        # ایجاد پست
        success = create_wordpress_post(persian_title, persian_content)
        print(f"نتیجه: {'موفق' if success else 'ناموفق'}")
    
    print("پایان عملیات")

if __name__ == "__main__":
    main()
