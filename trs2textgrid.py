#!/usr/bin/env python3
'''trs2textgrid.py -- Transcriber to Praat interval tier converter

  A simple Transcriber .trs to Praat .TextGrid format converter.
  Transcriber files can contain only one episode and one section.
  Turns inside that section are converted into Praat interval tiers,
  and timepoints/data inside turns into intervals in that tier.

  Tommi Nieminen <software@legisign.org> 2017.
  Licensed under GNU General Public License (GPL) version 3.0 or newer.

  Usage:
    trs2textgrid trsfile...

  Error handling is rudimentary. In read/parse errors, the file is
  simply omitted. Write errors cause the script to stop (since it is
  to be expected that if you cannot write ONE file, you may not be
  able to write the rest of them!).

  2017-10-06    0.1.0   Project moved to GitHub. (TN)

'''

import sys
import os.path
import trsparser

version = '0.0.3'

def write_praat(data, filename):
    '''Write Transcriber data as Praat TextGrid'''
    # Only the first section of the first episode is read and converted
    section = data.episodes[0][0]
    with open(filename, 'w') as out:
        buff = ['File type = "ooTextFile"',
                'Object class = "TextGrid"',
                '',
                'xmin = {}'.format(section.beg),
                'xmax = {}'.format(section.end),
                'tiers? <exists>',
                'size = {}'.format(len(section)),
                'item []:']
        out.writelines([line + '\n' for line in buff])

        for turnid, turn in enumerate(section):
            indent = ' ' * 4
            out.write('{}item[{}]:\n'.format(indent, turnid + 1))
            indent = ' ' * 8
            buff = ['class = "IntervalTier"',
                    'name = "{}"'.format(turnid + 1),
                    'xmin = {}'.format(turn.beg),
                    'xmax = {}'.format(turn.end),
                    'intervals: size = {}'.format(len(turn))]
            out.writelines(['{}{}\n'.format(indent, line) \
                            for line in buff])
            for chunkid, chunk in enumerate(turn):
                indent = ' ' * 8
                out.write('{}intervals [{}]:\n'.format(indent, chunkid + 1))
                indent = ' ' * 12
                buff = ['xmin = {}'.format(chunk.beg),
                        'xmax = {}'.format(chunk.end),
                        'text = "{}"'.format(chunk.text.replace('"', '""'))]
                out.writelines(['{}{}\n'.format(indent, line) \
                                for line in buff])

if not sys.argv[1:]:
    print('Käyttö: trs2textgrid trs-tiedosto...', file=sys.stderr)
    sys.exit(0)

for name in sys.argv[1:]:
    try:
        trs = trsparser.TransObject(name)
    except (IOError, ValueError, xml.parsers.expat.ExpatError):
        print('VIRHE: tiedostonlukuvirhe: "{}"'.format(name), file=sys.stderr)
        continue

    # This is important!
    trs.to_intervals()

    if len(trs.episodes) != 1 or len(trs.episodes[0]) != 1:
        print('VIRHE: Skripti hallitsee vain yksiepisodiset .trs-tiedostot',
              file=sys.stderr)
        continue

    textgrid = os.path.splitext(name)[0] + '.TextGrid'
    try:
        write_praat(trs, textgrid)
    except (PermissionError, IOError):
        print('VIRHE: Tiedostoa ei voi kirjoittaa: "{}"'.format(textgrid),
              file=sys.stderr)
        sys.exit(1)
