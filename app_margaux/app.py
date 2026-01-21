import streamlit as st
import pandas as pd
import os

# --- Configuration de la page (Mobile friendly) ---
st.set_page_config(page_title="Flashcards Mobile", page_icon="📱", layout="centered")
DATA_FOLDER = "mes_decks"

# Création du dossier si inexistant
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# --- CSS PERSONNALISÉ POUR MOBILE ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .stButton>button {
            width: 100%;
            height: 3em;
            font-size: 20px;
            font-weight: bold;
            border-radius: 12px;
        }
        div[data-testid="stVerticalBlock"] > div {
            gap: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- 1. Gestion de la mémoire (State) ---
if 'flashcards' not in st.session_state: st.session_state.flashcards = []
if 'retry_deck' not in st.session_state: st.session_state.retry_deck = []
if 'index' not in st.session_state: st.session_state.index = 0
if 'show_answer' not in st.session_state: st.session_state.show_answer = False
if 'game_active' not in st.session_state: st.session_state.game_active = False
if 'current_deck_name' not in st.session_state: st.session_state.current_deck_name = ""

# --- 2. Fonctions ---
def start_game(data_list, deck_name):
    st.session_state.flashcards = data_list
    st.session_state.retry_deck = []
    st.session_state.index = 0
    st.session_state.show_answer = False
    st.session_state.game_active = True
    st.session_state.current_deck_name = deck_name

def load_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        # On vérifie juste que les colonnes existent, peu importe l'ordre
        if "Question" in df.columns and "Reponse" in df.columns:
            return df.to_dict('records')
        return None
    except:
        return None

# --- 3. Barre Latérale (Menu & Réglages) ---
with st.sidebar:
    st.header("⚙️ Réglages")
    
    # --- NOUVEAUTÉ : LE BOUTON INVERSER ---
    reverse_mode = st.toggle("🔄 Inverser (Réponse → Question)")
    
    st.markdown("---")
    st.header("📂 Mes Decks")
    
    # 1. Charger un nouveau fichier (Temporaire)
    uploaded_file = st.file_uploader("Ajouter un fichier", type=["xlsx"])
    if uploaded_file:
        save_path = os.path.join(DATA_FOLDER, uploaded_file.name)
        with open(save_path, "wb") as f: f.write(uploaded_file.getbuffer())
        st.success("Ajouté !")
        st.rerun()

    # 2. Lister les fichiers (GitHub + Uploadés)
    files = []
    if os.path.exists(DATA_FOLDER):
        files += [f for f in os.listdir(DATA_FOLDER) if f.endswith('.xlsx')]
    files += [f for f in os.listdir('.') if f.endswith('.xlsx')]
    files = list(set(files)) # Enlever les doublons
    
    if files:
        selected_file = st.selectbox("Choisir un deck", files)
        
        col_go, col_del = st.columns(2)
        with col_go:
            if st.button("🚀 LANCER", type="primary"):
                full_path = selected_file
                if selected_file in os.listdir(DATA_FOLDER):
                    full_path = os.path.join(DATA_FOLDER, selected_file)
                
                data = load_excel(full_path)
                if data:
                    start_game(data, selected_file)
                    st.rerun()
        with col_del:
            if st.button("🗑️"):
                # On essaie de supprimer du dossier mes_decks
                try:
                    os.remove(os.path.join(DATA_FOLDER, selected_file))
                    if st.session_state.current_deck_name == selected_file:
                        st.session_state.game_active = False
                    st.rerun()
                except:
                    st.error("Impossible de supprimer (fichier GitHub ?)")

# --- 4. Interface Principale (Le Jeu) ---

if st.session_state.game_active and st.session_state.flashcards:
    
    # --- LOGIQUE D'INVERSION ---
    card = st.session_state.flashcards[st.session_state.index]
    
    if reverse_mode:
        # Mode inversé : On montre la Réponse, on cache la Question
        front_text = card['Reponse']
        back_text = card['Question']
        front_label = "INDICE / DÉFINITION"
        back_label = "MOT À TROUVER"
    else:
        # Mode normal
        front_text = card['Question']
        back_text = card['Reponse']
        front_label = "QUESTION"
        back_label = "RÉPONSE"

    # Barre de progression
    total = len(st.session_state.flashcards)
    current = st.session_state.index + 1
    st.progress(st.session_state.index / total)
    st.caption(f"📖 {st.session_state.current_deck_name} | {current}/{total}")

    # FIN DE JEU
    if st.session_state.index >= total:
        st.markdown("## 🏁 Terminé !")
        if len(st.session_state.retry_deck) > 0:
            st.warning(f"{len(st.session_state.retry_deck)} erreurs à revoir.")
            st.write("") 
            if st.button("🔄 REVOIR MES ERREURS", type="primary"):
                st.session_state.flashcards = st.session_state.retry_deck
                st.session_state.retry_deck = []
                st.session_state.index = 0
                st.session_state.show_answer = False
                st.rerun()
        else:
            st.success("🎉 100% Maîtrisé !")
            st.balloons()
            if st.button("🏠 Menu Principal"):
                st.session_state.game_active = False
                st.rerun()

    # AFFICHAGE CARTE
    else:
        # FACE A (Visible)
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
            <p style="color: #555; font-size: 14px; margin: 0; text-transform: uppercase;">{front_label}</p>
            <h2 style="color: #000; margin: 10px 0;">{front_text}</h2>
        </div>
        """, unsafe_allow_html=True)

        # FACE B (Cachée ou Révélée)
        if not st.session_state.show_answer:
            if st.button("👀 RETOURNER", type="primary", use_container_width=True):
                st.session_state.show_answer = True
                st.rerun()
        
        else:
            st.markdown(f"""
            <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; border: 2px solid #4CAF50;">
                <p style="color: #2e7d32; font-size: 14px; margin: 0; text-transform: uppercase;">{back_label}</p>
                <h2 style="color: #1b5e20; margin: 10px 0;">{back_text}</h2>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("❌ À revoir", use_container_width=True):
                    st.session_state.retry_deck.append(card)
                    st.session_state.index += 1
                    st.session_state.show_answer = False
                    st.rerun()
            with col2:
                if st.button("✅ Connu", use_container_width=True):
                    st.session_state.index += 1
                    st.session_state.show_answer = False
                    st.rerun()

else:
    st.title("📱 Flashcards")
    st.info("👈 Ouvre le menu pour choisir un deck.")
