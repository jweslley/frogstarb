"""
FrogstarB
=========

FrogstarB is simple tool to post to Blogger from the command line. It's a very easy way to format your content without writing any HTML. You give it text written in your favorite markup language, be that Markdown, Textile, ReStructuredText, or just plain HTML, and it transforms your text and post to Blogger.

## Usage

  frogstarb -p post.markdown

Run "frogstarb --help" to see more options.

## Author and License

Created by [Jonhnny Weslley](http://jonhnnyweslley.net).

Contact: jw [at] jonhnnyweslley.net

Copyright 2010 Jonhnny Weslley

License: MIT License (see COPYING for details)
"""

version = "0.1.0"
version_info = (0,1,0, "Beta")

import os.path, logging, ConfigParser
import markup

# pre processors ---------------------------------------------------------------

def set_title(data):
  if not data.has_key('title'):
    basename = os.path.basename(data['path'])
    data['title'] = os.path.splitext(basename)[0]

def metadata(data):
  import re
  key_value_re = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
  lines = data['content'].split('\n')
  while True:
    line = lines.pop(0)
    if line.strip() == '':
      break
    m1 = key_value_re.match(line)
    if m1:
      key = m1.group('key').lower().strip()
      data[key] = m1.group('value').strip()
    else:
      lines.insert(0, line)
      break
  data['content'] = '\n'.join(lines)


# post processors --------------------------------------------------------------

def pystaches(data):
  if data.get('pystaches','yes') == 'yes':
    from pystache import View
    from pystaches import EmbedVideo, SyntaxHighlighter

    class FatView(View, EmbedVideo, SyntaxHighlighter):
      def __init__(self, template, config):
        View.__init__(self, template, config)
        SyntaxHighlighter.tab_length = int(config.get('tab_length', '2'))
        SyntaxHighlighter.linenos    = config.get('linenos', 'no') == 'yes'
        SyntaxHighlighter.css_class  = config.get('css_class', 'highlight')
        SyntaxHighlighter.prefix     = config.get('syntax_prefix', 'highlight_')

    view = FatView(data['content'], data)
    data['content'] = view.render()

def smartypants(data):
  if data.get('smartypants','no') != 'no':
    import smartypants
    smartypants_opts = '1' if data['smartypants'] == 'yes' else data['smartypants']
    data['content'] = smartypants.smartyPants(data['content'], smartypants_opts)

def _apply_preprocessors(data):
  preprocessors = [set_title, metadata]
  for preprocessor in preprocessors:
    preprocessor(data)

def _apply_postprocessors(data):
  postprocessors = [pystaches, smartypants]
  for postprocessor in postprocessors:
    postprocessor(data)

# public api -------------------------------------------------------------------

def render(path,config):
  with open(path, 'r') as f: content = unicode(f.read(),'utf-8')
  renderer = markup.by_file_extension(path, config)
  config.update({'content':content, 'path':path})
  _apply_preprocessors(config)
  config.update({'content':renderer(config['content'], config)})
  _apply_postprocessors(config)
  return config

def publish(blog,path,config):
  data = render(path,config)
  return blog.publish(data)

def delete(blog,path,config):
  data = render(path,config)
  return blog.delete(data)

def preview(path,config):
  import glob, pystache, tempfile, webbrowser
  root = root_path()
  html_template_file = config.get('preview_html_template', os.path.join(root, 'preview', 'template.html'))
  stylesheets = glob.glob(config.get('preview_stylesheets', os.path.join(root, 'preview', '*.css')))
  config['preview_stylesheets'] = [{'stylesheet': stylesheet} for stylesheet in stylesheets]

  data = render(path,config)
  with open(html_template_file, 'r') as f: html_template = unicode(f.read(),'utf-8')
  html = pystache.render(html_template, data).encode('utf-8')
  __, filename = tempfile.mkstemp(suffix='.html')
  with open(filename, 'w') as f: f.write(html)
  webbrowser.open(filename)

def root_path():
  root = __file__
  if os.path.islink(root):
    root = os.path.realpath(root)
  return os.path.dirname(os.path.abspath(root))

def config(config_overrides={}):
  parser = ConfigParser.ConfigParser()
  parser.read([os.path.expanduser('~/.frogstarb')])

  config = dict(parser.items('blogger')) if parser.has_section('blogger') else {}
  config.update(config_overrides)

  # resolve blog alias if any
  if config.has_key('blog') \
      and parser.has_section('alias') \
      and parser.has_option('alias',config['blog']):
    config['blog'] = parser.get('alias',config['blog'])

  return config


# TODO def summary(path,config):
# post title
# author
# comment count
# url
# tags
