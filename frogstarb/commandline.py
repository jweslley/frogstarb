import frogstarb
import sys
import os.path
import optparse
import ConfigParser
from getpass import getpass

def parse_options():
  """
    Define and parse `optparse` options for command-line usage.
  """

  parser = optparse.OptionParser(
      usage =       "%prog [OPTIONS] ... [-p | -d <FILENAME>]",
      description = "Simple tool to post to Blogger.com from the command line.\n" \
                    "http://github.com/jweslley/frogstarb",
      version =     "%%prog %s" % frogstarb.version)
  parser.add_option("-p", "--publish", dest="publish", metavar="FILENAME",
    help="Publish the post. The post title is equal to the FILENAME without"  \
    " extension. If the post doesn't exist yet, it will be created; otherwise"\
    " the post will be updated.")
  parser.add_option("-d", "--delete", dest="delete", metavar="FILENAME",
    help="Delete the post whose title is equal to the FILENAME without extension.")
  parser.add_option("-u", "--username", dest="username", metavar="USERNAME",
    help="The username of the blogger user. This option is not required if " \
    "the 'username' property is defined in the configuration file.")
  parser.add_option("-P", "--password", dest="password", metavar="PASSWORD",
    help="The password of the blogger user. This option is not required if " \
    "the 'password' property is defined in the configuration file.")
  parser.add_option("-b", "--blog-name", dest="blog", metavar="BLOGNAME",
    help="The blog's name. This option is not required if either the "  \
    "blogger user has just one blog or the 'blog' property is defined " \
    "in the configuration file.")
  parser.add_option("-t", "--tags", dest="tags", metavar="TAG_LIST",
    help="The list of tags from the post, specified as a comma-separated list.")
  parser.add_option("-c", "--config-file", dest="config", metavar="CONFIG_FILE",
    help="The configuration file. Defaults to '~/.frogstarb'.", default='')

  (options, args) = parser.parse_args()
  return options

def configure(options,service='blogger'):
  """
    Configure frogstarb from both command-line and configuration file.
  """
  parser = ConfigParser.ConfigParser()
  parser.read([os.path.expanduser('~/.frogstarb'), options.config])

  config = dict(parser.items(service)) if parser.has_section(service) else {}

  # Allow command line options to overwrite config settings
  if options.username:
    config['username'] = options.username
  if options.password:
    config['password'] = options.password
  if options.blog:
    config['blog'] = options.blog
  if options.tags:
    config['tags'] = options.tags

  # prompt for required fields
  if not config.has_key('username'):
    config['username'] = raw_input('Username: ')
  if not config.has_key('password'):
    config['password'] = getpass("Enter your password(%s): "%config['username'])

  # resolve blog alias if any
  if config.has_key('blog') \
      and parser.has_section('alias') \
      and parser.has_option('alias',config['blog']):
    config['blog'] = parser.get('alias',config['blog'])

  return config

def run():
  """
    Run FrogstarB from the command line.
  """
  options = parse_options()
  config = configure(options)
  
  if not options.publish and not options.delete:
    print "No actions to be taken! :P"
    sys.exit(1)
  elif options.publish and options.delete:
    print "Choose just one action of publish or delete."
    sys.exit(2)

  if options.publish:
    if not os.path.exists(options.publish):
      print "No such file %s" % options.publish
      sys.exit(3)
    frogstarb.publish(options.publish, config)

  if options.delete:
    if not os.path.exists(options.delete):
      print "No such file %s" % options.delete
      sys.exit(3)
    frogstarb.delete(options.delete, config)

if __name__ == '__main__':
  run()
