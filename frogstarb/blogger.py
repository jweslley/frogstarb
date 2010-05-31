import gdata.blogger.client
import gdata.blogger.data
import atom

class Blog:
  """
    A simple class for interacting with a Blogger blog.
    It uses the Google gdata API to create, update and delete posts.
  """

  def __init__ (self, blog, client):
    self.blog = blog
    self.client = client

  def add_post(self, data):
    """
      Add a post to the blog. ``data`` is a dictionary object that
      provides the following attributes:

      - *title* -- post title
      - *content* -- post content (HTML)
      - *tags* -- post's tags, specified as a comma-separated list
      - *draft* -- if this post is a draft
    """
    tags = data.get('tags','').strip()
    tags = tags.split(',') if len(tags) > 0 else None
    print "tags %s" % tags
    return self.client.add_post(
      self.blog.get_blog_id(),
      data['title'],
      data['content'],
      labels=tags,
      draft=data.get('draft','no').lower() == 'yes'
      )

  def update_post(self, post, data):
    """
      Update title, content, and tags of the given post.
    """
    post.title = atom.data.Title(type='text', text=data['title'])
    post.content = atom.data.Content(type='html', text=data['content'])

    if post.control \
      and post.control.draft \
      and post.control.draft.text == 'yes' \
      and data.get('draft','no') == 'no':
      post.control.draft.text = 'no'

    for tag in data.get('tags','').split(','):
      post.add_label(tag)

    return self.client.update(post)

  def publish(self, data):
    """
      Publish the post to the blog. If no posts matched with the given title,
      then a new post will be created, otherwise the existent post will be updated.
    """
    post = self.get_post_by_title(data['title'])
    if post is None:
      self.add_post(data)
    else:
      self.update_post(post, data)

  def delete(self, post):
    """
      Delete a post.
    """
    return self.client.delete(post)

  def get_posts(self):
    """
      List all posts.
    """
    return self.client.get_posts(self.blog.get_blog_id()).entry

  def get_post_by_id(self, post_id):
    """
      Retrieve a post by id.
    """
    return self.client.get_feed(
      self.blog.get_post_link().href + '/%s' % post_id,
      auth_token=self.client.auth_token,
      desired_class=gdata.blogger.data.BlogPost)

  def get_post_by_title(self, post_title):
    """
      Retrieve a post by title.
    """
    posts = [post for post in self.get_posts() if post.title.text == post_title]
    return posts[0] if len(posts) == 1 else None


class NoSuchBlogError(Exception):
  pass

def connect(config):
  """
    ``config`` is a configuration dictionary that must provide values for:

    - *username* -- the email of the blogger user
    - *password* -- the password of the blogger user
  """
  client = gdata.blogger.client.BloggerClient()
  client.client_login(
    config['username'],
    config['password'],
    'frogstarb',
    service='blogger')
  return client

def select_blog(client,blog_name=''):
  """
    Select a blog by the name.
  """
  # TODO something like http://github.com/jweslley/frogstarb/blob/java/src/main/java/net/jonhnnyweslley/frogstarb/FrogstarB.java#getBlogId()
  blogs = client.get_blogs().entry
  if (len(blogs) == 0):
    raise NoSuchBlogError("Ooops! You don't have a blog yet!")
  elif (len(blogs) == 1):
    return blogs[0]
  else:
    for blog in blogs:
      if blog.title.text == blog_name:
        return blog
    raise NoSuchBlogError("Ooops! You don't have a blog %s" % blog_name)

def new(config):
  client = connect(config)
  blog = select_blog(client, config.get('blog',''))
  return Blog(blog, client)
