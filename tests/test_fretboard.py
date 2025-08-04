"""
Test suite for fretboard module.

Tests the guitar fretboard modeling, tuning configurations, and note-to-position mapping.
"""

import pytest
from src.fretboard import (
    FretPosition, GuitarTuning, Fretboard, StringNumber,
    STANDARD_TUNING, DROP_D_TUNING, DEFAULT_FRETBOARD
)
from src.music_theory import Note


class TestFretPosition:
    """Test cases for FretPosition class"""
    
    def test_fret_position_creation(self):
        """Test creating valid fret positions"""
        c_note = Note.from_name("C")
        pos = FretPosition(string=1, fret=0, note=c_note)
        
        assert pos.string == 1
        assert pos.fret == 0
        assert pos.note == c_note
    
    def test_open_string_detection(self):
        """Test open string detection"""
        open_pos = FretPosition(string=6, fret=0, note=Note.from_name("E"))
        fretted_pos = FretPosition(string=6, fret=1, note=Note.from_name("F"))
        
        assert open_pos.is_open_string()
        assert not fretted_pos.is_open_string()
    
    def test_invalid_string_numbers(self):
        """Test validation of string numbers"""
        with pytest.raises(ValueError):
            FretPosition(string=0, fret=0, note=Note.from_name("C"))
        
        with pytest.raises(ValueError):
            FretPosition(string=7, fret=0, note=Note.from_name("C"))
    
    def test_invalid_fret_numbers(self):
        """Test validation of fret numbers"""
        with pytest.raises(ValueError):
            FretPosition(string=1, fret=-1, note=Note.from_name("C"))
        
        with pytest.raises(ValueError):
            FretPosition(string=1, fret=25, note=Note.from_name("C"))
    
    def test_string_representation(self):
        """Test string representation of fret positions"""
        pos = FretPosition(string=3, fret=2, note=Note.from_name("A"))
        assert "String 3" in str(pos)
        assert "Fret 2" in str(pos)
        assert "A" in str(pos)


class TestGuitarTuning:
    """Test cases for GuitarTuning class"""
    
    def test_standard_tuning(self):
        """Test standard tuning creation"""
        standard = GuitarTuning.standard()
        
        assert standard.name == "Standard"
        assert len(standard.notes) == 6
        
        # Check the notes (low to high)
        expected_notes = ["E", "A", "D", "G", "B", "E"]
        actual_notes = [note.name for note in standard.notes]
        assert actual_notes == expected_notes
    
    def test_drop_d_tuning(self):
        """Test Drop D tuning creation"""
        drop_d = GuitarTuning.drop_d()
        
        assert drop_d.name == "Drop D"
        expected_notes = ["D", "A", "D", "G", "B", "E"]
        actual_notes = [note.name for note in drop_d.notes]
        assert actual_notes == expected_notes
    
    def test_get_open_note(self):
        """Test getting open notes for each string"""
        standard = GuitarTuning.standard()
        
        # Test all strings
        assert standard.get_open_note(6).name == "E"  # Low E
        assert standard.get_open_note(5).name == "A"
        assert standard.get_open_note(4).name == "D"
        assert standard.get_open_note(3).name == "G"
        assert standard.get_open_note(2).name == "B"
        assert standard.get_open_note(1).name == "E"  # High E
    
    def test_invalid_string_numbers(self):
        """Test validation of string numbers in get_open_note"""
        standard = GuitarTuning.standard()
        
        with pytest.raises(ValueError):
            standard.get_open_note(0)
        
        with pytest.raises(ValueError):
            standard.get_open_note(7)
    
    def test_invalid_tuning_creation(self):
        """Test validation of tuning with wrong number of notes"""
        with pytest.raises(ValueError):
            GuitarTuning("Invalid", [Note.from_name("E")])  # Only 1 note
        
        with pytest.raises(ValueError):
            GuitarTuning("Invalid", [Note.from_name("E")] * 7)  # 7 notes
    
    def test_tuning_string_representation(self):
        """Test string representation of tunings"""
        standard = GuitarTuning.standard()
        tuning_str = str(standard)
        
        assert "Standard tuning" in tuning_str
        assert "E-A-D-G-B-E" in tuning_str


