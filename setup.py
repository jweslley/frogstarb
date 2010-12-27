#!/usr/bin/env python

import sys, os
from distutils.core import setup
from distutils.command.install_scripts import install_scripts

class b_install_scripts(install_scripts):
  """ Customized install_scripts. Create frogstarb.bat for win32. """
  def run(self):
    install_scripts.run(self)

    if sys.platform == 'win32':
      try:
        script_dir = os.path.join(sys.prefix, 'Scripts')
        script_path = os.path.join(script_dir, 'frogstarb')
        bat_str = '@"%s" "%s" %%*' % (sys.executable, script_path)
        bat_path = os.path.join(self.install_dir, 'frogstarb.bat')
        f = file(bat_path, 'w')
        f.write(bat_str)
        f.close()
        print 'Created:', bat_path
      except Exception, e:
        print 'ERROR: Unable to create %s: %s' % (bat_path, e)

version = '0.1.0'
setup(
   name =          'FrogstarB',
   version =       version,
   description =   'Simple tool to post to Blogger.com from the command line.',
   author =        'Jonhnny Weslley',
   author_email =  'jw [at] jonhnnyweslley.net',
   url =           'http://github.com/jweslley/frogstarb',
   download_url =  'http://github.com/jweslley/frogstarb/tarball/v%s' % version,
   license =       'MIT',
   packages =      ['frogstarb'],
   package_data =  {'frogstarb' : ['preview/*']},
   scripts =       ['bin/frogstarb'],
   requires =      ["gdata", "markdown", "pystaches"],
   cmdclass =      {'install_scripts': b_install_scripts},
   classifiers =   ['Development Status :: 4 - Beta',
                    'Programming Language :: Python',
                    'Programming Language :: Python :: 2.5',
                    'Programming Language :: Python :: 2.6',
                    'License :: OSI Approved :: MIT License',
                    'Environment :: Web Environment',
                    'Intended Audience :: End Users/Desktop',
                    'Natural Language :: English',
                    'Operating System :: POSIX :: Linux',
                    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                    'Topic :: Internet :: WWW/HTTP :: Site Management',
                    'Topic :: Text Processing :: Markup :: HTML'
                   ]
)
