from folio import Folio
from os.path import exists

folio = Folio()

if __name__ == '__main__':
    if not exists(folio.build_path):
        folio.build()
    folio.run()
