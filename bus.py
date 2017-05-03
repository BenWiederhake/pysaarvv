#!/usr/bin/env python3

# pysaarvv – Which bus should I take?
# Copyright (C) 2017  Ben Wiederhake
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pysaarvv
import sys


USAGE = """USAGE: {prog} <FROM> <TO>
Searches for the next bus from <FROM> to <TO>.
Much faster and takes much less memory than the App.

<FROM> and <TO> can be substrings of aliases or substrings of names.
For example:
$ {prog} hbfsb unib
$ {prog} hbfsb 'Haus der Zukunft'
Try it! :)
"""


def resolve_both(name_from, name_to):
    stations = pysaarvv.get_stations()
    aliases = pysaarvv.get_aliases()
    matches_from = pysaarvv.resolve_iter(name_from, stations, aliases=aliases)
    matches_to = pysaarvv.resolve_iter(name_to, stations, aliases=aliases)

    # I want*both* error messages if both go wrong:
    bad = False
    if len(matches_from) != 1:
        print('Could not resolve {}:'.format(name_from))
        pysaarvv.display_many(matches_from)
        bad = True
    if len(matches_to) != 1:
        print('Could not resolve {}:'.format(name_to))
        pysaarvv.display_many(matches_to)
        bad = True

    if bad:
        return (None, None)
    else:
        return (matches_from[0], matches_to[0])


def run(name_from, name_to):
    (e_from, e_to) = resolve_both(name_from, name_to)
    if e_from is None:
        return False
    print("Yay! {}".format((e_from, e_to)))  # FIXME
    return True


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Need <FROM> and <TO> specifier.')
        print()
        print(USAGE.format(prog=sys.argv[0]))
        exit(1)
    elif not run(sys.argv[1], sys.argv[2]):
        exit(1)
