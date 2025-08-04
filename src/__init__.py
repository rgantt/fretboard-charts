"""
Guitar Chord Fingering Generator

A music theory-based tool for generating guitar chord fingerings and diagrams.
"""

__version__ = "0.1.0"
__author__ = "Guitar Chord Generator Project"

from .music_theory import Note, Chord, ChordQuality
from .chord_parser import ChordParser, parse_chord, quick_parse, ChordParseError
from .fretboard import FretPosition, GuitarTuning, Fretboard, STANDARD_TUNING, DROP_D_TUNING
from .fingering import Fingering, FingerAssignment, FingeringValidator
from .fingering_generator import FingeringGenerator, GenerationConfig, generate_chord_fingerings
from .chord_patterns import ChordPattern, ChordPatternDatabase, CHORD_PATTERNS

__all__ = [
    "Note",
    "Chord", 
    "ChordQuality",
    "ChordParser",
    "parse_chord",
    "quick_parse",
    "ChordParseError",
    "FretPosition",
    "GuitarTuning",
    "Fretboard",
    "STANDARD_TUNING",
    "DROP_D_TUNING",
    "Fingering",
    "FingerAssignment",
    "FingeringValidator",
    "FingeringGenerator",
    "GenerationConfig",
    "generate_chord_fingerings",
    "ChordPattern",
    "ChordPatternDatabase",
    "CHORD_PATTERNS"
]
