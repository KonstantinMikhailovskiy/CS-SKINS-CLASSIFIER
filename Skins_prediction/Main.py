import streamlit as st
from streamlit_option_menu import option_menu
import Cs_skins
import Info
import Settings
import News
from locales import get_text
import base64

# Настройка страницы
st.set_page_config(
    page_title="CS:Skins Classifier",
    page_icon="https://images.steamusercontent.com/ugc/2043000540794527621/55C1146394B4D4E22B26E7AE04B16C3EEB54B526/?imw=512&amp;imh=512&amp;ima=fit&amp;impolicy=Letterbox&amp;imcolor=%23000000&amp;letterbox=true",
    initial_sidebar_state="auto",
    layout="wide"
)

# Инициализация настроек
if 'theme' not in st.session_state:
    st.session_state.theme = get_text("theme_dark_classic", "Русский")
if 'notifications' not in st.session_state:
    st.session_state.notifications = True
if 'auto_save' not in st.session_state:
    st.session_state.auto_save = True
if 'language' not in st.session_state:
    st.session_state.language = "Русский"

# Применяем тему
Settings.apply_theme(st.session_state.theme)

lang = st.session_state.language

# Словарь цветов для редкости
rarity_colors = {
    "Consumer Grade": "#D3D3D3",
    "Industrial Grade": "#87CEEB",
    "Mil-Spec": "#4B9CD3",
    "Restricted": "#800080",
    "Classified": "#FF69B4",
    "Covert": "#DC143C",
    "Contraband": "#FF8C00",
    "Базовый": "#D3D3D3",
    "Промышленный": "#87CEEB",
    "Армейский": "#4B9CD3",
    "Запрещенный": "#800080",
    "Секретный": "#FF69B4",
    "Тайный": "#DC143C",
    "Контрабандный": "#FF8C00",
}


def get_rarity_color(rarity):
    """Получить цвет редкости"""
    for key, color in rarity_colors.items():
        if key.lower() in str(rarity).lower():
            return color
    return "#FFD700"


