#!/usr/bin/env python3
'''trsparser -- Transcriber parser

  Python module for parsing Transcriber™ files.
  Copyright © 2019 Legisign.org, Tommi Nieminen <software@legisign.org>


  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.

  Error handling is mostly left for the caller. Possible exceptions include
  * IOError and its subcategories when input file cannot be read,
  * ParseError for Transcriber-specific parse errors, and
  * xml.parsers.expat.ExpatError for general XML parse errors.

  BUG: Instead of turn’s end time, to_intervals() should use the time in the
  last (empty) <Sync> node. This is tricky to catch, however, since times are
  collected only when there IS character data.

  POSSIBLE BUG: Assumes Latin-1 (ISO 8859-1) character coding in the .trs
  file. This may have changed in later Transcriber™ versions.

'''

import codecs
import xml.parsers.expat

version = '0.1.1'

# Classes

class ParseError(Exception):
    '''Transcriber-specific parse error.'''
    pass

class Chunk(object):
    '''A chunk is the smallest-level object: text synced with time.'''
    def __init__(self, beg=0, end=0, text=None):
        self.beg = beg
        self.end = end
        self.text = text

class Turn(list):
    '''A turn is a list of chunks.'''
    def __init__(self, beg=0, end=0, chunks=None):
        self.beg = beg
        self.end = end
        if not chunks:
            chunks = []
        super().__init__(chunks)

class Section(list):
    '''A section is a list of turns.'''
    def __init__(self, category=None, beg=0, end=0, turns=None):
        self.category = category
        self.beg = beg
        self.end = end
        if not turns:
            turns = []
        super().__init__(turns)

class Episode(list):
    '''An episode is a list of sections.'''
    def __init__(self, sections=None):
        if not sections:
            sections = []
        super().__init__(sections)

class TransObject(object):
    '''Transcriber object: the largest-level object.

    Topmost is a list of Episodes, each of which contains one or more
    Sections, each of which contains one or more Turns, each of which
    contains one or more Chunks (transcribed speech data with timepoints).

    '''
    def __init__(self, filename):
        # XML Parser
        self._parser = xml.parsers.expat.ParserCreate()
        self._parser.StartElementHandler = self._start_element
        self._parser.EndElementHandler = self._end_element
        self._parser.CharacterDataHandler = self._char_data

        # Current episode, section, and turn
        self._curr_episode = None
        self._curr_section = None
        self._curr_turn = None

        # Sync time
        self._caret = None

        # Public: when using this module, use only these variables
        # and the to_intervals() and read() methods
        self.filename = filename
        self.episodes = []

        if self.filename:
            self.read()

    def _start_element(self, element, attrs):
        '''Private method: handle XML start elements.'''
        if element == 'Episode':
            self._curr_episode = Episode()
        elif element == 'Section':
            cat = attrs['type']
            try:
                beg = float(attrs['startTime'])
                end = float(attrs['endTime'])
            except ValueError:
                raise ParseError
            self._curr_section = Section(category=cat, beg=beg, end=end)
        elif element == 'Turn':
            try:
                beg = float(attrs['startTime'])
                end = float(attrs['endTime'])
            except ValueError:
                raise ParseError
            self._curr_turn = Turn(beg=beg, end=end)
        elif element == 'Sync':
            try:
                self._caret = float(attrs['time'])
            except ValueError:
                raise ParseError

    def _end_element(self, element):
        '''Private method: handle XML end elements.'''
        if element == 'Episode':
            self.episodes.append(self._curr_episode)
            self._curr_episode = None
        elif element == 'Section':
            self._curr_episode.append(self._curr_section)
            self._curr_section = None
        elif element == 'Turn':
            self._curr_section.append(self._curr_turn)
            self._curr_turn = None

    def _char_data(self, data):
        '''Private method: handle character data.'''
        data = data.strip()
        if data:
            self._curr_turn.append(Chunk(beg=self._caret, text=data))
            self._caret = None

    def to_intervals(self):
        '''Insert end times for each chunk.

        This is to ensure Praat interval layer compatibility.
        '''
        for episode in self.episodes:
            for section in episode:
                for turn in section:
                    for pred, succ in zip(turn[0:], turn[1:]):
                        pred.end = succ.beg
                    succ.end = turn.end

    def read(self, filename=None):
        '''Read and parse a .trs file.'''
        if filename:
            self.filename = filename
        if self.filename:
            with codecs.open(self.filename, 'r', encoding='iso8859-1') as infile:
                self._parser.Parse(''.join(infile.readlines()))

if __name__ == '__main__':
    import sys

    # A simple test if run as a script
    for arg in sys.argv[1:]:
        try:
            trs = TransObject(arg)
        except (FileNotFoundError, PermissionError, IOError):
            print('I/O error: {}'.format(arg), file=sys.stderr)
            continue
        except (ParseError, xml.parsers.expat.ExpatError):
            print('Parse error: {}'.format(arg), file=sys.stderr)
            continue
        for episode in trs.episodes:
            for section in episode:
                print('section type={} @ {} --> {}'.format(section.category,
                                                           section.beg,
                                                           section.end))
                for turn in section:
                    print('turn @ {} --> {}'.format(turn.beg, turn.end))
                    for chunk in turn:
                        print('@ {} --> {} = "{}"'.format(chunk.beg,
                                                          chunk.end,
                                                          chunk.text[:50]))
