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
            ),
            
            # F major (1-3-3-2-1-1) - E-shape barre chord
            ChordPattern(
                name="F_major_E_barre",
                quality=ChordQuality.MAJOR,
                frets=[1, 3, 3, 2, 1, 1],  # 1-3-3-2-1-1
                root_string=6,  # Root F on 6th string, 1st fret
                root_fret=1,
                finger_assignments={
                    6: FingerAssignment.INDEX,   # 1st fret (barre)
                    5: FingerAssignment.RING,    # 3rd fret
                    4: FingerAssignment.PINKY,   # 3rd fret
                    3: FingerAssignment.MIDDLE,  # 2nd fret
                    2: FingerAssignment.INDEX,   # 1st fret (barre)
                    1: FingerAssignment.INDEX,   # 1st fret (barre)
                },
                pattern_type=PatternType.BARRE_E,
                difficulty=0.5  # F barre is harder
            ),
            
            # Bb major (x-1-3-3-3-1) - A-shape barre chord
            ChordPattern(
                name="Bb_major_A_barre",
                quality=ChordQuality.MAJOR,
                frets=[None, 1, 3, 3, 3, 1],  # x-1-3-3-3-1
                root_string=5,  # Root Bb on 5th string, 1st fret
                root_fret=1,
                finger_assignments={
                    5: FingerAssignment.INDEX,   # 1st fret (barre)
                    4: FingerAssignment.MIDDLE,  # 3rd fret
                    3: FingerAssignment.RING,    # 3rd fret
                    2: FingerAssignment.PINKY,   # 3rd fret
                    1: FingerAssignment.INDEX,   # 1st fret (barre)
                },
                pattern_type=PatternType.BARRE_A,
                difficulty=0.4  # A-shape barre
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
            
            # Bbm (x-1-3-3-2-1) - A-shape minor barre chord
            ChordPattern(
                name="Bbm_minor_A_barre",
                quality=ChordQuality.MINOR,
                frets=[None, 1, 3, 3, 2, 1],  # x-1-3-3-2-1
                root_string=5,  # Root Bb on 5th string, 1st fret
                root_fret=1,
                finger_assignments={
                    5: FingerAssignment.INDEX,   # 1st fret (barre)
                    4: FingerAssignment.RING,    # 3rd fret
                    3: FingerAssignment.PINKY,   # 3rd fret
                    2: FingerAssignment.MIDDLE,  # 2nd fret
                    1: FingerAssignment.INDEX,   # 1st fret (barre)
                },
                pattern_type=PatternType.BARRE_A,
                difficulty=0.4  # A-shape minor barre
            ),
            
            # Fm (1-3-3-1-1-1) - E-shape minor barre chord
            ChordPattern(
                name="Fm_minor_E_barre",
                quality=ChordQuality.MINOR,
                frets=[1, 3, 3, 1, 1, 1],  # 1-3-3-1-1-1
                root_string=6,  # Root F on 6th string, 1st fret
                root_fret=1,
                finger_assignments={
                    6: FingerAssignment.INDEX,   # 1st fret (barre)
                    5: FingerAssignment.RING,    # 3rd fret
                    4: FingerAssignment.PINKY,   # 3rd fret
                    3: FingerAssignment.INDEX,   # 1st fret (barre)
                    2: FingerAssignment.INDEX,   # 1st fret (barre)
                    1: FingerAssignment.INDEX,   # 1st fret (barre)
                },
                pattern_type=PatternType.BARRE_E,
                difficulty=0.5  # E-shape minor barre
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
            
            # C7 (x-3-2-3-1-0) - standard open C7 without 5th
            ChordPattern(
                name="open_C7",
                quality=ChordQuality.DOMINANT_SEVENTH,
                frets=[None, 3, 2, 3, 1, 0],  # x-3-2-3-1-0
                root_string=5,  # Root C on 5th string, 3rd fret
                root_fret=3,
                finger_assignments={
                    5: FingerAssignment.RING,    # 3rd fret (C)
                    4: FingerAssignment.INDEX,   # 2nd fret (E)
                    3: FingerAssignment.PINKY,   # 3rd fret (Bb)
                    2: FingerAssignment.MIDDLE,  # 1st fret (C)
                    1: FingerAssignment.OPEN,    # open (E)
                },
                pattern_type=PatternType.OPEN
            ),
            
            # D7 (x-x-0-2-1-2)
            ChordPattern(
                name="open_D7",
                quality=ChordQuality.DOMINANT_SEVENTH,
                frets=[None, None, 0, 2, 1, 2],  # x-x-0-2-1-2
                root_string=4,  # Root D on 4th string, open
                root_fret=0,
                finger_assignments={
                    4: FingerAssignment.OPEN,    # open (D)
                    3: FingerAssignment.MIDDLE,  # 2nd fret (A)
                    2: FingerAssignment.INDEX,   # 1st fret (C)
                    1: FingerAssignment.RING,    # 2nd fret (F#)
                },
                pattern_type=PatternType.OPEN
            ),
            
            # A7 (x-0-2-0-2-0)
            ChordPattern(
                name="open_A7",
                quality=ChordQuality.DOMINANT_SEVENTH,
                frets=[None, 0, 2, 0, 2, 0],  # x-0-2-0-2-0
                root_string=5,  # Root A on 5th string, open
                root_fret=0,
                finger_assignments={
                    5: FingerAssignment.OPEN,    # open (A)
                    4: FingerAssignment.MIDDLE,  # 2nd fret (E)
                    3: FingerAssignment.OPEN,    # open (G)
                    2: FingerAssignment.RING,    # 2nd fret (C#)
                    1: FingerAssignment.OPEN,    # open (E)
                },
                pattern_type=PatternType.OPEN
            ),
            
            # E7 (0-2-0-1-0-0)
            ChordPattern(
                name="open_E7",
                quality=ChordQuality.DOMINANT_SEVENTH,
                frets=[0, 2, 0, 1, 0, 0],  # 0-2-0-1-0-0
                root_string=6,  # Root E on 6th string, open
                root_fret=0,
                finger_assignments={
                    6: FingerAssignment.OPEN,    # open (E)
                    5: FingerAssignment.MIDDLE,  # 2nd fret (B)
                    4: FingerAssignment.OPEN,    # open (D)
                    3: FingerAssignment.INDEX,   # 1st fret (G#)
                    2: FingerAssignment.OPEN,    # open (B)
                    1: FingerAssignment.OPEN,    # open (E)
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
            ),
            
            # Dm7 (x-x-0-2-1-1)
            ChordPattern(
                name="open_Dm7",
                quality=ChordQuality.MINOR_SEVENTH,
                frets=[None, None, 0, 2, 1, 1],  # x-x-0-2-1-1
                root_string=4,  # Root D on 4th string, open
                root_fret=0,
                finger_assignments={
                    4: FingerAssignment.OPEN,    # open
                    3: FingerAssignment.MIDDLE,  # 2nd fret
                    2: FingerAssignment.INDEX,   # 1st fret
                    1: FingerAssignment.INDEX,   # 1st fret
                },
                pattern_type=PatternType.OPEN
            ),
            
            # Em7 (0-2-0-0-0-0)
            ChordPattern(
                name="open_Em7",
                quality=ChordQuality.MINOR_SEVENTH,
                frets=[0, 2, 0, 0, 0, 0],  # 0-2-0-0-0-0
                root_string=6,  # Root E on 6th string, open
                root_fret=0,
                finger_assignments={
                    6: FingerAssignment.OPEN,    # open
                    5: FingerAssignment.MIDDLE,  # 2nd fret
                    4: FingerAssignment.OPEN,    # open
                    3: FingerAssignment.OPEN,    # open
                    2: FingerAssignment.OPEN,    # open
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
            
            # B7 (x-2-1-2-0-2)
            ChordPattern(
                name="open_B7",
                quality=ChordQuality.DOMINANT_SEVENTH,
                frets=[None, 2, 1, 2, 0, 2],  # x-2-1-2-0-2
                root_string=5,  # Root B on 5th string, 2nd fret
                root_fret=2,
                finger_assignments={
                    5: FingerAssignment.MIDDLE,  # 2nd fret
                    4: FingerAssignment.INDEX,   # 1st fret
                    3: FingerAssignment.RING,    # 2nd fret
                    2: FingerAssignment.OPEN,    # open
                    1: FingerAssignment.PINKY,   # 2nd fret
                },
                pattern_type=PatternType.OPEN
            )
        ]
        
        # Major 7th chord patterns
        major_seventh_patterns = [
            # Amaj7 (x-0-2-1-2-0)
            ChordPattern(
                name="open_Amaj7",
                quality=ChordQuality.MAJOR_SEVENTH,
                frets=[None, 0, 2, 1, 2, 0],  # x-0-2-1-2-0
                root_string=5,  # Root A on 5th string, open
                root_fret=0,
                finger_assignments={
                    5: FingerAssignment.OPEN,    # open
                    4: FingerAssignment.MIDDLE,  # 2nd fret
                    3: FingerAssignment.INDEX,   # 1st fret
                    2: FingerAssignment.RING,    # 2nd fret
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
            
            # Cmaj7 (x-3-2-0-0-0)
            ChordPattern(
                name="open_Cmaj7",
                quality=ChordQuality.MAJOR_SEVENTH,
                frets=[None, 3, 2, 0, 0, 0],  # x-3-2-0-0-0
                root_string=5,  # Root C on 5th string, 3rd fret
                root_fret=3,
                finger_assignments={
                    5: FingerAssignment.RING,    # 3rd fret
                    4: FingerAssignment.MIDDLE,  # 2nd fret
                    3: FingerAssignment.OPEN,    # open
                    2: FingerAssignment.OPEN,    # open
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
            
            # Dmaj7 (x-x-0-2-2-2)
            ChordPattern(
                name="open_Dmaj7",
                quality=ChordQuality.MAJOR_SEVENTH,
                frets=[None, None, 0, 2, 2, 2],  # x-x-0-2-2-2
                root_string=4,  # Root D on 4th string, open
                root_fret=0,
                finger_assignments={
                    4: FingerAssignment.OPEN,    # open
                    3: FingerAssignment.INDEX,   # 2nd fret (use index for all)
                    2: FingerAssignment.MIDDLE,  # 2nd fret
                    1: FingerAssignment.RING,    # 2nd fret
                },
                pattern_type=PatternType.OPEN
            ),
            
            # Emaj7 (0-2-1-1-0-0)
            ChordPattern(
                name="open_Emaj7",
                quality=ChordQuality.MAJOR_SEVENTH,
                frets=[0, 2, 1, 1, 0, 0],  # 0-2-1-1-0-0
                root_string=6,  # Root E on 6th string, open
                root_fret=0,
                finger_assignments={
                    6: FingerAssignment.OPEN,    # open
                    5: FingerAssignment.RING,    # 2nd fret
                    4: FingerAssignment.INDEX,   # 1st fret
                    3: FingerAssignment.MIDDLE,  # 1st fret
                    2: FingerAssignment.OPEN,    # open
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
            
            # Fmaj7 (x-x-3-2-1-0)
            ChordPattern(
                name="open_Fmaj7",
                quality=ChordQuality.MAJOR_SEVENTH,
                frets=[None, None, 3, 2, 1, 0],  # x-x-3-2-1-0
                root_string=4,  # Root F on 4th string, 3rd fret
                root_fret=3,
                finger_assignments={
                    4: FingerAssignment.RING,    # 3rd fret
                    3: FingerAssignment.MIDDLE,  # 2nd fret
                    2: FingerAssignment.INDEX,   # 1st fret
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
            
            # Gmaj7 (3-2-0-0-0-2)
            ChordPattern(
                name="open_Gmaj7",
                quality=ChordQuality.MAJOR_SEVENTH,
                frets=[3, 2, 0, 0, 0, 2],  # 3-2-0-0-0-2
                root_string=6,  # Root G on 6th string, 3rd fret
                root_fret=3,
                finger_assignments={
                    6: FingerAssignment.RING,    # 3rd fret
                    5: FingerAssignment.MIDDLE,  # 2nd fret
                    4: FingerAssignment.OPEN,    # open
                    3: FingerAssignment.OPEN,    # open
                    2: FingerAssignment.OPEN,    # open
                    1: FingerAssignment.INDEX,   # 2nd fret
                },
                pattern_type=PatternType.OPEN
            ),
        ]
        
        # Suspended chord patterns
        suspended_patterns = [
            # Asus2 (x-0-2-2-0-0)
            ChordPattern(
                name="open_Asus2",
                quality=ChordQuality.SUSPENDED_SECOND,
                frets=[None, 0, 2, 2, 0, 0],  # x-0-2-2-0-0
                root_string=5,  # Root A on 5th string, open
                root_fret=0,
                finger_assignments={
                    5: FingerAssignment.OPEN,    # open
                    4: FingerAssignment.INDEX,   # 2nd fret
                    3: FingerAssignment.MIDDLE,  # 2nd fret
                    2: FingerAssignment.OPEN,    # open
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
            
            # Asus4 (x-0-2-2-3-0)
            ChordPattern(
                name="open_Asus4",
                quality=ChordQuality.SUSPENDED_FOURTH,
                frets=[None, 0, 2, 2, 3, 0],  # x-0-2-2-3-0
                root_string=5,  # Root A on 5th string, open
                root_fret=0,
                finger_assignments={
                    5: FingerAssignment.OPEN,    # open
                    4: FingerAssignment.INDEX,   # 2nd fret
                    3: FingerAssignment.MIDDLE,  # 2nd fret
                    2: FingerAssignment.RING,    # 3rd fret
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
            
            # Csus2 (x-3-0-0-1-0)
            ChordPattern(
                name="open_Csus2",
                quality=ChordQuality.SUSPENDED_SECOND,
                frets=[None, 3, 0, 0, 1, 0],  # x-3-0-0-1-0
                root_string=5,  # Root C on 5th string, 3rd fret
                root_fret=3,
                finger_assignments={
                    5: FingerAssignment.RING,    # 3rd fret
                    4: FingerAssignment.OPEN,    # open
                    3: FingerAssignment.OPEN,    # open
                    2: FingerAssignment.INDEX,   # 1st fret
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
            
            # Csus4 (x-3-3-0-1-0)
            ChordPattern(
                name="open_Csus4",
                quality=ChordQuality.SUSPENDED_FOURTH,
                frets=[None, 3, 3, 0, 1, 0],  # x-3-3-0-1-0
                root_string=5,  # Root C on 5th string, 3rd fret
                root_fret=3,
                finger_assignments={
                    5: FingerAssignment.RING,    # 3rd fret
                    4: FingerAssignment.PINKY,   # 3rd fret
                    3: FingerAssignment.OPEN,    # open
                    2: FingerAssignment.INDEX,   # 1st fret
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
        ]
        
        # Diminished chord patterns
        diminished_patterns = [
            # Adim (x-0-1-2-1-x)
            ChordPattern(
                name="open_Adim",
                quality=ChordQuality.DIMINISHED,
                frets=[None, 0, 1, 2, 1, None],  # x-0-1-2-1-x
                root_string=5,  # Root A on 5th string, open
                root_fret=0,
                finger_assignments={
                    5: FingerAssignment.OPEN,    # open
                    4: FingerAssignment.INDEX,   # 1st fret
                    3: FingerAssignment.RING,    # 2nd fret
                    2: FingerAssignment.MIDDLE,  # 1st fret
                },
                pattern_type=PatternType.OPEN
            ),
            
            # Bdim (x-2-3-1-3-x)
            ChordPattern(
                name="open_Bdim",
                quality=ChordQuality.DIMINISHED,
                frets=[None, 2, 3, 1, 3, None],  # x-2-3-1-3-x
                root_string=5,  # Root B on 5th string, 2nd fret
                root_fret=2,
                finger_assignments={
                    5: FingerAssignment.MIDDLE,  # 2nd fret
                    4: FingerAssignment.RING,    # 3rd fret
                    3: FingerAssignment.INDEX,   # 1st fret
                    2: FingerAssignment.PINKY,   # 3rd fret
                },
                pattern_type=PatternType.OPEN
            ),
        ]
        
        # Augmented chord patterns
        augmented_patterns = [
            # Aaug (x-0-3-2-2-1)
            ChordPattern(
                name="open_Aaug",
                quality=ChordQuality.AUGMENTED,
                frets=[None, 0, 3, 2, 2, 1],  # x-0-3-2-2-1
                root_string=5,  # Root A on 5th string, open
                root_fret=0,
                finger_assignments={
                    5: FingerAssignment.OPEN,    # open
                    4: FingerAssignment.PINKY,   # 3rd fret
                    3: FingerAssignment.RING,    # 2nd fret
                    2: FingerAssignment.MIDDLE,  # 2nd fret
                    1: FingerAssignment.INDEX,   # 1st fret
                },
                pattern_type=PatternType.OPEN
            ),
            
            # Caug (x-3-2-1-1-0)
            ChordPattern(
                name="open_Caug",
                quality=ChordQuality.AUGMENTED,
                frets=[None, 3, 2, 1, 1, 0],  # x-3-2-1-1-0
                root_string=5,  # Root C on 5th string, 3rd fret
                root_fret=3,
                finger_assignments={
                    5: FingerAssignment.PINKY,   # 3rd fret
                    4: FingerAssignment.RING,    # 2nd fret
                    3: FingerAssignment.INDEX,   # 1st fret
                    2: FingerAssignment.MIDDLE,  # 1st fret
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
        ]
        
        # 6th chord patterns
        sixth_patterns = [
            # A6 (x-0-2-2-2-2)
            ChordPattern(
                name="open_A6",
                quality=ChordQuality.SIXTH,
                frets=[None, 0, 2, 2, 2, 2],  # x-0-2-2-2-2
                root_string=5,  # Root A on 5th string, open
                root_fret=0,
                finger_assignments={
                    5: FingerAssignment.OPEN,    # open
                    4: FingerAssignment.INDEX,   # 2nd fret (barre-like)
                    3: FingerAssignment.MIDDLE,  # 2nd fret
                    2: FingerAssignment.RING,    # 2nd fret
                    1: FingerAssignment.PINKY,   # 2nd fret
                },
                pattern_type=PatternType.OPEN
            ),
            
            # C6 (x-3-2-2-1-0)
            ChordPattern(
                name="open_C6",
                quality=ChordQuality.SIXTH,
                frets=[None, 3, 2, 2, 1, 0],  # x-3-2-2-1-0
                root_string=5,  # Root C on 5th string, 3rd fret
                root_fret=3,
                finger_assignments={
                    5: FingerAssignment.PINKY,   # 3rd fret
                    4: FingerAssignment.MIDDLE,  # 2nd fret
                    3: FingerAssignment.RING,    # 2nd fret
                    2: FingerAssignment.INDEX,   # 1st fret
                    1: FingerAssignment.OPEN,    # open
                },
                pattern_type=PatternType.OPEN
            ),
        ]
        
        # 9th chord patterns
        ninth_patterns = [
            # A9 (x-0-2-4-2-3)
            ChordPattern(
                name="open_A9",
                quality=ChordQuality.NINTH,
                frets=[None, 0, 2, 4, 2, 3],  # x-0-2-4-2-3
                root_string=5,  # Root A on 5th string, open
                root_fret=0,
                finger_assignments={
                    5: FingerAssignment.OPEN,    # open
                    4: FingerAssignment.INDEX,   # 2nd fret
                    3: FingerAssignment.PINKY,   # 4th fret
                    2: FingerAssignment.MIDDLE,  # 2nd fret
                    1: FingerAssignment.RING,    # 3rd fret
                },
                pattern_type=PatternType.OPEN
            ),
            
            # C9 (x-3-2-3-3-3)
            ChordPattern(
                name="open_C9",
                quality=ChordQuality.NINTH,
                frets=[None, 3, 2, 3, 3, 3],  # x-3-2-3-3-3
                root_string=5,  # Root C on 5th string, 3rd fret
                root_fret=3,
                finger_assignments={
                    5: FingerAssignment.MIDDLE,  # 3rd fret (barre-like)
                    4: FingerAssignment.INDEX,   # 2nd fret
                    3: FingerAssignment.RING,    # 3rd fret
                    2: FingerAssignment.PINKY,   # 3rd fret
                    1: FingerAssignment.PINKY,   # 3rd fret (same finger)
                },
                pattern_type=PatternType.OPEN
            ),
        ]
        
        # Store patterns by quality - separate by actual chord quality
        self.patterns[ChordQuality.MAJOR] = open_major_patterns
        self.patterns[ChordQuality.MINOR] = open_minor_patterns
        
        # Separate seventh patterns by their actual quality
        self.patterns[ChordQuality.DOMINANT_SEVENTH] = [p for p in seventh_patterns if p.quality == ChordQuality.DOMINANT_SEVENTH]
        self.patterns[ChordQuality.MINOR_SEVENTH] = [p for p in seventh_patterns if p.quality == ChordQuality.MINOR_SEVENTH]
        
        self.patterns[ChordQuality.MAJOR_SEVENTH] = major_seventh_patterns
        self.patterns[ChordQuality.SUSPENDED_SECOND] = [p for p in suspended_patterns if p.quality == ChordQuality.SUSPENDED_SECOND]
        self.patterns[ChordQuality.SUSPENDED_FOURTH] = [p for p in suspended_patterns if p.quality == ChordQuality.SUSPENDED_FOURTH]
        self.patterns[ChordQuality.DIMINISHED] = diminished_patterns
        self.patterns[ChordQuality.AUGMENTED] = augmented_patterns
        self.patterns[ChordQuality.SIXTH] = sixth_patterns
        self.patterns[ChordQuality.NINTH] = ninth_patterns
    
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
            # For barre chords, also check if we can transpose the pattern
            elif pattern.pattern_type in [PatternType.BARRE_E, PatternType.BARRE_A]:
                # Calculate semitone distance between pattern root and target root
                semitone_diff = (root_note.pitch_class - pattern_root.pitch_class) % 12
                
                # Create transposed pattern if it's reasonable (not too high on fretboard)
                max_fret = max(f for f in pattern.frets if f is not None)
                if max_fret + semitone_diff <= 12:  # Don't transpose beyond 12th fret
                    transposed = self._transpose_pattern(pattern, semitone_diff, root_note)
                    if transposed:
                        matching.append(transposed)
        
        # Sort by lowest fret position to prefer easier positions
        matching.sort(key=lambda p: min(f for f in p.frets if f is not None) if any(f is not None for f in p.frets) else 999)
        
        return matching
    
    def _transpose_pattern(self, pattern: ChordPattern, semitones: int, target_root: Note) -> Optional[ChordPattern]:
        """
        Transpose a barre chord pattern by the given number of semitones.
        
        Args:
            pattern: Original pattern to transpose
            semitones: Number of semitones to transpose up
            target_root: Target root note for the transposed pattern
            
        Returns:
            Transposed pattern or None if transposition fails
        """
        if semitones == 0:
            return pattern
        
        try:
            # Transpose all fret positions
            transposed_frets = []
            for fret in pattern.frets:
                if fret is None:
                    transposed_frets.append(None)  # Keep muted strings muted
                else:
                    new_fret = fret + semitones
                    if new_fret > 15:  # Don't transpose too high
                        return None
                    transposed_frets.append(new_fret)
            
            # Create new pattern name
            new_name = f"{pattern.name}_transposed_to_{target_root.name}"
            
            # Transpose finger assignments
            transposed_assignments = {}
            for string, finger in pattern.finger_assignments.items():
                transposed_assignments[string] = finger
            
            # Create transposed pattern
            return ChordPattern(
                name=new_name,
                quality=pattern.quality,
                frets=transposed_frets,
                root_string=pattern.root_string,
                root_fret=pattern.root_fret + semitones,
                finger_assignments=transposed_assignments,
                pattern_type=pattern.pattern_type,
                difficulty=pattern.difficulty
            )
        except Exception:
            return None
    
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