class TestFretboard:
    """Test cases for Fretboard class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.fretboard = Fretboard()
    
    def test_fretboard_creation(self):
        """Test creating a fretboard"""
        assert self.fretboard.tuning.name == "Standard"
        assert self.fretboard.num_frets == 22
    
    def test_custom_fretboard(self):
        """Test creating fretboard with custom settings"""
        drop_d_board = Fretboard(tuning=DROP_D_TUNING, num_frets=24)
        
        assert drop_d_board.tuning.name == "Drop D"
        assert drop_d_board.num_frets == 24
    
    def test_get_note_at_position(self):
        """Test getting notes at specific positions"""
        # Test open strings
        assert self.fretboard.get_note_at_position(6, 0).name == "E"  # Low E open
        assert self.fretboard.get_note_at_position(1, 0).name == "E"  # High E open
        
        # Test fretted positions
        # 6th string, 1st fret should be F (E + 1 semitone)
        f_note = self.fretboard.get_note_at_position(6, 1)
        assert f_note.pitch_class == 5  # F = 5
        
        # 5th string, 2nd fret should be B (A + 2 semitones)
        b_note = self.fretboard.get_note_at_position(5, 2)
        assert b_note.pitch_class == 11  # B = 11
    
    def test_invalid_positions(self):
        """Test validation of invalid positions"""
        with pytest.raises(ValueError):
            self.fretboard.get_note_at_position(0, 0)  # Invalid string
        
        with pytest.raises(ValueError):
            self.fretboard.get_note_at_position(1, 23)  # Invalid fret
    
    def test_get_positions_for_note(self):
        """Test finding positions for a specific note"""
        c_note = Note.from_name("C")
        positions = self.fretboard.get_positions_for_note(c_note)
        
        # There should be multiple positions for C on the fretboard
        assert len(positions) > 1
        
        # All positions should produce the same pitch class
        for pos in positions:
            assert pos.note.pitch_class == c_note.pitch_class
    
    def test_get_positions_with_max_fret(self):
        """Test finding positions with fret limit"""
        c_note = Note.from_name("C")
        
        all_positions = self.fretboard.get_positions_for_note(c_note)
        limited_positions = self.fretboard.get_positions_for_note(c_note, max_fret=5)
        
        # Limited search should return fewer or equal positions
        assert len(limited_positions) <= len(all_positions)
        
        # All limited positions should be within the fret limit
        for pos in limited_positions:
            assert pos.fret <= 5
    
    def test_get_positions_for_multiple_notes(self):
        """Test finding positions for multiple notes"""
        c_note = Note.from_name("C")
        e_note = Note.from_name("E")
        g_note = Note.from_name("G")
        
        positions_dict = self.fretboard.get_positions_for_notes([c_note, e_note, g_note])
        
        assert len(positions_dict) == 3
        assert c_note in positions_dict
        assert e_note in positions_dict
        assert g_note in positions_dict
        
        # Each note should have multiple positions
        for note, positions in positions_dict.items():
            assert len(positions) > 0
    
    def test_get_open_strings(self):
        """Test getting all open string positions"""
        open_positions = self.fretboard.get_open_strings()
        
        assert len(open_positions) == 6
        
        # All should be fret 0
        for pos in open_positions:
            assert pos.fret == 0
        
        # Should cover all strings
        strings = {pos.string for pos in open_positions}
        assert strings == {1, 2, 3, 4, 5, 6}
    
    def test_validate_position(self):
        """Test position validation"""
        assert self.fretboard.validate_position(1, 0)  # Valid
        assert self.fretboard.validate_position(6, 22)  # Valid
        
        assert not self.fretboard.validate_position(0, 0)  # Invalid string
        assert not self.fretboard.validate_position(1, 23)  # Invalid fret
    
    def test_get_fretboard_span(self):
        """Test calculating fret span for positions"""
        positions = [
            FretPosition(1, 0, Note.from_name("E")),  # Open - should be ignored
            FretPosition(2, 2, Note.from_name("C")),
            FretPosition(3, 5, Note.from_name("G")),
        ]
        
        span = self.fretboard.get_fretboard_span(positions)
        assert span == 3  # Fret 5 - fret 2 = 3
    
    def test_positions_to_chord_shape(self):
        """Test converting positions to chord shape"""
        positions = [
            FretPosition(6, 0, Note.from_name("E")),  # Low E open
            FretPosition(4, 2, Note.from_name("E")),  # D string, 2nd fret
            FretPosition(3, 1, Note.from_name("G#")), # G string, 1st fret
        ]
        
        shape = self.fretboard.positions_to_chord_shape(positions)
        
        # Should be a list of 6 elements
        assert len(shape) == 6
        
        # Check the specific fret positions
        assert shape[0] == 0   # String 6 (index 0) - open
        assert shape[1] is None  # String 5 (index 1) - muted
        assert shape[2] == 2   # String 4 (index 2) - 2nd fret
        assert shape[3] == 1   # String 3 (index 3) - 1st fret
        assert shape[4] is None  # String 2 (index 4) - muted
        assert shape[5] is None  # String 1 (index 5) - muted
    
    def test_find_note_intervals(self):
        """Test finding positions for intervals from a root note"""
        c_note = Note.from_name("C")
        intervals = [0, 4, 7]  # Root, major third, perfect fifth (C major chord)
        
        interval_positions = self.fretboard.find_note_intervals(c_note, intervals, max_fret=12)
        
        assert len(interval_positions) == 3
        assert 0 in interval_positions  # Root
        assert 4 in interval_positions  # Major third
        assert 7 in interval_positions  # Perfect fifth
        
        # Each interval should have multiple positions
        for interval, positions in interval_positions.items():
            assert len(positions) > 0
            # All positions should be within fret limit
            for pos in positions:
                assert pos.fret <= 12


class TestConstants:
    """Test pre-defined constants"""
    
    def test_standard_tuning_constant(self):
        """Test the STANDARD_TUNING constant"""
        assert STANDARD_TUNING.name == "Standard"
        assert len(STANDARD_TUNING.notes) == 6
    
    def test_drop_d_tuning_constant(self):
        """Test the DROP_D_TUNING constant"""
        assert DROP_D_TUNING.name == "Drop D"
        assert DROP_D_TUNING.get_open_note(6).name == "D"
    
    def test_default_fretboard_constant(self):
        """Test the DEFAULT_FRETBOARD constant"""
        assert DEFAULT_FRETBOARD.tuning.name == "Standard"
        assert DEFAULT_FRETBOARD.num_frets == 22
