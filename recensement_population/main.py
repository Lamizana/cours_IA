import sys
from logger import Logger

LOG = Logger("recensement_pop.log")
#####################################################################


# ---------------------------------------------------------------- #
def main() -> int:
    LOG.info("COUCOU")

    LOG.separator()
    return 0


#####################################################################
if __name__ == "__main__":
    sys.exit(main())

