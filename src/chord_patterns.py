"""
Common guitar chord patterns and shapes.

This module contains databases of well-known chord patterns that can be
used to enhance fingering generation with familiar, learnable chord shapes.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from .music_theory import Note, ChordQuality
from .fretboard import FretPosition, Fretboard, STANDARD_TUNING
from .fingering import Fingering, FingerAssignment


class PatternType(Enum):
    """Types of chord patterns"""
    OPEN = "open"           # Open position chords (frets 0-4)
    BARRE_E = "barre_e"     # E-shape barre chords
    BARRE_A = "barre_a"     # A-shape barre chords
    JAZZ = "jazz"           # Common jazz voicings


@dataclass
class ChordPattern:
    """
    Represents a chord pattern/shape that can be transposed.
    
    Attributes:
        name: Pattern name (e.g., "open_C_major", "E_shape_major")
        quality: Chord quality this pattern represents
        frets: Fret positions [string 6, string 5, ..., string 1], None = muted
        root_string: String number where the root note is located
        root_fret: Fret where root is located in this pattern
        finger_assignments: Suggested finger assignments
        pattern_type: Type of pattern (open, barre, etc.)
    """
    name: str
    quality: ChordQuality
    frets: List[Optional[int]]  # 6 elements, string 6 to string 1
    root_string: int
    root_fret: int
    finger_assignments: Dict[int, FingerAssignment]
    pattern_type: PatternType
    difficulty: float = 0.0


class ChordPatternDatabase:
    """Database of common chord patterns"""
    
    def __init__(self):
        """Initialize with common chord patterns"""
        self.patterns: Dict[ChordQuality, List[ChordPattern]] = {}
        self._build_pattern_database()
    
    def _build_pattern_database(self):
        """Build the database of common chord patterns"""
        
        # Open position major chords
        open_major_patterns = [
            # C major (x-3-2-0-1-0)
            ChordPattern(
                name="open_C_major",
                quality=ChordQuality.MAJOR,
                frets=[None, 3, 2, 0, 1, 0],  # x-3-2-0-1-0
                root_string=5,  # Root C on 5th string, 3rd fret
                root_fret=3,
                finger_assignments={
                    5: FingerAssignment.RING,    # 3rd fret
                    4: FingerAssignment.MIDDLE,  # 2nd fret
                    3: FingerAssignment.OPEN,    # open
                    2: FingerAssignment.INDEX,   # 1st fret
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
            
            # G major (3-2-0-0-3-3)
            ChordPattern(
                name="open_G_major",
                quality=ChordQuality.MAJOR,
                frets=[3, 2, 0, 0, 3, 3],  # 3-2-0-0-3-3
                root_string=6,  # Root G on 6th string, 3rd fret
                root_fret=3,
                finger_assignments={
                    6: FingerAssignment.MIDDLE,  # 3rd fret
                    5: FingerAssignment.INDEX,   # 2nd fret
                    4: FingerAssignment.OPEN,    # open
                    3: FingerAssignment.OPEN,    # open
                    2: FingerAssignment.RING,    # 3rd fret
                    1: FingerAssignment.PINKY,   # 3rd fret
                },
                pattern_type=PatternType.OPEN
            ),
            
            # D major (x-x-0-2-3-2)
            ChordPattern(
                name="open_D_major",
                quality=ChordQuality.MAJOR,
                frets=[None, None, 0, 2, 3, 2],  # x-x-0-2-3-2
                root_string=4,  # Root D on 4th string, open
                root_fret=0,
                finger_assignments={
                    4: FingerAssignment.OPEN,    # open
                    3: FingerAssignment.INDEX,   # 2nd fret
                    2: FingerAssignment.RING,    # 3rd fret
                    1: FingerAssignment.MIDDLE,  # 2nd fret
                },
                pattern_type=PatternType.OPEN
            ),
            
            # A major (x-0-2-2-2-0)
            ChordPattern(
                name="open_A_major",
                quality=ChordQuality.MAJOR,
                frets=[None, 0, 2, 2, 2, 0],  # x-0-2-2-2-0
                root_string=5,  # Root A on 5th string, open
                root_fret=0,
                finger_assignments={
                    5: FingerAssignment.OPEN,    # open
                    4: FingerAssignment.INDEX,   # 2nd fret
                    3: FingerAssignment.MIDDLE,  # 2nd fret
                    2: FingerAssignment.RING,    # 2nd fret
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
            
            # E major (0-2-2-1-0-0)
            ChordPattern(
                name="open_E_major",
                quality=ChordQuality.MAJOR,
                frets=[0, 2, 2, 1, 0, 0],  # 0-2-2-1-0-0
                root_string=6,  # Root E on 6th string, open
                root_fret=0,
                finger_assignments={
                    6: FingerAssignment.OPEN,    # open
                    5: FingerAssignment.MIDDLE,  # 2nd fret
                    4: FingerAssignment.RING,    # 2nd fret
                    3: FingerAssignment.INDEX,   # 1st fret
                    2: FingerAssignment.OPEN,    # open
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            )
        ]
        
        # Open position minor chords
        open_minor_patterns = [
            # A minor (x-0-2-2-1-0)
            ChordPattern(
                name="open_Am_minor",
                quality=ChordQuality.MINOR,
                frets=[None, 0, 2, 2, 1, 0],  # x-0-2-2-1-0
                root_string=5,  # Root A on 5th string, open
                root_fret=0,
                finger_assignments={
                    5: FingerAssignment.OPEN,    # open
                    4: FingerAssignment.MIDDLE,  # 2nd fret
                    3: FingerAssignment.RING,    # 2nd fret
                    2: FingerAssignment.INDEX,   # 1st fret
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
            
            # E minor (0-2-2-0-0-0)
            ChordPattern(
                name="open_Em_minor",
                quality=ChordQuality.MINOR,
                frets=[0, 2, 2, 0, 0, 0],  # 0-2-2-0-0-0
                root_string=6,  # Root E on 6th string, open
                root_fret=0,
                finger_assignments={
                    6: FingerAssignment.OPEN,    # open
                    5: FingerAssignment.MIDDLE,  # 2nd fret
                    4: FingerAssignment.RING,    # 2nd fret
                    3: FingerAssignment.OPEN,    # open
                    2: FingerAssignment.OPEN,    # open
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
            
            # D minor (x-x-0-2-3-1)
            ChordPattern(
                name="open_Dm_minor",
                quality=ChordQuality.MINOR,
                frets=[None, None, 0, 2, 3, 1],  # x-x-0-2-3-1
                root_string=4,  # Root D on 4th string, open
                root_fret=0,
                finger_assignments={
                    4: FingerAssignment.OPEN,    # open
                    3: FingerAssignment.INDEX,   # 2nd fret
                    2: FingerAssignment.RING,    # 3rd fret
                    1: FingerAssignment.MIDDLE,  # 1st fret
                },
                pattern_type=PatternType.OPEN
            )
        ]
        
        # Seventh chord patterns
        seventh_patterns = [
            # G7 (3-2-0-0-0-1)
            ChordPattern(
                name="open_G7",
                quality=ChordQuality.DOMINANT_SEVENTH,
                frets=[3, 2, 0, 0, 0, 1],  # 3-2-0-0-0-1
                root_string=6,  # Root G on 6th string, 3rd fret
                root_fret=3,
                finger_assignments={
                    6: FingerAssignment.MIDDLE,  # 3rd fret
                    5: FingerAssignment.INDEX,   # 2nd fret
                    4: FingerAssignment.OPEN,    # open
                    3: FingerAssignment.OPEN,    # open
                    2: FingerAssignment.OPEN,    # open
                    1: FingerAssignment.RING,    # 1st fret
                },
                pattern_type=PatternType.OPEN
            ),
            
            # C7 (x-3-2-3-1-0)
            ChordPattern(
                name="open_C7",
                quality=ChordQuality.DOMINANT_SEVENTH,
                frets=[None, 3, 2, 3, 1, 0],  # x-3-2-3-1-0
                root_string=5,  # Root C on 5th string, 3rd fret
                root_fret=3,
                finger_assignments={
                    5: FingerAssignment.RING,    # 3rd fret
                    4: FingerAssignment.INDEX,   # 2nd fret
                    3: FingerAssignment.PINKY,   # 3rd fret
                    2: FingerAssignment.MIDDLE,  # 1st fret
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
            
            # Am7 (x-0-2-0-1-0)
            ChordPattern(
                name="open_Am7",
                quality=ChordQuality.MINOR_SEVENTH,
                frets=[None, 0, 2, 0, 1, 0],  # x-0-2-0-1-0
                root_string=5,  # Root A on 5th string, open
                root_fret=0,
                finger_assignments={
                    5: FingerAssignment.OPEN,    # open
                    4: FingerAssignment.MIDDLE,  # 2nd fret
                    3: FingerAssignment.OPEN,    # open
                    2: FingerAssignment.INDEX,   # 1st fret
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            )
        ]
        
        # Store patterns by quality
        self.patterns[ChordQuality.MAJOR] = open_major_patterns
        self.patterns[ChordQuality.MINOR] = open_minor_patterns
        self.patterns[ChordQuality.DOMINANT_SEVENTH] = seventh_patterns[:2]  # G7, C7
        self.patterns[ChordQuality.MINOR_SEVENTH] = seventh_patterns[2:]     # Am7
    
    def get_patterns_for_quality(self, quality: ChordQuality) -> List[ChordPattern]:
        """Get all patterns for a given chord quality"""
        return self.patterns.get(quality, [])
    
    def find_matching_patterns(self, root_note: Note, quality: ChordQuality) -> List[ChordPattern]:
        """
        Find patterns that match a specific chord root and quality.
        
        Args:
            root_note: Root note of the chord
            quality: Chord quality
            
        Returns:
            List of matching patterns (may be empty if no matches)
        """
        patterns = self.get_patterns_for_quality(quality)
        matching = []
        
        fretboard = Fretboard(STANDARD_TUNING)
        
        for pattern in patterns:
            # Get the root note at the pattern's root position
            pattern_root = fretboard.get_note_at_position(pattern.root_string, pattern.root_fret)
            
            # Check if this pattern's root matches our target root (by pitch class)
            if pattern_root.pitch_class == root_note.pitch_class:
                matching.append(pattern)
        
        return matching
    
    def pattern_to_fingering(self, pattern: ChordPattern, chord) -> Fingering:
        """
        Convert a chord pattern to a Fingering object.
        
        Args:
            pattern: The chord pattern to convert
            chord: The chord this fingering represents
            
        Returns:
            Fingering object created from the pattern
        """
        fretboard = Fretboard(STANDARD_TUNING)
        positions = []
        
        # Convert fret pattern to positions
        for string_index, fret in enumerate(pattern.frets):
            if fret is not None:  # Not muted
                string = 6 - string_index  # Convert index to string number (6,5,4,3,2,1)
                note = fretboard.get_note_at_position(string, fret)
                position = FretPosition(string=string, fret=fret, note=note)
                positions.append(position)
        
        # Create fingering
        fingering = Fingering(
            positions=positions,
            finger_assignments=pattern.finger_assignments.copy(),
            chord=chord
        )
        
        return fingering


# Global pattern database instance
CHORD_PATTERNS = ChordPatternDatabase()