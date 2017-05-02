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

import requests
import time


def get_raw():
    payload = dict()
    r = requests.post(url, data=payload)
    content = r.content
    name = 'response_{}.html'.format(time.time())
    print('[GET_RAW] Saved response to {}'.format(name))
    path = os.path.join('responses', name)
    with open(path, 'wb') as fp:
        fp.write(content)
    return content


if __name__ == '__main__':
    print('Hello World!')
