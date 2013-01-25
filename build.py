from folio import Folio
from folio_markdown import MarkdownExtension

folio = Folio()

MarkdownExtension(folio, template_base='_markdown.html', extensions=['*.md'])

if __name__ == '__main__':
    folio.build()
    folio.run()
