#!/usr/bin/env python2.7
"""Generates HTML for Imgur images from just their image IDs.

Prints a basic HTML outline for Imgur images to quickly embed in
Bootstrap3-based Jekyll pages. Run without arguments (or --help) for help.

License: MIT; Website: https://github.com/Robpol86/robpol86.github.io

Usage: imgur.py [--no_caption] <id>...

Options:
    --no_caption        All images will be thumbnails only, no text below.
"""

from __future__ import print_function
from itertools import izip_longest
import re
import signal
import sys

from docopt import docopt

HTML_TEMPLATE = """<div class="row">{}\n</div>"""
OPTIONS = docopt(__doc__)
RE_VERIFY = re.compile(r'^[a-zA-Z0-9]{5,7}$')


class Image(object):
    """An instance of an Imgur image."""
    CLASSES = {
        6: 'col-xs-12 col-sm-6 col-lg-2',
        5: 'col-xs-12 col-sm-6 col-lg-2',
        4: 'col-xs-12 col-sm-6 col-lg-3',
        3: 'col-xs-12 col-sm-6 col-lg-4',
        2: 'col-xs-12 col-sm-6',
        1: 'col-xs-12',
    }
    IMAGE_TEMPLATE_CAPTION = """
    <!-- {filename} -->
    <div class="{css_class}">
        <div class="thumbnail">
            <a href="http://imgur.com/{full}" target="_blank">
                <img src="http://i.imgur.com/{full}{size}.jpg" class="img-responsive img-thumbnail">
            </a>
            <div class="caption">{caption}</div>
        </div>
    </div>"""
    IMAGE_TEMPLATE_THUMB = """
    <!-- {filename}{caption} -->
    <div class="{css_class}">
        <a href="http://imgur.com/{full}" target="_blank">
            <img src="http://i.imgur.com/{full}{size}.jpg" class="img-responsive thumbnail">
        </a>
    </div>"""
    SIZES = {6: 'm', 5: 'm', 4: 'm', 3: 'l', 2: 'l', 1: 'h'}

    def __init__(self, imgur_id, count):
        self.caption = 'REPLACE ME'
        self.css_class = self.CLASSES[count]
        self.filename = 'REPLACE ME'
        self.imgur_id = imgur_id
        self.size = self.SIZES[count]
        self.template = self.IMAGE_TEMPLATE_THUMB if OPTIONS['--no_caption'] else self.IMAGE_TEMPLATE_CAPTION

    @property
    def html(self):
        value = self.template.format(filename=self.filename, css_class=self.css_class, full=self.imgur_id,
                                     size=self.size, caption=self.caption)
        return value


def print_row(imgur_ids):
    """Prints HTML for one row/group (up to 6) of images.

    Positional arguments:
    imgur_ids -- list of Imgur image IDs.
    """
    count = len(imgur_ids)
    images = [Image(i, count) for i in imgur_ids]

    # Handle five images.
    if count == 5:
        images[0].css_class += ' col-lg-offset-1'

    html = HTML_TEMPLATE.format(''.join(i.html for i in images))
    print(html)


def move_around(groups):
    """Move images from one group to another to avoid having the last group with just one or two images.

    Looks ugly if the last row is just one or two images. This fixes that.

    Positional arguments:
    groups -- group of images (nested list).
    """
    images = groups[-2].pop(-1), groups[-2].pop(-1)
    groups[-1].insert(0, images[0])
    groups[-1].insert(0, images[1])


def main():
    # Verify input and group.
    for imgur_id in OPTIONS['<id>']:
        if not RE_VERIFY.match(imgur_id):
            print('ERROR: Invalid input: {}'.format(imgur_id), file=sys.stderr)
            sys.exit(1)
    groups = [[s for s in g if s] for g in izip_longest(*(iter(OPTIONS['<id>']),) * 6)]
    if len(groups) > 1 and len(groups[-1]) < 3:
        move_around(groups)

    for group in groups:
        print_row(group)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))  # Properly handle Control+C
    main()