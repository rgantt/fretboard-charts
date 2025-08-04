"""
Guitar fretboard modeling and note-to-position mapping.

This module provides classes and functions for:
- Modeling the physical guitar fretboard
- Mapping notes to string/fret positions
- Handling different tunings and configurations
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

from .music_theory import Note


class StringNumber(Enum):
    """Guitar string numbers (1 = high E, 6 = low E)"""
    HIGH_E = 1    # 1st string (thinnest)
    B = 2         # 2nd string
    G = 3         # 3rd string
    D = 4         # 4th string
    A = 5         # 5th string
    LOW_E = 6     # 6th string (thickest)


@dataclass(frozen=True)
class FretPosition:
    """
    Represents a specific position on the fretboard.
    
    Attributes:
        string: String number (1-6, where 1 is high E)
        fret: Fret number (0 = open, 1-22 = fretted)
        note: The note produced at this position
    """
    string: int
    fret: int
    note: Note
    
    def __post_init__(self):
        """Validate fret position parameters"""
        if not 1 <= self.string <= 6:
            raise ValueError(f"String number must be 1-6, got {self.string}")
        if not 0 <= self.fret <= 24:  # Allow up to 24 frets
            raise ValueError(f"Fret number must be 0-24, got {self.fret}")
    
    def is_open_string(self) -> bool:
        """Check if this position is an open string"""
        return self.fret == 0
    
    def __str__(self) -> str:
        return f"String {self.string}, Fret {self.fret} ({self.note})"
    
    def __repr__(self) -> str:
        return f"FretPosition(string={self.string}, fret={self.fret}, note={self.note})"


@dataclass
class GuitarTuning:
    """
    Represents a guitar tuning configuration.
    
    Attributes:
        name: Name of the tuning (e.g., "Standard", "Drop D")
        notes: List of open string notes from string 6 (low E) to string 1 (high E)
    """
    name: str
    notes: List[Note]
    
    def __post_init__(self):
        """Validate tuning configuration"""
        if len(self.notes) != 6:
            raise ValueError(f"Tuning must have exactly 6 notes, got {len(self.notes)}")
    
    def get_open_note(self, string: int) -> Note:
        """Get the open note for a given string number (1-6)"""
        if not 1 <= string <= 6:
            raise ValueError(f"String number must be 1-6, got {string}")
        # Convert string number to list index (string 6 = index 0, string 1 = index 5)
        return self.notes[6 - string]
    
    @classmethod
    def standard(cls) -> 'GuitarTuning':
        """Create standard tuning (E-A-D-G-B-E)"""
        return cls(
            name="Standard",
            notes=[
                Note.from_name("E"),   # String 6 (low E)
                Note.from_name("A"),   # String 5
                Note.from_name("D"),   # String 4
                Note.from_name("G"),   # String 3
                Note.from_name("B"),   # String 2
                Note.from_name("E"),   # String 1 (high E)
            ]
        )
    
    @classmethod
    def drop_d(cls) -> 'GuitarTuning':
        """Create Drop D tuning (D-A-D-G-B-E)"""
        return cls(
            name="Drop D",
            notes=[
                Note.from_name("D"),   # String 6 (low D)
                Note.from_name("A"),   # String 5
                Note.from_name("D"),   # String 4
                Note.from_name("G"),   # String 3
                Note.from_name("B"),   # String 2
                Note.from_name("E"),   # String 1 (high E)
            ]
        )
    
    def __str__(self) -> str:
        note_names = [note.name for note in self.notes]
        return f"{self.name} tuning: {'-'.join(note_names)}"


class Fretboard:
    """
    Models a guitar fretboard with string/fret coordinate system.
    
    Provides functionality for:
    - Note-to-position mapping
    - Position validation
    - Fretboard analysis and chord finding
    """
    
    def __init__(self, tuning: GuitarTuning = None, num_frets: int = 22):
        """
        Initialize a fretboard with given tuning and fret count.
        
        Args:
            tuning: Guitar tuning configuration (defaults to standard)
            num_frets: Number of frets on the guitar (default 22)
        """
        self.tuning = tuning or GuitarTuning.standard()
        self.num_frets = num_frets
        
        # Pre-calculate note positions for performance
        self._note_positions_cache: Dict[str, List[FretPosition]] = {}
        self._build_position_cache()
    
    def _build_position_cache(self):
        """Pre-calculate all note positions on the fretboard"""
        for string in range(1, 7):  # Strings 1-6
            open_note = self.tuning.get_open_note(string)
            
            for fret in range(self.num_frets + 1):  # Frets 0-22
                note = open_note.transpose(fret)
                position = FretPosition(string=string, fret=fret, note=note)
                
                # Add to cache by note name
                note_name = note.name
                if note_name not in self._note_positions_cache:
                    self._note_positions_cache[note_name] = []
                self._note_positions_cache[note_name].append(position)
    
    def get_note_at_position(self, string: int, fret: int) -> Note:
        """
        Get the note at a specific string/fret position.
        
        Args:
            string: String number (1-6)
            fret: Fret number (0-22)
        
        Returns:
            Note at that position
        """
        if not 1 <= string <= 6:
            raise ValueError(f"String number must be 1-6, got {string}")
        if not 0 <= fret <= self.num_frets:
            raise ValueError(f"Fret number must be 0-{self.num_frets}, got {fret}")
        
        open_note = self.tuning.get_open_note(string)
        return open_note.transpose(fret)
    
    def get_positions_for_note(self, note: Note, max_fret: int = None) -> List[FretPosition]:
        """
        Get all positions where a specific note can be played.
        
        Args:
            note: The note to find
            max_fret: Maximum fret to search (defaults to all frets)
        
        Returns:
            List of FretPosition objects where the note can be played
        """
        max_fret = max_fret or self.num_frets
        
        positions = self._note_positions_cache.get(note.name, [])
        return [pos for pos in positions if pos.fret <= max_fret]
    
    def get_positions_for_notes(self, notes: List[Note], max_fret: int = None) -> Dict[Note, List[FretPosition]]:
        """
        Get all positions for multiple notes.
        
        Args:
            notes: List of notes to find
            max_fret: Maximum fret to search
        
        Returns:
            Dictionary mapping each note to its list of positions
        """
        result = {}
        for note in notes:
            result[note] = self.get_positions_for_note(note, max_fret)
        return result
    
    def get_positions_in_range(self, min_fret: int = 0, max_fret: int = None) -> List[FretPosition]:
        """
        Get all positions within a fret range.
        
        Args:
            min_fret: Minimum fret (inclusive)
            max_fret: Maximum fret (inclusive)
        
        Returns:
            List of all positions in the range
        """
        max_fret = max_fret or self.num_frets
        positions = []
        
        for string in range(1, 7):
            for fret in range(min_fret, max_fret + 1):
                note = self.get_note_at_position(string, fret)
                positions.append(FretPosition(string=string, fret=fret, note=note))
        
        return positions
    
    def find_note_intervals(self, root_note: Note, intervals: List[int], max_fret: int = 12) -> Dict[int, List[FretPosition]]:
        """
        Find positions for a set of intervals from a root note.
        
        Args:
            root_note: The root note
            intervals: List of semitone intervals from root
            max_fret: Maximum fret to search
        
        Returns:
            Dictionary mapping each interval to its positions
        """
        result = {}
        
        for interval in intervals:
            target_note = root_note.transpose(interval)
            positions = self.get_positions_for_note(target_note, max_fret)
            result[interval] = positions
        
        return result
    
    def get_open_strings(self) -> List[FretPosition]:
        """Get all open string positions"""
        positions = []
        for string in range(1, 7):
            note = self.tuning.get_open_note(string)
            positions.append(FretPosition(string=string, fret=0, note=note))
        return positions
    
    def validate_position(self, string: int, fret: int) -> bool:
        """
        Validate if a string/fret position is valid on this fretboard.
        
        Args:
            string: String number (1-6)
            fret: Fret number (0-22)
        
        Returns:
            True if position is valid, False otherwise
        """
        return (1 <= string <= 6) and (0 <= fret <= self.num_frets)
    
    def get_fretboard_span(self, positions: List[FretPosition]) -> int:
        """
        Calculate the fret span required for a set of positions.
        
        Args:
            positions: List of fret positions
        
        Returns:
            Number of frets spanned (max_fret - min_fret)
        """
        if not positions:
            return 0
        
        frets = [pos.fret for pos in positions if pos.fret > 0]  # Ignore open strings
        if not frets:
            return 0
        
        return max(frets) - min(frets)
    
    def positions_to_chord_shape(self, positions: List[FretPosition]) -> List[Optional[int]]:
        """
        Convert a list of positions to a chord shape representation.
        
        Args:
            positions: List of fret positions
        
        Returns:
            List of 6 fret numbers (or None for muted strings)
            Order: [string 6, string 5, string 4, string 3, string 2, string 1]
        """
        # Initialize all strings as muted (None)
        shape = [None] * 6
        
        # Fill in the fret positions
        for pos in positions:
            # Convert string number to array index (string 6 = index 0, string 1 = index 5)
            string_index = 6 - pos.string
            shape[string_index] = pos.fret
        
        return shape
    
    def __str__(self) -> str:
        return f"Fretboard ({self.tuning.name}, {self.num_frets} frets)"
    
    def __repr__(self) -> str:
        return f"Fretboard(tuning={self.tuning}, num_frets={self.num_frets})"


# Pre-defined common tunings
STANDARD_TUNING = GuitarTuning.standard()
DROP_D_TUNING = GuitarTuning.drop_d()

# Default fretboard instance
DEFAULT_FRETBOARD = Fretboard(STANDARD_TUNING)
