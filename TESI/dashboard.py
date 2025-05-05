import streamlit as st
import os
import io
import sqlite3
from PIL import Image
from streamlit_option_menu import option_menu
import pandas as pd
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Login", layout="wide", page_icon="🌱")

st.markdown("""
    <style>
    html, body, .stApp {
        height: auto;
        overflow: auto;
    }
    .stApp {
        background-color: #a0b78b;
        font-family: 'Segoe UI', sans-serif;
    }
    .login-container {
        padding: 0rem 2rem;
        margin-top: 0rem;
    }
    .title {
        font-size: 2.3rem;
        font-weight: bold;
        color: #2f4f2f;
        text-align: center; 
        margin-top: 0rem; 
    }
    .subtitle {
        font-size: 1.1rem;
        color: #2f4f2f;
        text-align: center; 
        margin-bottom: 1rem; 
        font-weight: bold;
    }
    .stButton>button {
        background-color: #40693f;
        color: white;
        font-size: 1.1rem;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin-top: 0.5rem;
        margin-left: 15.5rem;  
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2f4f2f;
    }
    #MainMenu, header, footer {visibility: hidden;}
    .image-top {
        margin-top: 2rem; 
        margin-left: 10rem; 
    }
    .input-field {
        background-color: #f0f0df;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: bold;
        padding: 0.5rem;
        width: 65%; 
        color: black;
        font-weight: bold;
        margin-left: 8rem;  
    }
    div[data-testid="stTextInput"] {
        width: 300px !important;          
        margin-left: 140px !important; 
    }
    div[data-testid="stTextInput"] input {
        background-color: #f0f0f0;        
        color: black;               
        font-weight: bold;                 
    }

    .informazioni-container {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        width: 100%;
        height: 100%;
    }
    .informazioni-box {
        background-color: #D3D3D3;
        padding: 10px;
        font-size: 1.5rem;
        border-radius: 5px;
        width: 100%;
        text-align: center;
        margin-top: 1px;
        flex-grow: 1;
        display: flex;
        margin-left: -80px;

    }
    </style>
""", unsafe_allow_html=True)

def verifica_credenziali(username, password):
    db_path = 'database/users.db'
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute('SELECT * FROM utenti WHERE username = ? AND password = ?', (username, password))
        utente = c.fetchone()
        
        if utente:
            return True 
        else:
            return False 
    
    except sqlite3.Error as e:
        print(f"Errore durante la verifica delle credenziali: {e}")
        return False
    
    finally:
        conn.close()

