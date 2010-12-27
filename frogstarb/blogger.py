import gdata.blogger.client
import gdata.blogger.data
import atom

class Blog:
  """
    A simple class for interacting with a Blogger blog.
    It uses the Google gdata API to create, update and delete posts.
  """

  def __init__ (self, blog, client):
    self.client = client
    self.blog_id = blog.get_blog_id()

  def add_post(self, data):
    """
      Add a post to the blog. ``data`` is a dictionary object that
      provides the following attributes:

      - *title* -- post title
      - *content* -- post content (HTML)
      - *tags* -- post's tags, specified as a comma-separated list
      - *draft* -- if this post is a draft
    """
    return self.client.add_post(
      self.blog_id,
      data['title'],
      data['content'],
      labels=self.taglist(data),
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

    # synchronize tags
    declared_tags = self.taglist(data)
    current_tags = [category.term for category in post.category]
    tags_to_add = [tag for tag in declared_tags if tag not in current_tags]
    tags_to_remove = [tag for tag in current_tags if tag not in declared_tags]
    for tag in tags_to_add:
      post.add_label(tag)
    for tag in tags_to_remove:
      for category in post.category:
        if category.term == tag:
          post.category.remove(category)

    return self.client.update(post)

  def publish(self, data):
    """
      Publish the post to the blog. If no posts matched with the given title,
      then a new post will be created, otherwise the existent post will be updated.
    """
    post = self.get_post(data['title'])
    return self.update_post(post, data) if post else self.add_post(data)

  def delete(self, data):
    """
      Delete a post.
    """
    post = self.get_post(data['title'])
    return self.client.delete(post) if post else None

  def get_posts(self):
    """
      List all posts.
    """
    return [post.title.text for post in self.client.get_posts(self.blog_id).entry]

  def get_post(self, post_title):
    """
      Retrieve a post by title.
    """
    posts = [post for post in self.client.get_posts(self.blog_id).entry if post.title.text == post_title]
    return posts[0] if len(posts) == 1 else None

  def post_url(self, post):
    """
      Retrieve the url for a given post.
    """
    urls = [link.href for link in post.link if link.rel == 'alternate']
    return urls[0] if len(urls) == 1 else None

  def taglist(self,data):
    """
      Generates a tag list from a comma-separated string value
    """
    tags = data.get('tags','').strip()
    return [tag.strip() for tag in tags.split(',')] if len(tags) > 0 else []


class NoSuchBlogError(Exception):
  pass

class Account:

  def __init__ (self, config):
    """
      ``config`` is a configuration dictionary that must provide values for:

      - *username* -- the email of the blogger user
      - *password* -- the password of the blogger user
    """
    self.client = gdata.blogger.client.BloggerClient()
    self.client.client_login(config['username'], config['password'], 'frogstarb', service='blogger')

  def get_blogs(self):
    """
      List all blogs.
    """
    return [blog.title.text for blog in self.client.get_blogs().entry]

  def get_blog(self,blog_name):
    """
      Retrieve a blog by the name.
    """
    blogs = [blog for blog in self.client.get_blogs().entry if blog.title.text == blog_name]
    if len(blogs) > 0:
      return Blog(blogs[0], self.client)
    else:
      raise NoSuchBlogError("Blog not found: %s" % blog_name)

