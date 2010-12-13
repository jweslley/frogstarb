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
# TODO improve usage

version = "0.1.0"
version_info = (0,1,0, "Beta")

import sys, logging
import blogger
import markup, pystaches

def _apply_postprocessor(data):
  view = pystaches.FatView()
  view.template = data['content']
  data['content'] = view.render()

def get_blog(config):
  return blogger.new(config)

def publish(path,config):
  renderer = markup.by_file_extension(path, config)
  with open(path, 'r') as f: content = f.read()
  data = renderer(content, config)
  _apply_postprocessor(data)
#  print data['content']

#  blog = get_blog(config)
#  blog.publish(data)

def delete(path,config):
  renderer = markup.by_file_extension(path, config)
  data = renderer(path, config)
  blog = get_blog(config)
  post = blog.get_post_by_title(data['title'])
  if post is None:
    print "Post not found %s" % data['title']
  else:
    blog.delete(post)
