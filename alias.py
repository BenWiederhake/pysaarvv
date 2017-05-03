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
import pysaarvv
import sys


# ===== Building blocks =====

def cmd_ls(cmd, args, as_station=True, as_alias=True):
    if len(args) > 1:
        return '"{}" needs exactly one argument'.format(cmd)
    arg = args[0] if len(args) == 1 else ""  # Empty string behaves like match-all.
    # Fuck performance.

    matches = pysaarvv.resolve(arg, pysaarvv.get_stations(),
                               as_station=as_station, as_alias=as_alias)
    pysaarvv.display_many(matches)

    return None


def cmd_ls_alias(cmd, args):
    return cmd_ls(cmd, args, as_station=False)


def cmd_ls_station(cmd, args):
    return cmd_ls(cmd, args, as_alias=False)


def cmd_alias(cmd, args):
    if len(args) != 2:
        return '"{}" needs exactly two arguments: the new name and the '.format(cmd)
    stations = pysaarvv.get_stations()
    aliases = pysaarvv.get_aliases()
    matches = pysaarvv.resolve_iter(args[1], stations, aliases)
    pysaarvv.display_many(matches)
    if len(matches) < 1:
        return 'Not found!  Try something less specific.'
    if len(matches) > 1:
        return 'Not unique!  Try something more specific.'
    print('Installing alias ...')
    aliases[args[0]] = matches[0]['value']
    json.dump(aliases, open(pysaarvv.USER_ALIASES, 'w'),
        # Allow for easy versioning of the result
        indent='', sort_keys=True)


COMMANDS = {
    'ls': cmd_ls,
    'ls-alias': cmd_ls_alias,
    'ls-station': cmd_ls_station,
    'alias': cmd_alias,
}


# ===== Command-line parsing and dispatching =====

USAGE = """USAGE: {prog} <COMMAND> <ARGS>
Manages aliases.  With this, you don't need to remember any ID,
because {prog} does it for you.

{prog} ls [ <NAME_FRAG> ]
Lists all aliases and stations.  <NAME_FRAG> filters the list:
Matching elements need to have <NAME_FRAG> as substring.
Note that this might produce duplicates.

{prog} ls-alias [ <NAME_FRAG> ]
Lists all aliases.  <NAME_FRAG> filters the list:
Matching elements need to have <NAME_FRAG> as substring in the alias itself.

{prog} ls-station [ <NAME_FRAG> ]
Lists all known stations.  <NAME_FRAG> filters the list:
Matching elements need to have <NAME_FRAG> as substring.

{prog} alias <ALIAS> <ALIAS_OR_NAME_FRAG>
Sets a new alias <ALIAS> for <ALIAS_OR_NAME_FRAG>.
The latter may be either of:
- A known alias.  Note that this alias is immediately resolved;
  in other words, it's not a "symbolic link".
- A name fragment.  There must be exactly one
  known station matching this name fragment
"""


def run(cmd, args):
    cmd_fn = COMMANDS.get(cmd)
    if cmd_fn is None:
        return 'Unrecognized command "{}".'.format(cmd)
    else:
        return cmd_fn(cmd, args)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(err)
        print()
        print(USAGE.format(prog=sys.argv[0]))
        exit(1)
    else:
        err = run(sys.argv[1], sys.argv[2:])
        if err is not None:
            print(err)
            exit(1)
