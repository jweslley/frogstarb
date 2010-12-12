"""
Support for different markup languages for the body of a post.

The following markup languages are supported:
 - HTML
 - Plain text
 - ReStructured Text
 - Markdown
 - Textile

"""

import os.path

class NotSupportedMarkup(Exception):
  pass

def render_markdown(content,config={}):
  try:
    import markdown
  except ImportError:
    raise NotSupportedMarkup("Markdown support is not installed yet. Install python-markdown.")
  else:
    markdown_opts = config.get('markdown', 'meta;codehilite(force_linenos=True,css_class=highlight);footnotes')
    md = markdown.Markdown(markdown_opts.split(';'))
    html = md.convert(content)
    data = {'content':html}
    if md.Meta:
      data['tags'] = md.Meta.get('tags',[''])[0]
      data['title'] = md.Meta.get('title',[''])[0]
      data['draft'] = md.Meta.get('draft',[''])[0]
    return data

def render_textile(content,config={}):
  try:
    import textile
  except ImportError:
    raise NotSupportedMarkup("Textile support is not installed yet. Install python-textile.")
  else:
    data = {'content':textile.textile(content.encode(config.get('encoding','utf-8')))}
    return data

def render_rst(content,config={}):
  try:
    from docutils.core import publish_parts
    from cStringIO import StringIO
  except ImportError:
    raise NotSupportedMarkup("ReStructured Text support is not installed yet. Install python-docutils.")
  else:
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
 
    data = {'content':parts['html_body']}
    return data


# Mapping: file extension -> (human readable name, renderer)
MARKUP_MAP = {
  '.html':     ('HTML', lambda c: c),
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
