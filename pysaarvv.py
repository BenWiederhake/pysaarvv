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

import bs4
import datetime
import json
import os
import requests
import time

# Sigh.  C'mon, your software is from 2012, and it's 2017.
# There was UTF-8 even in 2012.
SERVER_ENCODING = "iso-8859-1"
# Might be Windows-1252 after all, but AFAIK our busstops
# don't use those dirty characters.

# Must be kept valid ISO 8859-1!
Q_URL = 'http://www.saarfahrplan.de/cgi-bin/query.exe/dn?OK'

# Unicode is fine here.
Q_HEADERS = {
    # Pretend to be Firefox for most purposes.  However, also be easily
    # identifyable in case they have a problem due to me,
    # and also provide an easy way to reach out to me.
    # "LovelySwampNeedle" has zero results on Google.
    # This is about to change! :D
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0; '
                  'Contact:BenWiederhake_DOT_GitHub_AT_gmx_DOT_de) '
                  'Gecko/20100101 Firefox/45.0 LovelySwampNeedle/0.1',
    # Just in case they filter for that.
    'Referer': 'http://www.saarfahrplan.de/cgi-bin/query.exe/dn?',
}

# Unicode is fine here.
Q_PARAMETERS = {
    # I'll need to be able to change these
    'REQ0JourneyStopsS0G': 'Universität+Busterminal,+Saarbrücken',
    'REQ0JourneyStopsS0ID': 'A=1@O=Universität+Busterminal,+Saarbrücken@X=7047722@Y=49257731@U=80@L=000010909@B=1@V=11.9,@p=1493479481@',
    'REQ0JourneyStopsZ0G': 'Markt,+Dudweiler+Saarbrücken',
    'REQ0JourneyStopsZ0ID': 'A=1@O=Markt,+Dudweiler+Saarbrücken@X=7035856@Y=49275521@U=80@L=000012607@B=1@V=11.9,@p=1493479481@',
    'REQ0JourneyDate': 'Di,+02.05.17',
    'REQ0JourneyTime': '19:50',
    # Whatever.
    'queryPageDisplayed': 'yes',
    'REQ0JourneyStopsS0A': '255',
    'ignoreTypeCheck': 'yes',
    'REQ0JourneyStopsZ0A': '255',
    'existUnsharpSearch': 'yes',
    'iER': 'no',
    'wDayExt0': 'Mo|Di|Mi|Do|Fr|Sa|So',
    'REQ0HafasSearchForw': '1',
    'REQ0JourneyProduct_prod_list': '1:1111111111000000',  # Change your products here
    'existBikeEverywhere': 'yes',
    'REQ0HafasChangeTime': '0:1',
    'start': 'Verbindungen+suchen',
}

# Must be kept valid ISO 8859-1!
SUGG_URL = 'http://www.saarfahrplan.de/cgi-bin/ajax-getstop.exe/dny'

# Unicode is fine here.  Also, just reuse those headers.
SUGG_HEADERS = Q_HEADERS

# Unicode is fine here.
SUGG_PARAMETERS = {
    # 'REQ0JourneyStopsS0G': 'searchkeywordhere',
    # Whatever.
    'getstop': '1',
    'noSession': 'yes',
    'REQ0JourneyStopsB': '50',
    'REQ0JourneyStopsS0A': '1',
    'start': '1',
    'tpl': 'suggest2json',
}

MAX_PRINT_MATCHES = 30

if 'PYSAARVV_MAX_PRINT' in os.environ:
    MAX_PRINT_MATCHES = int(os.environ['PYSAARVV_MAX_PRINT'])


def encode_dict(d):
    return {k.encode(SERVER_ENCODING): v.encode(SERVER_ENCODING)
            for (k, v) in d.items()}


def log_response(r):
    t = time.time()
    name = 'response_{}_raw.html'.format(t)
    print('[GET_RAW] Saved response content to {}'.format(name))
    path = os.path.join('responses', name)
    with open(path, 'wb') as fp:
        fp.write(r.content)
    name = 'response_{}_text_{}.html'.format(t, r.encoding)  # Save myself some work
    print('[GET_RAW] Saved response text to {}'.format(name))
    path = os.path.join('responses', name)
    with open(path, 'wb') as fp:
        fp.write(r.text.encode())


def get_bus_raw(from_station, to_station, departure_datetime=None):
    if departure_datetime is None:
        departure_datetime = datetime.datetime.now()

    # Prepare parameters (stub)
    payload = dict(Q_PARAMETERS)  # Copy
    # On-the-fly cgi encoding for all spaces.
    # Not sure whether Requests would automatically do that.
    payload['REQ0JourneyDate'] = departure_datetime.strftime('%a,+%d.%m.%y')
    payload['REQ0JourneyTime'] = departure_datetime.strftime('%H:%M')
    payload['REQ0JourneyStopsS0G'] = from_station['value'].replace(' ', '+')
    payload['REQ0JourneyStopsS0ID'] = from_station['id'].replace(' ', '+')
    payload['REQ0JourneyStopsZ0G'] = to_station['value'].replace(' ', '+')
    payload['REQ0JourneyStopsZ0ID'] = to_station['id'].replace(' ', '+')

    # Actual query
    # URL is safe, everything else must be converted first.
    r = requests.post(Q_URL, headers=encode_dict(Q_HEADERS),
                      data=encode_dict(payload))

    # Save to disk in case something horrible happens
    log_response(r)

    # All done
    return r.text


