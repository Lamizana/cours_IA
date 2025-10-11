# cours_IA

Miser en place de différentes IA en application avec Scikit-learn.

## Setup et installation


## TODO avec Pycharm

### ✅ 1. Ecrire une TODO dans le code

Il faut simplement ajouter un _comentaire spécial_ dans le code :

```python
# TODO: implémenter la fonction de nettoyage des données INSEE
def clean_data():
    pass
```

Il y a plusieurs variantes :

```python
# FIXME: corriger la normalisation PCA
# FEAT: Nouvel feature.
# HACK: solution rapide, à améliorer plus tard
```

### 🧭 Voir toutes les TODO dans Pycharm

1. Ouvrir le projet.
2. Va dans menu :
   1. **View -> Tool Windows -> TODO**
3. Une fenêtre s'ouvre avec la liste des TODO trouvé dans le code :
   1. Le fichier concerné.
   2. La ligne exacte.
   3. Le contenu en commentaire.

> 💡 Cliquer sur une ligne pour aller directement au code.


### 3. Ajouter tes propres filtres TODO

On a défini des **règles personalisées** (par exemple `@urgent`, `@review`, etc.) :

1. Aller dans :
   1. **File → Settings → Editor → TODO**

2. Cliquer sur ➕ pour ajouter une nouvelle règle :
   1. **Pattern** : `@urgent.*`
   2. **Case sensitive** : coché ou non selon ton besoin
   3. Choisir une couleur d'affichage.

Les TODO seront ensuite colorées à la vue dédiée.

Tu verras ensuite ces TODO colorés différemment dans la vue dédiée.

## 🧾 Journalisation (Logging)

Le projet utilise un système de journalisation centralisé basé sur un module `logger.py`, 
afin d’enregistrer les messages d’exécution et les erreurs dans un fichier de log.

---- 

### 📁 Structure du fichier

Le logger est défini dans :

```css
cours_IA/
├── logger.py
└── recensement_population/
    ├── main.py
    └── ...
```

### ⚙ Fonctionnement

Le fichier `logger.py` contient une classe `Logger` personnalisée, qui :

- Enregistre les messages dans un fichier (ex. `recensement_pop.log`) ;
- Affiche aussi les messages dans la console pour le suivi en temps réel.

### 🧩 Exemple d’utilisation

```python
# main.py
from logger import Logger

# Initialisation du logger (le fichier 'app.logs/' sera créé automatiquement)
log = Logger("logs/recensement_pop.log")


def main() -> int:
   log.info("Démarrage de l’application...")
   # ton code ici
   log.info("Fin de l’exécution.")
   return 0


if __name__ == "__main__":
   import sys

   sys.exit(main())
```

🧠 Exemple de sortie dans app.log

```yaml
2025-10-11 15:24:53,872 - INFO - Démarrage de l’application...
2025-10-11 15:24:55,123 - INFO - Fin de l’exécution.
```