# CSS стили
st.markdown(f"""
<style>
/* Основные стили */
.main .block-container {{
    padding-top: 0rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}}

header, footer, hr {{
    display: none !important;
}}

/* Убираем синюю полоску над меню */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0px !important;
    background-color: transparent !important;
}}

.stTabs [data-baseweb="tab"] {{
    background-color: transparent !important;
}}

/* Бегущая строка */
@keyframes marquee {{
    0% {{
        transform: translateX(100%);
    }}
    100% {{
        transform: translateX(-100%);
    }}
}}

.marquee {{
    width: 100%;
    overflow: hidden;
    background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(0,0,0,0.6));
    border-radius: 15px;
    padding: 20px 0;
    margin: 20px 0;
    border: 2px solid rgba(255,215,0,0.4);
    white-space: nowrap;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}}

.marquee-content {{
    display: inline-block;
    animation: marquee 20s linear infinite;
    font-size: 24px;
    color: white;
    font-weight: bold;
    padding-left: 100%;
    letter-spacing: 1px;
}}

.marquee-content span {{
    color: #FFD700;
    margin: 0 25px;
    font-size: 28px;
}}

.marquee:hover .marquee-content {{
    animation-play-state: running;
}}

/* Карточка скина с фоновым изображением */
.skin-card {{
    background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(0,0,0,0.6));
    background-image: url('https://public.blenderkit.com/thumbnails/assets/d3d7d7c20bff43788964d230f2ce6329/files/thumbnail_7777225a-b3f2-4982-857d-43be6f026ca4.jpg.2048x2048_q85.jpg');
    background-size: cover;
    background-position: center;
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 20px;
    text-align: center;
    border: 2px solid rgba(255,255,255,0.1);
    transition: all 0.3s ease;
    animation: fadeInUp 0.6s ease-out;
    min-height: 280px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
}}

.skin-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(0,0,0,0.7), rgba(0,0,0,0.5));
    border-radius: 15px;
    z-index: 0;
}}

.skin-card > * {{
    position: relative;
    z-index: 1;
}}

.skin-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}}

/* Контейнер для изображения */
.image-container {{
    width: 100%;
    height: 180px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-radius: 10px;
}}

.skin-card img {{
    max-width: 100%;
    max-height: 100%;
    width: auto;
    height: auto;
    object-fit: contain;
    transition: transform 0.3s ease;
    border-radius: 10px;
}}

.image-container:hover img {{
    transform: scale(1.05);
}}

/* Название скина */
.skin-name {{
    color: white;
    margin: 12px 0 5px 0;
    font-size: 15px;
    font-weight: bold;
    transition: all 0.3s ease;
    min-height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-shadow: 1px 1px 2px black;
}}

/* Анимации */
@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(30px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

@keyframes glow {{
    0% {{ box-shadow: 0 0 5px rgba(255,215,0,0.3); }}
    50% {{ box-shadow: 0 0 20px rgba(255,215,0,0.6); }}
    100% {{ box-shadow: 0 0 5px rgba(255,215,0,0.3); }}
}}

@keyframes float {{
    0% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-10px); }}
    100% {{ transform: translateY(0px); }}
}}

/* Карточки функционала */
.feature-card {{
    animation: fadeInUp 0.6s ease-out;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    cursor: pointer;
}}

.feature-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
}}

.feature-card::after {{
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, #FFD700, #FF6B6B, #4ECDC4);
    transform: scaleX(0);
    transition: transform 0.3s ease;
}}

.feature-card:hover::after {{
    transform: scaleX(1);
}}

/* Заголовки в карточках */
.feature-card h3 {{
    font-size: 28px !important;
    font-weight: bold !important;
    margin-bottom: 15px !important;
    color: #FFD700 !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}}

.feature-card p {{
    font-size: 18px !important;
    line-height: 1.5 !important;
    color: white !important;
    font-weight: 500 !important;
}}

/* Меню */
.floating-menu {{
    position: sticky;
    top: 0;
    z-index: 999;
    backdrop-filter: blur(10px);
    border-radius: 50px;
    padding: 5px;
    margin: 0 0 30px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    animation: fadeInUp 0.5s ease-out;
}}

/* Заголовок */
.custom-header {{
    text-align: center;
    padding: 20px 20px 10px 20px;
    margin-bottom: 20px;
}}

.custom-header h1 {{
    font-size: 48px;
    background: linear-gradient(135deg, #FFD700, #FF6B6B, #4ECDC4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    padding: 0;
    animation: fadeInUp 0.8s ease-out;
}}

.custom-header p {{
    font-size: 16px;
    opacity: 0.8;
    margin: 10px 0 0 0;
    padding: 0;
}}

/* Увеличенная инструкция */
.instruction-box {{
    background: rgba(0,0,0,0.7);
    backdrop-filter: blur(10px);
    padding: 30px;
    border-radius: 15px;
    margin: 20px 0;
    border: 1px solid rgba(255,215,0,0.3);
}}

.instruction-box ol {{
    color: #ffffff;
    font-size: 20px;
    line-height: 2.5;
    margin-bottom: 0;
    padding-left: 30px;
}}

.instruction-box li {{
    margin: 15px 0;
}}

.instruction-box strong {{
    color: #FFD700;
    font-size: 20px;
}}

/* Футер */
.floating-footer {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    text-align: center;
    padding: 8px;
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(10px);
    font-size: 11px;
    opacity: 0.7;
    z-index: 1000;
    border-top: 1px solid rgba(255,215,0,0.3);
    transition: all 0.3s ease;
}}

.floating-footer:hover {{
    opacity: 1;
}}

/* Стиль для заголовка секции */
.section-title {{
    font-size: 32px;
    font-weight: bold;
    color: #FFD700;
    text-align: center;
    margin-bottom: 30px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}}
</style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown("""
<div class="custom-header">
    <h1>
        <img src="https://avatars.mds.yandex.net/i?id=3d77b4cfd765996e2f81d78ecb623af1efe3d76e-5876724-images-thumbs&n=13" 
             style="height: 60px; vertical-align: middle; margin-right: 10px;">
        CS:SKINS CLASSIFIER
    </h1>
    <p>Классификация скинов Counter-Strike | Machine Learning Powered</p>
</div>
""", unsafe_allow_html=True)

# Меню
with st.container():
    st.markdown('<div class="floating-menu">', unsafe_allow_html=True)
    selected = option_menu(
        None,
        [get_text("home", lang), get_text("cs_skins", lang), get_text("news", lang),
         get_text("info", lang), get_text("settings", lang)],
        icons=['house-fill', 'grid-fill', 'newspaper', 'info-circle-fill', 'gear-fill'],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent", "justify-content": "center"},
            "icon": {"font-size": "18px", "margin-right": "10px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0 10px",
                "padding": "12px 30px",
                "border-radius": "40px",
                "transition": "all 0.3s ease"
            },
            "nav-link:hover": {"transform": "translateY(-2px)"},
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #FFD700, #FFA500) !important",
                "color": "#000 !important",
                "box-shadow": "0 4px 15px rgba(255,215,0,0.3)",
                "animation": "glow 2s infinite"
            }
        }
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Контент
if selected == get_text("home", lang):
    st.title(get_text("welcome", lang))

    # Бегущая строка с увеличенным текстом на русском
    if lang == "Русский":
        st.markdown("""
        <div class="marquee">
            <div class="marquee-content">
                <span>🎯</span> Используйте меню для навигации по разделам <span>⚡</span> 
                Узнавайте цены на скины CS:GO/CS2 <span>💰</span> 
                Сравнивайте цены в разных качествах <span>📊</span> 
                Ищите скины голосом <span>🎤</span> 
                <span>🔥</span> Приятного использования! <span>✨</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="marquee">
            <div class="marquee-content">
                <span>🎯</span> Use the menu to navigate sections <span>⚡</span> 
                Find CS:GO/CS2 skin prices <span>💰</span> 
                Compare prices across wear conditions <span>📊</span> 
                Search skins by voice <span>🎤</span> 
                <span>🔥</span> Enjoy using! <span>✨</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Карточки функционала
    st.markdown(f'<div class="section-title">🚀 {get_text("key_features", lang)}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="feature-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 15px; text-align: center; min-height: 250px;">
            <div style="font-size: 64px; margin-bottom: 20px; animation: float 3s ease-in-out infinite;">💰</div>
            <h3 style="color: #FFD700; font-size: 28px; margin-bottom: 15px;">🔍 {get_text("price_search", lang)}</h3>
            <p style="color: white; font-size: 18px; line-height: 1.5; font-weight: 500;">{get_text("price_search_desc", lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="feature-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 30px; border-radius: 15px; text-align: center; min-height: 250px;">
            <div style="font-size: 64px; margin-bottom: 20px; animation: float 3s ease-in-out infinite 0.5s;">📊</div>
            <h3 style="color: #FFD700; font-size: 28px; margin-bottom: 15px;">📈 {get_text("price_compare", lang)}</h3>
            <p style="color: white; font-size: 18px; line-height: 1.5; font-weight: 500;">{get_text("price_compare_desc", lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="feature-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 30px; border-radius: 15px; text-align: center; min-height: 250px;">
            <div style="font-size: 64px; margin-bottom: 20px; animation: float 3s ease-in-out infinite 1s;">🎤</div>
            <h3 style="color: #FFD700; font-size: 28px; margin-bottom: 15px;">🎙️ {get_text("voice_search", lang)}</h3>
            <p style="color: white; font-size: 18px; line-height: 1.5; font-weight: 500;">{get_text("voice_search_desc", lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    # Увеличенная инструкция
    st.markdown("---")
    st.markdown(f'<div class="section-title">📖 {get_text("how_to_start", lang)}</div>', unsafe_allow_html=True)

    if lang == "Русский":
        st.markdown(f"""
        <div class="instruction-box">
            <ol>
                <li>Перейдите в раздел <strong>"{get_text("cs_skins", lang)}"</strong></li>
                <li>Выберите оружие из выпадающего списка</li>
                <li>Выберите название скина</li>
                <li>Нажмите на кнопку <strong>"{get_text("get_price", lang)}"</strong> для предсказания стоимости</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="instruction-box">
            <ol>
                <li>Go to the <strong>"{get_text("cs_skins", lang)}"</strong> section</li>
                <li>Select weapon from dropdown list</li>
                <li>Select skin name</li>
                <li>Click the <strong>"{get_text("get_price", lang)}"</strong> button to predict the price</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    # Популярные скины
    st.markdown("---")
    st.markdown(f'<div class="section-title">🔥 {get_text("popular_skins", lang)}</div>', unsafe_allow_html=True)

    # Данные о скинах
    popular_skins = [
        {"name": "AK-47 | Vulcan", "rarity": "Тайный",
         "img": "https://cs.money/assets/rs:fit:0:0:0/q:90/f:webp/dpr:1/t:0:FF00FF:1:1/plain/https://screenshots.cs.money/csmoney2/846fef0c090c1cdc284f1a297aa2dc24_large_preview.png"},

        {"name": "M4A4 | Howl", "rarity": "Контрабандный",
         "img": "https://cs.money/assets/rs:fit:0:0:0/q:100/f:webp/dpr:1/t:0:FF00FF:1:1/plain/https://screenshots.cs.money/csmoney2/eba47401dd25eb759bc020a59701b2c9_large_preview.png"},

        {"name": "AWP | Asiimov", "rarity": "Тайный",
         "img": "https://cs.money/assets/rs:fit:0:0:0/q:100/f:webp/dpr:1/t:0:FF00FF:1:1/plain/https://screenshots.cs.money/csmoney2/a2c28af54bc520a24e2e113ee76ead7a_large_preview.png"},

        {"name": "Galil AR | Eco", "rarity": "Секретный",
         "img": "https://cs.money/assets/rs:fit:0:0:0/q:100/f:webp/dpr:1/t:0:FF00FF:1:1/plain/https://screenshots.cs.money/csmoney2/c183d3d52854d9c3172b6a5224596ea5_large_preview.png"},

        {"name": "M4A1-S | Printstream", "rarity": "Covert",
         "img": "https://cs.money/assets/rs:fit:0:0:0/q:100/f:webp/dpr:1/t:0:FF00FF:1:1/plain/https://screenshots.cs.money/csmoney2/a49d6d1902129732dc6b8de5fc0e306d_large_preview.png"},

        {"name": "USP-S | Kill Confirmed", "rarity": "Covert",
         "img": "https://cs.money/assets/rs:fit:0:0:0/q:100/f:webp/dpr:1/t:0:FF00FF:1:1/plain/https://screenshots.cs.money/csmoney2/7bfd31b5e623a7c0a8f75ef91d4ba529_large_preview.png"},

        {"name": "Desert Eagle | Code Red", "rarity": "Covert",
         "img": "https://cs.money/assets/rs:fit:0:0:0/q:100/f:webp/dpr:1/t:0:FF00FF:1:1/plain/https://screenshots.cs.money/csmoney2/aca3ebf31a47ef5598fe175d856c0b6b_large_preview.png"},

        {"name": "SSG 08 | Blood in the Water", "rarity": "Covert",
         "img": "https://cs.money/assets/rs:fit:0:0:0/q:100/f:webp/dpr:1/t:0:FF00FF:1:1/plain/https://screenshots.cs.money/csmoney2/78ba049a3bfcd10ebae312cf352b397a_large_preview.png"},

        {"name": "Glock-18 | Dragon Tattoo", "rarity": "Запрещенный",
         "img": "https://cs.money/assets/rs:fit:0:0:0/q:100/f:webp/dpr:1/t:0:FF00FF:1:1/plain/https://screenshots.cs.money/csmoney2/80767f407711acb2dbe389fd318a0f2b_large_preview.png"}
    ]

    # Отображаем сетку 3x3
    for i in range(0, len(popular_skins), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(popular_skins):
                skin = popular_skins[i + j]
                rarity_color = get_rarity_color(skin['rarity'])

                # Добавляем динамический CSS для каждой карточки
                st.markdown(f"""
                <style>
                .skin-card-{i + j} {{
                    transition: all 0.3s ease;
                }}
                .skin-card-{i + j}:hover {{
                    border-color: {rarity_color} !important;
                    box-shadow: 0 0 20px {rarity_color}40;
                }}
                .skin-card-{i + j}:hover .skin-name-{i + j} {{
                    color: {rarity_color};
                    text-shadow: 0 0 10px {rarity_color}80;
                }}
                </style>
                """, unsafe_allow_html=True)

                with cols[j]:
                    st.markdown(f"""
                    <div class="skin-card skin-card-{i + j}" style="border: 2px solid rgba(255,255,255,0.1);">
                        <div class="image-container">
                            <img src="{skin['img']}" alt="{skin['name']}">
                        </div>
                        <div class="skin-name skin-name-{i + j}" style="color: white;">{skin['name']}</div>
                    </div>
                    """, unsafe_allow_html=True)

elif selected == get_text("cs_skins", lang):
    Cs_skins.show()

elif selected == get_text("news", lang):
    News.show()

elif selected == get_text("info", lang):
    Info.show()

elif selected == get_text("settings", lang):
    Settings.show()

# Футер
st.markdown(
    f"""
    <div class="floating-footer">
        CS:Skins Classifier v1.0.0 | © 2026 | {get_text("footer_made_with", lang)}
    </div>
    """,
    unsafe_allow_html=True
)