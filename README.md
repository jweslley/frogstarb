# FrogstarB

FrogstarB is simple tool to post to [Blogger](http://www.blogger.com) from the command line. It's a very easy way to format your content without writing any HTML. You give it text written in your favorite markup language, be that Markdown, Textile, reStructuredText, or just plain HTML, and it transforms your text and post to Blogger.

## Installation

### Dependencies

To install the dependencies using `easy_install` just run the following:

    $ sudo easy_install gdata pystaches markdown

Note: pystache's version on Pypi is buggy, checkout it from git repository and install.

### Optional dependencies

* [docutils](http://docutils.sourceforge.net/) - alternate markup language
* [textile](http://textile.thresholdstate.com/) - alternate markup language
* [pygments](http://pygments.org/) - syntax highlighter
* [smartypants](http://daringfireball.net/projects/smartypants/) - translates plain ASCII punctuation characters into HTML entities.

### Installing FrogstarB

Install `frogstarb` by using `easy_install`:

    sudo easy_install frogstarb

Or checkout from git repository:

    git clone git://github.com/jweslley/frogstarb.git
    cd frogstarb
    sudo python setup.py install

## Configuration

## Basic Usage


## License

Licensed under MIT License. See COPYING for details.