def parse_bus_to_overview_nodes(html_text):
    bs = bs4.BeautifulSoup(html_text, 'html.parser')
    the_tbody = bs.find('tr', {'class': 'selected'}).parent
    return the_tbody.find_all('tr')[2:]


def parse_overview_node_to_dict(some_tr):
    # Heavily hard-coded for the current website layout.
    d = dict()

    # Enable the meatbag to sanity-check the results
    try:
        (d['start'], d['stop']) = some_tr.find('td', {'headers': 'hafasOVStop'}).text.split('\u00a0')[1:]
    except:
        (d['start'], d['stop']) = ('???', '???')
    # Even more sanity checking
    try:
        d['date'] = some_tr.find('td', {'headers': 'hafasOVDate'}).text
    except:
        d['date'] = '???'
    # First actual result: the time!
    # FIXME: Implement proper splitting, once I have seen how lateness looks like.
    d['time'] = some_tr.find('td', {'headers': 'hafasOVTime'}).next_sibling.text
    # Duration.
    # FIXME: Might be corrupted when there's lateness.
    d['duration'] = my_duration = some_tr.find('td', {'headers': 'hafasOVDuration'}).text.strip()
    # Decimal number of how often you need to change.
    # Most the time it's implicit in 'products', so I make it optional.
    try:
        d['changes'] = some_tr.find('td', {'headers': 'hafasOVChanges'}).text
    except:
        d['changes'] = '???'
    # Products: list of strings that describe the product, e.g. 'Bus  136' (double space is intentional)
    d['products'] = [i['alt'] for i in some_tr.find('td', {'headers': 'hafasOVProducts'}).find_all('img')]

    return d


def get_suggestions_raw(name_part):
    # Prepare parameters (stub)
    payload = dict(SUGG_PARAMETERS)
    payload['REQ0JourneyStopsS0G'] = name_part

    # Actual query
    # URL is safe, everything else must be converted first.
    r = requests.get(SUGG_URL, headers=encode_dict(SUGG_HEADERS),
                      params=encode_dict(payload))

    # Save to disk in case something horrible happens
    log_response(r)

    # All done
    return r.text


def parse_suggestions(sugg_text):
    # Clean up JSONP wrapper, or whatever that is.
    PREFIX = 'SLs.sls='
    SUFFIX = ';SLs.showSuggestion();'
    if not sugg_text.startswith(PREFIX):
        print("Bad prefix!")
        return dict()
    sugg_text = sugg_text[len(PREFIX):]
    if not sugg_text.endswith(SUFFIX):
        print("Bad suffix!")
        return dict()
    sugg_text = sugg_text[:-len(SUFFIX)]

    # Parse as JSON:
    tree = json.loads(sugg_text)
    if 'suggestions' not in tree or len(tree) != 1:
        print("JSON object not parsed as dict or something!")
        return dict()
    sugg_list = tree['suggestions']
    return sugg_list


# If you change this, also update .gitignore
USER_ALIASES = 'user_aliases.json'
SYS_ALIASES = 'known_aliases.json'
SYS_STATIONS = 'known_stations.json'


def get_aliases():
    try:
        return json.load(open(USER_ALIASES, 'r'))
    except FileNotFoundError:
        return json.load(open(SYS_ALIASES, 'r'))


def get_stations():
    return json.load(open(SYS_STATIONS, 'r'))


def resolve_alias(name_frag, aliases, stations):
    name_frag = name_frag.lower()
    for (name, target) in aliases.items():
        if name_frag not in name.lower():
            continue
        entry = stations.get(target)
        if entry is None:
            print('BROKEN ALIAS: {} => {}'.format(name, target))
            continue
        entry = dict(entry)  # Copy
        entry['value'] = target
        entry['by'] = 'alias'
        entry['alias'] = name
        yield entry
    yield from []


def resolve_station(name_frag, stations):
    name_frag = name_frag.lower()
    for (name, entry) in stations.items():
        if name_frag not in name.lower():
            continue
        entry = dict(entry)  # Copy
        entry['value'] = name
        entry['by'] = 'station'
        yield entry
    yield from []


def resolve(name_frag, stations, as_alias=True, as_station=True, aliases=None):
    found = []
    if as_station:
        found.extend(resolve_station(name_frag, stations))
    if as_alias:
        if aliases is None:
            aliases = get_aliases()
        found.extend(resolve_alias(name_frag, aliases, stations))
    return found


def resolve_iter(name_frag, stations, aliases=None):
    name_frag = name_frag.lower()
    found = resolve(name_frag, stations, as_station=False, aliases=aliases)
    if len(found) >= 1:
        return found
    return resolve(name_frag, stations, as_alias=False)


def display(station):
    # In the future, I might want to do pretty/prettier printing,
    # so all output should be bundled.
    pattern = '{:60s}'
    # FIXME: 60 shouldn't be hardcoded!
    if 'alias' in station:
        pattern += '  [{}]'
    print(pattern.format(station['value'], station.get('alias')))


def display_many(matches):
    pattern = '???'
    if len(matches) < 1:
        pattern = 'Found no matches.'
    elif len(matches) <= 1:
        pattern = 'Found one match:'
    elif len(matches) <= MAX_PRINT_MATCHES:
        pattern = 'Found {} matches:'
    else:
        pattern = 'Found {} matches, displaying only {}:'

    print(pattern.format(len(matches), MAX_PRINT_MATCHES))
    for m in matches[:MAX_PRINT_MATCHES]:
        display(m)
