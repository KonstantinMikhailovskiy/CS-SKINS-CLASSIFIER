import streamlit as st
from locales import get_text


def show():
    lang = st.session_state.get('language', 'Русский')

    st.title(get_text("settings_title", lang))

    # Инициализация настроек в session_state
    if 'theme' not in st.session_state:
        st.session_state.theme = "Темная (Классическая)"
    if 'language' not in st.session_state:
        st.session_state.language = "Русский"

    col1, col2 = st.columns(2)

    with col1:
        # Темы
        theme_options = {
            "Темная (Классическая)": get_text("theme_dark_classic", lang),
            "Синяя (Океан)": get_text("theme_blue_ocean", lang),
            "Фиолетовая (Космос)": get_text("theme_purple_space", lang),
            "Красная (Огонь)": get_text("theme_red_fire", lang),
            "Градиент (Закат)": get_text("theme_gradient_sunset", lang),
        }
        theme_display_list = list(theme_options.values())
        current_theme_display = theme_options.get(st.session_state.theme, theme_display_list[0])

        theme_display = st.selectbox(
            get_text("select_theme", lang),
            theme_display_list,
            index=theme_display_list.index(current_theme_display) if current_theme_display in theme_display_list else 0,
            help=get_text("theme_help", lang),
            key="theme_select"
        )
        theme = next((k for k, v in theme_options.items() if v == theme_display), st.session_state.theme)

    with col2:
        # Язык
        language = st.selectbox(
            get_text("select_language", lang),
            ["Русский", "English"],
            index=0 if st.session_state.language == "Русский" else 1,
            key="language_select"
        )

    #Текущие настройки
    with st.expander(get_text("current_settings", lang), expanded=False):
        st.write(f"{get_text('theme_label', lang)} **{st.session_state.theme}**")
        st.write(f"{get_text('language_label', lang)} **{st.session_state.language}**")

    # Кнопка сохранения
    if st.button(get_text("save_settings", lang), use_container_width=True, type="primary", key="save_btn"):
        st.session_state.theme = theme
        st.session_state.language = language
        st.success(get_text("settings_saved", lang))
        st.balloons()
        st.rerun()

    # Кнопка сброса
    if st.button(get_text("reset_default", lang), use_container_width=True, key="reset_btn"):
        st.session_state.theme = "Темная (Классическая)"
        st.session_state.language = "Русский"
        st.success(get_text("reset_success", lang))
        st.rerun()


def apply_theme(theme):
    """Применение выбранной темы"""
    themes_dict = {
        "Темная (Классическая)": {
            "bg": "#0e1117", "text": "#ffffff", "primary": "#FF4B4B", "secondary": "#1c1f2e",
            "menu_bg": "rgba(0,0,0,0.8)", "menu_hover": "rgba(255,75,75,0.2)", "menu_selected": "#FF4B4B"
        },
        "Синяя (Океан)": {
            "bg": "#001f3f", "text": "#ffffff", "primary": "#4A90E2", "secondary": "#003366",
            "menu_bg": "rgba(0,31,63,0.9)", "menu_hover": "rgba(74,144,226,0.2)", "menu_selected": "#4A90E2"
        },
        "Фиолетовая (Космос)": {
            "bg": "#1a0b2e", "text": "#e0b0ff", "primary": "#9b59b6", "secondary": "#2c1a4a",
            "menu_bg": "rgba(26,11,46,0.9)", "menu_hover": "rgba(155,89,182,0.2)", "menu_selected": "#9b59b6"
        },
        "Красная (Огонь)": {
            "bg": "#2c0000", "text": "#ffcccc", "primary": "#e74c3c", "secondary": "#4a0000",
            "menu_bg": "rgba(44,0,0,0.9)", "menu_hover": "rgba(231,76,60,0.2)", "menu_selected": "#e74c3c"
        },
        "Градиент (Закат)": {
            "bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", "text": "#ffffff",
            "primary": "#f093fb", "secondary": "#4f46e5",
            "menu_bg": "rgba(102,126,234,0.9)", "menu_hover": "rgba(240,147,251,0.2)", "menu_selected": "#f093fb"
        },
    }
    colors = themes_dict.get(theme, themes_dict["Темная (Классическая)"])

    # CSS
    st.markdown(f"""
    <style>
    .stApp {{
        background: {colors["bg"] if theme != "Градиент (Закат)" else "none"};
        {"background: " + colors["bg"] + ";" if theme == "Градиент (Закат)" else ""}
        color: {colors["text"]};
    }}

    .stSelectbox label, div[data-baseweb="select"] label {{
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 20px !important;
        margin-bottom: 8px !important;
    }}

    /* УВЕЛИЧЕННЫЙ ТЕКСТ ВНУТРИ ВЫПАДАЮЩЕГО СПИСКА */
    div[data-baseweb="select"] > div > div > div > div > span,
    div[data-baseweb="select"] div {{
        font-size: 18px !important;
    }}
    div[data-baseweb="select"] {{
        height: 55px !important;
    }}

    /* КНОПКИ */
    .stButton > button {{
        background: {colors["primary"]};
        color: {colors["text"]};
        border: none;
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 12px 20px !important;
        transition: all 0.3s ease;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        opacity: 0.9;
    }}

    .floating-menu {{
        background: {colors["menu_bg"]} !important;
        backdrop-filter: blur(10px);
    }}
    .nav-link.active {{
        background: {colors["menu_selected"]} !important;
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def get_setting(key, default=None):
    """Получение значения настройки"""
    return st.session_state.get(key, default)