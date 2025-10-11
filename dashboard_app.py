import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --- CONFIGURATION GÉNÉRALE ---
st.set_page_config(
    page_title="Tableau de bord - Décès INSEE 2025",
    page_icon="🕊️",
    layout="wide",
)

# --- TITRE ---
st.title("🕊️ Tableau de bord interactif — Décès en France (INSEE 2025)")
st.markdown(
    """
    Ce tableau de bord présente une analyse des décès enregistrés en France pour l’année 2025, 
    réalisée à partir des données **INSEE**.
    Vous pouvez explorer ici les cartes, les statistiques par département et des indicateurs de longévité.
    """
)

# --- SIDEBAR ---
st.sidebar.header("⚙️ Paramètres")
view = st.sidebar.selectbox(
    "Choisissez une vue :",
    [
        "Résumé global",
        "Carte : Nombre de décès",
        "Carte : Âge moyen au décès",
        "Carte : Cercles proportionnels",
        "Statistiques descriptives"
    ]
)

# --- DONNÉES ---
@st.cache_data
def charger_donnees(fichier):
    df = pd.read_csv(fichier)
    return df

# Ton fichier CSV propre (créé via ton script principal)
df = charger_donnees("recensement_population/data/deces-2025-m08.csv")

# --- CONTENU PRINCIPAL ---
if view == "Résumé global":
    st.subheader("📊 Statistiques générales")
    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre total de décès", f"{len(df):,}".replace(",", " "))
    col2.metric("Âge moyen au décès", f"{df['age_deces'].mean():.1f} ans")
    col3.metric("Âge médian", f"{df['age_deces'].median():.1f} ans")

    st.divider()
    st.image("recensement_population/cartes/deces_08-2025.png", caption="Répartition des décès en France")

    # Histogramme
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(df["age_deces"], bins=40, kde=True, color="#ff6666", ax=ax)
    plt.title("Distribution de l’âge au décès (France, 2025)")
    plt.xlabel("Âge au décès")
    plt.ylabel("Nombre de décès")
    st.pyplot(fig)

# --- FOOTER ---
st.markdown("---")
st.caption("© 2025 - Données : INSEE | Application : Alex LAMIZANA | Réalisée avec Streamlit & GeoPandas")
