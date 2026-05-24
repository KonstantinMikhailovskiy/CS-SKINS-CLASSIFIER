import streamlit as st
import base64
from PIL import Image
import Settings
from locales import get_text
from skin_price_predictor import get_predictor
import pandas as pd
from datetime import datetime
import speech_recognition as sr
import plotly.express as px
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def show():
    """Функция для отображения содержимого Cs_skins.py"""

    # Инициализация состояния приложения
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "price_search"
    if 'voice_price_results' not in st.session_state:
        st.session_state.voice_price_results = {}
    if 'classification_history' not in st.session_state:
        st.session_state.classification_history = []

    # Получаем настройки
    auto_save = Settings.get_setting('auto_save', True)
    lang = st.session_state.get('language', 'Русский')
    theme = st.session_state.get('theme', 'Темная (Классическая)')
    Settings.apply_theme(theme)
    predictor = get_predictor()

    # Словарь цветов для редкости
    rarity_colors = {
        "Consumer Grade": "#D3D3D3", "Industrial Grade": "#87CEEB", "Mil-Spec": "#4B9CD3",
        "Restricted": "#800080", "Classified": "#FF69B4", "Covert": "#DC143C", "Contraband": "#FF8C00",
        "Базовый": "#D3D3D3", "Промышленный": "#87CEEB", "Армейский": "#4B9CD3",
        "Запрещенный": "#800080", "Секретный": "#FF69B4", "Тайный": "#DC143C", "Контрабандный": "#FF8C00",
    }

    def get_rarity_color(rarity_name):
        if not rarity_name:
            return "#FFD700"
        rarity_lower = rarity_name.lower()
        for key, color in rarity_colors.items():
            if key.lower() in rarity_lower or rarity_lower in key.lower():
                return color
        return "#FFD700"

    # Цвета темы
    themes_dict = {
        "Темная (Классическая)": {"card_bg": "rgba(0,0,0,0.7)", "border_color": "rgba(255,215,0,0.3)"},
        "Синяя (Океан)": {"card_bg": "rgba(0,31,63,0.8)", "border_color": "rgba(74,144,226,0.3)"},
        "Фиолетовая (Космос)": {"card_bg": "rgba(26,11,46,0.8)", "border_color": "rgba(155,89,182,0.3)"},
        "Красная (Огонь)": {"card_bg": "rgba(44,0,0,0.8)", "border_color": "rgba(231,76,60,0.3)"},
        "Градиент (Закат)": {"card_bg": "rgba(102,126,234,0.8)", "border_color": "rgba(240,147,251,0.3)"},
    }
    current_theme_colors = themes_dict.get(theme, themes_dict["Темная (Классическая)"])

    # ==================== CSS ====================
    st.markdown(f"""
    <style>
    .main .block-container {{ padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; padding-left: 1rem !important; padding-right: 1rem !important; max-width: 100% !important; }}

    /* УВЕЛИЧЕННЫЙ ШРИФТ ВКЛАДОК */
    .stTabs {{ width: 100%; }}
    .stTabs [data-baseweb="tab-list"] {{ display: flex !important; flex-wrap: nowrap !important; justify-content: space-between !important; gap: 0px !important; background: {current_theme_colors["card_bg"]}; padding: 0px !important; border-radius: 0px !important; backdrop-filter: blur(10px); border-bottom: 2px solid {current_theme_colors["border_color"]}; margin-bottom: 0px !important; width: 100% !important; }}
    .stTabs [data-baseweb="tab"] {{ 
        flex: 1 !important; height: 85px !important; font-size: 34px !important; font-weight: bold !important; 
        padding: 0 10px !important; border-radius: 0px !important; background: transparent !important; 
        color: rgba(255,255,255,0.7) !important; transition: all 0.2s ease; border: none !important; 
        border-bottom: 3px solid transparent !important; white-space: nowrap !important; 
        text-align: center !important; justify-content: center !important; letter-spacing: 1px !important; 
    }}
    .stTabs [data-baseweb="tab"]:hover {{ background: rgba(255,215,0,0.1) !important; color: #FFD700 !important; border-bottom-color: rgba(255,215,0,0.5) !important; }}
    .stTabs [aria-selected="true"] {{ color: #FFD700 !important; border-bottom-color: #FFD700 !important; background: transparent !important; font-weight: bold !important; }}
    .stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.5rem; padding-bottom: 0rem; }}

    /* ПОДПИСИ SELECTBOX */
    .stSelectbox label, div[data-baseweb="Input"] label {{ 
        font-size: 22px !important; color: #FFD700 !important; font-weight: bold !important; margin-bottom: 8px !important; 
    }}
    div[data-baseweb="select"] {{ height: 55px !important; }}
    div[data-baseweb="select"] > div {{ font-size: 18px !important; }}

    .info-grid {{ display: flex; justify-content: flex-start; gap: 30px; margin: 30px 0; flex-wrap: wrap; }}
    .info-card {{ background: linear-gradient(135deg, {current_theme_colors["card_bg"]}, rgba(0,0,0,0.9)); backdrop-filter: blur(10px); border-radius: 20px; padding: 25px 35px; text-align: center; min-width: 200px; border: 2px solid {current_theme_colors["border_color"]}; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }}
    .info-card:hover {{ transform: translateY(-5px); border-color: #FFD700; box-shadow: 0 8px 25px rgba(255,215,0,0.2); }}
    .info-label {{ font-size: 18px; color: #FFD700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 12px; font-weight: bold; }}
    .info-value {{ font-size: 22px; color: white; font-weight: bold; word-break: break-word; }}
    .rarity-card {{ background: {current_theme_colors["card_bg"]}; backdrop-filter: blur(10px); border-radius: 20px; padding: 25px 35px; text-align: center; min-width: 200px; transition: all 0.3s ease; border: 3px solid; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }}
    .rarity-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.4); border-color: #FFD700; }}
    .price-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 35px; border-radius: 25px; margin: 20px 0; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3); transition: all 0.3s ease; }}
    .price-card:hover {{ transform: scale(1.02); box-shadow: 0 15px 40px rgba(0,0,0,0.4); }}
    .price-value {{ font-size: 56px; font-weight: bold; color: #FFD700; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
    .price-label {{ font-size: 24px; color: white; margin-bottom: 15px; font-weight: bold; }}
    .stButton button {{ background: linear-gradient(135deg, #FFD700, #FFA500); color: #000; border: none; border-radius: 15px; padding: 16px 32px; font-size: 20px; font-weight: bold; transition: all 0.3s ease; width: 100%; cursor: pointer; }}
    .stButton button:hover {{ transform: translateY(-3px); box-shadow: 0 8px 25px rgba(255,215,0,0.5); }}
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{ background: linear-gradient(135deg, #FFD700, #FFA500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold; margin-top: 0.5rem; margin-bottom: 0.5rem; font-size: 32px !important; }}
    .stat-card {{ background: linear-gradient(135deg, #FFD70020, #FFA50020); backdrop-filter: blur(10px); border-radius: 20px; padding: 30px 20px; text-align: center; border: 2px solid #FFD700; transition: all 0.3s ease; box-shadow: 0 8px 25px rgba(255,215,0,0.2); }}
    .stat-card:hover {{ transform: translateY(-5px); border-color: #FFD700; box-shadow: 0 12px 35px rgba(255,215,0,0.3); }}
    .stat-value {{ font-size: 48px !important; font-weight: bold; color: #FFD700; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
    .stat-label {{ font-size: 18px; color: white; margin-top: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; }}
    .video-container {{ position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 15px; margin: 20px 0; box-shadow: 0 8px 25px rgba(0,0,0,0.3); }}
    .video-container iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 15px; }}
    .skin-result {{ background: {current_theme_colors["card_bg"]}; backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; margin: 15px 0; border: 1px solid {current_theme_colors["border_color"]}; transition: all 0.3s ease; }}
    .skin-result:hover {{ border-color: #FFD700; box-shadow: 0 5px 15px rgba(255,215,0,0.2); }}
    .skin-title {{ font-size: 24px; font-weight: bold; color: #FFD700; margin-bottom: 15px; }}
    </style>
    """, unsafe_allow_html=True)

    # ==================== ЗАГОЛОВОК ====================
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("bro.jpg", use_container_width=True)
            st.markdown(f"""
                <p style="text-align: center; font-size: 36px; font-weight: bold; background: linear-gradient(135deg, #FFD700, #FFA500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 10px; margin-bottom: 20px;">
                    ⭐ {get_text("check_your_skin", lang)} ⭐
                </p>
            """, unsafe_allow_html=True)
        except:
            st.info(get_text("image_not_found", lang))

    # ==================== ВКЛАДКИ ====================
    tab1, tab2, tab3, tab4 = st.tabs([
        f"{get_text('price_search_tab', lang)}",
        f"{get_text('price_comparison_tab', lang)}",
        f"{get_text('search_by_name_tab', lang)}",
        f"{get_text('statistics_tab', lang)}"
    ])

    # ==================== ВКЛАДКА 1: Поиск цены ====================
    with tab1:
        st.session_state.active_tab = "price_search"
        st.markdown(f"### {get_text('find_skin_price', lang)}")

        left_col, right_col = st.columns(2)
        with left_col:
            weapons = predictor.get_all_weapons()
            weapon = st.selectbox(
                get_text('select_weapon', lang),
                options=weapons if weapons else [get_text("loading", lang)],
                key="weapon_select"
            )
            skin_name = None
            if weapon and weapon != get_text("loading", lang):
                skins = predictor.get_skins_by_weapon(weapon)
                skin_name = st.selectbox(
                    get_text('select_skin', lang),
                    options=skins if skins else [get_text("no_skins", lang)],
                    key="skin_select"
                )
            else:
                st.selectbox(
                    get_text('select_skin', lang),
                    options=[get_text("select_weapon_first", lang)],
                    disabled=True
                )

            # ЕДИНАЯ КНОПКА: получить инфо + предсказать цену
            if st.button(
                    get_text('get_price', lang),
                    type="primary",
                    key="btn_get_price_all",
                    disabled=not (weapon and skin_name)
            ):
                with st.spinner(get_text('loading_info_price', lang)):
                    logger.info(f"[TAB1] Fetching info & price: {weapon} | {skin_name}")
                    info = predictor.get_skin_info(weapon, skin_name)
                    result = predictor.predict_from_text_input(weapon, skin_name, 'Factory New', False)

                    st.session_state['tab1_skin_info'] = info
                    st.session_state['tab1_prediction'] = result
                    st.session_state['tab1_weapon'] = weapon
                    st.session_state['tab1_skin'] = skin_name

                    # Тихое сохранение в историю
                    if auto_save and result and not result.get('error'):
                        st.session_state.classification_history.append({
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'weapon': weapon,
                            'skin': skin_name,
                            'rarity': info.get('rarity', get_text('unknown', lang)) if info else get_text('unknown',
                                                                                                          lang),
                            'case': info.get('case', get_text('unknown', lang)) if info else get_text('unknown', lang),
                            'price': result.get('predicted_price', 0)
                        })
                    st.rerun()

        with right_col:
            # Карточки: кейс, редкость, износ
            if st.session_state.get('tab1_skin_info'):
                info = st.session_state['tab1_skin_info']
                rarity = info.get('rarity', get_text("unknown", lang))
                rarity_color = get_rarity_color(rarity)
                st.markdown(f"""
                <div class="info-grid">
                    <div class="info-card">
                        <div class="info-label">{get_text('case_label', lang)}</div>
                        <div class="info-value">{info.get('case', get_text('unknown', lang))}</div>
                    </div>
                    <div class="rarity-card" style="border-color: {rarity_color};">
                        <div class="info-label" style="color: {rarity_color};">{get_text('rarity_label', lang)}</div>
                        <div class="info-value" style="color: {rarity_color};">{rarity}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">{get_text('wear_label', lang)}</div>
                        <div class="info-value">{info.get('min_wear', 0):.2f} - {info.get('max_wear', 1):.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Результат предсказания цены
            if st.session_state.get('tab1_prediction'):
                result = st.session_state['tab1_prediction']
                if result.get('error') == 'not_found':
                    st.warning(f"❌ {get_text('skin_not_found', lang)}")
                else:
                    st.markdown(f"""
                    <div class="price-card">
                        <div class="price-label">{result.get('weapon', '')} | {result.get('skin', '')}</div>
                        <div class="price-value">${result.get('predicted_price', 0):.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ==================== ВКЛАДКА 2: Сравнение цен ====================
    with tab2:
        st.session_state.active_tab = "price_comparison"
        st.markdown(f"### {get_text('compare_prices_wear', lang)}")

        col1, col2 = st.columns(2)
        with col1:
            weapons = predictor.get_all_weapons()
            compare_weapon = st.selectbox(
                get_text('select_weapon', lang),
                options=weapons if weapons else [get_text("loading", lang)],
                key="compare_weapon"
            )
        with col2:
            compare_skin = None
            if compare_weapon and compare_weapon != get_text("loading", lang):
                skins = predictor.get_skins_by_weapon(compare_weapon)
                compare_skin = st.selectbox(
                    get_text('select_skin', lang),
                    options=skins if skins else [get_text("no_skins", lang)],
                    key="compare_skin"
                )

        # Кнопка сравнения — шарики ТОЛЬКО здесь
        if st.button(
                get_text('compare_prices_btn', lang),
                key="btn_load_comparison",
                disabled=not (compare_weapon and compare_skin)
        ):
            with st.spinner(get_text('searching_price', lang)):
                logger.info(f"[TAB2] Fetching comparison: {compare_weapon} | {compare_skin}")
                comp = predictor.get_price_comparison(compare_weapon, compare_skin)
                st.session_state['tab2_comparison'] = comp
                st.balloons()  # 🎈 Вылетают только при нажатии кнопки
                st.rerun()

        if st.session_state.get('tab2_comparison'):
            comparison = st.session_state['tab2_comparison']
            if comparison:
                # Обычная версия
                price_data = [
                    {get_text('condition', lang): c, get_text('price', lang): f"${p:.2f}"}
                    for c, p in comparison['prices'].items() if p
                ]
                if price_data:
                    st.markdown(f"#### {get_text('normal_version', lang)}")
                    st.dataframe(pd.DataFrame(price_data), use_container_width=True)

                # StatTrak версия
                if comparison.get('stattrak_prices'):
                    st_data = [
                        {get_text('condition', lang): c, get_text('price', lang): f"${p:.2f}"}
                        for c, p in comparison['stattrak_prices'].items() if p
                    ]
                    if st_data:
                        st.markdown(f"#### {get_text('stattrak_version', lang)}")
                        st.dataframe(pd.DataFrame(st_data), use_container_width=True)

                # График
                df_plot = pd.DataFrame([
                    {get_text('condition', lang): c, get_text('price', lang): p,
                     get_text('type', lang): get_text('normal', lang)}
                    for c, p in comparison['prices'].items() if p
                ])
                if comparison.get('stattrak_prices'):
                    df_st = pd.DataFrame([
                        {get_text('condition', lang): c, get_text('price', lang): p, get_text('type', lang): 'StatTrak'}
                        for c, p in comparison['stattrak_prices'].items() if p
                    ])
                    df_plot = pd.concat([df_plot, df_st])

                if not df_plot.empty:
                    fig = px.bar(
                        df_plot,
                        x=get_text('condition', lang),
                        y=get_text('price', lang),
                        color=get_text('type', lang),
                        title=f"<b style='color:#FFD700'>{get_text('price_comparison_chart', lang)}</b>",
                        barmode='group',
                        color_discrete_map={get_text('normal', lang): '#FFD700', 'StatTrak': '#FF6B6B'}
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0.5)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        title_x=0.5,
                        title_font_size=26,
                        title_xanchor='center'
                    )
                    st.plotly_chart(fig, use_container_width=True)

    # ==================== ВКЛАДКА 3: Голосовой поиск ====================
    with tab3:
        st.session_state.active_tab = "search_by_name"
        st.markdown(f"### {get_text('voice_search_header', lang)}")

        # Кнопка голосового поиска
        if st.button(
                get_text('voice_search_button', lang),
                key="voice_search_main",
                use_container_width=True,
                type="primary"
        ):
            try:
                with st.spinner(get_text('voice_listening', lang)):
                    recognizer = sr.Recognizer()
                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source, duration=1)
                        audio = recognizer.listen(source, timeout=6, phrase_time_limit=5)
                    voice_text = recognizer.recognize_google(audio, language="ru-RU")

                st.success(f"{get_text('voice_recognized', lang)}: **{voice_text}**")
                results = predictor.search_skins(voice_text)

                if results and len(results) > 0:
                    st.session_state['tab3_voice_results'] = results
                    st.rerun()
                else:
                    st.warning(get_text('voice_not_found', lang).format(voice_text=voice_text))

            except sr.WaitTimeoutError:
                st.error(get_text('voice_timeout', lang))
            except sr.UnknownValueError:
                st.error(get_text('voice_unknown', lang))
            except sr.RequestError as e:
                st.error(get_text('voice_request_error', lang).format(e=e))
            except Exception as e:
                st.error(get_text('voice_general_error', lang).format(e=str(e)))

        # Отображение результатов поиска
        if st.session_state.get('tab3_voice_results'):
            results = st.session_state['tab3_voice_results']
            st.success(get_text('voice_found_count', lang).format(count=len(results)))

            for idx, skin in enumerate(results[:20]):
                skin_info = predictor.get_skin_info(skin['Weapon'], skin['Case'])
                rarity = skin_info.get('rarity', get_text("unknown", lang)) if skin_info else get_text("unknown", lang)
                rarity_color = get_rarity_color(rarity)

                # Карточки в том же стиле, что на вкладке 1
                st.markdown(f"""
                <div class="skin-result">
                    <div class="skin-title">{skin['Weapon']} | {skin['Case']}</div>
                    <div class="info-grid">
                        <div class="info-card">
                            <div class="info-label">{get_text('case_label', lang)}</div>
                            <div class="info-value">{skin_info.get('case', get_text('unknown', lang)) if skin_info else get_text('unknown', lang)}</div>
                        </div>
                        <div class="rarity-card" style="border-color: {rarity_color};">
                            <div class="info-label" style="color: {rarity_color};">{get_text('rarity_label', lang)}</div>
                            <div class="info-value" style="color: {rarity_color};">{rarity}</div>
                        </div>
                        <div class="info-card">
                            <div class="info-label">{get_text('wear_label', lang)}</div>
                            <div class="info-value">{skin_info.get('min_wear', 0):.2f} - {skin_info.get('max_wear', 1):.2f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Кнопка получения цены для найденного скина
                btn_key = f"price_btn_{skin['Weapon']}_{skin['Case']}_{idx}".replace(" ", "_")
                if st.button(get_text('voice_get_price_btn', lang), key=btn_key):
                    with st.spinner(get_text('searching_price', lang)):
                        res = predictor.predict_from_text_input(skin['Weapon'], skin['Case'], 'Factory New', False)
                        key_res = f"{skin['Weapon']}_{skin['Case']}"
                        st.session_state.voice_price_results[key_res] = res
                        st.rerun()

                # Отображение предсказанной цены
                key_res = f"{skin['Weapon']}_{skin['Case']}"
                if key_res in st.session_state.voice_price_results:
                    res = st.session_state.voice_price_results[key_res]
                    if res and not res.get('error'):
                        st.markdown(
                            f"""<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin: 10px 0 20px 0; text-align: center; border: 2px solid #FFD700;">
                                <div style="font-size: 18px; color: white; margin-bottom: 10px;">
                                    {get_text('voice_predicted_price_label', lang)}
                                </div>
                                <div style="font-size: 36px; font-weight: bold; color: #FFD700;">
                                    ${res['predicted_price']:.2f}
                                </div>
                            </div>""",
                            unsafe_allow_html=True
                        )
                        if auto_save:
                            st.balloons()
                st.markdown("<hr>", unsafe_allow_html=True)

            # Кнопка очистки результатов
            if st.button(get_text('voice_clear_results', lang), key="clear_voice_results"):
                st.session_state.pop('tab3_voice_results', None)
                st.session_state.voice_price_results.clear()
                st.rerun()

    # ==================== ВКЛАДКА 4: Статистика ====================
    with tab4:
        st.session_state.active_tab = "statistics"
        st.markdown(f"### {get_text('database_statistics', lang)}")

        if predictor.df_skins is not None:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(
                    f"""<div class="stat-card">
                        <div class="stat-value">{len(predictor.df_skins)}</div>
                        <div class="stat-label">{get_text("total_skins", lang)}</div>
                    </div>""",
                    unsafe_allow_html=True
                )
            with col2:
                st.markdown(
                    f"""<div class="stat-card">
                        <div class="stat-value">{predictor.df_skins['Weapon'].nunique()}</div>
                        <div class="stat-label">{get_text("unique_weapons", lang)}</div>
                    </div>""",
                    unsafe_allow_html=True
                )
            with col3:
                st.markdown(
                    f"""<div class="stat-card">
                        <div class="stat-value">${predictor.df_skins['Factory New'].mean():.2f}</div>
                        <div class="stat-label">{get_text("average_price_fn", lang)}</div>
                    </div>""",
                    unsafe_allow_html=True
                )

            # Топ-10 самых дорогих скинов
            st.markdown(f"#### 💎 {get_text('top_10_expensive', lang)}")
            top_skins = predictor.df_skins.nlargest(10, 'Factory New')[
                ['Weapon', 'Case', 'Rarity', 'Factory New']].copy()
            top_skins['Factory New'] = top_skins['Factory New'].apply(lambda x: f"${x:.2f}")
            top_skins.columns = [
                get_text('weapon', lang),
                get_text('skin', lang),
                get_text('rarity', lang),
                get_text('price', lang)
            ]
            st.dataframe(top_skins, use_container_width=True)

            # 🎥 Видео с заголовком
            st.markdown(f"#### {get_text('video_header', lang)}")
            video_url = "https://www.youtube.com/watch?v=_12D0Z0frSM"
            video_id = video_url.split("watch?v=")[1].split("&")[0] if "watch?v=" in video_url else ""
            embed_url = f"https://www.youtube.com/embed/{video_id}" if video_id else video_url
            st.markdown(
                f"""<div class="video-container">
                    <iframe src="{embed_url}" frameborder="0" allowfullscreen></iframe>
                </div>""",
                unsafe_allow_html=True
            )