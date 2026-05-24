import streamlit as st
from locales import get_text


def show():
    lang = st.session_state.get('language', 'Русский')

    st.title(get_text("about_program", lang))

    # Стили оставляем, они не повредят
    st.markdown("""
    <style>
    .info-card {
        background: rgba(255,255,255,0.05);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        transition: transform 0.3s ease;
    }
    .info-card:hover {
        transform: translateY(-5px);
    }
    .tech-card {
        background: rgba(255,255,255,0.05);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
        transition: transform 0.3s ease;
    }
    .tech-card:hover {
        transform: translateY(-5px);
        background: rgba(255,255,255,0.1);
    }
    .contact-card {
        background: rgba(255,255,255,0.05);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
        transition: transform 0.3s ease;
    }
    .contact-card:hover {
        transform: translateY(-5px);
        background: rgba(255,255,255,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    # Краткое описание программы
    st.markdown(f"""
    <div class="info-card">
        <h2 style="text-align: center; color: #FFD700;">🎮 CS:Skins Classifier</h2>
        <p style="text-align: center;">{get_text('app_description_short', lang)}</p>
    </div>
    """, unsafe_allow_html=True)

    # Технологии
    st.markdown(f"###  {get_text('technologies', lang)}:")

    tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)

    with tech_col1:
        st.markdown(f"""
        <div class="tech-card" style="text-align: center;">
            <div style="font-size: 48px; margin-bottom: 10px;">🐍</div>
            <p><strong>Python</strong><br>{get_text('main_language', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    with tech_col2:
        st.markdown(f"""
        <div class="tech-card" style="text-align: center;">
            <div style="font-size: 48px; margin-bottom: 10px;">📊</div>
            <p><strong>Streamlit</strong><br>{get_text('web_framework', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    with tech_col3:
        st.markdown(f"""
        <div class="tech-card" style="text-align: center;">
            <div style="font-size: 48px; margin-bottom: 10px;">🤖</div>
            <p><strong>ML & FastAPI</strong><br>{get_text('ml_backend', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    with tech_col4:
        st.markdown(f"""
        <div class="tech-card" style="text-align: center;">
            <div style="font-size: 48px; margin-bottom: 10px;">🎙️</div>
            <p><strong>speech_recognition</strong><br>{get_text('voice_input', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    # Контакты
    st.markdown(f"### {get_text('contacts', lang)}:")

    col_contact1, col_contact2, col_contact3 = st.columns(3)

    with col_contact1:
        st.markdown(f"""
        <div class="contact-card" style="text-align: center;">
            <div style="font-size: 48px; margin-bottom: 10px;">👨‍💻</div>
            <p><strong>{get_text('developer_name', lang)}</strong><br>{get_text('developer_role', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_contact2:
        st.markdown(f"""
        <div class="contact-card" style="text-align: center;">
            <div style="font-size: 48px; margin-bottom: 10px;">📧</div>
            <p><strong>{get_text('email', lang)}</strong><br>konstantinm@gmail.com</p>
        </div>
        """, unsafe_allow_html=True)

    with col_contact3:
        st.markdown(f"""
        <div class="contact-card" style="text-align: center;">
            <div style="font-size: 48px; margin-bottom: 10px;">🎮</div>
            <p><strong>CS:Skins Classifier</strong><br>{get_text('version_label', lang)} v1.0.0</p>
        </div>
        """, unsafe_allow_html=True)