"""
Test suite for chord patterns module.

Tests the chord pattern database and pattern matching functionality.
"""

import pytest
from src.chord_patterns import (
    ChordPattern, ChordPatternDatabase, CHORD_PATTERNS, PatternType
)
from src.music_theory import Note, Chord, ChordQuality
from src.fingering import FingerAssignment


class TestChordPattern:
    """Test chord pattern representation"""
    
    def test_chord_pattern_creation(self):
        """Test creating a chord pattern"""
        pattern = ChordPattern(
            name="test_pattern",
            quality=ChordQuality.MAJOR,
            frets=[None, 3, 2, 0, 1, 0],
            root_string=5,
            root_fret=3,
            finger_assignments={5: FingerAssignment.RING},
            pattern_type=PatternType.OPEN
        )
        
        assert pattern.name == "test_pattern"
        assert pattern.quality == ChordQuality.MAJOR
        assert len(pattern.frets) == 6
        assert pattern.root_string == 5
        assert pattern.root_fret == 3


class TestChordPatternDatabase:
    """Test the chord pattern database"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.db = ChordPatternDatabase()
    
    def test_database_initialization(self):
        """Test that database initializes with patterns"""
        assert len(self.db.patterns) > 0
        
        # Should have patterns for basic chord qualities
        assert ChordQuality.MAJOR in self.db.patterns
        assert ChordQuality.MINOR in self.db.patterns
        assert ChordQuality.DOMINANT_SEVENTH in self.db.patterns
    
    def test_get_patterns_for_quality(self):
        """Test getting patterns by chord quality"""
        major_patterns = self.db.get_patterns_for_quality(ChordQuality.MAJOR)
        assert len(major_patterns) > 0
        
        # All patterns should be for major chords
        for pattern in major_patterns:
            assert pattern.quality == ChordQuality.MAJOR
        
        minor_patterns = self.db.get_patterns_for_quality(ChordQuality.MINOR)
        assert len(minor_patterns) > 0
        
        # All patterns should be for minor chords
        for pattern in minor_patterns:
            assert pattern.quality == ChordQuality.MINOR
    
    def test_find_matching_patterns_c_major(self):
        """Test finding patterns for C major"""
        c_note = Note.from_name("C")
        matching = self.db.find_matching_patterns(c_note, ChordQuality.MAJOR)
        
        # Should find the open C major pattern
        assert len(matching) > 0
        
        # All matches should be major chord patterns
        for pattern in matching:
            assert pattern.quality == ChordQuality.MAJOR
    
    def test_find_matching_patterns_a_minor(self):
        """Test finding patterns for A minor"""
        a_note = Note.from_name("A")
        matching = self.db.find_matching_patterns(a_note, ChordQuality.MINOR)
        
        # Should find the open Am pattern
        assert len(matching) > 0
        
        # All matches should be minor chord patterns
        for pattern in matching:
            assert pattern.quality == ChordQuality.MINOR
    
    def test_find_matching_patterns_no_match(self):
        """Test finding patterns when no match exists"""
        f_sharp = Note.from_name("F#")
        matching = self.db.find_matching_patterns(f_sharp, ChordQuality.MAJOR)
        
        # Should return empty list (no open F# major pattern)
        assert len(matching) == 0
    
    def test_pattern_to_fingering_c_major(self):
        """Test converting C major pattern to fingering"""
        c_chord = Chord(root=Note.from_name("C"), quality=ChordQuality.MAJOR)
        c_patterns = self.db.find_matching_patterns(c_chord.root, c_chord.quality)
        
        assert len(c_patterns) > 0
        
        pattern = c_patterns[0]  # Take first C major pattern
        fingering = self.db.pattern_to_fingering(pattern, c_chord)
        
        # Should be a valid fingering
        assert fingering is not None
        assert len(fingering.positions) > 0
        assert fingering.chord == c_chord
        
        # Should contain C major chord tones
        chord_notes = c_chord.get_notes()
        assert fingering.contains_notes(chord_notes)
        
        # Should have finger assignments
        assert len(fingering.finger_assignments) > 0
    
    def test_pattern_to_fingering_a_minor(self):
        """Test converting A minor pattern to fingering"""
        a_minor = Chord(root=Note.from_name("A"), quality=ChordQuality.MINOR)
        patterns = self.db.find_matching_patterns(a_minor.root, a_minor.quality)
        
        assert len(patterns) > 0
        
        pattern = patterns[0]
        fingering = self.db.pattern_to_fingering(pattern, a_minor)
        
        # Should be a valid fingering
        assert fingering is not None
        assert fingering.chord == a_minor
        
        # Should contain A minor chord tones
        chord_notes = a_minor.get_notes()
        assert fingering.contains_notes(chord_notes)


class TestGlobalPatternDatabase:
    """Test the global pattern database instance"""
    
    def test_global_instance_exists(self):
        """Test that global CHORD_PATTERNS instance exists"""
        assert CHORD_PATTERNS is not None
        assert isinstance(CHORD_PATTERNS, ChordPatternDatabase)
    
    def test_global_instance_has_patterns(self):
        """Test that global instance has patterns loaded"""
        major_patterns = CHORD_PATTERNS.get_patterns_for_quality(ChordQuality.MAJOR)
        assert len(major_patterns) > 0
        
        minor_patterns = CHORD_PATTERNS.get_patterns_for_quality(ChordQuality.MINOR)
        assert len(minor_patterns) > 0


class TestOpenChordPatterns:
    """Test specific open chord patterns"""
    
    def test_open_c_major_pattern(self):
        """Test the open C major pattern specifically"""
        c_note = Note.from_name("C")
        patterns = CHORD_PATTERNS.find_matching_patterns(c_note, ChordQuality.MAJOR)
        
        # Find the open C major pattern
        c_pattern = None
        for pattern in patterns:
            if "C_major" in pattern.name:
                c_pattern = pattern
                break
        
        assert c_pattern is not None
        assert c_pattern.frets == [None, 3, 2, 0, 1, 0]  # x-3-2-0-1-0
        assert c_pattern.root_string == 5
        assert c_pattern.root_fret == 3
        assert c_pattern.pattern_type == PatternType.OPEN
    
    def test_open_g_major_pattern(self):
        """Test the open G major pattern specifically"""
        g_note = Note.from_name("G")
        patterns = CHORD_PATTERNS.find_matching_patterns(g_note, ChordQuality.MAJOR)
        
        # Should find the open G major pattern
        assert len(patterns) > 0
        
        g_pattern = patterns[0]
        assert g_pattern.frets == [3, 2, 0, 0, 3, 3]  # 3-2-0-0-3-3
        assert g_pattern.root_string == 6
        assert g_pattern.root_fret == 3
    
    def test_open_a_minor_pattern(self):
        """Test the open A minor pattern specifically"""
        a_note = Note.from_name("A")
        patterns = CHORD_PATTERNS.find_matching_patterns(a_note, ChordQuality.MINOR)
        
        # Should find the open Am pattern
        assert len(patterns) > 0
        
        am_pattern = patterns[0]
        assert am_pattern.frets == [None, 0, 2, 2, 1, 0]  # x-0-2-2-1-0
        assert am_pattern.root_string == 5
        assert am_pattern.root_fret == 0


class TestPatternValidation:
    """Test pattern validation and conversion"""
    
    def test_all_patterns_convert_to_valid_fingerings(self):
        """Test that all patterns can be converted to valid fingerings"""
        test_chords = [
            Chord(root=Note.from_name("C"), quality=ChordQuality.MAJOR),
            Chord(root=Note.from_name("G"), quality=ChordQuality.MAJOR),
            Chord(root=Note.from_name("D"), quality=ChordQuality.MAJOR),
            Chord(root=Note.from_name("A"), quality=ChordQuality.MAJOR),
            Chord(root=Note.from_name("E"), quality=ChordQuality.MAJOR),
            Chord(root=Note.from_name("A"), quality=ChordQuality.MINOR),
            Chord(root=Note.from_name("E"), quality=ChordQuality.MINOR),
            Chord(root=Note.from_name("D"), quality=ChordQuality.MINOR),
        ]
        
        for chord in test_chords:
            patterns = CHORD_PATTERNS.find_matching_patterns(chord.root, chord.quality)
            
            for pattern in patterns:
                fingering = CHORD_PATTERNS.pattern_to_fingering(pattern, chord)
                
                # Should be a valid, playable fingering
                assert fingering is not None
                assert len(fingering.positions) >= 3  # At least 3 notes
                assert fingering.is_playable()
                
                # Should contain the required chord tones
                chord_notes = chord.get_notes()
                assert fingering.contains_notes(chord_notes)


if __name__ == "__main__":
    pytest.main([__file__])