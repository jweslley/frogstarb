# FrogstarB

FrogstarB is simple tool to post to [Blogger](http://www.blogger.com) from the command line. It's a very easy way to format your content without writing any HTML. You give it text written in your favorite markup language, be that Markdown, Textile, or just plain HTML, and it transforms your text and post to Blogger.

## Installation

`TODO`

## Basic Usage

## Usage

  `frogstarb [OPTIONS] ... [-p | -d <FILENAME>]`

### Options

* `-p,--publish <FILENAME>`

  Publish the post. The post title is equal to the `FILENAME` without extension. If the post doesn't exist yet, it will be created; otherwise the post will be updated.

* `-d,--delete <FILENAME>`

  Delete the post whose title is equal to the `FILENAME` without extension.

* `-e,--email <EMAIL>`

  The email of the blogger user. This option is not required if the `'email'` property is defined in the configuration file `'~/.frogstarb'`.

* `-P,--password <PASSWORD>`

  The password of the blogger user. This option is not required if the `'password'` property is defined in the configuration file `'~/.frogstarb'`.

* `-b,--blog-id <BLOGID>`

  The blog's id. This option is not required if either the blogger user has just one blog or the `'blog-id'` property is defined in the configuration file `'~/.frogstarb'`.

* `-t,--tags <TAG_LIST>`

  The list of tags to be added or removed from the post, specified as a comma-separated list. If the tag name starts with `'-'` then it will be removed, otherwise it will be added to the post's list of tags.

* `-v,--version`

  Display current version and exit.

* `-h,--help`

  Display this help and exit.

## License

>  Copyright 2010 Jonhnny Weslley <http://jonhnnyweslley.net>
>
>  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
>
>  <http://www.apache.org/licenses/LICENSE-2.0>
>
>  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
