import sys, os, os.path, logging
import optparse, ConfigParser
from getpass import getpass
import frogstarb, blogger

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)

def parse_options():
  """
    Define and parse `optparse` options for command-line usage.
  """

  parser = optparse.OptionParser(
      usage =       "%prog [OPTIONS] ... [-p | -d | -r <FILENAME>]",
      description = "Simple tool to post to Blogger.com from the command line.\n" \
                    "http://github.com/jweslley/frogstarb",
      version =     "%%prog %s" % frogstarb.version)
  parser.add_option("-p", "--publish", dest="publish", metavar="FILENAME",
    help="Publish the post. The post title is equal to the FILENAME without"  \
    " extension. If the post doesn't exist yet, it will be created; otherwise"\
    " the post will be updated.")
  parser.add_option("-d", "--delete", dest="delete", metavar="FILENAME",
    help="Delete the post whose title is equal to the FILENAME without extension.")
  parser.add_option("-r", "--render", dest="render", metavar="FILENAME",
    help="Print the rendered FILENAME to standard output instead of publish it.")
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

def check_file(filename):
  assert os.path.exists(filename), "No such file %s" % filename
  assert os.path.isfile(filename), "File is a directory: %s" % filename
  assert os.access(filename, os.R_OK), "No permission to read the file: %s" % filename

def _run():
  options = parse_options()
  config = configure(options)

  if options.render:
    check_file(options.render)
    print frogstarb.render(options.render,config)['content'].encode('utf-8')
    sys.exit(0)

  assert options.publish or options.delete, "No actions to be taken! :P"
  assert not(options.publish and options.delete), "Choose just one action of publish or delete."

  if options.publish:
    check_file(options.publish)
    frogstarb.publish(options.publish, config)

  if options.delete:
    check_file(options.delete)
    frogstarb.delete(options.delete, config)

def run():
  """
    Run FrogstarB from the command line.
  """
  try:
    _run()
  except ImportError as e:
    module_name = e.args[0].split()[-1]
    print "%s support is not installed yet. Install %s" % (module_name.capitalize(), module_name)
    sys.exit(1)
  except AssertionError as e:
    print e.args[0]
    sys.exit(2)
  except KeyboardInterrupt:
    print "Bye!"
    sys.exit(3)
  except blogger.NoSuchBlogError as e:
    print e.args[0]
    sys.exit(4)
