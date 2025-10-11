import sys
from logger import Logger

LOG = Logger("recensement_pop")
#####################################################################


# ---------------------------------------------------------------- #
def main() -> int:
    # TODO: Mettre en place une IA avec scikit.

    LOG.info("Démarrage de l’application...")

    LOG.info("Fin de l’exécution.")
    LOG.separator()
    return 0


#####################################################################
if __name__ == "__main__":
    sys.exit(main())

