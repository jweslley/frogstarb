"""
Support for different markup languages for the body of a post.

The following markup languages are supported:
 - HTML
 - Plain text
 - ReStructured Text
 - Markdown
 - Textile

"""

import logging
import os.path

def render_markdown(content,config):
  import markdown
  markdown_opts = config.get('markdown', 'meta;codehilite(css_class=highlight);footnotes')
  md = markdown.Markdown(markdown_opts.split(';'))
  content = md.convert(content)
  if hasattr(md, 'Meta'):
    for key in md.Meta.keys():
      config[key] = '\n'.join(md.Meta[key])
  return content

def render_textile(content,config):
  import textile
  return textile.textile(content.encode(config.get('encoding','utf-8')))

def render_rst(content,config):
  import docutils
  from docutils.core import publish_parts
  from cStringIO import StringIO

  warning_stream = StringIO()
  config.update({'_disable_config': True, 'embed_stylesheet': False,
                 'warning_stream': warning_stream, 'report_level': 2})
  parts = publish_parts(content, writer_name='html4css1',settings_overrides=config)
  rst_warnings = warning_stream.getvalue()
  if rst_warnings:
    logging.warn(rst_warnings)
 
  return parts['html_body']

def render_plain(content,config):
  html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    "\n": "<br/>\n" # line breaking
  }
  return "".join(html_escape_table.get(c,c) for c in content)


# Mapping: file extension -> (human readable name, renderer)
MARKUP = {
  '.html':     ('HTML', lambda content, config: content),
  '.txt':      ('Plain Text', render_plain),
  '.markdown': ('Markdown', render_markdown),
  '.mkdn':     ('Markdown', render_markdown),
  '.mkd':      ('Markdown', render_markdown),
  '.md':       ('Markdown', render_markdown),
  '.textile':  ('Textile', render_textile),
  '.rst':      ('ReStructuredText', render_rst),
}

def by_file_extension(path,config):
  ext = os.path.splitext(path)[1]
  return (MARKUP[ext] if MARKUP.has_key(ext) else MARKUP[config.get('markup','.txt')])[1]
