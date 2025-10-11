import re
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
from logger import Logger
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import seaborn as sns
LOG = Logger("recensement_pop.log")


#####################################################################
def lire_fichier_deces(fichier):
    
    LOG.info(f"Lecture du fichier deces: {fichier}")
    lignes = []
    try:
        with open(fichier, "r", encoding="utf-8", errors="ignore") as f:
            for ligne in f:
                # Découpage avec une expression régulière
                match = re.match(
                    r"^([A-ZÉÈÀÙÂÊÎÔÛÄËÏÖÜÇ' \-\*]+)/(?:\s*)(1|2)(\d{8})(\d{5})([A-Z \-']+)(\d{8})(\d{5})",
                    ligne
                )
                if match:
                    lignes.append(match.groups())
        
        colonnes = [
            "nom",
            "sexe",
            "date_naissance",
            "lieu_naissance_code",
            "lieu_naissance_nom",
            "date_deces",
            "lieu_deces_code",
        ]
        df = pd.DataFrame(lignes, columns=colonnes)
        
    except Exception as e:
        LOG.error(f"Lors de l'ouverture du fichier: {e}")
        raise
    
    return df


# ---------------------------------------------------------------- #
def add_age_to_death(df: pd.DataFrame) -> pd.DataFrame:
    
    try:
        # Conversion des dates
        df["date_naissance"] = pd.to_datetime(df["date_naissance"], format="%Y%m%d", errors="coerce")
        df["date_deces"] = pd.to_datetime(df["date_deces"], format="%Y%m%d", errors="coerce")

        # Calcul de l’âge au décès
        df["age_deces"] = ((df["date_deces"] - df["date_naissance"]).dt.days / 365.25)
        
        # Supprime les valeurs aberrantes :
        df.loc[~df["age_deces"].between(0, 130), "age_deces"] = pd.NA
        
        # Arrondi et converti :
        df["age_deces"] = df["age_deces"].round().astype("Int64")
        
    except Exception as e:
        LOG.error(f"Lors de la création du DataFrame: {e}")
        raise
    
    LOG.info(f"Ajout de l'age du décès au DataFrame réussi")
    return df


# ---------------------------------------------------------------- #
def recup_is_null(df: pd.DataFrame):
    
    # Détection des lignes contenant au moins une valeur manquante
    df_null = df[df.isnull().any(axis=1)]

    # Sauvegarde dans un fichier CSV :
    df_null.to_csv("deces-2025-m08_nulls.csv", index=False, encoding="utf-8")

    print(f"✅ {len(df_null)} lignes contenant au moins une valeur nulle ont été extraites dans 'deces-2025-m08_nulls.csv'")

    
# ---------------------------------------------------------------- #
def carte_deces(df, output_file="carte_deces_france_stylisee.png"):

    LOG.info("Génération de la carte des décès avec noms des départements...")
    try:


        # Charger la carte de la France (départements)
        france = gpd.read_file("https://france-geojson.gregoiredavid.fr/repo/departements.geojson")

        # Extraire le département à partir du code INSEE
        df["departement"] = df["lieu_deces_code"].str[:2]
        deces_par_dep = df.groupby("departement").size().reset_index(name="nb_deces")
        deces_par_dep.rename(columns={"departement": "code"}, inplace=True)

        # Fusionner carte + données
        france_deces = france.merge(deces_par_dep, on="code", how="left")
        france_deces["nb_deces"] = france_deces["nb_deces"].fillna(0)

        # Palette de couleurs explicite
        cmap = "Reds"

        # Création de la figure
        fig, ax = plt.subplots(figsize=(12, 12), facecolor="#f8f9fa")

        # Tracer la carte
        france_deces.plot(
            column="nb_deces",
            cmap=cmap,
            linewidth=0.6,
            edgecolor="#333333",
            legend=True,
            legend_kwds={
                "label": "Nombre de décès (Août 2025)",
                "orientation": "horizontal",
                "pad": 0.02,
                "shrink": 0.6
            },
            ax=ax
        )

        # ✅ Ajouter le nom des départements sur la carte
        france_deces["coords"] = france_deces["geometry"].centroid  # centroïdes
        for _, row in france_deces.iterrows():
            plt.text(
                row["coords"].x,
                row["coords"].y,
                row["nom"],               # nom du département
                fontsize=7,
                ha="center",
                va="center",
                color="#1a1a1a",
                path_effects=[path_effects.withStroke(linewidth=1,      foreground="white")]
            )

        # Titre
        ax.set_title(
            " Répartition des décès en France par département — Août 2025",
            fontsize=17,
            fontweight="bold",
            pad=25,
            color="#1a1a1a"
        )

        # Supprimer axes et cadre
        ax.set_axis_off()

        # Texte source
        plt.text(
            0.5, -0.14,
            "Source : INSEE — Données décès 2025  |  Carte générée avec GeoPandas  |  © Alex LAMIZANA",
            transform=ax.transAxes,
            ha="center", va="center",
            fontsize=9, color="#555"
        )

        # Sauvegarde
        plt.savefig(
            output_file,
            dpi=300,
            bbox_inches="tight",
            pad_inches=0.2,
            facecolor="#f8f9fa"
        )
        plt.close(fig)

        LOG.info(f"✅ Carte avec noms des départements enregistrée sous : {output_file}")
                
    except Exception as e:
        LOG.error(f"Lors de la création de la carte: {e}")
        raise


