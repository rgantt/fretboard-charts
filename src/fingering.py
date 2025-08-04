"""
Guitar fingering representation and validation.

This module provides classes and functions for:
- Representing guitar chord fingerings
- Validating fingering playability
- Calculating fingering difficulty and characteristics
"""

from typing import List, Dict, Tuple, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import math

from .music_theory import Note, Chord
from .fretboard import FretPosition, Fretboard, STANDARD_TUNING


class FingerAssignment(Enum):
    """Finger assignments for guitar playing"""
    MUTED = -1      # Muted string (not played)
    OPEN = 0        # Open string (no finger)
    INDEX = 1       # Index finger
    MIDDLE = 2      # Middle finger
    RING = 3        # Ring finger
    PINKY = 4       # Pinky finger


@dataclass
class Fingering:
    """
    Represents a complete guitar chord fingering.
    
    Attributes:
        positions: List of FretPosition objects for each played note
        finger_assignments: Dict mapping string numbers to finger assignments
        muted_strings: Set of string numbers that are muted
        chord: The chord this fingering represents (optional)
        difficulty: Calculated difficulty score (0.0-1.0)
        characteristics: Dict of fingering characteristics
    """
    positions: List[FretPosition]
    finger_assignments: Dict[int, FingerAssignment] = field(default_factory=dict)
    muted_strings: Set[int] = field(default_factory=set)
    chord: Optional[Chord] = None
    difficulty: float = 0.0
    characteristics: Dict[str, Union[bool, int, float]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize and validate the fingering"""
        self._validate_fingering()
        self._calculate_characteristics()
        self._calculate_difficulty()
    
    def _validate_fingering(self):
        """Validate that the fingering is internally consistent"""
        # Check that all positions have valid string numbers
        for pos in self.positions:
            if not 1 <= pos.string <= 6:
                raise ValueError(f"Invalid string number: {pos.string}")
            if not 0 <= pos.fret <= 22:
                raise ValueError(f"Invalid fret number: {pos.fret}")
        
        # Check that muted strings don't have positions
        played_strings = {pos.string for pos in self.positions}
        if played_strings & self.muted_strings:
            overlap = played_strings & self.muted_strings
            raise ValueError(f"Strings cannot be both played and muted: {overlap}")
        
        # Validate finger assignments
        for string, finger in self.finger_assignments.items():
            if not 1 <= string <= 6:
                raise ValueError(f"Invalid string number in finger assignment: {string}")
            if not isinstance(finger, FingerAssignment):
                raise ValueError(f"Invalid finger assignment: {finger}")
    
    def _calculate_characteristics(self):
        """Calculate various characteristics of this fingering"""
        # Initialize basic metrics (always set these, even for empty fingerings)
        frets = [pos.fret for pos in self.positions if pos.fret > 0] if self.positions else []
        
        self.characteristics.update({
            'num_notes': len(self.positions),
            'num_fretted_notes': len(frets),
            'num_open_strings': len([pos for pos in self.positions if pos.fret == 0]) if self.positions else 0,
            'num_muted_strings': len(self.muted_strings),
            'min_fret': min(frets) if frets else 0,
            'max_fret': max(frets) if frets else 0,
            'fret_span': max(frets) - min(frets) if len(frets) > 1 else 0,
        })
        
        # Early return for empty fingerings
        if not self.positions:
            self.characteristics.update({
                'is_open_position': False,
                'is_barre_chord': False,
                'has_open_strings': False,
                'requires_stretch': False,
                'fingers_used': 0,
                'hand_position': 1
            })
            return
        
        # Position characteristics
        self.characteristics.update({
            'is_open_position': self.characteristics['max_fret'] <= 3,
            'is_barre_chord': self._is_barre_chord(),
            'has_open_strings': self.characteristics['num_open_strings'] > 0,
            'requires_stretch': self.characteristics['fret_span'] > 3,
        })
        
        # Finger usage
        finger_count = len([f for f in self.finger_assignments.values() 
                           if f not in [FingerAssignment.OPEN, FingerAssignment.MUTED]])
        self.characteristics['fingers_used'] = finger_count
        
        # Hand position
        if frets:
            self.characteristics['hand_position'] = self._calculate_hand_position()
        else:
            self.characteristics['hand_position'] = 1  # Open position
    
    def _is_barre_chord(self) -> bool:
        """Check if this fingering requires a barre (one finger on multiple strings at same fret)"""
        if not self.finger_assignments:
            return False
        
        # Group positions by finger
        finger_positions = {}
        for string, finger in self.finger_assignments.items():
            if finger != FingerAssignment.OPEN and finger != FingerAssignment.MUTED:
                if finger not in finger_positions:
                    finger_positions[finger] = []
                # Find the fret for this string
                for pos in self.positions:
                    if pos.string == string:
                        finger_positions[finger].append(pos.fret)
                        break
        
        # Check if any finger plays the same fret on multiple strings
        for finger, frets in finger_positions.items():
            if len(frets) > 1 and len(set(frets)) == 1:  # Same fret, multiple strings
                return True
        
        return False
    
    def _calculate_hand_position(self) -> int:
        """Calculate the hand position (which fret the index finger is positioned at)"""
        frets = [pos.fret for pos in self.positions if pos.fret > 0]
        if not frets:
            return 1
        
        min_fret = min(frets)
        # Hand position is typically one fret lower than the minimum fret
        return max(1, min_fret - 1) if min_fret > 1 else 1
    
    def _calculate_difficulty(self):
        """Calculate a difficulty score from 0.0 (easy) to 1.0 (very hard)"""
        if not self.positions:
            self.difficulty = 0.0
            return
        
        # Start with base difficulty for any chord
        score = 0.1  # Base difficulty
        
        # Fret span difficulty
        fret_span = self.characteristics.get('fret_span', 0)
        if fret_span > 3:
            score += 0.2 * (fret_span - 3)  # Each fret beyond 3 adds difficulty
        elif fret_span > 1:
            score += 0.05 * (fret_span - 1)  # Some difficulty for any span
        
        # High fret positions are harder
        max_fret = self.characteristics.get('max_fret', 0)
        if max_fret > 12:
            score += 0.1 * (max_fret - 12) / 10  # Scale high fret difficulty
        elif max_fret > 5:
            score += 0.02 * (max_fret - 5) / 10  # Slight difficulty for mid-range frets
        
        # Barre chords are harder
        if self.characteristics.get('is_barre_chord', False):
            score += 0.3
        
        # Many fingers required
        fingers_used = self.characteristics.get('fingers_used', 0)
        if fingers_used > 3:
            score += 0.1 * (fingers_used - 3)
        elif fingers_used > 1:
            score += 0.02 * (fingers_used - 1)  # Slight difficulty for multiple fingers
        
        # Open strings make it easier
        if self.characteristics.get('has_open_strings', False):
            score -= 0.05  # Reduced reduction
        
        # Open position is easier
        if self.characteristics.get('is_open_position', False):
            score -= 0.05  # Reduced reduction
        
        # Clamp to 0.0-1.0 range
        self.difficulty = max(0.0, min(1.0, score))
    
    def get_chord_shape(self) -> List[Optional[int]]:
        """
        Get the chord shape as a list of fret numbers.
        
        Returns:
            List of 6 fret numbers (string 6 to string 1), None for muted strings
        """
        shape = [None] * 6  # Initialize all strings as muted
        
        # Fill in played strings
        for pos in self.positions:
            string_index = 6 - pos.string  # Convert to 0-based index (string 6 = index 0)
            shape[string_index] = pos.fret
        
        return shape
    
    def get_notes(self) -> List[Note]:
        """Get all notes in this fingering"""
        return [pos.note for pos in self.positions]
    
    def get_bass_note(self) -> Optional[Note]:
        """Get the bass note (lowest string being played)"""
        if not self.positions:
            return None
        
        # Find the lowest string number being played (highest string number = lowest pitch)
        lowest_string_pos = max(self.positions, key=lambda pos: pos.string)
        return lowest_string_pos.note
    
    def contains_notes(self, required_notes: List[Note]) -> bool:
        """Check if this fingering contains all required notes (by pitch class)"""
        fingering_pitch_classes = {note.pitch_class for note in self.get_notes()}
        required_pitch_classes = {note.pitch_class for note in required_notes}
        return required_pitch_classes.issubset(fingering_pitch_classes)
    
    def is_playable(self) -> bool:
        """Check if this fingering is physically playable"""
        # Basic playability checks
        if not self.positions:
            return False
        
        # Check fret span (most people can't stretch more than 4 frets)
        if self.characteristics.get('fret_span', 0) > 4:
            return False
        
        # Check for finger conflicts (same finger on different frets)
        finger_frets = {}
        for string, finger in self.finger_assignments.items():
            if finger in [FingerAssignment.OPEN, FingerAssignment.MUTED]:
                continue
            
            # Find the fret for this string
            fret = None
            for pos in self.positions:
                if pos.string == string:
                    fret = pos.fret
                    break
            
            if fret is not None:
                if finger in finger_frets:
                    # Same finger on different frets is only okay if it's a barre
                    if finger_frets[finger] != fret:
                        # Check if it's a valid barre (consecutive strings at same fret)
                        return False  # Simplified - could implement full barre validation
                else:
                    finger_frets[finger] = fret
        
        return True
    
    def __str__(self) -> str:
        shape = self.get_chord_shape()
        shape_str = '-'.join([str(f) if f is not None else 'x' for f in shape])
        chord_name = str(self.chord) if self.chord else "Unknown"
        return f"{chord_name}: {shape_str} (difficulty: {self.difficulty:.2f})"
    
    def __repr__(self) -> str:
        return f"Fingering({len(self.positions)} notes, difficulty={self.difficulty:.2f})"


class FingeringValidator:
    """
    Validates and scores guitar fingerings for playability and quality.
    """
    
    def __init__(self, fretboard: Fretboard = None):
        """Initialize the validator with a fretboard"""
        self.fretboard = fretboard or Fretboard()
    
    def validate_fingering(self, fingering: Fingering) -> Dict[str, Union[bool, str, float]]:
        """
        Comprehensive validation of a fingering.
        
        Args:
            fingering: The fingering to validate
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'is_valid': True,
            'is_playable': True,
            'issues': [],
            'warnings': [],
            'score': 1.0
        }
        
        # Basic structure validation
        if not fingering.positions:
            results['is_valid'] = False
            results['issues'].append("No positions specified")
            return results
        
        # Check for valid positions
        for pos in fingering.positions:
            if not self.fretboard.validate_position(pos.string, pos.fret):
                results['is_valid'] = False
                results['issues'].append(f"Invalid position: {pos}")
        
        if not results['is_valid']:
            return results
        
        # Playability checks
        playability_score = self._check_playability(fingering, results)
        
        # Musical quality checks
        musical_score = self._check_musical_quality(fingering, results)
        
        # Overall score
        results['score'] = (playability_score + musical_score) / 2
        results['is_playable'] = playability_score > 0.3  # Threshold for playability
        
        return results
    
    def _check_playability(self, fingering: Fingering, results: Dict) -> float:
        """Check physical playability of the fingering"""
        score = 1.0
        
        # Fret span check
        fret_span = fingering.characteristics.get('fret_span', 0)
        if fret_span > 4:
            results['issues'].append(f"Fret span too large: {fret_span} frets")
            score -= 0.8  # Much larger penalty for impossible spans
        elif fret_span > 3:
            results['warnings'].append(f"Large fret span: {fret_span} frets")
            score -= 0.2
        
        # High fret difficulty
        max_fret = fingering.characteristics.get('max_fret', 0)
        if max_fret > 15:
            results['warnings'].append(f"Very high position: fret {max_fret}")
            score -= 0.1
        
        # Finger assignment conflicts
        if not self._check_finger_assignments(fingering):
            results['issues'].append("Impossible finger assignments")
            score -= 0.5
        
        return max(0.0, score)
    
    def _check_musical_quality(self, fingering: Fingering, results: Dict) -> float:
        """Check musical quality of the fingering"""
        score = 1.0
        
        # Prefer open strings in appropriate positions
        if fingering.characteristics.get('is_open_position', False):
            if fingering.characteristics.get('num_open_strings', 0) == 0:
                results['warnings'].append("No open strings in open position")
                score -= 0.1
        
        # Check for good bass note
        bass_note = fingering.get_bass_note()
        if fingering.chord and bass_note:
            chord_root = fingering.chord.root
            if bass_note.pitch_class != chord_root.pitch_class:
                # Not root in bass - check if it's a specified bass note
                if fingering.chord.bass:
                    if bass_note.pitch_class != fingering.chord.bass.pitch_class:
                        results['warnings'].append("Bass note doesn't match chord root or specified bass")
                        score -= 0.1
                else:
                    results['warnings'].append("Bass note is not chord root")
                    score -= 0.05
        
        return max(0.0, score)
    
    def _check_finger_assignments(self, fingering: Fingering) -> bool:
        """Check if finger assignments are physically possible"""
        # This is a simplified check - a full implementation would be more complex
        finger_positions = {}
        
        for string, finger in fingering.finger_assignments.items():
            if finger in [FingerAssignment.OPEN, FingerAssignment.MUTED]:
                continue
            
            # Find the fret for this string
            fret = None
            for pos in fingering.positions:
                if pos.string == string:
                    fret = pos.fret
                    break
            
            if fret is not None:
                if finger in finger_positions:
                    # Check if it's a valid barre or impossible stretch
                    prev_string, prev_fret = finger_positions[finger]
                    if prev_fret != fret:
                        # Different frets with same finger - only valid in very specific cases
                        return False
                    # Same fret - check if strings are adjacent enough for barre
                    string_distance = abs(string - prev_string)
                    if string_distance > 5:  # Can't barre across all 6 strings easily
                        return False
                
                finger_positions[finger] = (string, fret)
        
        return True
    
    def rank_fingerings(self, fingerings: List[Fingering]) -> List[Fingering]:
        """
        Rank a list of fingerings by quality and playability.
        
        Args:
            fingerings: List of fingerings to rank
        
        Returns:
            List of fingerings sorted by quality (best first)
        """
        def score_fingering(fingering: Fingering) -> float:
            validation = self.validate_fingering(fingering)
            if not validation['is_playable']:
                return -1.0  # Unplayable fingerings go to the end
            
            score = validation['score']
            
            # Bonus for common characteristics
            if fingering.characteristics.get('is_open_position', False):
                score += 0.1
            if fingering.characteristics.get('has_open_strings', False):
                score += 0.05
            
            # Penalty for difficulty
            score -= fingering.difficulty * 0.2
            
            return score
        
        # Sort by score (descending)
        return sorted(fingerings, key=score_fingering, reverse=True)
