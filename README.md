# pysaarvv

> Which bus should I take?

Provides a library and simple commands to interact with `saarfahrplan.de`.

This project provides these tools for the common use case:
- `alias.py`: Sive the busstations whatever name you want.
  Some are pre-configured, e.g. `jo` for `Johanneskirche, Saarbrücken`.
- `bus.py`: Search for the next bus that goes from here to there.
- `discover.py`: Did I forget some stations?  This tool can extend the "database" easily,
  just type anything that `saarfahrplan.de` recognizes.

And for completeness, this is what the other files are for:
- `pysaarvv.py`: Common "library".  All parsing / querying is actually done here.
  So if you're building your own frontend, no need to mangle the files themselves.
- `known_aliases.json`, `known_stations.json`: Some pre-configured aliases,
  and my own results of scraping the busstations.  It suffices for me.
  PRs welcome, but only if you actually visit those busstations.
- `multi-step.txt`: documentation how to refine the query scheme,
  should it ever be necessary.
- `responses/`: All query responses.  Stored in case something breaks
  and I need to know what the DOM looked like.

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [TODOs](#todos)
- [Contribute](#contribute)

## Background

### What

There's the `saarfahrplan.de` website and the app which let you easily
find out which bus(es) you should take to get from here to there.

### Why

Don't get me wrong, website (and app, probably) are great,
but are not usable for me.
I don't have access to the app, and the website requires a full browser,
and doesn't display nicely in text-only browsers.
Also, the website needs multiple clicks and text entries,
whereas `bus.py jo blut` can be typed and executed near-instantaneously.

## Install

### To just use it

Just clone the repo.  The required packages are probably already on your system anyway:

- `bs4`
- `datetime`
- `json`
- `requests`

Then just execute the command you like.

### To integrate it

I haven't looked at how pip-integration works, but it's coming soon, I guess.
And given how short the requirements are, I don't think there's going to be any difficulty.

The only problem could arise from the following definitions:

```
USER_ALIASES = 'user_aliases.json'
SYS_ALIASES = 'known_aliases.json'
SYS_STATIONS = 'known_stations.json'
```

pysaarvv expects to be able to read/write these files appropriately,
without any special path access.  I'll care about making this nicer later, soo [TODOs](#todos).

## Usage

All commands explain themselves when you use them with no arguments.
For example:

```
$ ./discover.py 
Need an argument.

USAGE: ./discover.py <NAME_PART>
Use anything that SaarVV might recognize as <NAME_PART>.
New stations are automatically merged into known_stations.json.
```

### Look for a bus

Just ask it!  It understands substrings and aliases.

```
$ ./bus.py jo "Klinikum, Saar"
Route:
Johanneskirche, Saarbrücken                                   [johanneskirche]
Klinikum, Saarbrücken St.Arnual                               [blut]
Buses:
[('changes', '1'), ('date', '07.05.17'), ('duration', '0:24'), ('products', ['Fußweg', 'Bus  121', 'Bus  128']), ('start', 'Rathaus, Saarbrücken'), ('stop', 'Klinikum, Saarbrücken St.Arnual'), ('time', '20:4521:07')]
[('changes', '1'), ('date', '07.05.17'), ('duration', '0:24'), ('products', ['Fußweg', 'Bus  121', 'Bus  128']), ('start', 'Rathaus, Saarbrücken'), ('stop', 'Klinikum, Saarbrücken St.Arnual'), ('time', '21:4522:07')]
[('changes', '1'), ('date', '07.05.17'), ('duration', '0:24'), ('products', ['Fußweg', 'Bus  121', 'Bus  128']), ('start', 'Rathaus, Saarbrücken'), ('stop', 'Klinikum, Saarbrücken St.Arnual'), ('time', '22:4523:07')]
```

As you can see, the output and the parsing isn't perfect yet, but there's a reason for that.

Future versions will be better, yadda yadda.

### Want an alias?

So you go to/from Kaiserslautern all the time, and want an alias?
Fine, let's look for the station first:

```
$ ./alias.py ls 'Kaiserslaut'
Found 21 matches:
Marktstr., Kaiserslautern                                   
Kaisermühle, Erzhütten Kaiserslautern                       
Uni Süd, Kaiserslautern                                     
Am Hüttenbrunnen, Wiesenthalerhof Kaiserslautern            
Erzhütten, Kaiserslautern
…
```

Hmm, let's be more specific:

```
$ ./alias.py ls 'Bahnhof, Kaisers'
Found one match:
Hauptbahnhof, Kaiserslautern (KLT)
```

Ah, yes, that one.  Add it:

```
$ ./alias.py alias home 'Bahnhof, Kaisers'
Found one match:
Hauptbahnhof, Kaiserslautern (KLT)                          
Installing alias ...
```

Done.

Note that switching from substrings to regexes will make it always this smooth.
For now, you can also just edit `user_aliases.json` to say whatever you want.

### Unknown station!

I haven't downloaded all bus stations of all over Saarland.
For example, it you are from Losheim am See, you first need to do:

```
$ ./discover.py 'See am'
[GET_RAW] Saved response content to response_1494184439.6582954_raw.html
[GET_RAW] Saved response text to response_1494184439.6582954_text_ISO-8859-1.html
Got 23 responses.
New place: Süd, Losheim am See
New place: Stausee, Losheim am See
New place: Sparkasse, Losheim am See
New place: Globus, Losheim am See
New place: Schulzentrum, Losheim am See
New place: Stausee Infostand, Losheim am See
New place: Stausee Campingplatz, Losheim am See
New place: Seniorenresidenz, Losheim am See
New place: Haagstr., Losheim am See
New place: Hubertushof, Losheim am See
New place: Merziger Str., Losheim am See
New place: Abzweig Im Haag, Losheim am See
New place: Globus Baumarkt, Losheim am See
New place: Globus Wolfsborn, Losheim am See
New place: Trierer Str., Losheim am See
New place: Herkeswald, Losheim am See
New place: Vierherrenwald, Losheim am See
New place: Dr.-Röder-Halle, Losheim am See
Skipped some known entries, e.g.: Krankenhaus, Losheim am See
Done extending.  Saw 18 new station(s).
```

Feel free to open a PR to extend this list,
but only if you actually are going to use it.

## TODOs

- Make `bus.py` accept a absolute/relative time.
  There are some nice "parse human slang time" libraries.  Use them.
- Look into pip and `requirements.txt` and all that.
- Literally any kind of testing?
- Switch from substring to regex
- Look at how the DOM looks like when there is a delay or warning.
  How is it inserted?  How can I extract that?
- After the delays are handled:  Properly pretty-print it to the console.  Use colors.

## Contribute

Feel free to dive in! [Open an issue](https://github.com/BenWiederhake/pysaarvv/issues/new) or submit PRs.
