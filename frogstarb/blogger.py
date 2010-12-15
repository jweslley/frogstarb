import gdata.blogger.client
import gdata.blogger.data
import atom
import sys

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
    return self.client.add_post(
      self.blog.get_blog_id(),
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
    post = self.get_post_by_title(data['title'])
    return self.update_post(post, data) if post else self.add_post(data)

  def delete(self, data):
    """
      Delete a post.
    """
    post = self.get_post_by_title(data['title'])
    return self.client.delete(post) if post else None

  def get_posts(self):
    """
      List all posts.
    """
    return self.client.get_posts(self.blog.get_blog_id()).entry

  def get_post_by_title(self, post_title):
    """
      Retrieve a post by title.
    """
    posts = [post for post in self.get_posts() if post.title.text == post_title]
    return posts[0] if len(posts) == 1 else None

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
    self.client.client_login(
      config['username'],
      config['password'],
      'frogstarb',
      service='blogger')

  def get_blog_by_title(self,blog_name):
    """
      Select a blog by the name.
    """
    blog = self.select_blog(blog_name)
    return Blog(blog, self.client)

  def select_blog(self,blog_name):
    """
      Select a blog by the name or interactively, if necessary.
    """
    blogs = self.client.get_blogs().entry
    if len(blogs) == 0:
      raise NoSuchBlogError("Ooops! You don't have a blog yet!")

    if len(blogs) == 1:
      return blogs[0]

    for blog in blogs:
      if blog.title.text == blog_name:
        return blog

    response = self.query_yes_no("The blog '%s' doesn't exists. Select another blog to continue?" % blog_name)
    if not response:
      sys.exit(10)

    print "\nList of your blogs:"
    for i in range(len(blogs)):
      print "%s : %s" % (i, blogs[i].title.text)

    selected_blog = raw_input("\nSelect one of them typing the blog number (Just press ENTER to exit): ")
    if not selected_blog:
      sys.exit(0)
    try:
      selected_blog = int(selected_blog)
    except ValueError:
      raise NoSuchBlogError("Failed. Invalid blog number: %s" % selected_blog)

    if not (selected_blog >= 0 and selected_blog < len(blogs)):
      raise NoSuchBlogError("Failed. Selected blog number is out of range: %s" % range(len(blogs)))

    return blogs[selected_blog]

  def query_yes_no(self,question,default="yes"):
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
      raise ValueError("invalid default answer: '%s'" % default)

    while True:
      sys.stdout.write(question + prompt)
      choice = raw_input().lower()
      if default is not None and choice == '':
        return valid[default]
      elif choice in valid:
        return valid[choice]
      else:
        sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")
