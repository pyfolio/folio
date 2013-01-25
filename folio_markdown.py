from __future__ import with_statement

import os
import markdown

__all__ = ['MarkdownExtension']

class MarkdownExtension():
    def __init__(self, folio, template_base=None, template_extensions=None,
                 markdown_extensions=None):
        if template_base is None:
            template_base = '_markdown.html'
        if template_extensions is None:
            template_extensions = ['*.md']
        if markdown_extensions is None:
            markdown_extensions = ['meta']

        self.folio = folio
        self.template_base = template_base

        template_base = os.path.join(self.folio.template_path,
                                     self.template_base)
        if not os.path.exists(template_base):
            raise TypeError('Template base "%s" not found' % (template_base, ))

        for extension in template_extensions:
            self.folio.builders.append((extension, self.markdown_builder))

        self.markdown = markdown.Markdown(extensions=markdown_extensions)

    def markdown_builder(self, env, template_name, context):
        head, tail = os.path.split(template_name)

        if head:
            dirname = os.path.join(self.folio.build_path, head)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

        content, meta = self.parse(template_name)

        context['content'] = content
        context.update(meta)

        dest_name = self.translate_template_name(template_name)
        destination = os.path.join(self.folio.build_path, dest_name)

        template = env.get_template(self.template_base)
        template.stream(**context).dump(destination,
                                        encoding=self.folio.encoding)

    def translate_template_name(self, template_name):
        name, ext = os.path.splitext(template_name)
        return '.'.join([name, 'html'])

    def parse(self, template_name):
        with open(os.path.join(self.folio.template_path, template_name)) as f:
            content = f.read()

        markdown = self.markdown.convert(content)
        meta = self.markdown.Meta

        return (markdown, meta)