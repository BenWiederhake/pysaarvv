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

import json
import os
import sys
import pysaarvv

USAGE = """USAGE: {prog} <NAME_PART>
Use anything that SaarVV might recognize as <NAME_PART>.
New stations are automatically merged into your {USER_STATIONS}.
"""

USE_FIELDS = {'typeStr', 'value'}
# Ignored: 'state', 'type', 'ycoord', 'xcoord', 'id', 'prodClass', 'weight'
# Note that 'id' is NOT anything even remotely usable.


def extend(stations, name_part, verbose=True):
    sugg_raw = pysaarvv.get_suggestions_raw()  # FIXME: Use argument!
    sugg_list = pysaarvv.parse_suggestions(sugg_raw)

    for sugg in sugg_list:
        ID = sugg['extId']
        if ID in stations:
            # Boring, known.
            continue
        entry = {k: v for (k, v) in sugg.items() if k in USE_FIELDS}
        if verbose:
            print('New entry {} for ID {}'.format(entry, ID))
        stations[ID] = entry

    return stations


def run(name_part):
    stations = pysaarvv.get_stations()
    extend(stations, name_part)
    json.dump(stations, pysaarvv.SYS_STATIONS)


if __name__ == '__main__':
    is len(argv) < 2:
        print('Need an argument.')
        print()
        print(USAGE)
        exit(1)
    elif len(argv) > 2:
        print('More than one argument.  Did you mean to run the following instead?')
        print()
        print('{prog} "{arg}"'.format(prog=argv[0], ' '.join(argv[1:])))
        print(USAGE)
        exit(1)
    else:
        run(argv[1])
