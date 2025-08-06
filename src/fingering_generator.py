"""
Guitar chord fingering generation engine.

This module implements the core algorithm for generating practical, playable
guitar chord fingerings from chord symbols using a hybrid approach:
- Position-based search across fretboard regions
- Pattern matching for common chord shapes
- Post-processing for finger assignments and ranking
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import itertools

from .music_theory import Note, Chord, ChordQuality
from .fretboard import Fretboard, FretPosition, STANDARD_TUNING
from .fingering import Fingering, FingerAssignment, FingeringValidator
from .chord_patterns import CHORD_PATTERNS


class FretboardRegion(Enum):
    """Fretboard regions for position-based generation"""
    OPEN = "open"        # frets 0-4
    LOW = "low"          # frets 2-7  
    MID = "mid"          # frets 5-12


@dataclass(frozen=True)
class ChordToneRequirement:
    """Defines requirements for chord tone inclusion"""
    note: Note
    priority: int        # 1=required, 2=preferred, 3=optional
    interval: int        # semitone interval from root
    name: str           # "root", "3rd", "5th", "7th", etc.


@dataclass
class GenerationConfig:
    """Configuration for fingering generation"""
    max_results: int = 5
    max_fret_span: int = 4
    min_required_tones: int = 3
    prefer_open_strings: bool = True
    include_doubled_notes: bool = True
    max_fret: int = 12


class FingeringGenerator:
    """
    Main engine for generating guitar chord fingerings.
    
    Uses a hybrid approach combining position-based search with 
    pattern matching to generate practical, playable fingerings.
    """
    
    def __init__(self, fretboard: Fretboard = None, validator: FingeringValidator = None):
        """
        Initialize the fingering generator.
        
        Args:
            fretboard: Fretboard instance to use (defaults to standard tuning)
            validator: FingeringValidator instance for quality checks
        """
        self.fretboard = fretboard or Fretboard(STANDARD_TUNING)
        self.validator = validator or FingeringValidator(self.fretboard)
        
        # Define fretboard regions
        self.regions = {
            FretboardRegion.OPEN: (0, 4),
            FretboardRegion.LOW: (2, 7),
            FretboardRegion.MID: (5, 12)
        }
    
    def generate_fingerings(self, chord: Chord, config: GenerationConfig = None) -> List[Fingering]:
        """
        Generate multiple fingerings for a given chord.
        
        Args:
            chord: The chord to generate fingerings for
            config: Generation configuration parameters
            
        Returns:
            List of fingerings ranked by quality (best first)
        """
        config = config or GenerationConfig()
        
        # Step 1: Analyze chord and determine requirements
        requirements = self._analyze_chord_requirements(chord)
        
        # Step 2: Generate candidate fingerings across all regions
        candidates = []
        
        # First, try to find known chord patterns (especially for open position)
        pattern_fingerings = self._generate_from_patterns(chord, config)
        candidates.extend(pattern_fingerings)
        
        chord_name = str(chord)
        
        
        # Then generate using position-based search
        # Prioritize regions: open first, then low, then mid
        for region in [FretboardRegion.OPEN, FretboardRegion.LOW, FretboardRegion.MID]:
            region_fingerings = self._generate_for_region(chord, requirements, region, config)
            candidates.extend(region_fingerings)
        
        # Step 3: Post-process finger assignments
        # Only assign fingers for fingerings that don't already have complete assignments
        for fingering in candidates:
            # Skip if this already has comprehensive finger assignments (from patterns)
            has_fretted_assignments = any(
                finger not in [FingerAssignment.OPEN, FingerAssignment.MUTED] 
                for finger in fingering.finger_assignments.values()
            )
            
            # If it has good assignments for all fretted notes, don't override
            fretted_strings = {pos.string for pos in fingering.positions if pos.fret > 0}
            assigned_fretted_strings = {
                string for string, finger in fingering.finger_assignments.items() 
                if finger not in [FingerAssignment.OPEN, FingerAssignment.MUTED]
            }
            
            if has_fretted_assignments and fretted_strings.issubset(assigned_fretted_strings):
                # Pattern has good assignments, don't override
                continue
            else:
                # Need to assign fingers
                self._assign_fingers(fingering)
        
        # Step 4: Validate and filter
        valid_fingerings = []
        
        for fingering in candidates:
            validation = self.validator.validate_fingering(fingering)
            # Use both the validator's assessment AND the fingering's own method
            if validation['is_playable'] and validation['score'] > 0.3 and fingering.is_playable():
                valid_fingerings.append(fingering)
        
        # Step 5: Rank and return top results
        ranked_fingerings = self.validator.rank_fingerings(valid_fingerings)
        
        
        return ranked_fingerings[:config.max_results]
    
    def _analyze_chord_requirements(self, chord: Chord) -> List[ChordToneRequirement]:
        """
        Analyze a chord to determine which tones are required vs optional.
        
        Args:
            chord: Chord to analyze
            
        Returns:
            List of chord tone requirements with priorities
        """
        requirements = []
        intervals = chord.get_intervals()
        chord_notes = chord.get_notes()
        
        # Map intervals to chord tone names and priorities
        interval_info = {
            0: ("root", 1),      # Root is always required
            3: ("b3rd", 1),      # Minor 3rd required for minor chords
            4: ("3rd", 1),       # Major 3rd required for major chords  
            6: ("b5th", 1),      # Diminished 5th required for dim chords
            7: ("5th", 2),       # Perfect 5th preferred but optional
            8: ("#5th", 1),      # Augmented 5th required for aug chords
            10: ("b7th", 1),     # Minor 7th required for dom7, m7, etc.
            11: ("7th", 1),      # Major 7th required for maj7
            2: ("9th", 3),       # 9th is optional extension
            5: ("11th", 3),      # 11th is optional extension
            9: ("13th", 3),      # 13th is optional extension
        }
        
        # Special handling for different chord qualities
        if chord.quality in [ChordQuality.MAJOR, ChordQuality.MINOR]:
            # For basic triads, 5th is more important
            interval_info[7] = ("5th", 1)
        elif chord.quality in [ChordQuality.SUSPENDED_SECOND, ChordQuality.SUSPENDED_FOURTH]:
            # For sus chords, the suspended note is required
            if 2 in intervals:  # sus2
                interval_info[2] = ("2nd", 1) 
            if 5 in intervals:  # sus4
                interval_info[5] = ("4th", 1)
        
        # Build requirements list
        for i, (interval, note) in enumerate(zip(intervals, chord_notes)):
            if interval in interval_info:
                name, priority = interval_info[interval]
                requirements.append(ChordToneRequirement(
                    note=note,
                    priority=priority,
                    interval=interval,
                    name=name
                ))
            else:
                # Unknown interval - treat as optional extension
                requirements.append(ChordToneRequirement(
                    note=note,
                    priority=3,
                    interval=interval,
                    name=f"interval_{interval}"
                ))
        
        # Handle slash chord bass note - make it highest priority
        if chord.bass:
            bass_interval = (chord.bass.pitch_class - chord.root.pitch_class) % 12
            bass_req = ChordToneRequirement(
                note=chord.bass,
                priority=0,  # Highest priority - even higher than root
                interval=bass_interval,
                name="bass"
            )
            requirements.append(bass_req)
        
        # Sort by priority (required first, then preferred, then optional)
        requirements.sort(key=lambda req: req.priority)
        
        return requirements
    
    def _generate_from_patterns(self, chord: Chord, config: GenerationConfig) -> List[Fingering]:
        """
        Generate fingerings using known chord patterns.
        
        Args:
            chord: The chord to generate fingerings for
            config: Generation configuration
            
        Returns:
            List of fingerings from matching patterns
        """
        pattern_fingerings = []
        
        # Find matching patterns for this chord
        matching_patterns = CHORD_PATTERNS.find_matching_patterns(chord.root, chord.quality)
        
        for pattern in matching_patterns:
            try:
                fingering = CHORD_PATTERNS.pattern_to_fingering(pattern, chord)
                
                
                # Validate the pattern fingering
                if fingering.is_playable() and len(fingering.positions) >= config.min_required_tones:
                    # Check if it contains the required chord tones
                    chord_notes = chord.get_notes()
                    contains_required = fingering.contains_notes(chord_notes)
                    
                    # For extended chords, allow patterns that omit the 5th (common in guitar voicings)
                    if not contains_required and chord.quality.name in ['DOMINANT_SEVENTH', 'SIXTH', 'NINTH']:
                        chord_notes = chord.get_notes()
                        if chord.quality.name == 'DOMINANT_SEVENTH':
                            # Check if it contains root, 3rd, and 7th (allow omitting 5th)
                            essential_notes = [chord.root, chord_notes[1], chord_notes[3]]  # Root, 3rd, 7th
                        elif chord.quality.name == 'SIXTH':
                            # Check if it contains root, 3rd, and 6th (allow omitting 5th)
                            essential_notes = [chord.root, chord_notes[1], chord_notes[3]]  # Root, 3rd, 6th
                        elif chord.quality.name == 'NINTH':
                            # Check if it contains root, 3rd, 7th, and 9th (allow omitting 5th)
                            if len(chord_notes) >= 5:
                                essential_notes = [chord.root, chord_notes[1], chord_notes[3], chord_notes[4]]  # Root, 3rd, 7th, 9th
                            else:
                                essential_notes = chord_notes  # Fallback to all notes
                        
                        contains_required = fingering.contains_notes(essential_notes)
                    
                    # For slash chords, validate that bass note is on bass strings
                    bass_valid = True
                    if chord.bass:
                        bass_note = fingering.get_bass_note()
                        if not bass_note or bass_note.pitch_class != chord.bass.pitch_class:
                            bass_valid = False
                        else:
                            # Check that bass note is on strings 4, 5, or 6
                            bass_positions = [pos for pos in fingering.positions if pos.string >= 4]
                            if not bass_positions:
                                bass_valid = False
                            else:
                                lowest_string = max(pos.string for pos in fingering.positions)
                                bass_string_positions = [pos for pos in bass_positions if pos.string == lowest_string]
                                if not any(self.fretboard.get_note_at_position(pos).pitch_class == chord.bass.pitch_class 
                                          for pos in bass_string_positions):
                                    bass_valid = False
                    
                    if contains_required and bass_valid:
                        pattern_fingerings.append(fingering)
                        
                        # Limit pattern results
                        if len(pattern_fingerings) >= 3:
                            break
            except Exception as e:
                continue
        
        return pattern_fingerings
    
    def _generate_for_region(self, chord: Chord, requirements: List[ChordToneRequirement], 
                           region: FretboardRegion, config: GenerationConfig) -> List[Fingering]:
        """
        Generate fingerings for a specific fretboard region.
        
        Args:
            chord: The chord being generated
            requirements: Chord tone requirements
            region: Fretboard region to search
            config: Generation configuration
            
        Returns:
            List of fingerings found in this region
        """
        min_fret, max_fret = self.regions[region]
        max_fret = min(max_fret, config.max_fret)
        
        # Get positions for each required note in this region
        note_positions = {}
        for req in requirements:
            positions = self.fretboard.get_positions_for_note(req.note, max_fret=max_fret)
            # Filter to region
            region_positions = [pos for pos in positions if min_fret <= pos.fret <= max_fret]
            if region_positions:  # Only include notes that have positions in this region
                note_positions[req] = region_positions
        
        # Generate combinations of positions
        fingerings = []
        
        # Get requirements by priority, with special handling for bass notes (priority 0)
        bass_reqs = [req for req in requirements if req.priority == 0 and req in note_positions]
        required_reqs = [req for req in requirements if req.priority == 1 and req in note_positions]
        preferred_reqs = [req for req in requirements if req.priority == 2 and req in note_positions]
        
        # For slash chords, we need to prioritize bass note on bass strings (4, 5, 6)
        if bass_reqs:
            bass_req = bass_reqs[0]  # Should only be one bass requirement
            # Get bass note positions and filter to only bass strings (4, 5, 6)
            all_bass_positions = note_positions[bass_req]
            bass_positions = [pos for pos in all_bass_positions if pos.string >= 4]
            # Sort by string (descending - string 6 is lowest)
            bass_positions.sort(key=lambda pos: pos.string, reverse=True)
            
            # If no valid bass positions, return empty (slash chord requires bass note on bass strings)
            if not bass_positions:
                return []
            
            # Try bass positions, prioritizing lower strings
            for bass_pos in bass_positions:
                # Generate fingerings with this bass position
                remaining_reqs = required_reqs + preferred_reqs
                bass_fingerings = self._generate_with_bass_note(bass_pos, bass_req, remaining_reqs, note_positions, config, chord)
                fingerings.extend(bass_fingerings)
                
                # Limit fingerings from each bass position
                if len(fingerings) >= 10:
                    break
            
            return fingerings[:config.max_results]
        
        if len(required_reqs) < config.min_required_tones:
            return []  # Not enough required notes available in this region
        
        # Generate combinations starting with required notes
        for req_combo in self._generate_position_combinations(required_reqs, note_positions, config):
            # Try adding preferred notes if space allows
            current_positions = list(req_combo)
            current_span = self._calculate_fret_span(current_positions)
            
            if current_span <= config.max_fret_span:
                # Try to add preferred notes
                for pref_req in preferred_reqs:
                    if pref_req in note_positions:
                        for pref_pos in note_positions[pref_req]:
                            test_positions = current_positions + [pref_pos]
                            if self._calculate_fret_span(test_positions) <= config.max_fret_span:
                                current_positions.append(pref_pos)
                                break  # Take first valid preferred position
                
                # Create fingering
                if len(current_positions) >= config.min_required_tones:
                    fingering = Fingering(
                        positions=current_positions,
                        chord=chord
                    )
                    fingerings.append(fingering)
        
        return fingerings
    
    def _generate_with_bass_note(self, bass_pos: FretPosition, bass_req: ChordToneRequirement,
                               remaining_reqs: List[ChordToneRequirement],
                               note_positions: Dict[ChordToneRequirement, List[FretPosition]],
                               config: GenerationConfig, chord: Chord) -> List[Fingering]:
        """
        Generate fingerings that include a specific bass note position.
        
        Args:
            bass_pos: The bass position to include
            bass_req: The bass requirement
            remaining_reqs: Other chord tone requirements
            note_positions: Available positions for each requirement
            config: Generation configuration
            chord: The chord being generated
            
        Returns:
            List of fingerings with the given bass note
        """
        fingerings = []
        
        # Filter remaining requirements to avoid duplicating the bass note
        filtered_reqs = []
        for req in remaining_reqs:
            if req.note.pitch_class != bass_req.note.pitch_class:
                filtered_reqs.append(req)
            elif req in note_positions:
                # Same note as bass - only include positions on different strings
                different_string_positions = [pos for pos in note_positions[req] if pos.string != bass_pos.string]
                if different_string_positions:
                    # Create a new requirement with filtered positions
                    filtered_positions = {req: different_string_positions}
                    note_positions.update(filtered_positions)
                    filtered_reqs.append(req)
        
        # Generate combinations with the bass note fixed
        for req_combo in self._generate_position_combinations(filtered_reqs, note_positions, config):
            all_positions = [bass_pos] + list(req_combo)
            
            # Validate the complete combination
            if self._validate_position_combination(all_positions, config):
                # Check that bass note is on a bass string (4, 5, or 6) AND the lowest string played
                played_strings = [pos.string for pos in all_positions]
                lowest_string = max(played_strings)  # Higher number = lower string
                
                if bass_pos.string >= 4 and bass_pos.string == lowest_string:
                    # For slash chords, try to add more chord tones if possible for fuller sound
                    final_positions = list(all_positions)
                    
                    # Try to add additional instances of chord tones on higher strings for fuller sound
                    chord_notes = chord.get_notes()
                    used_strings = {pos.string for pos in final_positions}
                    
                    # Prioritize higher strings (1, 2, 3) for melody notes, avoid low strings
                    for string in range(1, 4):  # Only strings 1-3 (treble strings)
                        if string not in used_strings:
                            for note in chord_notes:
                                # Prefer root note for melody completion
                                if note.pitch_class == chord.root.pitch_class:
                                    # Find positions for root note on this string in the open region
                                    for fret in range(0, 5):  # Open region, frets 0-4
                                        if self.fretboard.validate_position(string, fret):
                                            fret_note = self.fretboard.get_note_at_position(string, fret)
                                            if fret_note.pitch_class == note.pitch_class:
                                                test_pos = FretPosition(string, fret, fret_note)
                                                test_positions = final_positions + [test_pos]
                                                
                                                # Check if adding this position improves the fingering
                                                if (self._validate_position_combination(test_positions, config) and
                                                    self._calculate_fret_span(test_positions) <= config.max_fret_span):
                                                    final_positions.append(test_pos)
                                                    break  # Take first valid addition per string
                    
                    fingering = Fingering(
                        positions=final_positions,
                        chord=chord
                    )
                    fingerings.append(fingering)
                    
                    # Limit to prevent too many combinations
                    if len(fingerings) >= 5:
                        break
        
        return fingerings
    
    def _generate_position_combinations(self, requirements: List[ChordToneRequirement], 
                                      note_positions: Dict[ChordToneRequirement, List[FretPosition]],
                                      config: GenerationConfig) -> List[List[FretPosition]]:
        """
        Generate valid combinations of positions for required chord tones.
        
        Args:
            requirements: Required chord tones
            note_positions: Available positions for each requirement
            config: Generation configuration
            
        Returns:
            List of position combinations that meet constraints
        """
        if not requirements:
            return []
        
        combinations = []
        
        # Use itertools.product to generate all combinations
        position_lists = [note_positions[req] for req in requirements]
        
        for combo in itertools.product(*position_lists):
            positions = list(combo)
            
            # Check constraints
            if self._validate_position_combination(positions, config):
                combinations.append(positions)
                
                # Limit combinations to prevent explosion
                if len(combinations) >= 20:
                    break
        
        return combinations
    
    def _validate_position_combination(self, positions: List[FretPosition], 
                                     config: GenerationConfig) -> bool:
        """
        Validate that a combination of positions meets basic constraints.
        
        Args:
            positions: List of fret positions
            config: Generation configuration
            
        Returns:
            True if combination is valid
        """
        if not positions:
            return False
        
        # Check fret span
        if self._calculate_fret_span(positions) > config.max_fret_span:
            return False
        
        # Check for string conflicts (same string, different frets)
        string_frets = {}
        for pos in positions:
            if pos.string in string_frets:
                if string_frets[pos.string] != pos.fret:
                    return False  # Same string, different frets - conflict
            else:
                string_frets[pos.string] = pos.fret
        
        # Must have at least minimum required tones
        if len(positions) < config.min_required_tones:
            return False
        
        return True
    
    def _calculate_fret_span(self, positions: List[FretPosition]) -> int:
        """Calculate the fret span for a list of positions."""
        if not positions:
            return 0
        
        frets = [pos.fret for pos in positions if pos.fret > 0]  # Ignore open strings
        if not frets:
            return 0
        
        return max(frets) - min(frets)
    
    def _assign_fingers(self, fingering: Fingering) -> None:
        """
        Post-process finger assignments for a fingering.
        
        Args:
            fingering: Fingering to assign fingers to (modified in place)
        """
        if not fingering.positions:
            return
        
        # Simple heuristic finger assignment
        finger_assignments = {}
        
        # Sort positions by fret (ascending)
        sorted_positions = sorted(fingering.positions, key=lambda pos: (pos.fret, pos.string))
        
        # Assign fingers based on fret positions
        fret_to_finger = {}
        available_fingers = [FingerAssignment.INDEX, FingerAssignment.MIDDLE, 
                           FingerAssignment.RING, FingerAssignment.PINKY]
        finger_index = 0
        
        for pos in sorted_positions:
            if pos.fret == 0:
                # Open string
                finger_assignments[pos.string] = FingerAssignment.OPEN
            else:
                # Fretted position
                if pos.fret not in fret_to_finger:
                    if finger_index < len(available_fingers):
                        fret_to_finger[pos.fret] = available_fingers[finger_index]
                        finger_index += 1
                    else:
                        # Fallback - reuse last finger (indicates barre or stretch)
                        fret_to_finger[pos.fret] = available_fingers[-1]
                
                finger_assignments[pos.string] = fret_to_finger[pos.fret]
        
        # Update fingering
        fingering.finger_assignments = finger_assignments
        
        # Recalculate characteristics with new finger assignments
        fingering._calculate_characteristics()
        fingering._calculate_difficulty()


# Convenience function for direct use
def generate_chord_fingerings(chord_symbol: str, max_results: int = 5) -> List[Fingering]:
    """
    Convenience function to generate fingerings from a chord symbol string.
    
    Args:
        chord_symbol: Chord symbol string (e.g., "Cmaj7", "Dm7/G")
        max_results: Maximum number of fingerings to return
        
    Returns:
        List of fingerings ranked by quality
    """
    from .chord_parser import quick_parse
    
    chord = quick_parse(chord_symbol)
    generator = FingeringGenerator()
    config = GenerationConfig(max_results=max_results)
    
    return generator.generate_fingerings(chord, config)