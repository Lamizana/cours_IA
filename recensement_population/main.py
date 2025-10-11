import re
import sys
import pandas as pd
from logger import Logger

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
    
    LOG.info(f"Ajout de l'age du décès au DataFrame {df} réussi")
    return df


# ---------------------------------------------------------------- #
def recup_is_null(df: pd.DataFrame):
    
    # Détection des lignes contenant au moins une valeur manquante
    df_null = df[df.isnull().any(axis=1)]

    # Sauvegarde dans un fichier CSV :
    df_null.to_csv("deces-2025-m08_nulls.csv", index=False, encoding="utf-8")

    print(f"✅ {len(df_null)} lignes contenant au moins une valeur nulle ont été extraites dans 'deces-2025-m08_nulls.csv'")

    
# ---------------------------------------------------------------- #
def main() -> int:
    # TODO: Mettre en place une IA avec scikit.

    LOG.info("Démarrage de l’application...")

    try:
        df = lire_fichier_deces("deces-2025-m08.txt")
        print(df.head())
        
        add_age_to_death(df)
        # recup_is_null(df)
        # df.to_csv("deces-2025-m08.csv", index=False, encoding="utf-8")
        
        
        
    except Exception as e:
        LOG.critical("FERMETURE FORCE -")

    LOG.info("Fin de l’exécution.")
    LOG.separator()
    return 0


#####################################################################
if __name__ == "__main__":
    sys.exit(main())

