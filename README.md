# trsparser -- a Transcriber™ parser for Python

## Description

A simple **Transcriber™ parser module** for Python (version 3) and a **Transcriber™-to-Praat TextGrid converter** utilizing it.

The classes defined are, in the order from largest to smallest:

* `TransObject` -- largest object; contains one or more `Episode`s
* `Episode` -- a `list` of `Section`s
* `Section` -- a `list` of `Turn`s
* `Turn` -- a `list` of `Chunk`s
* `Chunk` -- smallest object, some text synced with time.

The hierarchy of objects correspond to how Transcriber™ presents the transcription, and the names “episode”, “section”, and “turn” are Transcriber™’s terminology.

## Version

This file documents `trsparser` version 0.1.1.

## Copyright

Copyright © 2019 Legisign.org, Tommi Nieminen <software@legisign.org>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

## Module contents

### 0. Module properties

`trsparser.version` gives the version number (as string).

### 1. TransObject

Largest object. A `TransObject` is a `list` of `Episode`s.

#### 1.1. Methods

* `read()` -- read and parse a `.trs` file
* `to_intervals()` -- ensure Praat compatibility by adding end times for each chunk. No arguments.

### 2. Episode

Second to largest object. Each `Episode` is a part of some `TransObject` and in itself a `list` of one or more `Section`s.

No properties or methods besides those inherited from `list`.

### 3. Section

Each `Section` is a part of some `Episode` and in itself a `list` of one or more `Turn`s.

No properties or methods besides those inherited from `list`.

### 4. Turn

Each `Turn` is a part of some `Section` and in itself a `list` of one or more `Chunk`s.

No properties or methods besides those inherited from `list`.
