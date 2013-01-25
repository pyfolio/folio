from folio import Folio

folio = Folio()

@folio.context('index.html')
def index(env):
    return {'title': 'Hello World'}

if __name__ == '__main__':
    folio.build()
    folio.watch()