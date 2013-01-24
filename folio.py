# -*- coding: utf-8 -*-
"""
    Folio is an static website generator using jinja2 template engine.
"""

import os
import shutil

from jinja2 import Environment, FileSystemLoader

def _filter_templates(filename):
    _, tail = os.path.split(filename)
    nrender = tail.startswith('.') or tail.startswith('_')
    
    return not nrender

def build(build_path='build', template_path='templates', static_path='static'):
    if os.path.exists(build_path):
        for path, dirs, files in os.walk(build_path, topdown=False):
            for file in files:
                os.remove(os.path.join(path, file))
            os.rmdir(path)
    
    if os.path.exists(static_path):
        shutil.copytree(static_path, build_path)
    else:
        os.mkdir(build_path)
    
    loader = FileSystemLoader(searchpath=template_path)
    jinja2 = Environment(loader=loader)
    
    for template_name in jinja2.list_templates(filter_func=_filter_templates):
        head, tail = os.path.split(template_name)
        
        if head:
            head = os.path.join(build_path, head)
            if not os.path.exists(head):
                os.makedirs(head)
        
        template = jinja2.get_template(template_name)
        template.stream().dump(os.path.join(build_path, template_name),
                               encoding='utf-8')
