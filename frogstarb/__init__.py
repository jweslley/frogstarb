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

License: Apache License v2.0 (see docs/LICENSE for details)
"""

version = "0.1.0"
version_info = (0,1,0, "Beta")

import logging
import blogger, markup

# pre processors ---------------------------------------------------------------

def set_title(data,config):
  import os.path
  if not data.has_key('title'):
    basename = os.path.basename(data['path'])
    data['title'] = os.path.splitext(basename)[0]

def metadata(data,config):
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

def pystaches(data,config):
  try:
    import pystaches
  except ImportError:
    raise Exception, "Pystaches support is not installed yet. Install pystaches."
  else:
    view = pystaches.FatView()
    view.template = data['content']
    data['content'] = view.render()

def smartypants(data,config):
  try:
    import smartypants
  except ImportError:
    raise Exception, "Smartypants support is not installed yet. Install smartypants."
  else:
    data['content'] = smartypants.smartyPants(data['content'])

def _apply_preprocessors(data,config):
  preprocessors = [set_title, metadata]
  for preprocessor in preprocessors:
    preprocessor(data,config)

def _apply_postprocessors(data,config):
  postprocessors = [pystaches, smartypants]
  for postprocessor in postprocessors:
    postprocessor(data,config)

def render(path,config):
  with open(path, 'r') as f: content = f.read()
  renderer = markup.by_file_extension(path, config)
  data = {'content':content, 'path':path}
  _apply_preprocessors(data,config)
  data.update(renderer(data['content'], config))
  _apply_postprocessors(data,config)
  return data

def get_blog(config):
  blogger_account = blogger.Account(config)
  return blogger_account.get_blog_by_title(config.get('blog',''))

def publish(path,config):
  data = render(path,config)
  #print data['content']
  data.pop('content')
  print data
  blog = get_blog(config)
  post = blog.publish(data)
  post_url = [link.href for link in post.link if link.rel == 'alternate']
  if post_url:
    print "Your blog post was published successfully!"
    print "View post at %s" % post_url[0]
  else:
    print "Draft saved"

def delete(path,config):
  data = render(path,config)
  blog = get_blog(config)
  post = blog.delete(data)
  if post:
    print "Your blog post was deleted!"
  else:
    print "Post not found: %s" % data['title']

# TODO def summary(path,config):
# post title
# author
# comment count
# url
# tags