# ---------------------------------------------------------------- #
def carte_age_cercles(df, output_file="carte_age_moyen_cercles.png"):
    import geopandas as gpd
    import matplotlib.pyplot as plt
    import numpy as np

    LOG.info("Génération de la carte à cercles proportionnels (âge moyen au décès)...")

    # Charger la carte des départements
    france = gpd.read_file("https://france-geojson.gregoiredavid.fr/repo/departements.geojson")

    # Extraire le département depuis le code INSEE
    df["departement"] = df["lieu_deces_code"].str[:2]

    # Calculer l'âge moyen et le nombre de décès
    stats = (
        df.groupby("departement")
          .agg(age_moyen=("age_deces", "mean"), nb_deces=("age_deces", "count"))
          .reset_index()
          .rename(columns={"departement": "code"})
    )

    # Fusionner avec la carte
    france_stats = france.merge(stats, on="code", how="left")
    france_stats["age_moyen"] = france_stats["age_moyen"].fillna(0)
    france_stats["nb_deces"] = france_stats["nb_deces"].fillna(0)

    # Calcul du centroïde de chaque département (pour placer les cercles)
    france_stats["coords"] = france_stats["geometry"].centroid
    france_stats["x"] = france_stats["coords"].x
    france_stats["y"] = france_stats["coords"].y

    # Création de la figure
    fig, ax = plt.subplots(figsize=(10, 12), facecolor="#f8f9fa")

    # Dessiner la carte de base
    france.boundary.plot(ax=ax, linewidth=0.5, color="gray")

    # Échelle de taille : de petits cercles pour faibles âges, plus grands pour forts
    sizes = (france_stats["age_moyen"] - france_stats["age_moyen"].min()) / (
        france_stats["age_moyen"].max() - france_stats["age_moyen"].min()
    )
    sizes = np.clip(sizes, 0, 1) * 2000 + 200  # plage de tailles

    # Échelle de couleur basée sur le nombre de décès
    colors = plt.cm.Reds(france_stats["nb_deces"] / france_stats["nb_deces"].max())

    # Tracer les cercles proportionnels
    ax.scatter(
        france_stats["x"],
        france_stats["y"],
        s=sizes,
        color=colors,
        alpha=0.7,
        edgecolor="black",
        linewidth=0.5
    )

    # Titre
    ax.set_title(
        " Âge moyen au décès par département (taille des cercles) — France, Août 2025",
        fontsize=15,
        fontweight="bold",
        pad=20
    )

    # Légende manuelle pour la taille (âge moyen)
    for val in [65, 75, 85]:
        ax.scatter([], [], s=(val - 60) * 80, color="#ff9999", alpha=0.6, edgecolor="black", label=f"{val} ans")
    plt.legend(scatterpoints=1, frameon=False, labelspacing=1, title="Âge moyen", loc="lower left")

    # Nettoyage
    ax.set_axis_off()

    # Sauvegarde
    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.2,
        facecolor="#f8f9fa"
    )
    plt.close(fig)

    print(f"✅ Carte à cercles enregistrée sous : {output_file}")


# ---------------------------------------------------------------- #
def main() -> int:
    # TODO: Mettre en place une IA avec scikit.

    LOG.info("Démarrage de l’application...")

    try:
        file = "recensement_population/data/deces-2025-m08.txt"
        df = lire_fichier_deces(file)
        
        add_age_to_death(df)
        # recup_is_null(df)
        # df.to_csv("deces-2025-m08.csv", index=False, encoding="utf-8")
        
        carte_deces(df, "recensement_population/cartes/deces_08-2025.png" )
        # carte_age_cercles(df)
        
        
    except Exception as e:
        LOG.critical("FERMETURE FORCE -")

    LOG.info("Fin de l’exécution.")
    LOG.separator()
    return 0


#####################################################################
if __name__ == "__main__":
    sys.exit(main())

