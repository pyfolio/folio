from folio import Folio

folio = Folio()

@folio.context('index.html')
def index(env):
    return {'title': 'Hello World'}

@folio.builder('*.md')
def markdown_builder(env, template_name, context, build_path, encoding):
    pass

if __name__ == '__main__':
    folio.build()
    folio.watch()