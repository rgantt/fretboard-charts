"""
Core music theory classes and functions for guitar chord generation.

This module provides the fundamental musical building blocks:
- Note representation with enharmonic handling
- Interval calculations
- Chord theory and interval patterns
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class NoteClass(Enum):
    """Chromatic note classes (pitch classes 0-11)"""
    C = 0
    C_SHARP = 1
    D = 2
    D_SHARP = 3
    E = 4
    F = 5
    F_SHARP = 6
    G = 7
    G_SHARP = 8
    A = 9
    A_SHARP = 10
    B = 11


@dataclass(frozen=True)
class Note:
    """
    Represents a musical note with enharmonic awareness.
    
    Attributes:
        pitch_class: Integer 0-11 representing chromatic position
        name: String representation of the note (e.g., "C", "F#", "Bb")
    """
    pitch_class: int
    name: str
    
    def __post_init__(self):
        """Validate note parameters"""
        if not 0 <= self.pitch_class <= 11:
            raise ValueError(f"Pitch class must be 0-11, got {self.pitch_class}")
        if not self.name:
            raise ValueError("Note name cannot be empty")
    
    @classmethod
    def from_name(cls, name: str) -> 'Note':
        """Create a Note from string name (e.g., 'C#', 'Bb', 'F')"""
        name = name.strip().title()
        
        # Handle enharmonic spellings
        note_map = {
            'C': 0, 'B#': 0,
            'C#': 1, 'Db': 1,
            'D': 2,
            'D#': 3, 'Eb': 3,
            'E': 4, 'Fb': 4,
            'F': 5, 'E#': 5,
            'F#': 6, 'Gb': 6,
            'G': 7,
            'G#': 8, 'Ab': 8,
            'A': 9,
            'A#': 10, 'Bb': 10,
            'B': 11, 'Cb': 11,
        }
        
        if name not in note_map:
            raise ValueError(f"Invalid note name: {name}")
        
        return cls(pitch_class=note_map[name], name=name)
    
    def interval_to(self, other: 'Note') -> int:
        """Calculate semitone interval from this note to another (0-11)"""
        return (other.pitch_class - self.pitch_class) % 12
    
    def transpose(self, semitones: int) -> 'Note':
        """Transpose this note by given number of semitones"""
        new_pitch_class = (self.pitch_class + semitones) % 12
        
        # Generate appropriate enharmonic spelling based on direction
        sharp_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        flat_names = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
        
        # Use sharps for upward transposition, flats for downward
        if semitones >= 0:
            new_name = sharp_names[new_pitch_class]
        else:
            new_name = flat_names[new_pitch_class]
            
        return Note(pitch_class=new_pitch_class, name=new_name)
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"Note({self.name})"


class ChordQuality(Enum):
    """Common chord qualities with their interval patterns"""
    MAJOR = "maj"
    MINOR = "min"
    DIMINISHED = "dim"
    AUGMENTED = "aug"
    MAJOR_SEVENTH = "maj7"
    MINOR_SEVENTH = "min7"
    DOMINANT_SEVENTH = "7"
    DIMINISHED_SEVENTH = "dim7"
    HALF_DIMINISHED = "m7b5"
    MINOR_MAJOR_SEVENTH = "mM7"
    SUSPENDED_SECOND = "sus2"
    SUSPENDED_FOURTH = "sus4"
    SIXTH = "6"
    MINOR_SIXTH = "m6"
    NINTH = "9"
    MINOR_NINTH = "m9"
    MAJOR_NINTH = "maj9"


@dataclass
class Chord:
    """
    Represents a musical chord with all its components.
    
    Attributes:
        root: The root note of the chord
        quality: The chord quality (major, minor, etc.)
        extensions: List of extension intervals (7, 9, 11, 13)
        alterations: Dict of altered intervals {interval: alteration}
        bass: Optional bass note for slash chords
        added_tones: List of added intervals (e.g., add9)
    """
    root: Note
    quality: ChordQuality
    extensions: List[int] = None
    alterations: Dict[int, str] = None  # {interval: "b" or "#"}
    bass: Optional[Note] = None
    added_tones: List[int] = None
    
    def __post_init__(self):
        """Initialize empty collections if None"""
        if self.extensions is None:
            self.extensions = []
        if self.alterations is None:
            self.alterations = {}
        if self.added_tones is None:
            self.added_tones = []
    
    def get_intervals(self) -> List[int]:
        """
        Get the complete set of intervals for this chord.
        Returns list of semitone intervals from the root.
        """
        # Base intervals for each chord quality
        base_intervals = {
            ChordQuality.MAJOR: [0, 4, 7],
            ChordQuality.MINOR: [0, 3, 7],
            ChordQuality.DIMINISHED: [0, 3, 6],
            ChordQuality.AUGMENTED: [0, 4, 8],
            ChordQuality.MAJOR_SEVENTH: [0, 4, 7, 11],
            ChordQuality.MINOR_SEVENTH: [0, 3, 7, 10],
            ChordQuality.DOMINANT_SEVENTH: [0, 4, 7, 10],
            ChordQuality.DIMINISHED_SEVENTH: [0, 3, 6, 9],
            ChordQuality.HALF_DIMINISHED: [0, 3, 6, 10],
            ChordQuality.MINOR_MAJOR_SEVENTH: [0, 3, 7, 11],
            ChordQuality.SUSPENDED_SECOND: [0, 2, 7],
            ChordQuality.SUSPENDED_FOURTH: [0, 5, 7],
            ChordQuality.SIXTH: [0, 4, 7, 9],
            ChordQuality.MINOR_SIXTH: [0, 3, 7, 9],
            ChordQuality.NINTH: [0, 4, 7, 10, 14],  # Dom9 = 1-3-5-b7-9
            ChordQuality.MINOR_NINTH: [0, 3, 7, 10, 14],  # Min9 = 1-b3-5-b7-9
            ChordQuality.MAJOR_NINTH: [0, 4, 7, 11, 14],  # Maj9 = 1-3-5-7-9
        }
        
        intervals = base_intervals[self.quality].copy()
        
        # Add extensions
        for ext in self.extensions:
            if ext == 7:
                intervals.append(10 if self.quality != ChordQuality.MAJOR_SEVENTH else 11)
            elif ext == 9:
                intervals.append(2)
            elif ext == 11:
                intervals.append(5)
            elif ext == 13:
                intervals.append(9)
        
        # Add added tones
        for add in self.added_tones:
            if add == 2 or add == 9:
                intervals.append(2)
            elif add == 4 or add == 11:
                intervals.append(5)
            elif add == 6 or add == 13:
                intervals.append(9)
        
        # Apply alterations
        for scale_degree, alteration in self.alterations.items():
            # Map scale degrees to semitone intervals
            degree_to_semitone = {
                1: 0,   # Root
                2: 2,   # 2nd
                3: 4,   # Major 3rd (will be 3 for minor)
                4: 5,   # 4th
                5: 7,   # 5th
                6: 9,   # Major 6th
                7: 11,  # Major 7th (will be 10 for minor 7th)
                9: 2,   # 9th = 2nd + octave
                11: 5,  # 11th = 4th + octave
                13: 9,  # 13th = 6th + octave
            }
            
            # Get the natural interval for this scale degree
            if scale_degree in degree_to_semitone:
                natural_interval = degree_to_semitone[scale_degree]
                
                # Remove the natural interval if it exists
                if natural_interval in intervals:
                    intervals.remove(natural_interval)
                
                # Add the altered interval
                if alteration == "b":
                    altered_interval = (natural_interval - 1) % 12
                    intervals.append(altered_interval)
                elif alteration == "#":
                    altered_interval = (natural_interval + 1) % 12
                    intervals.append(altered_interval)
        
        # Remove duplicates and sort
        return sorted(list(set(intervals)))
    
    def get_notes(self) -> List[Note]:
        """Get all notes in this chord based on the root and intervals"""
        intervals = self.get_intervals()
        notes = []
        
        for interval in intervals:
            note = self.root.transpose(interval)
            notes.append(note)
        
        return notes
    
    def __str__(self) -> str:
        """String representation of the chord"""
        result = str(self.root)
        
        # Add quality
        if self.quality != ChordQuality.MAJOR:
            result += self.quality.value
        
        # Add extensions
        for ext in sorted(self.extensions):
            result += str(ext)
        
        # Add alterations
        for interval in sorted(self.alterations.keys()):
            alt = self.alterations[interval]
            result += f"{alt}{interval}"
        
        # Add added tones
        for add in sorted(self.added_tones):
            result += f"add{add}"
        
        # Add bass note
        if self.bass:
            result += f"/{self.bass}"
        
        return result
    
    def __repr__(self) -> str:
        return f"Chord({self})"


def calculate_interval_semitones(interval_name: str) -> int:
    """
    Convert interval name to semitones.
    
    Args:
        interval_name: String like "P1", "M3", "P5", "m7", etc.
    
    Returns:
        Number of semitones
    """
    interval_map = {
        "P1": 0, "U": 0,      # Perfect unison
        "m2": 1, "b2": 1,     # Minor second
        "M2": 2, "2": 2,      # Major second
        "m3": 3, "b3": 3,     # Minor third
        "M3": 4, "3": 4,      # Major third
        "P4": 5, "4": 5,      # Perfect fourth
        "b5": 6, "d5": 6,     # Diminished fifth
        "P5": 7, "5": 7,      # Perfect fifth
        "#5": 8, "b6": 8,     # Augmented fifth / minor sixth
        "M6": 9, "6": 9,      # Major sixth
        "m7": 10, "b7": 10,   # Minor seventh
        "M7": 11, "7": 11,    # Major seventh
        "P8": 12, "8": 12,    # Perfect octave
    }
    
    if interval_name not in interval_map:
        raise ValueError(f"Unknown interval: {interval_name}")
    
    return interval_map[interval_name]


def notes_in_key(key: Note, mode: str = "major") -> List[Note]:
    """
    Get all notes in a given key and mode.
    
    Args:
        key: The key center (tonic note)
        mode: The mode ("major", "minor", etc.)
    
    Returns:
        List of notes in the key
    """
    # Interval patterns for different modes (in semitones)
    mode_patterns = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "lydian": [0, 2, 4, 6, 7, 9, 11],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
        "locrian": [0, 1, 3, 5, 6, 8, 10],
    }
    
    if mode not in mode_patterns:
        raise ValueError(f"Unknown mode: {mode}")
    
    pattern = mode_patterns[mode]
    return [key.transpose(interval) for interval in pattern]
