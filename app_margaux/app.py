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
# Cela réduit les marges énormes de Streamlit et grossit les boutons
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
        if "Question" in df.columns and "Reponse" in df.columns:
            return df.to_dict('records')
        return None
    except:
        return None

# --- 3. Menu (Caché dans la sidebar pour ne pas gêner) ---
with st.sidebar:
    st.header("📂 Mes Decks")
    uploaded_file = st.file_uploader("Nouveau fichier", type=["xlsx"])
    if uploaded_file:
        save_path = os.path.join(DATA_FOLDER, uploaded_file.name)
        with open(save_path, "wb") as f: f.write(uploaded_file.getbuffer())
        st.success("Ajouté !")
        st.rerun()

    st.markdown("---")
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.xlsx')]
    
    if files:
        selected_file = st.selectbox("Choisir un deck", files)
        if st.button("🚀 LANCER", use_container_width=True):
            data = load_excel(os.path.join(DATA_FOLDER, selected_file))
            if data:
                start_game(data, selected_file)
                st.rerun()
        
        st.markdown("---")
        if st.button("🗑️ Supprimer le deck", use_container_width=True):
            os.remove(os.path.join(DATA_FOLDER, selected_file))
            if st.session_state.current_deck_name == selected_file:
                st.session_state.game_active = False
            st.rerun()

# --- 4. Interface Principale (Le Jeu) ---

if st.session_state.game_active and st.session_state.flashcards:
    
    # Barre de progression minimaliste en haut
    total = len(st.session_state.flashcards)
    current = st.session_state.index + 1
    progress = st.session_state.index / total
    st.progress(progress)
    
    # Petit indicateur discret
    st.caption(f"📖 {st.session_state.current_deck_name} | Carte {current}/{total}")

    # LOGIQUE DE FIN DE JEU
    if st.session_state.index >= total:
        st.markdown("## 🏁 Terminé !")
        
        if len(st.session_state.retry_deck) > 0:
            st.warning(f"{len(st.session_state.retry_deck)} erreurs à revoir.")
            # Espace vide pour aérer
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

    # AFFICHAGE DE LA CARTE
    else:
        card = st.session_state.flashcards[st.session_state.index]

        # Bloc Question (Gros titre pour lecture facile)
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
            <p style="color: #555; font-size: 14px; margin: 0;">QUESTION</p>
            <h2 style="color: #000; margin: 10px 0;">{card['Question']}</h2>
        </div>
        """, unsafe_allow_html=True)

        # Si la réponse est cachée
        if not st.session_state.show_answer:
            # Gros bouton primaire
            if st.button("👀 VOIR LA RÉPONSE", type="primary", use_container_width=True):
                st.session_state.show_answer = True
                st.rerun()
        
        # Si la réponse est visible
        else:
            # Bloc Réponse (Style différent)
            st.markdown(f"""
            <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; border: 2px solid #4CAF50;">
                <p style="color: #2e7d32; font-size: 14px; margin: 0;">RÉPONSE</p>
                <h2 style="color: #1b5e20; margin: 10px 0;">{card['Reponse']}</h2>
            </div>
            """, unsafe_allow_html=True)

            # Boutons de vote côte à côte
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
    # Écran d'accueil simple
    st.title("📱 Flashcards")
    st.info("👈 Ouvre le menu en haut à gauche pour choisir un deck.")