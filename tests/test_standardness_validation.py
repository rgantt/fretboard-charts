"""
Test suite for standardness validation improvements.

Tests that the enhanced validation system properly prioritizes standard,
expected guitar chord fingerings that real guitarists use.
"""

import pytest
from src import generate_chord_fingerings
from src.fingering import FingeringValidator
from src.music_theory import Chord, ChordQuality, Note


class TestStandardnessValidation:
    """Test the standardness scoring system"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.validator = FingeringValidator()
    
    def test_standard_open_chords_ranked_first(self):
        """Test that standard open chord fingerings are ranked first"""
        standard_chords_and_shapes = [
            ('C', 'x-3-2-0-1-0'),    # Standard open C major
            ('G', '3-2-0-0-3-3'),    # Standard open G major  
            ('Am', 'x-0-2-2-1-0'),   # Standard open A minor
            ('Em', '0-2-2-0-0-0'),   # Standard open E minor
            ('Dm', 'x-x-0-2-3-1'),   # Standard open D minor
            ('G7', '3-2-0-0-0-1'),   # Standard open G7
            ('Am7', 'x-0-2-0-1-0')   # Standard open Am7
        ]
        
        for chord_name, expected_shape in standard_chords_and_shapes:
            fingerings = generate_chord_fingerings(chord_name, max_results=3)
            
            # Check that we got fingerings
            assert len(fingerings) > 0, f"No fingerings found for {chord_name}"
            
            # Check that the first fingering matches the expected standard shape
            first_fingering = fingerings[0]
            actual_shape = '-'.join([str(f) if f is not None else 'x' 
                                   for f in first_fingering.get_chord_shape()])
            
            assert actual_shape == expected_shape, \
                f"For {chord_name}, expected {expected_shape} first, got {actual_shape}"
            
            # Check that the standard fingering has a high score
            validation = self.validator.validate_fingering(first_fingering)
            assert validation['score'] >= 0.9, \
                f"Standard {chord_name} fingering has low score: {validation['score']}"
    
    def test_pattern_matching_bonus(self):
        """Test that pattern matching gives appropriate bonuses"""
        # Generate C major fingerings
        c_fingerings = generate_chord_fingerings('C', max_results=5)
        
        # Find the standard pattern and a non-standard one
        standard_fingering = None
        non_standard_fingering = None
        
        for f in c_fingerings:
            shape = '-'.join([str(fret) if fret is not None else 'x' 
                            for fret in f.get_chord_shape()])
            if shape == 'x-3-2-0-1-0':  # Standard C major
                standard_fingering = f
            elif len(f.positions) == 3:  # Simpler, non-standard fingering
                non_standard_fingering = f
        
        assert standard_fingering is not None, "Standard C major fingering not found"
        assert non_standard_fingering is not None, "Non-standard fingering not found"
        
        # Validate both
        standard_validation = self.validator.validate_fingering(standard_fingering)
        non_standard_validation = self.validator.validate_fingering(non_standard_fingering)
        
        # Standard should score higher
        assert standard_validation['score'] > non_standard_validation['score'], \
            f"Standard C major scored {standard_validation['score']}, " \
            f"non-standard scored {non_standard_validation['score']}"
        
        # Standard should have pattern match warning
        pattern_matched = any('pattern' in warning.lower() 
                            for warning in standard_validation['warnings'])
        assert pattern_matched, "Standard pattern should be detected"
    
    def test_completeness_bonus(self):
        """Test that fingerings with more chord tones score higher"""
        fingerings = generate_chord_fingerings('G', max_results=5)
        
        # Find fingerings with different numbers of notes
        full_fingering = None
        minimal_fingering = None
        
        for f in fingerings:
            if len(f.positions) >= 5:  # Full chord
                full_fingering = f
            elif len(f.positions) == 3:  # Minimal chord
                minimal_fingering = f
        
        if full_fingering and minimal_fingering:
            full_validation = self.validator.validate_fingering(full_fingering)
            minimal_validation = self.validator.validate_fingering(minimal_fingering)
            
            # Full chord should generally score higher (unless minimal is a perfect standard pattern)
            # This tests the completeness bonus
            if not any('pattern' in w.lower() for w in minimal_validation['warnings']):
                assert full_validation['score'] >= minimal_validation['score'], \
                    f"Full chord should score at least as high as minimal chord"
    
    def test_bass_note_correctness(self):
        """Test that correct bass notes get bonuses"""
        dm_fingerings = generate_chord_fingerings('Dm', max_results=3)
        
        # Find fingerings with different bass notes
        root_bass_fingering = None
        wrong_bass_fingering = None
        
        for f in dm_fingerings:
            bass_note = f.get_bass_note()
            if bass_note and bass_note.name == 'D':  # Correct root in bass
                root_bass_fingering = f
            elif bass_note and bass_note.name != 'D':  # Wrong bass note
                wrong_bass_fingering = f
        
        if root_bass_fingering and wrong_bass_fingering:
            root_validation = self.validator.validate_fingering(root_bass_fingering)
            wrong_validation = self.validator.validate_fingering(wrong_bass_fingering)
            
            # Root in bass should score higher
            assert root_validation['score'] > wrong_validation['score'], \
                f"Root bass should score higher than wrong bass"
    
    def test_open_position_bonus(self):
        """Test that common open chords get open position bonuses"""
        # Test a chord that should be played in open position
        c_fingerings = generate_chord_fingerings('C', max_results=5)
        
        # The top fingering for C should be in open position
        top_fingering = c_fingerings[0]
        
        # Check it's actually in open position
        max_fret = max([pos.fret for pos in top_fingering.positions])
        assert max_fret <= 4, f"Top C major fingering should be in open position, max fret: {max_fret}"
        
        # Check it has some open strings
        has_open_strings = any(pos.fret == 0 for pos in top_fingering.positions)
        assert has_open_strings, "Open position C major should have open strings"


class TestMusicalIntelligence:
    """Test that the system makes musically intelligent choices"""
    
    def test_common_chord_progression(self):
        """Test fingerings for a common chord progression make sense"""
        progression = ['C', 'Am', 'F', 'G']  # vi-IV-I-V in C major
        
        fingering_results = {}
        for chord in progression:
            fingerings = generate_chord_fingerings(chord, max_results=1)
            fingering_results[chord] = fingerings[0] if fingerings else None
        
        # All chords should have fingerings
        for chord in progression:
            assert fingering_results[chord] is not None, f"No fingering for {chord}"
        
        # Check that the fingerings are reasonable for a progression
        # (This is a basic test - more sophisticated voice leading could be tested)
        for chord, fingering in fingering_results.items():
            assert fingering.is_playable(), f"{chord} fingering is not playable"
            
            # Should contain the chord tones
            chord_obj = fingering.chord
            if chord_obj:
                chord_notes = chord_obj.get_notes()
                assert fingering.contains_notes(chord_notes), \
                    f"{chord} fingering doesn't contain required chord tones"
    
    def test_jazz_chord_handling(self):
        """Test that jazz chords are handled reasonably"""
        jazz_chords = ['Cmaj7', 'Dm7', 'G7']
        
        for chord_name in jazz_chords:
            fingerings = generate_chord_fingerings(chord_name, max_results=2)
            
            assert len(fingerings) > 0, f"No fingerings for {chord_name}"
            
            # Check the top fingering
            top_fingering = fingerings[0]
            
            # Should be playable
            assert top_fingering.is_playable(), f"{chord_name} top fingering not playable"
            
            # Should have at least 4 notes (seventh chords need the 7th)
            assert len(top_fingering.positions) >= 4, \
                f"{chord_name} should have at least 4 notes, got {len(top_fingering.positions)}"
            
            # Should contain the seventh
            chord_notes = top_fingering.chord.get_notes()
            fingering_notes = top_fingering.get_notes()
            
            # Check that key chord tones are present
            note_names = {note.name for note in fingering_notes}
            if chord_name == 'Cmaj7':
                assert 'B' in note_names, "Cmaj7 should contain B (major 7th)"
            elif chord_name in ['Dm7', 'G7']:
                assert 'C' in note_names or 'F' in note_names, \
                    f"{chord_name} should contain the 7th"


if __name__ == "__main__":
    pytest.main([__file__])