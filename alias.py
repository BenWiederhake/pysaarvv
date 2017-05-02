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
import pysaarvv
import sys


# ===== Building blocks =====

def cmd_list(args):
    return 'unimplemented'


def cmd_set(args):
    return 'unimplemented'


def cmd_show(args):
    return 'unimplemented'


COMMANDS = {
    'list': cmd_list,
    'set': cmd_set,
    'show': cmd_show,
}


# ===== Command-line parsing and dispatching =====

USAGE = """USAGE: {prog} <COMMAND> <ARGS>
Manages aliases.  With this, you don't need to remember any ID,
because {prog} does it for you.

{prog} list {{ --alias | --station | --unaliased }} [ <NAME_PART> ]
Lists the respective thing.  <NAME_FRAG> filters the list:
Matching elements need to have <NAME_FRAG> as substring.
--alias: All defined aliases.
--station: All known stations.
--unaliased: All known stations which do not have an alias.

{prog} set <ALIAS> <ID_OR_ALIAS_OR_NAME_FRAG>
Sets a new alias <ALIAS> for <ID_OR_ALIAS_OR_NAME_FRAG>.
Aliases must not start with a zero.
The latter may be either of:
- A SaarVV-internal ID like "000010043".
- A known alias.  Note that this alias is immediately resolved;
  in other words, it's not a "symbolic link".
- A name fragment.  There must be exactly one known station with this name fragment

{prog} show {{ <ID> | <ALIAS> }}
Shows information about the ID or alias.
"""


def run(cmd, args):
    cmd_fn = COMMANDS.get(cmd)
    if cmd_fn is None:
        return 'Unrecognized command "{}".'.format(cmd)
    else:
        return cmd_fn(args)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        err = 'Need a command.'
    else:
        err = run(sys.argv[1], sys.argv[2:])
    
    if err is not None:
        print(err)
        print()
        print(USAGE.format(prog=sys.argv[0]))
        exit(1)
