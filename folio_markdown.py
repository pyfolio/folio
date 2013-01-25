from __future__ import with_statement

import os
import markdown

class MarkdownExtension():
    def __init__(self, folio, template_base=None, extensions=None):
        if template_base is None:
            template_base = '_markdown.html'
        if extensions is None:
            extensions = ['*.md']

        self.folio = folio
        self.template_base = template_base
        self.extensions = extensions

        template_base = os.path.join(self.folio.template_path,
                                     self.template_base)
        if not os.path.exists(template_base):
            raise TypeError('Template base "%s" not found' % (template_base, ))

        for extension in self.extensions:
            self.folio.builders.append((extension, self.markdown_builder))

        self.markdown = markdown.Markdown(extensions=['meta'])

    def markdown_builder(self, env, template_name, context):
        head, tail = os.path.split(template_name)
        name, ext = os.path.splitext(tail)

        if head:
            dirname = os.path.join(self.folio.build_path, head)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

        destname = '%s.html' % (name, )
        destination = os.path.join(self.folio.build_path, head, destname)

        with open(os.path.join(self.folio.template_path, template_name)) as f:
            content = f.read()

        context['content'] = self.markdown.convert(content)
        context.update(self.markdown.Meta)

        template = env.get_template(self.template_base)
        template.stream(**context).dump(destination,
                                        encoding=self.folio.encoding)