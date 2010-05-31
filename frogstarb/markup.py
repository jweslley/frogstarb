"""
Support for different markup languages for the body of a post.

The following markup languages are supported:
 - HTML
 - Plain text
 - ReStructured Text
 - Markdown
 - Textile

For ReStructuredText and Markdown syntax highlighting of source code is
available.
"""

import os.path

def render_markdown(path,config={}):
  try:
    import markdown
  except ImportError:
    pass
  else:
    markdown_opts = config.get('markdown', 'meta;codehilite(force_linenos=True,css_class=highlight;footnotes')
    with open(path, 'r') as f: content = f.read()
    md = markdown.Markdown(markdown_opts.split(';'))
    html = md.convert(content)
    data = {'content':html}
    data['tags'] = md.Meta.get('tags',[''])[0]
    data['title'] = md.Meta.get('title',[''])[0]
    data['draft'] = md.Meta.get('draft',[''])[0]
    return data

def render_textile(path,config={}):
  try:
    import textile
  except ImportError:
    pass
  else:
    with open(path, 'r') as f: content = f.read()
    return textile.textile(content.encode(config.get('encoding','utf-8')))

def render_rst(path,config={}):
  try:
    from docutils.core import publish_parts
    from cStringIO import StringIO
  except ImportError:
    pass
  else:
    with open(path, 'r') as f: content = f.read()
    warning_stream = StringIO()
    parts = publish_parts(content, writer_name='html4css1',
                        settings_overrides={
                          '_disable_config': True,
                          'embed_stylesheet': False,
                          'warning_stream': warning_stream,
                          'report_level': 2,
                        })
    rst_warnings = warning_stream.getvalue()
    if rst_warnings:
      logging.warn(rst_warnings)
    return parts['html_body']


# Mapping: file extension -> (human readable name, renderer)
MARKUP_MAP = {
#  '.html':     ('HTML', lambda c: c),
#  '.txt':      ('Plain Text', lambda c: html.linebreaks(html.escape(c))),
  '.markdown': ('Markdown', render_markdown),
  '.mkdn':     ('Markdown', render_markdown),
  '.mkd':      ('Markdown', render_markdown),
  '.md':       ('Markdown', render_markdown),
  '.textile':  ('Textile', render_textile),
  '.rst':      ('ReStructuredText', render_rst),
}

def by_file_extension(path,config={}):
  ext = os.path.splitext(path)[1]
  return (MARKUP_MAP[ext] if MARKUP_MAP.has_key(ext) else MARKUP_MAP[config.get('markup','.txt')])[1]