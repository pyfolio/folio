import os

from folio import Folio
from folio_markdown import MarkdownExtension

folio = Folio()
md = MarkdownExtension(folio)

@folio.context('index.html')
def index(env):
    articles = []
    templates = env.list_templates(
                    filter_func=lambda f: f.startswith('articles/'))

    for template_name in templates:
        markdown, meta = md.parse(template_name)
        articles.append({
            'file' : template_name,
            'path' : md.translate_template_name(template_name),
            'meta' : meta,
        })

    return {'articles': articles}

if __name__ == '__main__':
    folio.build()
    folio.run()
