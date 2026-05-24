import streamlit as st
from locales import get_text
import feedparser
from datetime import datetime, timedelta
import time
import requests
from bs4 import BeautifulSoup
import re
import random


def show():
    lang = st.session_state.get('language', 'Русский')

    # Заголовок для настоящих любителей Counter-Strike
    st.markdown(
        f"""<h1 style="text-align: center; color: #FFD700; margin-bottom: 5px;">
                {get_text("news_title", lang)}
            </h1>""",
        unsafe_allow_html=True
    )

    # Дефолтные картинки (определяем в начале функции)
    default_images = [
        "https://static.wikia.nocookie.net/cswikia/images/2/2b/Csgo_logo.png",

    ]

    # Функция для извлечения изображения из Reddit
    def get_reddit_image(entry):
        """Извлекает изображение из Reddit записи"""
        try:
            if hasattr(entry, 'content'):
                for content in entry.content:
                    img_pattern = r'<img[^>]+src="([^">]+)"'
                    match = re.search(img_pattern, content.value)
                    if match:
                        return match.group(1)

            if hasattr(entry, 'summary'):
                img_pattern = r'<img[^>]+src="([^">]+)"'
                match = re.search(img_pattern, entry.summary)
                if match:
                    return match.group(1)

            if hasattr(entry, 'link') and any(ext in entry.link.lower() for ext in ['.jpg', '.png', '.jpeg', '.gif']):
                return entry.link
        except Exception:
            pass
        return None

    # Функция для извлечения изображения из HLTV
    def get_hltv_image(entry):
        """Извлекает изображение из HLTV новости"""
        try:
            if 'hltv_images' not in st.session_state:
                st.session_state.hltv_images = {}

            if entry.link not in st.session_state.hltv_images:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(entry.link, timeout=10, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    img_tag = None

                    for class_name in ['newsimage', 'article-image', 'featured-image']:
                        container = soup.find('div', class_=class_name)
                        if container:
                            img_tag = container.find('img')
                            if img_tag:
                                break

                    if not img_tag:
                        img_tag = soup.find('img', class_='large-news-image')

                    if not img_tag:
                        img_tag = soup.find('meta', property='og:image')
                        if img_tag and img_tag.get('content'):
                            st.session_state.hltv_images[entry.link] = img_tag['content']
                            return st.session_state.hltv_images[entry.link]

                    if img_tag and img_tag.get('src'):
                        img_url = img_tag['src']
                        if not img_url.startswith('http'):
                            img_url = 'https://www.hltv.org' + img_url
                        st.session_state.hltv_images[entry.link] = img_url
                    else:
                        st.session_state.hltv_images[entry.link] = None

            return st.session_state.hltv_images.get(entry.link)
        except Exception:
            return None

    # Функция для парсинга даты из строки
    def parse_date(date_string):
        """Парсит дату из разных форматов"""
        if not date_string or date_string == "Дата неизвестна":
            return None

        try:
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%a, %d %b %Y %H:%M:%S %Z', '%Y-%m-%dT%H:%M:%S%z']:
                try:
                    return datetime.strptime(date_string[:19], fmt)
                except:
                    continue
            return datetime.now()
        except:
            return None

    @st.cache_data(ttl=300)
    def get_cs_news():
        news_items = []

        # RSS ленты новостей
        rss_feeds = {
            "HLTV.org": "https://www.hltv.org/rss/news",
            "Reddit CS:GO": "https://www.reddit.com/r/GlobalOffensive/.rss",
        }

        seven_days_ago = datetime.now() - timedelta(days=7)

        for source_name, feed_url in rss_feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:30]:
                    # Получаем дату и проверяем, что новость не старше 7 дней
                    pub_date = None
                    date_str = "Дата неизвестна"

                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                        date_str = pub_date.strftime("%Y-%m-%d %H:%M")
                    elif hasattr(entry, 'published'):
                        date_str = entry.published[:16] if len(entry.published) > 16 else entry.published
                        pub_date = parse_date(date_str)
                    elif hasattr(entry, 'updated'):
                        date_str = entry.updated[:16] if len(entry.updated) > 16 else entry.updated
                        pub_date = parse_date(date_str)

                    # Пропускаем новости старше 7 дней
                    if pub_date and pub_date < seven_days_ago:
                        continue

                    # Получаем изображение
                    image_url = None
                    if 'reddit' in source_name.lower():
                        image_url = get_reddit_image(entry)
                    elif 'hltv' in source_name.lower():
                        image_url = get_hltv_image(entry)

                    # Если нет изображения, берем случайную дефолтную картинку
                    if not image_url:
                        image_url = random.choice(default_images)

                    # Очищаем summary от HTML тегов
                    summary = entry.summary if hasattr(entry, 'summary') else ""
                    summary = re.sub(r'<[^>]+>', '', summary)
                    summary = re.sub(r'\s+', ' ', summary).strip()
                    summary = summary[:300] + '...' if len(summary) > 300 else summary

                    news_items.append({
                        'title': entry.title[:100] if hasattr(entry, 'title') else "Без заголовка",
                        'summary': summary if summary else "Нет описания",
                        'link': entry.link,
                        'date': date_str,
                        'date_obj': pub_date if pub_date else datetime.now(),
                        'source': source_name,
                        'image_url': image_url
                    })
                time.sleep(0.5)
            except Exception as e:
                st.error(f"Ошибка загрузки {source_name}: {str(e)}")
                continue

        # Сортируем по дате (свежие сверху)
        news_items.sort(key=lambda x: x['date_obj'], reverse=True)

        return news_items

    # Загружаем новости
    all_news = get_cs_news()

    if not all_news:
        st.warning(get_text("no_news", lang))
        return

    # Инициализируем session_state для пагинации
    if 'news_index' not in st.session_state:
        st.session_state.news_index = 0

    # Показываем по 5 новостей на странице
    news_per_page = 5
    start_idx = st.session_state.news_index
    end_idx = start_idx + news_per_page
    current_news = all_news[start_idx:end_idx]

    # Отображаем новости
    for item in current_news:
        with st.container():
            # Используем обычную HTML картинку с onerror
            image_html = f'<img src="{item["image_url"]}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 10px;" onerror="this.src=\'{random.choice(default_images)}\'">'

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
                        padding: 20px; 
                        border-radius: 15px; 
                        margin: 15px 0;
                        border: 1px solid rgba(255,215,0,0.2);
                        transition: all 0.3s ease;">
                <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                    <div style="flex: 0 0 200px;">
                        {image_html}
                    </div>
                    <div style="flex: 1;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap;">
                            <h4 style="color: #FFD700; margin: 0;">📰 {item['title']}</h4>
                            <span style="background: rgba(255,215,0,0.2); padding: 4px 12px; border-radius: 20px; font-size: 12px;">
                                {item['source']}
                            </span>
                        </div>
                        <p style="color: #e0e0e0; font-size: 14px; line-height: 1.6; margin: 10px 0;">
                            {item['summary']}
                        </p>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                            <span style="color: #888; font-size: 12px;">📅 {item['date']}</span>
                            <a href="{item['link']}" target="_blank" style="
                                background: linear-gradient(135deg, #FFD700, #FFA500);
                                color: #000;
                                padding: 5px 15px;
                                border-radius: 20px;
                                text-decoration: none;
                                font-size: 12px;
                                font-weight: bold;
                                display: inline-block;">
                                🔗 {get_text("read_more", lang)}
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Кнопки пагинации
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col2:
        if st.session_state.news_index > 0:
            if st.button("◀ " + get_text("previous", lang), use_container_width=True):
                st.session_state.news_index -= news_per_page
                st.rerun()

    with col4:
        if end_idx < len(all_news):
            if st.button(get_text("next", lang) + " ▶", use_container_width=True):
                st.session_state.news_index += news_per_page
                st.rerun()

    st.markdown("---")