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
  parser.add_option("-r", "--preview", dest="preview", metavar="FILENAME",
    help="Display the rendered FILENAME using the default browser.")
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

  (options, args) = parser.parse_args()
  return options

def configure(options,service='blogger'):
  """
    Configure frogstarb from both command-line and configuration file.
  """
  parser = ConfigParser.ConfigParser()
  parser.read([os.path.expanduser('~/.frogstarb')])

  config = dict(parser.items(service)) if parser.has_section(service) else {}

  # Allow command line options to overwrite config settings
  if options.username:
    config['username'] = options.username
  if options.password:
    config['password'] = options.password
  if options.blog:
    config['blog'] = options.blog

  # resolve blog alias if any
  if config.has_key('blog') \
      and parser.has_section('alias') \
      and parser.has_option('alias',config['blog']):
    config['blog'] = parser.get('alias',config['blog'])

  return config

def select_blog(blogs,blog_name):
  """
    Select a blog by the name or interactively, if necessary.
  """
  if len(blogs) == 0:
    raise NoSuchBlogError("Ooops! You don't have a blog yet!")

  if len(blogs) == 1:
    return blogs[0]

  for blog in blogs:
    if blog == blog_name:
      return blog

  response = query_yes_no("The blog '%s' doesn't exists. Select another blog to continue?" % blog_name)
  if not response:
    sys.exit(42)

  print "\nList of your blogs:"
  for i in range(len(blogs)):
    print "%s : %s" % (i, blogs[i])

  selected_blog = raw_input("\nSelect one of them typing the blog number (Just press ENTER to exit): ")
  if not selected_blog:
    sys.exit(10)
  try:
    selected_blog = int(selected_blog)
  except ValueError:
    raise NoSuchBlogError("Failed. Invalid blog number: %s" % selected_blog)

  if not (selected_blog >= 0 and selected_blog < len(blogs)):
    raise NoSuchBlogError("Failed. Selected blog number is out of range: %s" % range(len(blogs)))

  return blogs[selected_blog]

def query_yes_no(question,default="yes"):
  """
    Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
      It must be "yes" (the default), "no" or None (meaning
      an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
  """
  valid = {"yes":True, "ye":True, "y":True, "no":False, "n":False}
  if default == None:
    prompt = " [y/n] "
  elif default == "yes":
    prompt = " [Y/n] "
  elif default == "no":
    prompt = " [y/N] "
  else:
    raise ValueError("Invalid default answer: '%s'" % default)

  while True:
    choice = raw_input(question + prompt).lower()
    if default is not None and choice == '':
      return valid[default]
    elif choice in valid:
      return valid[choice]
    else:
      print "Please respond with 'yes' or 'no' (or 'y' or 'n')."

def check_file(filename):
  assert os.path.exists(filename), "No such file %s" % filename
  assert os.path.isfile(filename), "File is a directory: %s" % filename
  assert os.access(filename, os.R_OK), "No permission to read the file: %s" % filename

def get_blog(config):
  # prompt for required fields
  if not config.has_key('username'):
    config['username'] = raw_input('Username: ')
  if not config.has_key('password'):
    config['password'] = getpass("Enter your password(%s): "%config['username'])

  blogger_account = blogger.Account(config)
  blogs = blogger_account.get_blogs()
  blog_name = selected_blog(blogs, config.get('blog',''))
  return blogger_account.get_blog(blog_name)

def _run():
  options = parse_options()
  config = configure(options)

  if options.preview:
    check_file(options.preview)
    frogstarb.preview(options.preview,config)
    sys.exit(0)

  assert options.publish or options.delete, "No actions to be taken! :P"
  assert not(options.publish and options.delete), "Choose just one action of publish or delete."

  if options.publish:
    check_file(options.publish)
    blog = get_blog(config)
    post = frogstarb.publish(blog, options.publish, config)
    post_url = blog.post_url(post)
    if post_url:
      print "Your blog post was published successfully!"
      print "View post at %s" % post_url
    else:
      print "Draft saved"

  if options.delete:
    check_file(options.delete)
    blog = get_blog(config)
    post = frogstarb.delete(blog, options.delete, config)
    if post:
      print "Your blog post was deleted!"
    else:
      print "Post not found: %s" % data['title']

def run():
  """
    Run FrogstarB from the command line.
  """
  from socket import gaierror
  try:
    _run()
  except ImportError as e:
    module_name = e.args[0].split()[-1]
    print "The library '%s' is currently not installed. You can install it by typing:" % module_name
    print "sudo easy_install %s" % module_name
    sys.exit(1)
  except AssertionError as e:
    print e.args[0]
    sys.exit(2)
  except KeyboardInterrupt:
    print "Bye!"
    sys.exit(3)
  except EOFError:
    print "Bye!"
    sys.exit(3)
  except blogger.NoSuchBlogError as e:
    print e.args[0]
    sys.exit(4)
  except gaierror:
    print "Please, check your network connection."
    sys.exit(5)