def login_page():
    st.markdown("""
        <style>
        html, body, .stApp {
            height: 100vh;
            overflow: hidden;
        }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            overflow: hidden;
            max-height: 100vh;
        }
        </style>
    """, unsafe_allow_html=True)


    col1, col2 = st.columns([1, 1])

    with col1:
        img_sx_path = os.path.join("foto", "foto2.png")
        if os.path.exists(img_sx_path):
            st.markdown('<div class="image-top">', unsafe_allow_html=True)
            img_sx = Image.open(img_sx_path)
            st.image(img_sx, width=350)

        st.markdown("<div class='title'>Orto&Sapori S.R.L</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>Benvenuto nel gestionale aziendale,<br>inserisci le tue credenziali per accedere.</div>", unsafe_allow_html=True)

        st.markdown("<div style='font-size: 2.1rem; color: #2f4f2f; font-weight: bold; text-align: center;'>Login</div>", unsafe_allow_html=True)

        st.markdown("<div style='font-size: 1.2rem; color: #2f4f2f; font-weight: bold; text-align: center;'>Username</div>", unsafe_allow_html=True)
        username = st.text_input('Username', key="username", label_visibility="collapsed")

        st.markdown("<div style='font-size: 1.2rem; color: #2f4f2f; font-weight: bold; text-align: center;'>Password</div>", unsafe_allow_html=True)
        password = st.text_input('Password', key="password", label_visibility="collapsed")

        if st.button("Login"):
            if "autenticato" not in st.session_state:
                st.session_state.autenticato = False

            if verifica_credenziali(username, password):
                st.session_state.autenticato = True
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Credenziali errate. Riprova.")

    with col2:
        img_dx_path = os.path.join("foto", "foto1.jpeg")
        if os.path.exists(img_dx_path):
            img_dx = Image.open(img_dx_path)
            st.markdown(
                "<div style='margin-top: 40px;'>",
                unsafe_allow_html=True
            )
            st.image(img_dx, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

def get_dati_meteo():
    db_path = 'database/meteo.db'
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        today = pd.to_datetime('today').strftime('%Y-%m-%d')
        
        c.execute('SELECT * FROM meteo_fittizio WHERE Data = ?', (today,))
        meteo = c.fetchone()
        
        if meteo:
            return {
                "data": meteo[0],
                "temperatura": meteo[1],
                "descrizione": meteo[2],
                "umidita": meteo[3],
                "precipitazioni": meteo[4]
            }
        else:
            return None  
    
    except sqlite3.Error as e:
        print(f"Errore durante il recupero dei dati meteo: {e}")
        return None
    
    finally:
        conn.close()

def get_stagione_corrente(mese_corrente):
    if mese_corrente in [3, 4, 5]:
        return "Primavera"
    elif mese_corrente in [6, 7, 8]:
        return "Estate"
    elif mese_corrente in [9, 10, 11]:
        return "Autunno"
    else:
        return "Inverno"

def get_ortaggi_stagionali(stagione_corrente):
    db_path = 'database/ortaggi.db'

    mesi_per_stagione = {
        "primavera": ["2025-03", "2025-04", "2025-05"],
        "estate": ["2025-06", "2025-07", "2025-08"],
        "autunno": ["2025-09", "2025-10", "2025-11"],
        "inverno": ["2024-12", "2025-01", "2025-02"]
    }

    stagione_corrente = stagione_corrente.lower()
    mesi_da_considerare = mesi_per_stagione.get(stagione_corrente, [])

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute('PRAGMA table_info(ortaggi)')
        colonne_db = [col[1] for col in c.fetchall()]

        mesi_validi = [mese for mese in mesi_da_considerare if mese in colonne_db]
        mesi_mancanti = [mese for mese in mesi_da_considerare if mese not in colonne_db]

        if not mesi_validi:
            print("Nessun mese disponibile per questa stagione.")
            return []

        colonne_select = ", ".join([f'"{mese}"' for mese in mesi_validi])
        query = f'SELECT nome, stagione, {colonne_select} FROM ortaggi'
        c.execute(query)

        ortaggi_stagionali = []
        for row in c.fetchall():
            nome_ortaggio = row[0]
            stagione = row[1]
            prezzi = row[2:]

            if stagione.lower() == stagione_corrente:
                prezzi_valori = [p for p in prezzi if p is not None and p > 0]
                if prezzi_valori:
                    prezzo_medio = round(sum(prezzi_valori) / len(prezzi_valori), 2)
                    ortaggi_stagionali.append((nome_ortaggio, prezzo_medio))

        return ortaggi_stagionali

    except sqlite3.Error as e:
        print(f"Errore durante il recupero degli ortaggi: {e}")
        return []
    
    finally:
        conn.close()



def dashboard_page():
    dati_meteo = get_dati_meteo()

    if dati_meteo:
        emoji_meteo = get_weather_emoji(dati_meteo['temperatura'], dati_meteo['umidita'], dati_meteo['precipitazioni'])
        
        st.markdown(
            f"""
            <div style="width: 113.5%; display: flex; justify-content: space-between; background-color: #40693f; color: white; padding: 1rem; margin-left: -80px; box-sizing: border-box;margin-top: -112px;">
                <div style="font-size: 1.2rem; font-weight: bold;">Data: {dati_meteo['data']}</div>
                <div style="font-size: 1.2rem; font-weight: bold;">Temperatura: {dati_meteo['temperatura']}°</div>
                <div style="font-size: 1.2rem; font-weight: bold;">Meteo: {emoji_meteo}</div>
                <div style="font-size: 1.2rem; font-weight: bold;">Umidità: {dati_meteo['umidita']}%</div>
                <div style="font-size: 1.2rem; font-weight: bold;">Precipitazioni: {dati_meteo['precipitazioni']}mm</div>
            </div>
            """, unsafe_allow_html=True
        )

        today = pd.to_datetime('today').strftime('%Y-%m-%d')
        today_date = pd.to_datetime(today)
        stagione_corrente = get_stagione_corrente(today_date.month)
        ortaggi_stagionali = get_ortaggi_stagionali(stagione_corrente)

        st.markdown(f"<div style='text-align: center; margin-bottom: -2rem; margin-top: -4.5rem; color: #2f4f2f; font-weight: bold; font-size: 2.5rem;'>Ortaggi di stagione per la {stagione_corrente}:</div>", unsafe_allow_html=True)

        if ortaggi_stagionali:
            ortaggi_con_prezzo = ""
            for i, (ortaggio, prezzo) in enumerate(ortaggi_stagionali):
                if i == 0:
                    ortaggi_con_prezzo += f"<span style='margin-left: -0.5rem; font-weight: bold;'>{ortaggio}: {prezzo}€</span> "
                else:
                    ortaggi_con_prezzo += f"<span style='margin-left: 5rem;'>{ortaggio}: {prezzo}€</span> "

            st.markdown(f"""<div style='max-height: 400px; overflow-y: auto; font-size: 1.7rem; text-align: center; padding: 1rem; color: #2f4f2f; font-weight: bold; margin-top: -2rem;'>{ortaggi_con_prezzo}</div>""", unsafe_allow_html=True)

        st.markdown("""
            <style>
                .stButton > button {
                    margin-right: -2rem;
                    margin-left: 0.5rem;
                    padding: 0.6rem 1.2rem;
                    font-size: 1rem;
                    background-color: #40693f;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }
            </style>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 1], gap="small")

        with col1:
            if st.button("🌱 Semina", key="b1_semina"):
                st.session_state["b1_selezione_visibile"] = True
                st.session_state["b1_selezionato"] = False
                st.session_state.pop("blocco_1", None)
                st.session_state["b1_trapiantato"] = False

        with col2:
            if st.button("🌿 Trapianto", key="b1_trapianto"):
                st.session_state["b1_trapiantato"] = True
                ortaggio_b1 = st.session_state.get("blocco_1")
                if ortaggio_b1:
                    log_azione("Trapianto", ortaggio_b1)
                st.rerun()

        with col3:
            raccolto_b1 = st.button("🌾 Raccolto", key="b1_raccolto")

        with col4:
            st.markdown('</div>', unsafe_allow_html=True)

        with col5:
            if st.button("🌱 Semina", key="b2_semina"):
                st.session_state["b2_selezione_visibile"] = True
                st.session_state["b2_selezionato"] = False
                st.session_state.pop("blocco_2", None)
                st.session_state["b2_trapiantato"] = False

        with col6:
            if st.button("🌿 Trapianto", key="b2_trapianto"):
                st.session_state["b2_trapiantato"] = True
                ortaggio_b2 = st.session_state.get("blocco_2")
                if ortaggio_b2:
                    log_azione("Trapianto", ortaggio_b2)
                st.rerun()

        with col7:
            raccolto_b2 = st.button("🌾 Raccolto", key="b2_raccolto")

        if raccolto_b1:
            ortaggio_b1 = st.session_state.get("blocco_1")
            if ortaggio_b1:
                log_azione("Raccolto", ortaggio_b1)
            st.session_state.pop("blocco_1", None)
            st.session_state["b1_selezionato"] = False
            st.session_state["b1_trapiantato"] = False
            st.session_state["b1_selezione_visibile"] = False
            st.rerun()

        if raccolto_b2:
            ortaggio_b2 = st.session_state.get("blocco_2")
            if ortaggio_b2:
                log_azione("Raccolto", ortaggio_b2)
            st.session_state.pop("blocco_2", None)
            st.session_state["b2_selezionato"] = False
            st.session_state["b2_trapiantato"] = False
            st.session_state["b2_selezione_visibile"] = False
            st.rerun()

        col1, col2, col3 = st.columns(3, gap="medium")

        with col1:
            if st.session_state.get("b1_selezione_visibile", False) and not st.session_state.get("b1_selezionato", False):
                ortaggio_b1 = st.radio("Scegli l'ortaggio per la semina", [o[0] for o in ortaggi_stagionali], key="radio_b1_semina", index=None)
                if ortaggio_b1:
                    st.session_state["blocco_1"] = ortaggio_b1
                    st.session_state["b1_selezionato"] = True
                    st.session_state["b1_selezione_visibile"] = False
                    log_azione("Semina", ortaggio_b1)
                    st.rerun()

        with col2:
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            if st.session_state.get("b2_selezione_visibile", False) and not st.session_state.get("b2_selezionato", False):
                ortaggio_b2 = st.radio("Scegli l'ortaggio per la semina", [o[0] for o in ortaggi_stagionali], key="radio_b2_semina", index=None)
                if ortaggio_b2:
                    st.session_state["blocco_2"] = ortaggio_b2
                    st.session_state["b2_selezionato"] = True
                    st.session_state["b2_selezione_visibile"] = False
                    log_azione("Semina", ortaggio_b2)
                    st.rerun()

        EMOJI_ORTAGGI = {
            "Asparagi": "🌿", "Carciofi": "🌿", "Carote": "🥕", "Cavolfiori": "🥦",
            "Cavoli": "🥬", "Cipolle": "🧅", "Fagiolini": "🌱", "Finocchi": "🌿",
            "Lattuga": "🥬", "Patate": "🥔", "Pomodori": "🍅", "Radicchio": "🥬",
            "Sedano": "🌿", "Melanzane": "🍆", "Peperoni": "🫑", "Zucchine": "🥒"
        }

        ortaggio_b1 = st.session_state.get("blocco_1")
        ortaggio_b2 = st.session_state.get("blocco_2")

        emoji_b1 = EMOJI_ORTAGGI.get(ortaggio_b1, "") if ortaggio_b1 else ""
        emoji_b2 = EMOJI_ORTAGGI.get(ortaggio_b2, "") if ortaggio_b2 else ""

        trapiantato_b1 = st.session_state.get("b1_trapiantato", False)
        trapiantato_b2 = st.session_state.get("b2_trapiantato", False)

        bg_b1 = "#a3d9a5" if ortaggio_b1 else "#a67c52"
        bg_b2 = "#a3d9a5" if ortaggio_b2 else "#a67c52"

        content_b1 = (
            f"<div style='font-size: 1.5rem; font-weight: bold; margin-bottom: 4.3rem;'>Trapiantato</div><div style='font-size: 1.2rem; font-weight: bold; margin-bottom: 5.8em;'>{emoji_b1} {ortaggio_b1}</div>"
            if ortaggio_b1 and trapiantato_b1 else
            f"<div style='font-size: 1.2rem; font-weight: bold;'>{emoji_b1} {ortaggio_b1}</div>" if ortaggio_b1 else "<div></div>"
        )

        content_b2 = (
            f"<div style='font-size: 1.5rem; font-weight: bold; margin-bottom: 4.3rem;'>Trapiantato</div><div style='font-size: 1.2rem; font-weight: bold; margin-bottom: 5.8em;'>{emoji_b2} {ortaggio_b2}</div>"
            if ortaggio_b2 and trapiantato_b2 else
            f"<div style='font-size: 1.2rem; font-weight: bold;'>{emoji_b2} {ortaggio_b2}</div>" if ortaggio_b2 else "<div></div>"
        )

        st.markdown(f"""
            <div style='display: flex; justify-content: center; gap: 4rem; margin-top: 2rem;'>
                <div style='width: 300px; height: 250px; border: 2px solid #2f4f2f; border-radius: 10px; padding: 1rem; background-color: {bg_b1}; display: flex; flex-direction: column; justify-content: center; text-align: center;'>
                    {content_b1}
                </div>
                <div style='width: 300px; height: 250px; border: 2px solid #2f4f2f; border-radius: 10px; margin-left: 22rem; margin-right: 1rem; padding: 1rem; background-color: {bg_b2}; display: flex; flex-direction: column; justify-content: center; text-align: center;'>
                    {content_b2}
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <style>
                div.stDownloadButton > button {
                    background-color: #40693f !important;
                    color: white !important;
                    margin-left: 33.5rem !important;
                    padding: 0.6rem 1.2rem;
                    font-size: 1rem;
                    border: none;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        excel_file = leggi_contenuto_database()
        if excel_file:
            st.download_button(
                label="📄 Record",
                data=excel_file,
                file_name="report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_record"
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""<hr style="border: none; margin-left: -5rem; margin-right: -5rem; margin-top: -0.5rem; height: 2px; background-color: #2f4f2f;">""", unsafe_allow_html=True)

        st.markdown(f"<div style='text-align: center; margin-top: -1rem; color: #2f4f2f; font-weight: bold; font-size: 2.3rem;'>Dashboard meteo:</div>", unsafe_allow_html=True)
        
        if "mese_selezionato" not in st.session_state:
            st.session_state.mese_selezionato = None
        if "mese_selezionato_secondo" not in st.session_state:
            st.session_state.mese_selezionato_secondo = None
        if "show_mesi" not in st.session_state:
            st.session_state.show_mesi = False
        if "show_mesi_secondo" not in st.session_state:
            st.session_state.show_mesi_secondo = False

        col1, col2, col3 = st.columns([1, 0.5, 1], gap="large") 

        with col2: 
            if st.button("📅 Seleziona mese", key="seleziona_mese"):
                st.session_state.show_mesi = True

        data_min, data_max = get_data_min_max_da_gennaio_2024()
        data_corrente = datetime.strptime(data_min, "%Y-%m")
        data_fine = datetime.strptime(data_max, "%Y-%m")

        mesi_opzioni = []
        while data_corrente <= data_fine:
            mesi_opzioni.append(data_corrente.strftime("%m %Y"))
            if data_corrente.month == 12:
                data_corrente = data_corrente.replace(year=data_corrente.year + 1, month=1)
            else:
                data_corrente = data_corrente.replace(month=data_corrente.month + 1)

        if st.session_state.show_mesi:
            num_col = 10
            righe = (len(mesi_opzioni) + num_col - 1) // num_col
            for i in range(righe):
                cols = st.columns(num_col)
                for j in range(num_col):
                    idx = i * num_col + j
                    if idx < len(mesi_opzioni):
                        mese = mesi_opzioni[idx]

                        if cols[j].button(mese, key=f"mese_{mese}"):
                            st.session_state.mese_selezionato = mese
                            st.session_state.show_mesi = False
                            st.rerun()

        if st.session_state.mese_selezionato:
            mostra_grafico_temperatura_raw(st.session_state.mese_selezionato)
            
        st.markdown("""<hr style="border: none; margin-left: -5rem; margin-right: -5rem; margin-top: 1rem; height: 2px; background-color: #2f4f2f;">""", unsafe_allow_html=True)

        st.markdown(f"<div style='text-align: center; margin-top: -1rem; color: #2f4f2f; font-weight: bold; font-size: 2.3rem;'>Dashboard ortaggi:</div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 0.5, 1], gap="large") 

        with col2:  
            if st.button("📅 Seleziona mese", key="seleziona_mese_secondo"):
                st.session_state.show_mesi_secondo = True

        st.markdown("""<hr style="border: none; margin-left: -5rem; margin-right: -5rem; margin-top: 1rem; height: 2px; background-color: #2f4f2f;">""", unsafe_allow_html=True)

        if st.session_state.get("show_mesi_secondo", False):
            mesi_disponibili = get_tutte_date_da_mese_corrente() 

            if mesi_disponibili:
                mesi_opzioni = mesi_disponibili

                num_col = 10
                righe = (len(mesi_opzioni) + num_col - 1) // num_col

                for i in range(righe):
                    cols = st.columns(num_col)
                    for j in range(num_col):
                        idx = i * num_col + j
                        if idx < len(mesi_opzioni):
                            mese = mesi_opzioni[idx]

                            if cols[j].button(mese, key=f"mese_secondo_{mese}"):
                                st.session_state.mese_selezionato_secondo = mese  
                                st.session_state.show_mesi_secondo = False 
                                st.rerun()  
            else:
                st.write("Non sono disponibili mesi nel database.")
        
        if st.session_state.mese_selezionato_secondo:

            df = esporta_prezzi_per_mese(st.session_state.mese_selezionato_secondo)

            mese_formattato = datetime.strptime(st.session_state.mese_selezionato_secondo, "%m %Y").strftime("%Y-%m")

            crea_grafico_prezzi(df, mese_formattato)
            
            st.markdown("""<hr style="border: none; margin-left: -5rem; margin-right: -5rem; margin-top: 1rem; height: 2px; background-color: #2f4f2f;">""", unsafe_allow_html=True)

def crea_grafico_prezzi(df, mese_formattato):
    if df.empty:
        st.write("Non ci sono dati disponibili per questo mese.")
        return
    
    if mese_formattato not in df.columns:
        st.write(f"Non ci sono dati per il mese {mese_formattato}.")
        return

    fig_bar = go.Figure(data=[
        go.Bar(
            x=df['Nome'], 
            y=df[mese_formattato], 
            marker=dict(color='#2f4f2f')
        )
    ])
    
    fig_bar.update_layout(
        title=f"Prezzi degli Ortaggi di Stagione - Mese: {mese_formattato}",
        title_font=dict(size=20, color='#2f4f2f', family='Arial Bold'),
        title_x=0.3,
        xaxis=dict(
            title="🌽 Ortaggio",
            title_font=dict(size=18, color='#2f4f2f', family='Arial Bold'),
            tickfont=dict(size=14, color='#2f4f2f', family='Arial Bold'),
            title_standoff=25
        ),
        yaxis=dict(
            title="💶 Prezzo (€)",
            title_font=dict(size=18, color='#2f4f2f', family='Arial Bold'),
            tickfont=dict(size=14, color='#2f4f2f', family='Arial Bold')
        ),
        plot_bgcolor='#819c5c', 
        paper_bgcolor='#819c5c', 
        margin=dict(l=40, r=40, t=60, b=40),
        bargap=0.5,
        shapes=[  
            dict(
                type='rect',
                x0=0, x1=1, y0=0, y1=1, 
                xref='paper', yref='paper', 
                line=dict(
                    color='black',  
                    width=2 
                ),
                fillcolor='rgba(0,0,0,0)' 
            )
        ]
    )
    
    fig_pie = go.Figure(data=[
        go.Pie(
            labels=df['Nome'], 
            values=df['Produzione_2024_mgl'], 
            marker=dict(colors=['#4db8b1', '#f28f8f', '#3b8b79', '#a67c52']),  
            hole=0, 
            name="Produzione",
            textinfo="percent", 
            textfont=dict(size=14, color='#2f4f2f', family='Arial', weight="bold")  
        )
    ])
    
    fig_pie.update_layout(
        title=f"Produzione degli Ortaggi di Stagione - Mese: {mese_formattato}",
        title_font=dict(size=20, color='#2f4f2f', family='Arial Bold'), 
        title_x=0.3,
        plot_bgcolor='#819c5c', 
        paper_bgcolor='#819c5c',  
        legend=dict(
            x=0.75, 
            y=0.75,
            traceorder="normal",  
            font=dict(
                family="Arial",
                size=18,
                color="#2f4f2f",
                weight="bold"
            )
        ),
        annotations=[
            dict(
                text="Legenda",
                x=0.84,
                y=0.9, 
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(
                    size=24,
                    color="#2f4f2f",
                    family="Arial Bold"
                ),
                align="left"
            )
        ]
    )

    st.plotly_chart(fig_bar)
    
    st.markdown("""<hr style="border: none; margin-left: -5rem; margin-right: -5rem; margin-top: 1rem; height: 2px; background-color: #2f4f2f;">""", unsafe_allow_html=True)
    
    st.plotly_chart(fig_pie)
    
    ortaggio_consigliato(df, mese_formattato)


def ortaggio_consigliato(df, mese_formattato):
    if df.empty:
        st.write("Non ci sono dati disponibili per questo mese.")
        return
    
    ortaggio_vendita_max = df.loc[df[mese_formattato].idxmax()]
    ortaggio_produzione_max = df.loc[df['Produzione_2024_mgl'].idxmax()]

    nome_ortaggio_vendita_max = ortaggio_vendita_max['Nome']
    prezzo_ortaggio_vendita_max = ortaggio_vendita_max[mese_formattato]
    produzione_ortaggio_vendita_max = ortaggio_vendita_max['Produzione_2024_mgl']
    guadagno_vendita_max = prezzo_ortaggio_vendita_max * produzione_ortaggio_vendita_max  
    
    nome_ortaggio_produzione_max = ortaggio_produzione_max['Nome']
    produzione_ortaggio_produzione_max = ortaggio_produzione_max['Produzione_2024_mgl']
    prezzo_ortaggio_produzione_max = ortaggio_produzione_max[mese_formattato]
    guadagno_produzione_max = prezzo_ortaggio_produzione_max * produzione_ortaggio_produzione_max 
    
    st.markdown("""<hr style="border: none; margin-left: -5rem; margin-right: -5rem; margin-top: 1rem; height: 2px; background-color: #2f4f2f;">""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"<div style='margin-left: 3rem; margin-top: -1rem; color: #2f4f2f; font-weight: bold; font-size: 1.6rem;'>Ortaggio consigliato per maggiore vendita:</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-left: 3rem; margin-top: 0rem; color: #2f4f2f; font-weight: bold; font-size: 1.3rem;'>- Nome: {nome_ortaggio_vendita_max}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-left: 3rem; margin-top: 0rem; color: #2f4f2f; font-weight: bold; font-size: 1.3rem;'>- Prezzo di vendita: {prezzo_ortaggio_vendita_max:.2f} € per kg</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-left: 3rem; margin-top: 0rem; color: #2f4f2f; font-weight: bold; font-size: 1.3rem;'>- Produzione nel 2024: {produzione_ortaggio_vendita_max} mgl</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-left: 3rem; margin-top: 0rem; color: #2f4f2f; font-weight: bold; font-size: 1.3rem;'>- Guadagno totale: {guadagno_vendita_max:.2f} €</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div style='margin-left: 3rem; margin-top: -1rem; color: #2f4f2f; font-weight: bold; font-size: 1.6rem;'>Ortaggio consigliato per maggiore produzione:</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-left: 3rem; margin-top: 0rem; color: #2f4f2f; font-weight: bold; font-size: 1.3rem;'>- Nome: {nome_ortaggio_produzione_max}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-left: 3rem; margin-top: 0rem; color: #2f4f2f; font-weight: bold; font-size: 1.3rem;'>- Prezzo di vendita: {prezzo_ortaggio_produzione_max:.2f} € per kg</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-left: 3rem; margin-top: 0rem; color: #2f4f2f; font-weight: bold; font-size: 1.3rem;'>- Produzione nel 2024: {produzione_ortaggio_produzione_max} mgl</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-left: 3rem; margin-top: 0rem; color: #2f4f2f; font-weight: bold; font-size: 1.3rem;'>- Guadagno totale: {guadagno_produzione_max:.2f} €</div>", unsafe_allow_html=True)
        
    st.markdown("""<hr style="border: none; margin-left: -5rem; margin-right: -5rem; margin-top: 1rem; height: 2px; background-color: #2f4f2f;">""", unsafe_allow_html=True)

    fig = go.Figure(data=[
        go.Bar(
            x=[nome_ortaggio_vendita_max, nome_ortaggio_produzione_max],
            y=[guadagno_vendita_max, guadagno_produzione_max],
            marker=dict(color='#2f4f2f')
        )
    ])
    
    fig.update_layout(
        title=f"Confronto tra Guadagno per Vendita e Produzione - Mese: {mese_formattato}",
        title_font=dict(size=20, color='#2f4f2f', family='Arial Bold'),
        title_x=0.25,
        xaxis=dict(
            title="🍅 Ortaggio",
            title_font=dict(size=18, color='#2f4f2f', family='Arial Bold'),
            tickfont=dict(size=14, color='#2f4f2f', family='Arial Bold'),
            title_standoff=25
        ),
        yaxis=dict(
            title="💶 Guadagno (€)",
            title_font=dict(size=18, color='#2f4f2f', family='Arial Bold'),
            tickfont=dict(size=14, color='#2f4f2f', family='Arial Bold')
        ),
        plot_bgcolor='#819c5c',  
        paper_bgcolor='#819c5c',  
        margin=dict(l=40, r=40, t=60, b=40), 
        bargap=0.7,
        shapes=[  
            dict(
                type='rect', 
                x0=0, x1=1, y0=0, y1=1,
                xref='paper', yref='paper', 
                line=dict(
                    color='black',  
                    width=2  
                ),
                fillcolor='rgba(0,0,0,0)'  
            )
        ]
    )

    st.plotly_chart(fig)


def esporta_prezzi_per_mese(mese_input):
    stagioni = {
        "Inverno": [1, 2, 12],
        "Primavera": [3, 4, 5],
        "Estate": [6, 7, 8],
        "Autunno": [9, 10, 11]
    }

    mese_input = mese_input.strip()
    mese_numero, anno = mese_input.split()
    mese_formattato = f"{anno}-{mese_numero.zfill(2)}"
    mese_int = int(mese_numero)

    stagione_corrente = None
    for stagione, mesi in stagioni.items():
        if mese_int in mesi:
            stagione_corrente = stagione
            break

    if not stagione_corrente:
        print("Mese non valido per la determinazione della stagione.")
        return None

    db_path = os.path.join("database", "ortaggi.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(ortaggi)")
        colonne = [col[1] for col in cursor.fetchall()]

        if mese_formattato not in colonne:
            print(f"Il mese {mese_formattato} non è presente tra le colonne.")
            return None

        query = f'''
            SELECT nome, valuta, "{mese_formattato}", stagione, "produzione_2024"
            FROM ortaggi
            WHERE stagione = ?
        '''
        cursor.execute(query, (stagione_corrente,))
        righe = cursor.fetchall()

        if not righe:
            print(f"Nessun ortaggio trovato per la stagione {stagione_corrente}.")
            return None

        df = pd.DataFrame(righe, columns=["Nome", "Valuta", mese_formattato, "Stagione", "Produzione_2024_mgl"])

        return df

    except Exception as e:
        print(f"Errore durante l'estrazione: {e}")
        return None

    finally:
        conn.close()



def get_weather_emoji(temperatura, umidita, precipitazioni):
    if temperatura <= 0:
        emoji_temp = "❄️"  
    elif temperatura <= 15:
        emoji_temp = "🌦️"  
    elif temperatura <= 25:
        emoji_temp = "🌤️" 
    else:
        emoji_temp = "☀️"

    if umidita > 80:
        emoji_umidita = "💧" 
    else:
        emoji_umidita = "💨" 

    if precipitazioni > 5:  
        emoji_precipitazioni = "🌧️"
    elif precipitazioni > 0: 
        emoji_precipitazioni = "🌦️"
    else: 
        emoji_precipitazioni = "🌤️"

    return f"{emoji_temp} {emoji_umidita} {emoji_precipitazioni}"

def log_azione(azione, ortaggio):
    oggi = pd.to_datetime("today").strftime("%Y-%m-%d")

    if not os.path.exists('database'):
        os.makedirs('database')

    db_path = os.path.join('database', 'report.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS report (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        azione TEXT,
        ortaggio TEXT
    )
    ''')

    cursor.execute('''
    INSERT INTO report (data, azione, ortaggio)
    VALUES (?, ?, ?)
    ''', (oggi, azione, ortaggio))

    conn.commit()
    conn.close()

def leggi_contenuto_database():
    if not os.path.exists('database'):
        os.makedirs('database')

    db_path = os.path.join('database', 'report.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS report (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Data TEXT,
            Azione TEXT,
            Ortaggio TEXT
        )
    ''')
    conn.commit()

    cursor.execute("SELECT * FROM report")
    risultati = cursor.fetchall()

    if risultati:
        columns = ['ID', 'Data', 'Azione', 'Ortaggio']
        df = pd.DataFrame(risultati, columns=columns)

        excel_file = io.BytesIO()
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        excel_file.seek(0)

        return excel_file
    else:
        print("Nessun record trovato.")
        return None

def get_data_min_max_da_gennaio_2024():
    try:
        db_path = os.path.join('database', 'meteo.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                MIN(strftime('%Y-%m', data)), 
                MAX(strftime('%Y-%m', data))
            FROM meteo_fittizio
            WHERE data >= '2024-01-01'
        """)
        row = cursor.fetchone()
        conn.close()

        data_min = row[0] if row[0] else "2024-01"
        data_max = row[1] if row[1] else datetime.now().strftime("%Y-%m")

        return data_min, data_max

    except Exception as e:
        st.error(f"Errore durante il recupero delle date: {e}")
        return "2024-01", datetime.now().strftime("%Y-%m")


def get_tutte_date_da_mese_corrente():
    try:
        db_path = os.path.join('database', 'ortaggi.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name
            FROM pragma_table_info('ortaggi') 
            WHERE name LIKE '____-__'
        """)
        mesi_colonne = [col[0] for col in cursor.fetchall()]

        mesi_convertiti = [datetime.strptime(mese, "%Y-%m").strftime("%m %Y") for mese in mesi_colonne]

        conn.close()

        return mesi_convertiti

    except Exception as e:
        print(f"Errore: {e}")
        return []
    
def mostra_grafico_temperatura_raw(mese_selezionato):
    db_file = os.path.join("database", "meteo.db")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    try:
        
        mese_formattato = mese_selezionato.strip().split(" ")
        mese_formattato = f"{mese_formattato[1]}-{mese_formattato[0]}"

        query = """
        SELECT * FROM meteo_fittizio
        WHERE strftime('%Y-%m', Data) = ?
        ORDER BY Data
        """
        c.execute(query, (mese_formattato,))
        rows = c.fetchall()
        
        if not rows:
            st.warning("Nessun dato trovato per il mese selezionato.")
            return

        dati = []
        for row in rows:
            data = row[0] 
            temperatura = float(str(row[1]).replace("°C", ""))
            dati.append((data, temperatura))

        df = pd.DataFrame(dati, columns=["Data", "Temperatura"])
        df["Data"] = pd.to_datetime(df["Data"]) 

        df["Data"] = df["Data"].dt.strftime('%d') 

        giorno_piu_caldo = df.loc[df['Temperatura'].idxmax()]
        giorno_piu_freddo = df.loc[df['Temperatura'].idxmin()]

        st.markdown(f"""
            <div style='text-align: center; color: #2f4f2f; font-weight: bold; font-size: 1.8rem;'>
                📈 Giorno più caldo: {giorno_piu_caldo['Data']} con {giorno_piu_caldo['Temperatura']}°C
            </div>
            <div style='text-align: center; color: #2f4f2f; font-weight: bold; font-size: 1.8rem;'>
                📉 Giorno più freddo: {giorno_piu_freddo['Data']} con {giorno_piu_freddo['Temperatura']}°C
            </div>
        """, unsafe_allow_html=True) 

        fig = px.line(
            df,
            x="Data",
            y="Temperatura",
            title=f"Andamento della Temperatura - {mese_formattato}",
            labels={"Data": "🗓️ Giorno", "Temperatura": "🌡️ Temperatura (°C)"},
            markers=True
        )
        
        fig.update_traces(line=dict(color="black"))

        fig.update_layout(
            title={
                'text': f"Andamento della Temperatura - {mese_formattato}",
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    'size': 24,
                    'color': '#2f4f2f',
                    'family': 'Arial Black'
                }
            },
            xaxis=dict(
                title_font=dict(size=18, color='#2f4f2f', family='Arial Bold'),
                tickfont=dict(size=14, color='#2f4f2f', family='Arial Bold'),
                tickmode='array',
                tickvals=df['Data'],
                title_standoff=25
            ),
            yaxis=dict(
                title_font=dict(size=18, color='#2f4f2f', family='Arial Bold'),
                tickfont=dict(size=14, color='#2f4f2f', family='Arial Bold')
            ),
            plot_bgcolor='#819c5c',
            paper_bgcolor='#819c5c',
            shapes=[  
                dict(
                    type='rect', 
                    x0=0, x1=1, y0=0, y1=1, 
                    xref='paper', yref='paper', 
                    line=dict(
                        color='black', 
                        width=2  
                    ),
                    fillcolor='rgba(0,0,0,0)'  
                )
            ]
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Errore durante il caricamento dei dati: {e}")
        print(f"Errore: {e}")


if "autenticato" in st.session_state and st.session_state.autenticato:
    dashboard_page()
else:
    login_page()
