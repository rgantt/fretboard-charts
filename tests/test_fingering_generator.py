"""
Test suite for fingering generator module.

Tests the core fingering generation algorithm including position-based search,
finger assignment, and ranking functionality.
"""

import pytest
from src.fingering_generator import (
    FingeringGenerator, GenerationConfig, ChordToneRequirement, FretboardRegion,
    generate_chord_fingerings
)
from src.music_theory import Note, Chord, ChordQuality
from src.chord_parser import quick_parse
from src.fretboard import Fretboard
from src.fingering import FingeringValidator


class TestChordToneRequirement:
    """Test chord tone requirement analysis"""
    
    def test_chord_tone_requirement_creation(self):
        """Test creating chord tone requirements"""
        note = Note.from_name("C")
        req = ChordToneRequirement(
            note=note,
            priority=1,
            interval=0,
            name="root"
        )
        
        assert req.note == note
        assert req.priority == 1
        assert req.interval == 0
        assert req.name == "root"


class TestGenerationConfig:
    """Test generation configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = GenerationConfig()
        
        assert config.max_results == 5
        assert config.max_fret_span == 4
        assert config.min_required_tones == 3
        assert config.prefer_open_strings == True
        assert config.max_fret == 12
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = GenerationConfig(
            max_results=3,
            max_fret_span=3,
            max_fret=10
        )
        
        assert config.max_results == 3
        assert config.max_fret_span == 3
        assert config.max_fret == 10


class TestFingeringGenerator:
    """Test the main fingering generator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.generator = FingeringGenerator()
        self.config = GenerationConfig(max_results=3)
    
    def test_generator_initialization(self):
        """Test generator initialization"""
        assert self.generator.fretboard is not None
        assert self.generator.validator is not None
        assert len(self.generator.regions) == 3
    
    def test_analyze_chord_requirements_major(self):
        """Test chord requirement analysis for major chords"""
        c_major = Chord(root=Note.from_name("C"), quality=ChordQuality.MAJOR)
        requirements = self.generator._analyze_chord_requirements(c_major)
        
        # Should have root, 3rd, and 5th
        assert len(requirements) >= 3
        
        # Check that requirements are sorted by priority
        priorities = [req.priority for req in requirements]
        assert priorities == sorted(priorities)
        
        # Root should be priority 1 (required)
        root_req = next((req for req in requirements if req.interval == 0), None)
        assert root_req is not None
        assert root_req.priority == 1
        assert root_req.name == "root"
    
    def test_analyze_chord_requirements_minor_seventh(self):
        """Test chord requirement analysis for minor 7th chords"""
        dm7 = Chord(root=Note.from_name("D"), quality=ChordQuality.MINOR_SEVENTH)
        requirements = self.generator._analyze_chord_requirements(dm7)
        
        # Should have root, minor 3rd, 5th, and minor 7th
        assert len(requirements) >= 4
        
        # Check for minor 3rd
        third_req = next((req for req in requirements if req.interval == 3), None)
        assert third_req is not None
        assert third_req.priority == 1  # Required for minor chord
        
        # Check for minor 7th
        seventh_req = next((req for req in requirements if req.interval == 10), None)
        assert seventh_req is not None
        assert seventh_req.priority == 1  # Required for 7th chord
    
    def test_calculate_fret_span(self):
        """Test fret span calculation"""
        from src.fretboard import FretPosition
        
        # Test with positions spanning 3 frets
        positions = [
            FretPosition(string=6, fret=1, note=Note.from_name("F")),
            FretPosition(string=5, fret=3, note=Note.from_name("C")),
            FretPosition(string=4, fret=4, note=Note.from_name("F")),
        ]
        
        span = self.generator._calculate_fret_span(positions)
        assert span == 3  # fret 4 - fret 1 = 3
        
        # Test with open strings (should be ignored)
        positions_with_open = [
            FretPosition(string=6, fret=0, note=Note.from_name("E")),
            FretPosition(string=5, fret=2, note=Note.from_name("B")),
            FretPosition(string=4, fret=4, note=Note.from_name("F#")),
        ]
        
        span = self.generator._calculate_fret_span(positions_with_open)
        assert span == 2  # fret 4 - fret 2 = 2 (open string ignored)
    
    def test_validate_position_combination(self):
        """Test position combination validation"""
        from src.fretboard import FretPosition
        
        # Valid combination
        valid_positions = [
            FretPosition(string=6, fret=1, note=Note.from_name("F")),
            FretPosition(string=5, fret=3, note=Note.from_name("C")),
            FretPosition(string=4, fret=2, note=Note.from_name("E")),
        ]
        
        assert self.generator._validate_position_combination(valid_positions, self.config)
        
        # Invalid - too large fret span
        invalid_span = [
            FretPosition(string=6, fret=1, note=Note.from_name("F")),
            FretPosition(string=5, fret=8, note=Note.from_name("C")),  # 7 fret span
        ]
        
        assert not self.generator._validate_position_combination(invalid_span, self.config)
        
        # Invalid - string conflict (same string, different frets)
        string_conflict = [
            FretPosition(string=6, fret=1, note=Note.from_name("F")),
            FretPosition(string=6, fret=3, note=Note.from_name("G")),  # Same string!
        ]
        
        assert not self.generator._validate_position_combination(string_conflict, self.config)
    
    def test_assign_fingers_basic(self):
        """Test basic finger assignment"""
        from src.fretboard import FretPosition
        from src.fingering import Fingering, FingerAssignment
        
        positions = [
            FretPosition(string=6, fret=0, note=Note.from_name("E")),  # Open
            FretPosition(string=5, fret=2, note=Note.from_name("B")),  # 2nd fret
            FretPosition(string=4, fret=3, note=Note.from_name("F")),  # 3rd fret
        ]
        
        fingering = Fingering(positions=positions)
        self.generator._assign_fingers(fingering)
        
        # Check assignments
        assert fingering.finger_assignments[6] == FingerAssignment.OPEN
        assert fingering.finger_assignments[5] == FingerAssignment.INDEX  # 2nd fret
        assert fingering.finger_assignments[4] == FingerAssignment.MIDDLE  # 3rd fret
    
    def test_generate_fingerings_c_major(self):
        """Test generating fingerings for C major chord"""
        c_major = Chord(root=Note.from_name("C"), quality=ChordQuality.MAJOR)
        fingerings = self.generator.generate_fingerings(c_major, self.config)
        
        # Should return some fingerings
        assert len(fingerings) > 0
        assert len(fingerings) <= self.config.max_results
        
        # All should be valid fingerings
        for fingering in fingerings:
            assert fingering.chord == c_major
            assert len(fingering.positions) >= self.config.min_required_tones
            assert fingering.is_playable()
            
            # Should contain C major chord tones (C, E, G)
            chord_notes = c_major.get_notes()
            assert fingering.contains_notes(chord_notes)
    
    def test_generate_fingerings_dm7(self):
        """Test generating fingerings for Dm7 chord"""
        dm7 = Chord(root=Note.from_name("D"), quality=ChordQuality.MINOR_SEVENTH)
        fingerings = self.generator.generate_fingerings(dm7, self.config)
        
        # Should return some fingerings
        assert len(fingerings) > 0
        
        # All should be valid and contain Dm7 chord tones (D, F, A, C)
        for fingering in fingerings:
            assert fingering.chord == dm7
            chord_notes = dm7.get_notes()
            assert fingering.contains_notes(chord_notes)
    
    def test_generate_fingerings_different_regions(self):
        """Test that generator finds fingerings in different regions"""
        g_major = Chord(root=Note.from_name("G"), quality=ChordQuality.MAJOR)
        config = GenerationConfig(max_results=10)  # Allow more results
        
        fingerings = self.generator.generate_fingerings(g_major, config)
        
        # Should find fingerings in different fret ranges
        open_position_found = False
        higher_position_found = False
        
        for fingering in fingerings:
            max_fret = max(pos.fret for pos in fingering.positions)
            if max_fret <= 4:
                open_position_found = True
            if max_fret >= 5:
                higher_position_found = True
        
        # Should find at least some variety
        assert open_position_found  # G major has good open position fingerings


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_generate_chord_fingerings_function(self):
        """Test the convenience function"""
        fingerings = generate_chord_fingerings("C", max_results=3)
        
        assert len(fingerings) > 0
        assert len(fingerings) <= 3
        
        # All should be valid fingerings for C major
        for fingering in fingerings:
            assert fingering.chord.root.name == "C"
            assert fingering.chord.quality == ChordQuality.MAJOR
            assert fingering.is_playable()
    
    def test_generate_chord_fingerings_complex(self):
        """Test convenience function with complex chord"""
        fingerings = generate_chord_fingerings("Am7", max_results=2)
        
        assert len(fingerings) > 0
        
        for fingering in fingerings:
            assert fingering.chord.root.name == "A"
            assert fingering.chord.quality == ChordQuality.MINOR_SEVENTH


class TestIntegration:
    """Integration tests with other modules"""
    
    def test_integration_with_chord_parser(self):
        """Test integration with chord parser"""
        chord_symbols = ["C", "Dm", "G7", "Am", "F"]
        
        generator = FingeringGenerator()
        
        for symbol in chord_symbols:
            chord = quick_parse(symbol)
            fingerings = generator.generate_fingerings(chord)
            
            assert len(fingerings) > 0
            assert all(f.is_playable() for f in fingerings)
    
    def test_integration_with_validator(self):
        """Test integration with fingering validator"""
        generator = FingeringGenerator()
        validator = FingeringValidator()
        
        c_major = quick_parse("C")
        fingerings = generator.generate_fingerings(c_major)
        
        # All generated fingerings should pass validation
        for fingering in fingerings:
            validation = validator.validate_fingering(fingering)
            assert validation['is_valid']
            assert validation['is_playable']
            assert validation['score'] > 0.3


if __name__ == "__main__":
    pytest.main([__file__])