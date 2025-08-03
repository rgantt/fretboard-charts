"""
Guitar Chord Fingering Generator

A music theory-based tool for generating guitar chord fingerings and diagrams.
"""

__version__ = "0.1.0"
__author__ = "Guitar Chord Generator Project"

from .music_theory import Note, Chord, ChordQuality
from .chord_parser import ChordParser, parse_chord, quick_parse, ChordParseError

__all__ = [
    "Note",
    "Chord", 
    "ChordQuality",
    "ChordParser",
    "parse_chord",
    "quick_parse",
    "ChordParseError"
]
